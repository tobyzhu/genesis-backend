#coding = utf-8
"""助手导出字段中文名与说明。"""

from __future__ import annotations

from typing import Any, Dict, List, Set

# field -> {label, description}
FIELD_REGISTRY: Dict[str, Dict[str, str]] = {
    "vipuuid": {"label": "会员UUID", "description": "vip 表主键 uuid"},
    "vcode": {"label": "会员编号", "description": "门店会员号 vcode"},
    "vname": {"label": "会员姓名", "description": "vip.vname"},
    "mtcode": {"label": "手机号", "description": "会员手机 mtcode"},
    "telph": {"label": "联系电话", "description": "vip.telph"},
    "viptype": {"label": "会员类型", "description": "10=会员，20=散客"},
    "status": {"label": "会员状态", "description": "vip.status"},
    "viplevel": {"label": "会员级别", "description": "vip.viplevel"},
    "ecode": {"label": "顾问工号", "description": "负责顾问员工编号"},
    "adviser_name": {"label": "顾问姓名", "description": "负责顾问姓名"},
    "ecode2": {"label": "护理师工号", "description": "负责护理师/美疗师员工编号"},
    "therapist_name": {"label": "护理师姓名", "description": "负责护理师姓名"},
    "indate": {"label": "入会日期", "description": "vip.indate，入会日期"},
    "birth": {"label": "生日", "description": "vip.birth"},
    "last_visit_date": {"label": "最后到店日期", "description": "有效成交 valiflag=Y 的最近 vsdate（YYYY-MM-DD）"},
    "last_vsdate": {"label": "最后到店日期(原始)", "description": "vsdate 原始值，常为 YYYYMMDD"},
    "cash_amount": {"label": "现金消费金额", "description": "Sum(expense.s_mount*expense.cashratio)，已结账有效交易"},
    "card_amount": {"label": "卡付消费金额", "description": "Sum(expense.s_mount*expense.cardratio)"},
    "send_amount": {"label": "赠送消费金额", "description": "Sum(expense.s_mount*expense.sendratio)"},
    "service_amount": {"label": "服务消费金额", "description": "ttype=S，Sum(s_mount*(cashratio+cardratio))，不含赠送"},
    "goods_amount": {"label": "商品消费金额", "description": "ttype=G，Sum(s_mount*(cashratio+cardratio))，不含赠送"},
    "sale_amount": {"label": "明细销售额", "description": "统计区间内 expense 行 Sum(s_mount)"},
    "expense_line_count": {"label": "消费明细行数", "description": "纳入统计的 expense 行数"},
    "days_since_last_visit": {"label": "未到店天数", "description": "距最后有效消费 vsdate 的天数"},
    "lifetime_amount": {"label": "累计消费金额", "description": "历史有效成交 totmount 合计"},
    "lifetime_trans_count": {"label": "累计消费笔数", "description": "历史有效成交笔数"},
    "risk_level": {"label": "流失风险", "description": "warning/critical/never_visited 等"},
    "uuid": {"label": "UUID", "description": "记录主键"},
    "exptxserno": {"label": "成交单号", "description": "交易流水号"},
    "totmount": {"label": "成交金额", "description": "expvstoll.totmount 整单金额"},
    "vsdate": {"label": "发生日期", "description": "交易发生日期 vsdate"},
    "cdate": {"label": "记账日期", "description": "记账日期 cdate"},
    "ttype": {"label": "项目大类", "description": "G商品/S服务/C售卡/I充值"},
    "valiflag": {"label": "有效标志", "description": "Y=有效成交"},
    "srvcode": {"label": "项目编码", "description": "服务/商品编码"},
    "pcode": {"label": "付款方式编码", "description": "toll.pcode"},
    "pname": {"label": "付款方式", "description": "付款方式名称"},
    "iscash": {"label": "是否现金类", "description": "paymode.iscash"},
    "amount": {"label": "金额", "description": "金额"},
    "count": {"label": "笔数", "description": "记录笔数"},
    "line_count": {"label": "明细行数", "description": "明细行数"},
    "qty": {"label": "数量", "description": "销售数量"},
    "total_amount": {"label": "总金额", "description": "合计金额"},
    "dim_label": {"label": "维度名称", "description": "管理属性维度显示名"},
    "dim_value": {"label": "维度编码", "description": "管理属性维度值"},
    "cash_ratio": {"label": "现金占比", "description": "expense.cashratio"},
    "card_ratio": {"label": "卡付占比", "description": "expense.cardratio"},
    "send_ratio": {"label": "赠送占比", "description": "expense.sendratio"},
    "trans_count": {"label": "交易笔数", "description": "成交笔数"},
    "top_n": {"label": "TOP条数", "description": "排行截取条数"},
    "result_count": {"label": "结果条数", "description": "实际返回条数"},
    "from": {"label": "开始日期", "description": "统计区间起始"},
    "to": {"label": "结束日期", "description": "统计区间结束"},
    "company": {"label": "公司", "description": "company"},
    "storecode": {"label": "门店", "description": "storecode"},
    "date_field": {"label": "日期字段", "description": "vsdate 或 cdate"},
    "create_time": {"label": "创建时间", "description": "记录创建时间"},
    "source": {"label": "来源", "description": "会员来源"},
    "email": {"label": "邮箱", "description": "vip.email"},
    "wechat": {"label": "微信", "description": "vip.wechat"},
    "addr": {"label": "地址", "description": "vip.addr"},
    "sex": {"label": "性别", "description": "vip.sex"},
    "tags": {"label": "标签", "description": "vip.tags"},
    "occupation": {"label": "职业", "description": "vip.occupation"},
    "referrervcode": {"label": "推荐人会员号", "description": "推荐人 vcode"},
}


