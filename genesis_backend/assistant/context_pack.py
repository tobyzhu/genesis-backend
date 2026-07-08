#coding = utf-8
"""
每次助手调用前注入的「系统默认字典」摘要：来自 common.constants 及当前公司的 paymode 等。
便于模型正确理解 ttype、flag、挂单状态等编码含义。
"""

from __future__ import annotations

from typing import Any, List, Tuple

import common.constants as C


def _fmt_choice_block(title: str, choices: Any, max_items: int = 80) -> str:
    if not choices:
        return ""
    if isinstance(choices, dict):
        seq: List[Tuple[Any, Any]] = list(choices.items())
    else:
        seq = list(choices)  # type: ignore[arg-type]
    lines: List[str] = [title]
    n = 0
    for row in seq:
        if n >= max_items:
            rest = max(0, len(seq) - max_items)
            lines.append(f"  …（其余约 {rest} 项已省略）")
            break
        if isinstance(row, (list, tuple)) and len(row) >= 2:
            code, label = row[0], row[1]
            if code == "" and label == "":
                continue
            lines.append(f"  - {code!r}: {label}")
            n += 1
    return "\n".join(lines) + "\n"


def _paymode_lines(company: str, limit: int = 100) -> str:
    try:
        from baseinfo.models import Paymode
    except Exception:
        return ""
    pm = Paymode.ISCASH
    isc_map = {str(a[0]): a[1] for a in pm}
    rows = (
        Paymode.objects.filter(company=company, flag="Y")
        .order_by("pcode")
        .values_list("pcode", "pname", "iscash")[:limit]
    )
    lines = [
        f"【当前公司 company={company!r} 的付款方式 paymode（节选，用于理解 pcode / iscash）】",
        "  iscash 含义：0=卡付类；1=现金类；2=赠送类（与 Paymode.ISCASH 一致）。",
    ]
    for pcode, pname, iscash in rows:
        im = isc_map.get(str(iscash or "").strip(), str(iscash or ""))
        lines.append(f"  - pcode={pcode!r}, pname={pname!r}, iscash={iscash!r} ({im})")
    if not rows:
        lines.append("  （未查到有效 paymode 记录，可能 company 无配置）")
    return "\n".join(lines) + "\n"


def _psstatus_lines(company: str, limit: int = 30) -> str:
    """psstatus / psstatus_hung：服务流程节点，与结账无直接对应。"""
    default_rows = [
        ("10", "已开单"),
        ("20", "配料完成"),
        ("30", "配料确认"),
        ("40", "服务完成确认"),
        ("50", "客户确认"),
        ("60", "挂账"),
        ("70", "结帐完成"),
    ]
    lines = [
        "【psstatus / psstatus_hung — 服务/配料/确认流程状态，与是否结账无直接对应】",
        "  - 挂单主表 expvstoll_hung 用字段 psstatus_hung；表示开单后服务、商品、配料等流程节点。",
        "  - 不要把它当作「是否已付款/已结账」的判断依据；结账看数据是否在 expvstoll/expense/toll。",
        f"  - 常量 CAN_CHECKOUT_FLAG={getattr(C, 'CAN_CHECKOUT_FLAG', '70')!r} 为流程节点编码之一，不等于 SQL 层结账判定。",
        "  - 常见编码（以公司 appoption seg=psstatus 为准，节选）：",
    ]
    try:
        from baseinfo.models import Appoption

        rows = list(
            Appoption.objects.filter(company=company, flag="Y", seg="psstatus")
            .order_by("itemname")
            .values_list("itemname", "itemvalues")[:limit]
        )
    except Exception:
        rows = []
    if not rows:
        rows = default_rows
    for code, label in rows:
        lines.append(f"  - {code!r}: {label}")
    return "\n".join(lines) + "\n"


