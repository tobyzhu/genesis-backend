# coding=utf-8
"""营业流水表（明细行）：expense × expvstoll，对齐传统 yinyeliushuibiao 字段。"""
from collections import defaultdict

from django.db import connection

TTYPE_LABELS = {
    'S': '服务',
    'G': '商品',
    'C': '售卡',
    'I': '充值',
}

VIPTYPE_LABELS = {
    '10': '10-会员',
    '20': '20-散客',
}

ROW_LIMIT_DEFAULT = 5000


def _f(v, nd=2):
    try:
        return round(float(v or 0), nd)
    except (TypeError, ValueError):
        return 0.0


def _fmt_date(s):
    s = (s or '').strip()
    if len(s) == 8 and s.isdigit():
        return f'{s[0:4]}-{s[4:6]}-{s[6:8]}'
    return s


def _fmt_time(s):
    s = ''.join(ch for ch in str(s or '') if ch.isdigit())
    if not s:
        return ''
    s = s.zfill(6)[:6]
    return f'{s[0:2]}:{s[2:4]}:{s[4:6]}'


def _disc_percent(secdisc):
    """secdisc 存 1=100%，展示为百分比数值（不含 % 号，前端 format=percent）。"""
    try:
        d = float(secdisc if secdisc is not None else 1)
    except (TypeError, ValueError):
        d = 1.0
    # 兼容已是百分数（>2）的脏数据
    if d > 2:
        return round(d, 2)
    return round(d * 100, 2)


def _specified_label(secoldcustflag):
    """是否指定美疗师1：取自 expense.secoldcustflag（挂单 secoldcustflag_hung）。"""
    raw = (secoldcustflag or '').strip()
    if not raw:
        return ''
    upper = raw.upper()
    if upper in ('1', 'Y', 'YES', '是'):
        return '是'
    if upper in ('0', 'N', 'NO', '否'):
        return '否'
    return raw


def _build_payinfo_map(company, trans_ids):
    """transuuid -> '疗程卡付=398.83;现金=100.00'"""
    if not trans_ids:
        return {}
    placeholders = ','.join(['%s'] * len(trans_ids))
    sql = f"""
        SELECT t.transuuid, t.PCODE AS pcode, t.TOTMOUNT AS amount,
               COALESCE(p.pname, t.PCODE) AS pname
        FROM toll t
        LEFT JOIN paymode p
               ON p.company = t.company AND p.pcode = t.PCODE AND p.flag = 'Y'
        WHERE t.company = %s
          AND t.flag = 'Y'
          AND t.transuuid IN ({placeholders})
        ORDER BY t.transuuid, t.PCODE
    """
    params = [company] + list(trans_ids)
    buckets = defaultdict(list)
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        for transuuid, _pcode, amount, pname in cursor.fetchall():
            key = str(transuuid)
            amt = _f(amount)
            if amt == 0:
                continue
            buckets[key].append(f'{pname or _pcode}={amt:.2f}')
    return {k: ';'.join(v) for k, v in buckets.items()}