def get_field_meta(field: str, dataset_name: str = "") -> Dict[str, str]:
    """返回字段的 label / description；未知字段回退为字段名本身。"""
    key = (field or "").strip()
    reg = FIELD_REGISTRY.get(key, {})
    label = reg.get("label") or key
    desc = reg.get("description") or label
    return {
        "field": key,
        "label": label,
        "description": desc,
        "dataset": dataset_name,
    }


def collect_columns_from_datasets(datasets: List[Dict[str, Any]]) -> List[tuple[str, str]]:
    """(dataset_name, column) 有序去重列表。"""
    seen: Set[tuple[str, str]] = set()
    out: List[tuple[str, str]] = []
    for ds in datasets or []:
        if not isinstance(ds, dict):
            continue
        ds_name = str(ds.get("name") or "sheet")
        rows = ds.get("rows") or []
        if not isinstance(rows, list):
            continue
        col_seen: Set[str] = set()
        ordered_cols: List[str] = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            for k in r.keys():
                k2 = str(k)
                if k2 not in col_seen:
                    col_seen.add(k2)
                    ordered_cols.append(k2)
        for c in ordered_cols:
            pair = (ds_name, c)
            if pair not in seen:
                seen.add(pair)
                out.append(pair)
    return out


def build_field_glossary_for_datasets(datasets: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """生成字段说明表行：数据集、字段名、中文名称、字段说明。"""
    glossary: List[Dict[str, str]] = []
    for ds_name, col in collect_columns_from_datasets(datasets):
        meta = get_field_meta(col, ds_name)
        glossary.append(
            {
                "dataset": ds_name,
                "field": meta["field"],
                "label": meta["label"],
                "description": meta["description"],
            }
        )
    return glossary


def attach_field_meta_to_datasets(datasets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """为每个 dataset 附加 columns_meta（导出用）。"""
    out: List[Dict[str, Any]] = []
    for ds in datasets or []:
        if not isinstance(ds, dict):
            continue
        ds_name = str(ds.get("name") or "sheet")
        rows = ds.get("rows") or []
        cols: List[str] = []
        seen: Set[str] = set()
        for r in rows:
            if not isinstance(r, dict):
                continue
            for k in r.keys():
                k2 = str(k)
                if k2 not in seen:
                    seen.add(k2)
                    cols.append(k2)
        columns_meta = [get_field_meta(c, ds_name) for c in cols]
        enriched = dict(ds)
        enriched["columns_meta"] = columns_meta
        out.append(enriched)
    return out
