#coding:utf-8
"""卡类规则：Ruler 解析、消费权限/折扣定价、折扣分类同步。"""
import re
from datetime import date
from decimal import Decimal

from django.db import connection


_TIER_RE = re.compile(r'^(?P<ordinal>\d+)(?:st|nd|rd|th)times$', re.I)


def _to_decimal(value):
    try:
        return Decimal(str(value).strip())
    except Exception:
        return None


def parse_ruler(text):
    """解析 #key=value# 格式的逻辑卡规则。

    示例：#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#
    返回 {ttype, itemcode, tiers: [(seq, price)], others}；无法解析返回 {}。
    """
    if not text or '#' not in text:
        return {}
    parts = [p for p in (text or '').split('#') if p and '=' in p]
    data = {}
    for part in parts:
        key, _, value = part.partition('=')
        key = key.strip().lower()
        value = value.strip()
        if not key:
            continue
        data[key] = value

    ttype = data.get('ttype', '').upper()
    itemcode = data.get('srvcode') or data.get('gcode') or data.get('itemcode') or ''
    if not ttype or not itemcode:
        return {}

    tiers = []
    for key, val in data.items():
        m = _TIER_RE.match(key)
        if m:
            price = _to_decimal(val)
            if price is not None:
                tiers.append((int(m.group('ordinal')), price))
    tiers.sort(key=lambda x: x[0])

    others = _to_decimal(data['others']) if data.get('others') else None
    return {'ttype': ttype, 'itemcode': itemcode, 'tiers': tiers, 'others': others}


def ruler_lookup(parsed, usecount):
    """按已用次数取逻辑卡阶梯价；超出阶梯用 others，未配置 others 用最后一档。"""
    if not parsed or not parsed.get('tiers'):
        return None
    for seq, price in parsed['tiers']:
        if usecount + 1 <= seq:
            return price
    if parsed.get('others') is not None:
        return parsed['others']
    return parsed['tiers'][-1][1]


def _column_exists(table, column):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
            [table, column],
        )
        row = cur.fetchone()
        return bool(row and row[0])


def ensure_card_rule_schema():
    """幂等补齐卡类规则所需列（开发/测试/生产库均可执行）。"""
    changes = []
    with connection.cursor() as cur:
        if not _column_exists('cardvsdi', 'consume_flag'):
            cur.execute(
                "ALTER TABLE cardvsdi "
                "ADD COLUMN consume_flag varchar(8) NULL DEFAULT 'Y' AFTER flag"
            )
            changes.append('cardvsdi.consume_flag')
        if not _column_exists('cardinfo', 'logic_cycle_month'):
            cur.execute(
                "ALTER TABLE cardinfo ADD COLUMN logic_cycle_month varchar(7) NULL"
            )
            changes.append('cardinfo.logic_cycle_month')
        if not _column_exists('cardinfo', 'logic_usecount'):
            cur.execute(
                "ALTER TABLE cardinfo ADD COLUMN logic_usecount int NULL DEFAULT 0"
            )
            changes.append('cardinfo.logic_usecount')
        # 老数据一次性迁移：flag 曾表示“可否消费”，迁到 consume_flag 后 flag 只作软删除。
        # 只处理 consume_flag 为空的历史行，避免把后来软删除的行重新置为 Y。
        cur.execute(
            "UPDATE cardvsdi SET consume_flag = COALESCE(NULLIF(flag, ''), 'Y'), flag = 'Y' "
            "WHERE consume_flag IS NULL OR consume_flag = ''"
        )
    return changes


def card_use_for_month(cardinfo, now_month=None):
    """逻辑卡当前自然月已到店次数；跨自然月视为 0。"""
    if cardinfo is None:
        return 0
    month = now_month or date.today().strftime('%Y-%m')
    if (cardinfo.logic_cycle_month or '') != month:
        return 0
    return cardinfo.logic_usecount or 0


def advance_card_use(cardinfo, now_month=None):
    """逻辑卡到店次数 +1，跨自然月自动重置。"""
    month = now_month or date.today().strftime('%Y-%m')
    if (cardinfo.logic_cycle_month or '') != month:
        cardinfo.logic_cycle_month = month
        cardinfo.logic_usecount = 0
    cardinfo.logic_usecount = (cardinfo.logic_usecount or 0) + 1


def cardtype_bound_itemcode(cardtype):
    """返回卡类绑定的服务/商品编号；无绑定返回 None。"""
    if not cardtype:
        return None
    from baseinfo.models import Goods, Serviece

    ttype = (cardtype.ttype or '').upper()
    if cardtype.sguuid:
        try:
            if ttype == 'G':
                goods = Goods.objects.filter(uuid=cardtype.sguuid, flag='Y').first()
                if goods:
                    return goods.gcode or ''
            else:
                srv = Serviece.objects.filter(uuid=cardtype.sguuid, flag='Y').first()
                if srv:
                    return srv.svrcdoe or ''
        except Exception:
            pass
    # 计次卡历史约定：卡类编号 = 项目编号
    return cardtype.cardtype or None