def build_system_lexicon(company: str) -> str:
    """
    生成一段纯文本，拼在 planner / answer 的 system 提示后。
    """
    parts: List[str] = []
    parts.append("【Genesis 系统编码与业务约定 — 解释查询结果时必须优先对照本节】\n")

    parts.append(_fmt_choice_block("ttype / ttype_hung（交易大类：商品/服务/售卡/充值）", C.TTYPE))
    parts.append(
        "【开单 / 结账 两套表 — 统计与 readonly_sql 必须先分清】\n"
        "  - 未结账（挂单中）：物理表 expvstoll_hung + expense_hung。"
        "数据仍在 hung 表即表示尚未结账转为正式成交；查未结账客人、挂单明细用这套表。\n"
        "  - 已结账（正式成交）：物理表 expvstoll + expense + toll。"
        "门店营业额、付款方式、现金/卡付统计、会员消费历史等应查这套表；有效成交 expvstoll.valiflag='Y'。\n"
        "  - 不要用 psstatus/psstatus_hung 单独推断是否已结账；"
        "结账与否看记录是在 hung 表还是 expvstoll/expense/toll 表。\n"
    )
    parts.append(_psstatus_lines(company, limit=30))
    parts.append(
        "【明细行 stype_hung（挂账明细性质，与卡类赠送逻辑等相关）】\n"
        "  - 常见：P=赠送；N=正价/常规；其它单字母代码以库内实际数据为准。\n"
    )
    parts.append(_fmt_choice_block("stype（部分主数据上的「正常/赠送」类字典；与 stype_hung 字母码不同层）", C.STYPE))

    parts.append(_fmt_choice_block("flag（记录是否有效）", C.FLAG))
    parts.append(_fmt_choice_block("comptype / 卡大类计费方式（amount=计费，times=计次）", C.COMPTYPE))
    parts.append(_fmt_choice_block("cardsupertype 等卡大类 suptype 常用取值（CARDSUPTYPE）", C.CARDSUPTYPE))
    parts.append(_fmt_choice_block("会员类型 viptype", C.VIPTYPE))
    parts.append(_fmt_choice_block("会员状态 status（VIPSTATUS）", C.VIPSTATUS))
    parts.append(_fmt_choice_block("案例类型 CASETYPE", C.CASETYPE))
    parts.append(_fmt_choice_block("案例状态 CASESTATUS", C.CASESTATUS))
    parts.append(_fmt_choice_block("库存/调拨 saleatr（SALEATR）", C.SALEATR))
    parts.append(_fmt_choice_block("ARCHIVEMENTTYPE（部分业绩/归档分类）", C.ARCHIVEMENTTYPE, max_items=40))

    parts.append(
        "【readonly_sql 表名约定】\n"
        "  - SQL 中必须使用 MySQL 物理表名（list_table_catalog 返回的 db_table），"
        "不要写 Django app 前缀。\n"
        "  - 正确：FROM expvstoll、JOIN toll、FROM vip。\n"
        "  - 错误：cashier.expvstoll、baseinfo.vip（系统会自动尝试纠正 FROM/JOIN 中的 app.表名，但仍应写物理名）。\n"
    )

    parts.append(
        "【readonly_sql 主键与外键列名 — 写 SELECT/JOIN 时必须遵守】\n"
        "  - vip 表：主键是 uuid（没有 vipuuid 列）。会员号 vcode，手机 mtcode/telph。\n"
        "  - expvstoll 表：主键 uuid；vipuuid → vip.uuid；成交总额 totmount。\n"
        "  - expense 表：transuuid → expvstoll.uuid；项目金额 S_MOUNT（s_mount）、cashratio/cardratio/sendratio 仅在本表。\n"
        "  - toll 表：transuuid → expvstoll.uuid；实付金额 totmount、pcode。\n"
        "  - 勿在 expvstoll 别名上写 s_mount/cashratio；按会员现金消费应 expense→expvstoll→vip 或 toll→paymode→expvstoll→vip。\n"
        "  - cardinfo / crmcase / vipcasedetail 等：列 vipuuid 指向 vip.uuid。\n"
        "  - paymode 表：付款方式编码 pcode；iscash='1' 为现金类。\n"
        "  - 口语「会员 vipuuid」是 UUID 值：在 vip 表用 v.uuid，在 expvstoll 用 e.vipuuid。\n"
        "  - 联表示例：FROM expvstoll e JOIN vip v ON e.vipuuid = v.uuid；"
        "FROM toll t JOIN expvstoll e ON t.transuuid = e.uuid。\n"
        "  - 写 SQL 前务必 describe_table 核对 column 名；不要凭 Django 模型属性名臆造列名。\n"
    )

    parts.append(
        "【expvstoll 已结账成交主表（物理表名 expvstoll，配套 expense + toll）】\n"
        "  - 与 expvstoll_hung（未结账）相对；进入本表表示已结账生成正式成交。\n"
        "  - valiflag='Y' 表示有效交易，valiflag='N' 表示作废交易。\n"
        "  - vsdate = 发生交易日期（业务发生日）；cdate = 记账日期（财务入账日）。\n"
        "  - 付款明细在 toll（transuuid → expvstoll.uuid）；现金/卡付统计应联 toll + paymode。\n"
        "  - 做时间统计时需明确使用 vsdate 还是 cdate。\n"
    )

    parts.append(
        "【expense 明细 ttype 与来源表映射（物理表名 expense）】\n"
        "  - ttype='S'：服务项目，对应 serviece 表（按 srvcode 对应服务编码）。\n"
        "  - ttype='G'：商品项目，对应 goods 表（按 srvcode 对应商品编码）。\n"
        "  - ttype in {'C','I'}：售卡/充值，先按 srvcode 作为卡号关联 cardinfo，再由 cardinfo.cardtype 关联 cardtype。\n"
    )


    parts.append(
        "【expense 明细金额与支付方式折算（物理表 expense，不在 expvstoll）】\n"
        "  - s_mount（库列常为 S_MOUNT）：明细行项目总金额，仅 expense 表有此列。\n"
        "  - cashratio / cardratio / sendratio：仅 expense 表；现金折算 = s_mount * cashratio。\n"
        "  - expvstoll 只有 totmount（整单成交额），没有 s_mount、cashratio。\n"
        "  - 按会员汇总现金消费示例：FROM expense x JOIN expvstoll e ON x.transuuid=e.uuid "
        "JOIN vip v ON e.vipuuid=v.uuid，再 SUM(x.s_mount*x.cashratio)；日期条件用 e.vsdate。\n"
        "  - 按 toll 实付现金示例：FROM toll t JOIN expvstoll e ON t.transuuid=e.uuid "
        "JOIN paymode p ON p.pcode=t.pcode AND p.company=e.company WHERE p.iscash='1'。\n"
        "  - 含义：整笔交易在 toll 上存在多种付款方式时，系统把付款构成折算比例写到各行 expense。\n"
        "  - 与 paymode.iscash：0=卡付→cardratio；1=现金→cashratio；2=赠送→sendratio。\n"
        "  - 统计注意：Sum(s_mount) 是明细标价合计；现金占比用行级 s_mount*ratio 汇总，"
        "或与 toll 层 iscash='1' 的 totmount 汇总（两种口径不要混用）。\n"
    )

    parts.append(
        "【会员卡 cardinfo 与卡类型 cardtype — 查询卡项余额必须先了解这两张表】\n"
        "  - cardinfo（物理表 cardinfo）：会员卡实例，每条记录一张卡。\n"
        "    - CCODE：卡号；LEFTMONEY：余额（金额计费卡）；leftqty：剩余次数（计次卡）\n"
        "    - CARDTYPE：卡类型代码（关联 cardtype.cardtype）\n"
        "    - suptype：卡大类（10=储值卡, 15=产品卡, 20=疗程卡, 30=赠送储值, 40=赠送疗程）\n"
        "    - stype：来源类型（N=正常购买, P=赠送）\n"
        "    - status：状态（O=正常使用中, C=已关闭）\n"
        "    - SENDDATE：发卡日期，VALDATE：有效期\n"
        "  - cardtype（物理表 cardtype）：卡类型定义（每种卡的模板）。\n"
        "    - cardtype：代码（主键）；cardname：名称；comptype：计费方式（amount/times）\n"
        "    - brand：品牌代码；displayclass1：显示分类代码\n"
        "    - marketclass1~3、financeclass1~2、discountclass 等管理分类\n"
        "    - 联表：FROM cardinfo ci JOIN cardtype ct ON ci.CARDTYPE=ct.cardtype AND ci.company=ct.company\n"
        "  - 卡分析流程：按 comptype 分金额/计次→过滤有效卡→按 brand/displayclass1 分组→翻译代码\n"
    )
    parts.append(
        "【公司动态字典 appoption — 品牌/显示分类/营销分类均由此表配置】\n"
        "  - 物理表 appoption，公司自行配置，查询须传 company。\n"
        "  - seg：字典段名（brand/displayclass1/marketclass1~3/financeclass1~2/discountclass/psstatus 等）\n"
        "  - itemname：代码值；itemvalues：代码对应的可读名称\n"
        "  - 查询：SELECT itemname, itemvalues FROM appoption WHERE company=\'<公司>\' AND flag=\'Y\' AND seg=\'<seg>\'\n"
        "  - 列出所有段：SELECT DISTINCT seg FROM appoption WHERE company=\'<公司>\'\n"
    )
    
    parts.append(_paymode_lines(company, limit=100))

    parts.append(
        "\n【公司/门店上下文】\n"
        f"  - 默认公司常量 COMPANYID（仅作参考，实际以请求传入的 company 为准）: {getattr(C, 'COMPANYID', '')!r}\n"
        f"  - 演示公司 DEMO_COMPANY={getattr(C, 'DEMO_COMPANY', '')!r}, DEMO_STORECODE={getattr(C, 'DEMO_STORECODE', '')!r}\n"
    )

    text = "\n".join(parts)
    # 防止极端情况下过长挤爆上下文
    max_chars = 12000
    if len(text) > max_chars:
        text = text[: max_chars - 40] + "\n...[系统字典已截断]..."
    return text
