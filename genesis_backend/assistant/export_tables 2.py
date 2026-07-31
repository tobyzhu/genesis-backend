#coding = utf-8
"""将 assistant tool_results 扁平化为可导出的表格数据集。"""

from __future__ import annotations

import json
from typing import Any, Dict, List


def _is_table(rows: Any) -> bool:
    return isinstance(rows, list) and len(rows) > 0 and all(isinstance(x, dict) for x in rows)


def _scalarize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in row.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False, default=str)
        else:
            out[k] = v
    return out


def _append_table(out: List[Dict[str, Any]], name: str, rows: List[Dict[str, Any]]) -> None:
    if not _is_table(rows):
        return
    out.append({"name": name or "table", "rows": [_scalarize_row(r) for r in rows]})


def _walk_export(name: str, obj: Any, out: List[Dict[str, Any]], *, depth: int = 0, max_depth: int = 12) -> None:
    if depth > max_depth or obj is None:
        return

    if _is_table(obj):
        _append_table(out, name, obj)
        return

    if isinstance(obj, dict):
        if obj.get("error") and len(obj) <= 3:
            return

        table_found = False
        for key, value in obj.items():
            child_name = f"{name}_{key}" if name else str(key)

            if _is_table(value):
                _append_table(out, child_name, value)
                table_found = True
                continue

            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                has_nested_lines = any(
                    _is_table(item.get("lines"))
                    for item in value
                    if isinstance(item, dict)
                )
                if has_nested_lines:
                    for idx, item in enumerate(value):
                        if not isinstance(item, dict):
                            continue
                        parent = {k: v for k, v in item.items() if k not in {"lines", "summary"}}
                        lines = item.get("lines")
                        if _is_table(lines):
                            merged_rows = [{**parent, **line} for line in lines]
                            _append_table(out, f"{child_name}_{idx}_lines", merged_rows)
                            table_found = True
                        summary = item.get("summary")
                        if isinstance(summary, dict) and summary:
                            _append_table(out, f"{child_name}_{idx}_summary", [{**parent, **summary}])
                            table_found = True
                    continue

                _append_table(out, child_name, value)
                table_found = True
                continue

            if isinstance(value, dict):
                _walk_export(child_name, value, out, depth=depth + 1, max_depth=max_depth)
                table_found = True

        if not table_found and obj:
            _append_table(out, name or "summary", [obj])
        return

    if isinstance(obj, list):
        for idx, item in enumerate(obj):
            _walk_export(f"{name}_{idx}", item, out, depth=depth + 1, max_depth=max_depth)


def flatten_tool_results_for_export(tool_results: Any) -> List[Dict[str, Any]]:
    """将 run_tool_plan 的 tool_results 转为 [{name, rows}, ...]。"""
    out: List[Dict[str, Any]] = []
    if not isinstance(tool_results, list):
        return out

    for tr in tool_results:
        if not isinstance(tr, dict):
            continue
        if tr.get("ok") is False:
            continue
        tool = str(tr.get("tool") or "tool")
        data = tr.get("data")
        if data is None:
            continue
        if isinstance(data, list):
            _walk_export(tool, data, out)
        elif isinstance(data, dict):
            if data.get("error") and len(data) <= 3:
                continue
            _walk_export(tool, data, out)
    return out


def flatten_panel_payload(tool_name: str, payload: Any) -> List[Dict[str, Any]]:
    """将页顶面板（维度统计、沉睡预警等）的 data 对象转为可导出数据集。"""
    if payload is None:
        return []
    fake_results = [{"tool": tool_name, "ok": True, "data": payload}]
    return flatten_tool_results_for_export(fake_results)