def _blocked(reason):
    return {
        'allowed': False,
        'price': Decimal('0'),
        'source': 'blocked',
        'reason': reason,
        'discounttype': '',
        'disc': None,
    }


def resolve_card_item_price(
    company,
    cardtype,
    cardinfo,
    *,
    ttype='',
    itemcode='',
    discountclass='',
    topcode='',
    original_price=Decimal('0'),
    now_month=None,
):
    """计算某卡支付某项目时的单价与消费权限。

    优先级：逻辑卡 Ruler 阶梯价 > consume_flag 权限 > 折扣分类规则 > 服务大类兼容 > 原价。
    """
    from baseinfo.models import CardtypeVsDiscountClass, Cardvsdi

    ttype = (ttype or '').upper()
    original_price = Decimal(str(original_price or 0))
    if cardtype is None:
        return {
            'allowed': True,
            'price': original_price,
            'source': 'original',
            'reason': '',
            'discounttype': '',
            'disc': None,
        }

    comptype = (cardtype.comptype or '').strip().lower()

    # 逻辑卡：计费卡 + 已配置 Ruler
    if comptype == 'amount' and cardtype.ruler_id:
        parsed = parse_ruler(cardtype.ruler.ruler if cardtype.ruler else '')
        if not parsed:
            return _blocked('逻辑卡规则未配置或格式错误')
        if parsed['ttype'] != ttype or parsed['itemcode'] != (itemcode or ''):
            return _blocked('此卡绑定项目不匹配')
        usecount = card_use_for_month(cardinfo, now_month)
        price = ruler_lookup(parsed, usecount)
        if price is None:
            return _blocked('逻辑卡未找到对应阶梯价')
        return {
            'allowed': True,
            'price': price,
            'source': 'ruler',
            'reason': '',
            'discounttype': 'PRICE',
            'disc': None,
        }

    # 时效卡：校验绑定项目 + 有效期，不扣次数/金额
    if comptype == 'period':
        bound = cardtype_bound_itemcode(cardtype)
        if bound and bound != (itemcode or ''):
            return _blocked('此卡绑定项目不匹配')
        if cardinfo and cardinfo.valdate:
            if cardinfo.valdate < date.today().strftime('%Y%m%d'):
                return _blocked('卡已过期')
        return {
            'allowed': True,
            'price': original_price,
            'source': 'period',
            'reason': '',
            'discounttype': '',
            'disc': None,
        }

    # 计次卡：只校验绑定项目，按次数扣减
    if comptype == 'times':
        bound = cardtype_bound_itemcode(cardtype)
        if bound and bound != (itemcode or ''):
            return _blocked('此卡绑定项目不匹配')
        return {
            'allowed': True,
            'price': original_price,
            'source': 'times',
            'reason': '',
            'discounttype': '',
            'disc': None,
        }

    # 计费卡：折扣分类规则优先，服务大类兼容回退
    if comptype == 'amount':
        rule = CardtypeVsDiscountClass.objects.filter(
            company=company,
            cardtypeuuid=cardtype,
            ttype=ttype,
            discountclass=discountclass or '',
            flag='Y',
        ).first()
        if rule:
            if (rule.consume_flag or 'Y') != 'Y':
                return _blocked('该项目禁止使用此储值卡')
            if rule.discounttype == 'PRICE' and rule.price is not None:
                return {
                    'allowed': True,
                    'price': rule.price,
                    'source': 'discountclass',
                    'reason': '',
                    'discounttype': 'PRICE',
                    'disc': None,
                }
            return {
                'allowed': True,
                'price': original_price * (rule.disc or Decimal('1')),
                'source': 'discountclass',
                'reason': '',
                'discounttype': 'DISC',
                'disc': rule.disc if rule.disc is not None else Decimal('1'),
            }

        legacy = Cardvsdi.objects.filter(
            company=company,
            cardtypeuuid=cardtype,
            ttype=ttype,
            topcode=topcode or '',
            flag='Y',
        ).first()
        if legacy:
            if (legacy.consume_flag or 'Y') != 'Y':
                return _blocked('该项目禁止使用此储值卡')
            if legacy.pricetype == 'PRICE' and legacy.cardvsprice is not None:
                return {
                    'allowed': True,
                    'price': legacy.cardvsprice,
                    'source': 'cardvsdi',
                    'reason': '',
                    'discounttype': 'PRICE',
                    'disc': None,
                }
            return {
                'allowed': True,
                'price': original_price * (legacy.cardvsdisc or Decimal('1')),
                'source': 'cardvsdi',
                'reason': '',
                'discounttype': 'DISC',
                'disc': legacy.cardvsdisc if legacy.cardvsdisc is not None else Decimal('1'),
            }

        return {
            'allowed': True,
            'price': original_price,
            'source': 'original',
            'reason': '',
            'discounttype': '',
            'disc': None,
        }

    # 未知消费模式：允许原价
    return {
        'allowed': True,
        'price': original_price,
        'source': 'original',
        'reason': '',
        'discounttype': '',
        'disc': None,
    }


