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
        return {'allowed': True, 'price': original_price, 'source': 'original', 'reason': ''}

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
        return {'allowed': True, 'price': price, 'source': 'ruler', 'reason': ''}

    # 时效卡：校验绑定项目 + 有效期，不扣次数/金额
    if comptype == 'period':
        bound = cardtype_bound_itemcode(cardtype)
        if bound and bound != (itemcode or ''):
            return _blocked('此卡绑定项目不匹配')
        if cardinfo and cardinfo.valdate:
            if cardinfo.valdate < date.today().strftime('%Y%m%d'):
                return _blocked('卡已过期')
        return {'allowed': True, 'price': original_price, 'source': 'period', 'reason': ''}

    # 计次卡：只校验绑定项目，按次数扣减
    if comptype == 'times':
        bound = cardtype_bound_itemcode(cardtype)
        if bound and bound != (itemcode or ''):
            return _blocked('此卡绑定项目不匹配')
        return {'allowed': True, 'price': original_price, 'source': 'times', 'reason': ''}

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
                return {'allowed': True, 'price': rule.price, 'source': 'discountclass', 'reason': ''}
            return {
                'allowed': True,
                'price': original_price * (rule.disc or Decimal('1')),
                'source': 'discountclass',
                'reason': '',
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
                return {'allowed': True, 'price': legacy.cardvsprice, 'source': 'cardvsdi', 'reason': ''}
            return {
                'allowed': True,
                'price': original_price * (legacy.cardvsdisc or Decimal('1')),
                'source': 'cardvsdi',
                'reason': '',
            }

        return {'allowed': True, 'price': original_price, 'source': 'original', 'reason': ''}

    # 未知消费模式：允许原价
    return {'allowed': True, 'price': original_price, 'source': 'original', 'reason': ''}


def sync_card_discount_rules(company=None):
    """把服务/商品大类同步到折扣分类，并把 Cardvsdi 迁移为折扣分类规则。"""
    from baseinfo.models import (
        Appoption, Cardtype, CardtypeVsDiscountClass, Cardvsdi,
        Goods, Goodsct, Serviece, Srvtopty,
    )

    ensure_card_rule_schema()
    stats = {
        'srv_categories': 0,
        'goods_categories': 0,
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

        for st in Srvtopty.objects.filter(company=co, flag='Y'):
            Appoption.objects.update_or_create(
                company=co, seg='srvdiscountclass', itemname=st.topcode,
                defaults={'itemvalues': st.ttname or st.topcode, 'flag': 'Y'},
            )
            stats['srv_categories'] += 1

        for gc in Goodsct.objects.filter(company=co, flag='Y'):
            Appoption.objects.update_or_create(
                company=co, seg='goodsdiscountclass', itemname=gc.goodsct,
                defaults={'itemvalues': gc.goodsctname or gc.goodsct, 'flag': 'Y'},
            )
            stats['goods_categories'] += 1

        # 通用折扣分类合并到专用 seg，避免存量项目已有编码失效
        for opt in Appoption.objects.filter(company=co, seg='discountclass', flag='Y'):
            for seg in ('srvdiscountclass', 'goodsdiscountclass'):
                Appoption.objects.update_or_create(
                    company=co, seg=seg, itemname=opt.itemname,
                    defaults={'itemvalues': opt.itemvalues, 'flag': 'Y'},
                )

        for sv in Serviece.objects.filter(company=co, flag='Y').exclude(topcode__isnull=True).exclude(topcode=''):
            if not (sv.discountclass or ''):
                sv.discountclass = sv.topcode
                sv.save(update_fields=['discountclass'])
                stats['items_backfilled'] += 1

        for gd in Goods.objects.filter(company=co, flag='Y').exclude(goodsct__isnull=True).exclude(goodsct=''):
            if not (gd.discountclass or ''):
                gd.discountclass = gd.goodsct
                gd.save(update_fields=['discountclass'])
                stats['items_backfilled'] += 1

        for cv in Cardvsdi.objects.filter(company=co, flag='Y'):
            ct = cv.cardtypeuuid or Cardtype.objects.filter(
                company=co, cardtype=cv.cardtype, flag='Y').first()
            if not (cv.cardtype or ''):
                continue
            defaults = {
                'discounttype': 'PRICE' if (cv.pricetype or '').upper() == 'PRICE' else 'DISC',
                'disc': cv.cardvsdisc if (cv.pricetype or '').upper() != 'PRICE' else Decimal('1'),
                'price': cv.cardvsprice or Decimal('0'),
                'consume_flag': cv.consume_flag or 'Y',
                'emplguideperc': cv.guideperc or Decimal('1'),
                'flag': 'Y',
            }
            if ct:
                defaults['cardtypeuuid'] = ct
            _, created = CardtypeVsDiscountClass.objects.update_or_create(
                company=co,
                cardtype=cv.cardtype,
                ttype=cv.ttype or 'S',
                discountclass=cv.topcode or '',
                defaults=defaults,
            )
            if created:
                stats['rules_created'] += 1
            else:
                stats['rules_updated'] += 1

    return stats