def build_business_line_flow(
    company,
    storecodes,
    from_date='',
    to_date='',
    limit=ROW_LIMIT_DEFAULT,
):
    """
    返回明细行 + KPI/totals。
    行粒度：expense（有效单据）。
    """
    codes = [str(c).strip() for c in (storecodes or []) if str(c).strip()]
    if not company or not codes:
        return {
            'rows': [],
            'kpis': {},
            'totals': {},
            'meta': {'truncated': False, 'row_count': 0, 'limit': limit},
        }

    placeholders = ','.join(['%s'] * len(codes))
    lim = int(limit or ROW_LIMIT_DEFAULT)
    if lim < 1:
        lim = ROW_LIMIT_DEFAULT
    # 多取 1 行判断是否截断
    fetch_n = lim + 1

    sql = f"""
        SELECT
            e.storecode,
            e.cashposition,
            e.vsdate,
            e.vstime,
            x.TTYPE AS ttype,
            x.srvcode,
            CASE
                WHEN x.TTYPE = 'S' THEN sv.SVRNAME
                WHEN x.TTYPE = 'G' THEN g.GNAME
                WHEN x.TTYPE IN ('C', 'I') THEN COALESCE(ct.cardname, x.srvcode)
                ELSE x.srvcode
            END AS item_name,
            x.S_QTY AS s_qty,
            x.S_PRICE AS s_price,
            x.SECDISC AS secdisc,
            x.S_MOUNT AS s_mount,
            COALESCE(x.srvmondisc, 0) AS free_amount,
            COALESCE(x.cashratio, 0) AS cashratio,
            COALESCE(x.cardratio, 0) AS cardratio,
            COALESCE(x.sendratio, 0) AS sendratio,
            x.stype,
            x.PMCODE AS pmcode,
            emp_pm.ENAME AS pmname,
            x.ASSCODE1 AS asscode1,
            emp1.ENAME AS assname1,
            x.ASSCODE2 AS asscode2,
            emp2.ENAME AS assname2,
            e.ccode,
            e.vcode,
            v.vname,
            v.viptype,
            e.promotionsid,
            e.cdate,
            x.secoldcustflag,
            e.uuid AS transuuid,
            x.uuid AS expense_uuid,
            s.storename
        FROM expense x
        INNER JOIN expvstoll e ON e.uuid = x.transuuid
        LEFT JOIN storeinfo s
               ON s.company = e.company AND s.storecode = e.storecode AND s.flag = 'Y'
        LEFT JOIN vip v
               ON v.uuid = e.vipuuid
        LEFT JOIN serviece sv
               ON sv.company = x.company AND sv.SVRCDOE = x.srvcode AND sv.flag = 'Y'
        LEFT JOIN goods g
               ON g.company = x.company AND g.GCODE = x.srvcode AND g.flag = 'Y'
        LEFT JOIN cardinfo ci
               ON ci.company = x.company AND ci.ccode = x.srvcode AND ci.flag = 'Y'
        LEFT JOIN cardtype ct
               ON ct.uuid = ci.cardtypeuuid
        LEFT JOIN empl emp_pm
               ON emp_pm.company = x.company AND emp_pm.ECODE = x.PMCODE AND emp_pm.flag = 'Y'
        LEFT JOIN empl emp1
               ON emp1.company = x.company AND emp1.ECODE = x.ASSCODE1 AND emp1.flag = 'Y'
        LEFT JOIN empl emp2
               ON emp2.company = x.company AND emp2.ECODE = x.ASSCODE2 AND emp2.flag = 'Y'
        WHERE e.company = %s
          AND e.flag = 'Y' AND e.valiflag = 'Y'
          AND x.flag = 'Y'
          AND e.storecode IN ({placeholders})
    """
    params = [company] + codes
    if from_date:
        sql += " AND e.vsdate >= %s"
        params.append(from_date)
    if to_date:
        sql += " AND e.vsdate <= %s"
        params.append(to_date)
    sql += " ORDER BY e.vsdate DESC, e.vstime DESC, e.storecode, x.ditem LIMIT %s"
    params.append(fetch_n)

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        col_names = [d[0] for d in cursor.description]
        raw_rows = [dict(zip(col_names, row)) for row in cursor.fetchall()]

    truncated = len(raw_rows) > lim
    if truncated:
        raw_rows = raw_rows[:lim]

    trans_ids = list({str(r['transuuid']) for r in raw_rows if r.get('transuuid')})
    payinfo_map = _build_payinfo_map(company, trans_ids)

    rows = []
    totals = {
        's_qty': 0.0,
        's_mount': 0.0,
        'free_amount': 0.0,
        'cash_amount': 0.0,
        'card_amount': 0.0,
        'send_amount': 0.0,
    }
    am_S = am_G = am_C = am_I = 0.0

    for r in raw_rows:
        mount = _f(r.get('s_mount'))
        qty = _f(r.get('s_qty'), 2)
        cash_ratio = _f(r.get('cashratio'), 4)
        card_ratio = _f(r.get('cardratio'), 4)
        send_ratio = _f(r.get('sendratio'), 4)
        cash_amount = round(mount * cash_ratio, 2)
        card_amount = round(mount * card_ratio, 2)
        send_amount = round(mount * send_ratio, 2)
        free_amount = _f(r.get('free_amount'))
        # 赠送行且未写 srvmondisc 时，用赠送金额作为免单/赠送参考
        if free_amount == 0 and (r.get('stype') or '').upper() == 'P':
            free_amount = send_amount or mount

        ttype = (r.get('ttype') or '').upper()
        viptype = (r.get('viptype') or '').strip()
        item = {
            'storecode': r.get('storecode') or '',
            'storename': r.get('storename') or r.get('storecode') or '',
            'cashposition': r.get('cashposition') or '',
            'vsdate': _fmt_date(r.get('vsdate')),
            'vsdate_raw': r.get('vsdate') or '',
            'vstime': _fmt_time(r.get('vstime')),
            'ttype': ttype,
            'ttype_label': TTYPE_LABELS.get(ttype, ttype or ''),
            'srvcode': r.get('srvcode') or '',
            'item_name': r.get('item_name') or r.get('srvcode') or '',
            's_qty': qty,
            's_price': _f(r.get('s_price')),
            'secdisc': _disc_percent(r.get('secdisc')),
            's_mount': mount,
            'free_amount': free_amount,
            'cash_amount': cash_amount,
            'card_amount': card_amount,
            'send_amount': send_amount,
            'pmcode': r.get('pmcode') or '',
            'pmname': r.get('pmname') or r.get('pmcode') or '',
            'asscode1': r.get('asscode1') or '',
            'assname1': r.get('assname1') or r.get('asscode1') or '',
            'asscode2': r.get('asscode2') or '',
            'assname2': r.get('assname2') or r.get('asscode2') or '',
            'ccode': r.get('ccode') or '',
            'vcode': r.get('vcode') or '',
            'vname': r.get('vname') or '',
            'viptype': viptype,
            'viptype_label': VIPTYPE_LABELS.get(viptype, viptype),
            # 活动编号 / 记账日期 ← expvstoll；是否指定 ← expense.secoldcustflag
            'promotionsid': r.get('promotionsid') or '',
            'cdate': _fmt_date(r.get('cdate')),
            'secoldcustflag': (r.get('secoldcustflag') or '').strip(),
            'specified': _specified_label(r.get('secoldcustflag')),
            'pay_info': payinfo_map.get(str(r.get('transuuid')), ''),
            'transuuid': str(r.get('transuuid') or ''),
            'expense_uuid': str(r.get('expense_uuid') or ''),
        }
        rows.append(item)

        totals['s_qty'] += qty
        totals['s_mount'] += mount
        totals['free_amount'] += free_amount
        totals['cash_amount'] += cash_amount
        totals['card_amount'] += card_amount
        totals['send_amount'] += send_amount
        if ttype == 'S':
            am_S += mount
        elif ttype == 'G':
            am_G += mount
        elif ttype == 'C':
            am_C += mount
        elif ttype == 'I':
            am_I += mount

    for k in totals:
        totals[k] = round(totals[k], 2)

    kpis = {
        'am_S': round(am_S, 2),
        'am_G': round(am_G, 2),
        'am_C': round(am_C, 2),
        'am_I': round(am_I, 2),
        'total': round(am_S + am_G + am_C + am_I, 2),
        'cash_amount': totals['cash_amount'],
        'card_amount': totals['card_amount'],
        'send_amount': totals['send_amount'],
        'row_count': len(rows),
        'trans_count': len(trans_ids),
    }

    return {
        'rows': rows,
        'kpis': kpis,
        'totals': totals,
        'meta': {
            'truncated': truncated,
            'row_count': len(rows),
            'limit': lim,
            'view': 'line',
        },
    }