def sync_card_discount_rules(company=None):
    """把服务/商品大类同步到折扣分类，并把 Cardvsdi 迁移为折扣分类规则。"""
    from baseinfo.models import (
        Appoption, Cardsupertype, CardtypeVsDiscountClass, Cardvsdi,
        Goods, Goodsct, Serviece, Srvtopty,
    )
    from django.db.models import F, Q
    import time

    ensure_card_rule_schema()
    print(f"[sync] 开始同步 company={company or 'ALL'} schema 已就绪", flush=True)
    stats = {
        'srv_categories': 0,
        'goods_categories': 0,
        'skipped_null_categories': 0,
        'items_backfilled': 0,
        'rules_created': 0,
        'rules_updated': 0,
    }

    if company:
        companies = [company]
    else:
        companies = sorted(set(
            list(Srvtopty.objects.values_list('company', flat=True))
            + list(Goodsct.objects.values_list('company', flat=True))
            + list(Cardvsdi.objects.values_list('company', flat=True))
        ))

    for co in companies:
        if not co:
            continue
        t0 = time.time()
        print(f"[sync] 处理公司 {co}: 同步服务/商品大类", flush=True)

        for st in Srvtopty.objects.filter(company=co, flag='Y'):
            code = (st.topcode or '').strip()
            name = (st.ttname or '').strip()
            if not code or not name:
                stats['skipped_null_categories'] += 1
                continue
            Appoption.objects.update_or_create(
                company=co, seg='srvdiscountclass', itemname=code,
                defaults={'itemvalues': name, 'flag': 'Y'},
            )
            stats['srv_categories'] += 1

        for gc in Goodsct.objects.filter(company=co, flag='Y'):
            code = (gc.goodsct or '').strip()
            name = (gc.goodsctname or '').strip()
            if not code or not name:
                stats['skipped_null_categories'] += 1
                continue
            Appoption.objects.update_or_create(
                company=co, seg='goodsdiscountclass', itemname=code,
                defaults={'itemvalues': name, 'flag': 'Y'},
            )
            stats['goods_categories'] += 1

        # 卡大类同步到通用折扣分类，供 ttype=C 的规则使用
        for cs in Cardsupertype.objects.filter(company=co, flag='Y'):
            code = (cs.code or '').strip()
            name = (cs.name or '').strip()
            if not code or not name:
                stats['skipped_null_categories'] += 1
                continue
            Appoption.objects.update_or_create(
                company=co, seg='discountclass', itemname=code,
                defaults={'itemvalues': name, 'flag': 'Y'},
            )

        # 通用折扣分类合并到专用 seg，避免存量项目已有编码失效
        for opt in Appoption.objects.filter(company=co, seg='discountclass', flag='Y'):
            if not (opt.itemname or '').strip():
                continue
            for seg in ('srvdiscountclass', 'goodsdiscountclass'):
                exists = Appoption.objects.filter(
                    company=co, seg=seg, itemname=opt.itemname).exists()
                if not exists:
                    Appoption.objects.create(
                        company=co, seg=seg, itemname=opt.itemname,
                        itemvalues=opt.itemvalues, flag='Y',
                    )

        # 项目折扣分类空值回填（批量，避免逐行 save）
        print(f"[sync] 公司 {co}: 项目 discountclass 空值回填", flush=True)
        sv_qs = Serviece.objects.filter(company=co, flag='Y') \
            .exclude(topcode__isnull=True).exclude(topcode='') \
            .filter(Q(discountclass__isnull=True) | Q(discountclass=''))
        stats['items_backfilled'] += sv_qs.update(discountclass=F('topcode'))

        gd_qs = Goods.objects.filter(company=co, flag='Y') \
            .exclude(goodsct__isnull=True).exclude(goodsct='') \
            .filter(Q(discountclass__isnull=True) | Q(discountclass=''))
        stats['items_backfilled'] += gd_qs.update(discountclass=F('goodsct'))

        # Cardvsdi → 新规则（批量创建/更新）
        print(f"[sync] 公司 {co}: 开始镜像 Cardvsdi 规则", flush=True)
        existing = list(CardtypeVsDiscountClass.objects.filter(company=co, flag='Y'))
        existing_map = {
            (r.cardtype or '', r.ttype or 'S', r.discountclass or ''): r
            for r in existing
        }
        create_objs = []
        update_objs = []

        cv_rows = list(Cardvsdi.objects.filter(company=co, flag='Y').values(
            'cardtype', 'topcode', 'ttype', 'pricetype',
            'cardvsdisc', 'cardvsprice', 'consume_flag', 'guideperc',
            'cardtypeuuid',
        ))
        for idx, cv in enumerate(cv_rows, start=1):
            cardtype_code = (cv.get('cardtype') or '').strip()
            topcode = (cv.get('topcode') or '').strip()
            if not cardtype_code or not topcode:
                continue
            ttype = (cv.get('ttype') or 'S').upper()
            ct_id = cv.get('cardtypeuuid')
            defaults = {
                'discounttype': 'PRICE' if (cv.get('pricetype') or '').upper() == 'PRICE' else 'DISC',
                'disc': cv.get('cardvsdisc') if (cv.get('pricetype') or '').upper() != 'PRICE' else Decimal('1'),
                'price': cv.get('cardvsprice') or Decimal('0'),
                'consume_flag': cv.get('consume_flag') or 'Y',
                'emplguideperc': cv.get('guideperc') or Decimal('1'),
                'flag': 'Y',
            }
            key = (cardtype_code, ttype, topcode)
            obj = existing_map.get(key)
            if obj:
                obj.discounttype = defaults['discounttype']
                obj.disc = defaults['disc']
                obj.price = defaults['price']
                obj.consume_flag = defaults['consume_flag']
                obj.emplguideperc = defaults['emplguideperc']
                if ct_id:
                    obj.cardtypeuuid_id = ct_id
                update_objs.append(obj)
                stats['rules_updated'] += 1
            else:
                create_objs.append(CardtypeVsDiscountClass(
                    company=co, cardtype=cardtype_code, ttype=ttype,
                    discountclass=topcode, cardtypeuuid_id=ct_id, **defaults,
                ))
                stats['rules_created'] += 1
            if idx % 500 == 0:
                print(f"[sync] 公司 {co}: 已处理 {idx}/{len(cv_rows)} 行 Cardvsdi", flush=True)
            if time.time() - t0 > 30 and idx % 500 == 0:
                print(f"[sync] 警告: 公司 {co} 规则同步已超过 30 秒，请检查是否有锁", flush=True)

        # 补全规则里出现但大类表缺失的编码，保证折扣分类下拉有对应名称
        from django.db.models import Count as _Count
        used = (
            Cardvsdi.objects.filter(company=co, flag='Y')
            .exclude(topcode__isnull=True).exclude(topcode='')
            .values('ttype', 'topcode').annotate(n=_Count('uuid'))
        )
        srv_name_map = {
            st.topcode: st.ttname
            for st in Srvtopty.objects.filter(company=co, flag='Y')
            if st.topcode
        }
        goods_name_map = {
            gc.goodsct: gc.goodsctname
            for gc in Goodsct.objects.filter(company=co, flag='Y')
            if gc.goodsct
        }
        card_name_map = {
            cs.code: cs.name
            for cs in Cardsupertype.objects.filter(company=co, flag='Y')
            if cs.code
        }
        for row in used:
            ttype = (row['ttype'] or 'S').upper()
            code = row['topcode']
            if ttype == 'G':
                seg = 'goodsdiscountclass'
                name = goods_name_map.get(code) or code
            elif ttype == 'C':
                seg = 'discountclass'
                name = card_name_map.get(code) or code
            else:
                seg = 'srvdiscountclass'
                name = srv_name_map.get(code) or code
            if not Appoption.objects.filter(company=co, seg=seg, itemname=code).exists():
                Appoption.objects.create(
                    company=co, seg=seg, itemname=code,
                    itemvalues=name, flag='Y',
                )

        if create_objs:
            CardtypeVsDiscountClass.objects.bulk_create(create_objs, batch_size=500)
        if update_objs:
            CardtypeVsDiscountClass.objects.bulk_update(
                update_objs,
                ['discounttype', 'disc', 'price', 'consume_flag', 'emplguideperc', 'cardtypeuuid'],
                batch_size=500,
            )
        print(f"[sync] 公司 {co} 完成，耗时 {time.time() - t0:.1f}s，统计: {stats}", flush=True)

    print(f"[sync] 全部完成: {stats}", flush=True)
    return stats
