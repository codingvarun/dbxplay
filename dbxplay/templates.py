"""
templates.py — Generates self-contained HTML/CSS/JS for the Databricks-style table.

Features:
  - Per-column filter dropdowns with unique value checkboxes
  - Global search across column names AND values
  - Column visibility selector
  - "+" tab with Visualization and Data Profile views
  - Excel-like cell range selection with copy
  - Context menu with copy-as formats, filter, exclude
  - Column sorting, resizing, side panel
  - CSV / Excel download
"""

import json
from typing import Any, Dict, List, Optional

from dbxplay.icons import (
    get_type_icon_svg,
    get_sort_icon_svg,
    get_chevron_down_svg,
    get_plus_svg,
    get_search_svg,
    get_close_svg,
)


def render_table_html(
    table_id: str,
    records: List[Dict[str, str]],
    columns: List[Dict[str, str]],
    total_rows: Optional[int],
    truncated: bool,
    limit: int,
    title: str = "Table",
    height: Optional[int] = None,
) -> str:
    """Render a complete, self-contained HTML string for the interactive table."""

    num_display = len(records)
    height_px = height or 520

    col_meta_json = json.dumps(columns)
    records_json = json.dumps(records)

    type_icons = {}
    for col in columns:
        type_icons[col["name"]] = get_type_icon_svg(col["dtype_category"])

    sort_icon = get_sort_icon_svg()
    chevron = get_chevron_down_svg(10)
    plus_icon = get_plus_svg(13)
    search_icon = get_search_svg()
    close_icon = get_close_svg(10)

    if total_rows is not None:
        if truncated:
            row_summary = f"Showing 1 – {num_display} of {total_rows:,} rows (limited to {limit:,})"
        else:
            row_summary = f"{total_rows:,} row{'s' if total_rows != 1 else ''}"
    else:
        if truncated:
            row_summary = f"Showing first {num_display:,} rows (limited to {limit:,})"
        else:
            row_summary = f"{num_display:,} row{'s' if num_display != 1 else ''}"

    html = f"""
<div id="{table_id}" class="db-display-root" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: #1b1f23; border: 1px solid #dce0e5; border-radius: 6px; overflow: hidden; background: #fff; position: relative;">

<style>
  #{table_id} * {{ box-sizing: border-box; }}
  #{table_id} .db-topbar {{
    display: flex; align-items: center; border-bottom: 1px solid #dce0e5;
    background: #f8f9fb; padding: 0; height: 38px; user-select: none; position: relative;
    overflow-x: auto; overflow-y: hidden; flex-shrink: 0;
  }}
  #{table_id} .db-tab {{
    display: inline-flex; align-items: center; gap: 5px; padding: 0 14px; height: 100%;
    font-size: 13px; font-weight: 500; color: #666; cursor: pointer;
    border-bottom: 2px solid transparent; background: transparent; white-space: nowrap; flex-shrink: 0;
  }}
  #{table_id} .db-tab.active {{ color: #1a73e8; border-bottom-color: #1a73e8; }}
  #{table_id} .db-tab:hover {{ background: #eef1f5; }}
  #{table_id} .db-tab-close {{
    display: inline-flex; align-items: center; margin-left: 4px; padding: 2px;
    border-radius: 3px; cursor: pointer;
  }}
  #{table_id} .db-tab-close:hover {{ background: rgba(0,0,0,0.1); }}
  #{table_id} .db-plus-btn {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; margin-left: 2px; cursor: pointer;
    border-radius: 4px; border: none; background: transparent; flex-shrink: 0;
    position: relative;
  }}
  #{table_id} .db-plus-btn:hover {{ background: #e2e6ea; }}
  #{table_id} .db-plus-btn svg, #{table_id} .db-tab-chevron svg {{ pointer-events: none; }}

  /* Dropdowns */
  #{table_id} .db-dropdown {{
    position: absolute; z-index: 1000; min-width: 220px; background: #fff;
    border: 1px solid #dce0e5; border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12), 0 1px 4px rgba(0,0,0,0.06);
    padding: 4px 0; display: none;
  }}
  #{table_id} .db-dropdown.open {{ display: block; }}
  #{table_id} .db-dropdown-item {{
    display: flex; align-items: center; gap: 8px; padding: 7px 14px;
    font-size: 13px; color: #333; cursor: pointer; white-space: nowrap;
  }}
  #{table_id} .db-dropdown-item:hover {{ background: #eef1f5; }}
  #{table_id} .db-dropdown-item .db-shortcut {{ margin-left: auto; color: #888; font-size: 11px; }}
  #{table_id} .db-dropdown-sep {{ height: 1px; background: #e5e7eb; margin: 4px 0; }}
  #{table_id} .db-dropdown-item.has-sub {{ position: relative; }}
  #{table_id} .db-dropdown-item.has-sub::after {{ content: '›'; margin-left: auto; font-size: 15px; color: #888; }}
  #{table_id} .db-sub-dropdown {{
    position: absolute; left: 100%; top: -4px; min-width: 120px; background: #fff;
    border: 1px solid #dce0e5; border-radius: 6px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    padding: 4px 0; display: none;
  }}
  #{table_id} .db-dropdown-item.has-sub:hover .db-sub-dropdown {{ display: block; }}

  /* Toolbar */
  #{table_id} .db-toolbar {{
    display: flex; align-items: center; padding: 5px 10px; gap: 8px;
    border-bottom: 1px solid #eaecf0; background: #fbfcfd; min-height: 36px; flex-wrap: wrap;
  }}
  #{table_id} .db-search-box {{
    display: inline-flex; align-items: center; background: #fff;
    border: 1px solid #d0d5dd; border-radius: 4px; padding: 3px 8px; gap: 5px; flex-shrink: 0;
  }}
  #{table_id} .db-search-box:focus-within {{ border-color: #1a73e8; box-shadow: 0 0 0 2px rgba(26,115,232,0.15); }}
  #{table_id} .db-search-input {{
    border: none; outline: none; font-size: 12px; width: 180px; background: transparent;
    color: #333; font-family: inherit;
  }}
  #{table_id} .db-toolbar-btn {{
    display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px;
    border: 1px solid #d0d5dd; border-radius: 4px; background: #fff; cursor: pointer;
    font-size: 12px; color: #444; font-family: inherit; white-space: nowrap;
  }}
  #{table_id} .db-toolbar-btn:hover {{ background: #f3f5f8; border-color: #bbb; }}
  #{table_id} .db-toolbar-btn.has-active {{ border-color: #1a73e8; color: #1a73e8; background: #e8f0fe; }}
  #{table_id} .db-filter-pill {{
    display: inline-flex; align-items: center; gap: 4px; background: #e8f0fe;
    color: #1a56db; border-radius: 12px; padding: 2px 10px 2px 8px;
    font-size: 11px; font-weight: 500; cursor: default; white-space: nowrap;
  }}
  #{table_id} .db-filter-pill .db-pill-close {{
    cursor: pointer; display: inline-flex; align-items: center;
    margin-left: 2px; border-radius: 50%; padding: 1px;
  }}
  #{table_id} .db-filter-pill .db-pill-close:hover {{ background: rgba(26,86,219,0.15); }}
  #{table_id} .db-row-summary {{ margin-left: auto; font-size: 11px; color: #777; white-space: nowrap; }}

  /* Column Selector Dropdown */
  #{table_id} .db-col-selector {{
    position: absolute; z-index: 1001; width: 260px; max-height: 360px;
    background: #fff; border: 1px solid #dce0e5; border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: none; flex-direction: column;
  }}
  #{table_id} .db-col-selector.open {{ display: flex; }}
  #{table_id} .db-col-selector-header {{
    padding: 8px 12px; border-bottom: 1px solid #eaecf0; display: flex;
    align-items: center; gap: 6px;
  }}
  #{table_id} .db-col-selector-header input {{
    flex: 1; border: 1px solid #d0d5dd; border-radius: 4px; padding: 4px 8px;
    font-size: 12px; outline: none; font-family: inherit;
  }}
  #{table_id} .db-col-selector-header input:focus {{ border-color: #1a73e8; }}
  #{table_id} .db-col-selector-body {{
    flex: 1; overflow-y: auto; padding: 4px 0;
  }}
  #{table_id} .db-col-selector-item {{
    display: flex; align-items: center; gap: 8px; padding: 5px 12px;
    cursor: pointer; font-size: 12px; color: #333;
  }}
  #{table_id} .db-col-selector-item:hover {{ background: #f3f5f8; }}
  #{table_id} .db-col-selector-item input[type="checkbox"] {{ cursor: pointer; accent-color: #1a73e8; }}
  #{table_id} .db-col-selector-actions {{
    padding: 6px 12px; border-top: 1px solid #eaecf0; display: flex; gap: 8px; justify-content: flex-end;
  }}
  #{table_id} .db-col-selector-actions button {{
    padding: 4px 12px; border-radius: 4px; font-size: 12px; cursor: pointer;
    font-family: inherit; border: 1px solid #d0d5dd; background: #fff; color: #333;
  }}
  #{table_id} .db-col-selector-actions button:hover {{ background: #f3f5f8; }}
  #{table_id} .db-col-selector-actions button.primary {{
    background: #1a73e8; color: #fff; border-color: #1a73e8;
  }}
  #{table_id} .db-col-selector-actions button.primary:hover {{ background: #1557b0; }}

  /* Column Filter Dropdown */
  #{table_id} .db-col-filter {{
    position: absolute; z-index: 1002; width: 240px; max-height: 320px;
    background: #fff; border: 1px solid #dce0e5; border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: none; flex-direction: column;
  }}
  #{table_id} .db-col-filter.open {{ display: flex; }}
  #{table_id} .db-col-filter-search {{
    padding: 8px; border-bottom: 1px solid #eaecf0;
  }}
  #{table_id} .db-col-filter-search input {{
    width: 100%; border: 1px solid #d0d5dd; border-radius: 4px; padding: 5px 8px;
    font-size: 12px; outline: none; font-family: inherit;
  }}
  #{table_id} .db-col-filter-search input:focus {{ border-color: #1a73e8; }}
  #{table_id} .db-col-filter-selectall {{
    padding: 5px 10px; border-bottom: 1px solid #f0f1f3; display: flex;
    align-items: center; gap: 8px; font-size: 12px; color: #444; cursor: pointer;
  }}
  #{table_id} .db-col-filter-selectall:hover {{ background: #f3f5f8; }}
  #{table_id} .db-col-filter-body {{
    flex: 1; overflow-y: auto; padding: 2px 0; max-height: 180px;
  }}
  #{table_id} .db-col-filter-item {{
    display: flex; align-items: center; gap: 8px; padding: 4px 10px;
    cursor: pointer; font-size: 12px; color: #333;
  }}
  #{table_id} .db-col-filter-item:hover {{ background: #f3f5f8; }}
  #{table_id} .db-col-filter-item input[type="checkbox"] {{ cursor: pointer; accent-color: #1a73e8; flex-shrink: 0; }}
  #{table_id} .db-col-filter-item span {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  #{table_id} .db-col-filter-item .val-count {{ margin-left: auto; color: #999; font-size: 11px; flex-shrink: 0; }}
  #{table_id} .db-col-filter-actions {{
    padding: 6px 8px; border-top: 1px solid #eaecf0; display: flex; gap: 6px; justify-content: flex-end;
  }}
  #{table_id} .db-col-filter-actions button {{
    padding: 4px 12px; border-radius: 4px; font-size: 12px; cursor: pointer;
    font-family: inherit; border: 1px solid #d0d5dd; background: #fff; color: #333;
  }}
  #{table_id} .db-col-filter-actions button:hover {{ background: #f3f5f8; }}
  #{table_id} .db-col-filter-actions button.primary {{
    background: #1a73e8; color: #fff; border-color: #1a73e8;
  }}
  #{table_id} .db-col-filter-actions button.primary:hover {{ background: #1557b0; }}

  /* Table */
  #{table_id} .db-table-wrap {{ overflow: auto; max-height: {height_px}px; position: relative; }}
  #{table_id} table {{ width: 100%; border-collapse: separate; border-spacing: 0; table-layout: auto; }}
  #{table_id} thead {{ position: sticky; top: 0; z-index: 10; }}
  #{table_id} thead th {{
    background: #f3f5f8; border-bottom: 1px solid #dce0e5; border-right: 1px solid #eaecf0;
    padding: 0; font-weight: 600; font-size: 12px; color: #444;
    text-align: left; white-space: nowrap; user-select: none; position: relative;
  }}
  #{table_id} thead th:last-child {{ border-right: none; }}
  #{table_id} thead th .db-th-content {{
    display: flex; align-items: center; padding: 6px 10px; gap: 4px; cursor: pointer;
  }}
  #{table_id} thead th:hover {{ background: #e9ecf1; }}
  #{table_id} thead th .db-th-inner {{ display: inline-flex; align-items: center; gap: 4px; flex: 1; }}
  #{table_id} thead th .db-sort-icon {{ opacity: 0.35; transition: opacity 0.15s; flex-shrink: 0; }}
  #{table_id} thead th:hover .db-sort-icon {{ opacity: 0.7; }}
  #{table_id} thead th.sorted-asc .db-sort-asc {{ fill: #1a73e8; opacity: 1; }}
  #{table_id} thead th.sorted-asc .db-sort-icon,
  #{table_id} thead th.sorted-desc .db-sort-icon {{ opacity: 1; }}
  #{table_id} thead th.sorted-desc .db-sort-desc {{ fill: #1a73e8; opacity: 1; }}
  #{table_id} thead th.has-filter .db-th-content {{ background: #e8f0fe; }}
  #{table_id} .db-th-filter-btn {{
    display: inline-flex; align-items: center; padding: 2px; border-radius: 3px;
    cursor: pointer; opacity: 0; transition: opacity 0.1s; flex-shrink: 0;
  }}
  #{table_id} thead th:hover .db-th-filter-btn {{ opacity: 0.6; }}
  #{table_id} thead th.has-filter .db-th-filter-btn {{ opacity: 1; color: #1a73e8; }}
  #{table_id} .db-th-filter-btn:hover {{ opacity: 1 !important; background: rgba(0,0,0,0.06); }}
  #{table_id} .db-row-idx {{
    width: 48px; min-width: 48px; max-width: 48px; text-align: right; color: #999;
    font-size: 11px; font-weight: 400; background: #f9fafb; cursor: default;
    padding-right: 12px !important; border-right: 1px solid #eaecf0;
  }}
  #{table_id} thead th.db-row-idx {{ background: #f3f5f8; padding: 6px 12px 6px 6px !important; }}
  #{table_id} thead th.db-row-idx:hover {{ background: #f3f5f8; }}
  #{table_id} tbody td {{
    padding: 5px 10px; border-bottom: 1px solid #f0f1f3; border-right: 1px solid #f5f6f8;
    font-size: 13px; color: #1b1f23; white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; max-width: 320px; cursor: default;
  }}
  #{table_id} tbody td:last-child {{ border-right: none; }}
  #{table_id} tbody tr:hover td {{ background: #f7f9fc; }}
  #{table_id} tbody td.db-null {{ color: #bbb; font-style: italic; }}
  #{table_id} tbody td.db-bool-true {{ color: #16a34a; font-weight: 500; }}
  #{table_id} tbody td.db-bool-false {{ color: #b91c1c; font-weight: 500; }}
  #{table_id} tbody td.db-number {{ font-variant-numeric: tabular-nums; text-align: right; }}

  /* Excel-like selection */
  #{table_id} tbody td.db-sel {{ background: #d2e3fc !important; }}
  #{table_id} tbody td.db-sel-border-top {{ border-top: 2px solid #1a73e8 !important; }}
  #{table_id} tbody td.db-sel-border-bottom {{ border-bottom: 2px solid #1a73e8 !important; }}
  #{table_id} tbody td.db-sel-border-left {{ border-left: 2px solid #1a73e8 !important; }}
  #{table_id} tbody td.db-sel-border-right {{ border-right: 2px solid #1a73e8 !important; }}

  /* Column Resize */
  #{table_id} .db-resize-handle {{
    position: absolute; right: 0; top: 0; bottom: 0; width: 5px; cursor: col-resize; z-index: 5;
  }}
  #{table_id} .db-resize-handle:hover, #{table_id} .db-resize-handle.active {{ background: #1a73e8; opacity: 0.3; }}

  /* Context Menu */
  #{table_id} .db-context-menu {{
    position: fixed; z-index: 10000; min-width: 210px; background: #fff;
    border: 1px solid #dce0e5; border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.14), 0 2px 6px rgba(0,0,0,0.06);
    padding: 4px 0; display: none; font-size: 13px;
  }}
  #{table_id} .db-context-menu.open {{ display: block; }}
  #{table_id} .db-ctx-item {{
    display: flex; align-items: center; gap: 8px; padding: 7px 14px;
    cursor: pointer; white-space: nowrap; color: #333;
  }}
  #{table_id} .db-ctx-item:hover {{ background: #eef1f5; }}
  #{table_id} .db-ctx-item .ctx-shortcut {{ margin-left: auto; color: #999; font-size: 11px; }}
  #{table_id} .db-ctx-item.has-sub {{ position: relative; }}
  #{table_id} .db-ctx-item.has-sub::after {{ content: '›'; margin-left: auto; font-size: 16px; color: #888; line-height: 1; }}
  #{table_id} .db-ctx-sub {{
    position: absolute; left: 100%; top: -4px; min-width: 120px; background: #fff;
    border: 1px solid #dce0e5; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.14);
    padding: 4px 0; display: none;
  }}
  #{table_id} .db-ctx-item.has-sub:hover .db-ctx-sub {{ display: block; }}
  #{table_id} .db-ctx-sep {{ height: 1px; background: #e5e7eb; margin: 4px 0; }}

  /* Side Panel */
  #{table_id} .db-side-panel {{
    position: absolute; right: 0; top: 0; bottom: 0; width: 320px; background: #fff;
    border-left: 1px solid #dce0e5; box-shadow: -4px 0 12px rgba(0,0,0,0.06);
    z-index: 50; display: none; flex-direction: column; overflow: hidden;
  }}
  #{table_id} .db-side-panel.open {{ display: flex; }}
  #{table_id} .db-side-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px; border-bottom: 1px solid #eaecf0; font-weight: 600; font-size: 13px; color: #333;
  }}
  #{table_id} .db-side-close {{ cursor: pointer; display: inline-flex; align-items: center; padding: 4px; border-radius: 4px; }}
  #{table_id} .db-side-close:hover {{ background: #f0f1f3; }}
  #{table_id} .db-side-body {{ flex: 1; overflow-y: auto; padding: 12px 14px; }}
  #{table_id} .db-side-row {{ margin-bottom: 10px; }}
  #{table_id} .db-side-label {{ font-size: 11px; font-weight: 600; color: #888; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.3px; }}
  #{table_id} .db-side-value {{ font-size: 13px; color: #1b1f23; word-break: break-all; }}

  /* View containers */
  #{table_id} .db-view {{ display: none; }}
  #{table_id} .db-view.active {{ display: block; }}

  /* Data Profile */
  #{table_id} .db-profile {{ padding: 16px; overflow: auto; max-height: {height_px + 60}px; }}
  #{table_id} .db-profile table {{ font-size: 12px; }}
  #{table_id} .db-profile th {{ background: #f3f5f8; padding: 8px 12px; text-align: left; font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #dce0e5; }}
  #{table_id} .db-profile td {{ padding: 7px 12px; border-bottom: 1px solid #f0f1f3; font-size: 12px; }}
  #{table_id} .db-profile .db-spark {{
    display: inline-block; width: 80px; height: 20px; vertical-align: middle;
  }}
  #{table_id} .db-profile .db-spark rect {{ fill: #1a73e8; opacity: 0.7; }}

  /* Visualization */
  #{table_id} .db-viz {{ padding: 16px; overflow: auto; max-height: {height_px + 60}px; }}
  #{table_id} .db-viz-controls {{
    display: flex; gap: 10px; align-items: center; margin-bottom: 16px; flex-wrap: wrap;
  }}
  #{table_id} .db-viz-controls select {{
    padding: 5px 10px; border: 1px solid #d0d5dd; border-radius: 4px; font-size: 12px;
    font-family: inherit; color: #333; background: #fff; outline: none; cursor: pointer;
  }}
  #{table_id} .db-viz-controls select:focus {{ border-color: #1a73e8; }}
  #{table_id} .db-viz-controls label {{ font-size: 12px; color: #555; font-weight: 500; }}
  #{table_id} .db-chart-area {{
    background: #fafbfc; border: 1px solid #eaecf0; border-radius: 6px;
    padding: 20px; min-height: 300px; position: relative;
  }}
  #{table_id} .db-chart-area svg {{ width: 100%; }}

  /* Status Bar */
  #{table_id} .db-status-bar {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 4px 12px; border-top: 1px solid #eaecf0; background: #f8f9fb;
    font-size: 11px; color: #777;
  }}

  /* Profile Modal */
  #{table_id} .db-modal-backdrop {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.45); z-index: 5000;
    display: none; align-items: center; justify-content: center;
  }}
  #{table_id} .db-modal-backdrop.open {{ display: flex; }}
  #{table_id} .db-modal-card {{
    background: #fff; border-radius: 8px; border: 1px solid #dce0e5;
    box-shadow: 0 12px 32px rgba(0,0,0,0.25); width: 640px; max-width: 92%;
    max-height: 85%; display: flex; flex-direction: column; overflow: hidden;
  }}
  #{table_id} .db-modal-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 16px; border-bottom: 1px solid #eaecf0; background: #f8f9fb;
    font-weight: 600; font-size: 14px; color: #1b1f23;
  }}
  #{table_id} .db-modal-close {{
    cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
    padding: 4px 8px; border-radius: 4px; border: none; background: transparent; color: #666;
    font-size: 14px; font-weight: bold;
  }}
  #{table_id} .db-modal-close:hover {{ background: #eef1f5; color: #111; }}
  #{table_id} .db-modal-body {{ padding: 16px; overflow-y: auto; flex: 1; }}
  #{table_id} .db-spark-btn {{
    cursor: pointer; display: inline-flex; align-items: center; gap: 4px; padding: 2px 6px;
    border-radius: 4px; border: 1px solid #e0e0e0; background: #fafafa; transition: all 0.15s;
  }}
  #{table_id} .db-spark-btn:hover {{
    background: #e8f0fe; border-color: #1a73e8; color: #1a73e8;
  }}

  /* Toast */
  #{table_id} .db-toast {{
    position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%) translateY(10px);
    background: #333; color: #fff; padding: 8px 18px; border-radius: 6px; font-size: 12px;
    opacity: 0; pointer-events: none; transition: opacity 0.2s, transform 0.2s; z-index: 200;
  }}
  #{table_id} .db-toast.show {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
</style>

<!-- ═══ Top Bar ═══ -->
<div class="db-topbar" id="{table_id}_topbar">
  <div class="db-tab active" data-view="table" id="{table_id}_tab_table">
    {title} <span class="db-tab-chevron">{chevron}</span>
  </div>
  <div class="db-plus-btn" id="{table_id}_plus_btn" title="Add view">
    {plus_icon}
  </div>
</div>

<!-- Tab dropdown (outside topbar to avoid overflow clipping) -->
<div class="db-dropdown" id="{table_id}_tab_dd" style="top:38px;left:0;">
  <div class="db-dropdown-item" data-action="download-csv">Download all rows</div>
  <div class="db-dropdown-item" data-action="download-excel">Download all rows – Excel</div>
  <div class="db-dropdown-sep"></div>
  <div class="db-dropdown-item" data-action="copy-all">Copy results to clipboard</div>
</div>

<!-- Plus dropdown (outside topbar to avoid overflow clipping) -->
<div class="db-dropdown" id="{table_id}_plus_dd" style="top:38px;left:0;">
  <div class="db-dropdown-item" data-action="add-viz">📊 Visualization</div>
  <div class="db-dropdown-item" data-action="add-profile">📋 Data Profile</div>
</div>

<!-- ═══ Table View ═══ -->
<div class="db-view active" id="{table_id}_view_table">
  <div class="db-toolbar" id="{table_id}_toolbar">
    <div class="db-search-box">
      {search_icon}
      <input class="db-search-input" placeholder="Search columns & values…" id="{table_id}_search" autocomplete="off"/>
    </div>
    <button class="db-toolbar-btn" id="{table_id}_col_vis_btn">
      Columns {chevron}
    </button>
    <div id="{table_id}_filters" style="display:inline-flex;gap:4px;flex-wrap:wrap;"></div>
    <span class="db-row-summary" id="{table_id}_summary">{row_summary}</span>
  </div>
  <div class="db-table-wrap" id="{table_id}_wrap">
    <table id="{table_id}_table">
      <thead><tr id="{table_id}_thead_tr"></tr></thead>
      <tbody id="{table_id}_tbody"></tbody>
    </table>
  </div>
</div>

<!-- ═══ Visualization View ═══ -->
<div class="db-view" id="{table_id}_view_viz">
  <div class="db-viz">
    <div class="db-viz-controls" id="{table_id}_viz_controls">
      <label>X Axis:</label>
      <select id="{table_id}_viz_x_col"></select>

      <label>Y Axis:</label>
      <select id="{table_id}_viz_y_col"></select>

      <label>Aggregation:</label>
      <select id="{table_id}_viz_agg">
        <option value="COUNT">COUNT (Row count)</option>
        <option value="SUM">SUM</option>
        <option value="AVG">AVG (Mean)</option>
        <option value="MIN">MIN</option>
        <option value="MAX">MAX</option>
      </select>

      <label>Chart Type:</label>
      <select id="{table_id}_viz_type">
        <option value="bar">Bar Chart</option>
        <option value="line">Line Chart</option>
        <option value="scatter">Scatter Plot</option>
        <option value="histogram">Histogram</option>
      </select>
    </div>
    <div class="db-chart-area" id="{table_id}_chart_area"></div>
  </div>
</div>

<!-- ═══ Profile Chart Pop-Out Modal ═══ -->
<div class="db-modal-backdrop" id="{table_id}_modal">
  <div class="db-modal-card">
    <div class="db-modal-header">
      <span id="{table_id}_modal_title">Column Distribution</span>
      <button class="db-modal-close" id="{table_id}_modal_close">{close_icon}</button>
    </div>
    <div class="db-modal-body" id="{table_id}_modal_body"></div>
  </div>
</div>

<!-- ═══ Data Profile View ═══ -->
<div class="db-view" id="{table_id}_view_profile">
  <div class="db-profile" id="{table_id}_profile_body"></div>
</div>

<!-- ═══ Status Bar ═══ -->
<div class="db-status-bar">
  <span id="{table_id}_status_left"></span>
  <span id="{table_id}_status_right"></span>
</div>

<!-- ═══ Context Menu ═══ -->
<div class="db-context-menu" id="{table_id}_ctx">
  <div class="db-ctx-item" data-action="copy">Copy <span class="ctx-shortcut">⌘C</span></div>
  <div class="db-ctx-item has-sub" data-action="copy-as">
    Copy as
    <div class="db-ctx-sub">
      <div class="db-ctx-item" data-action="copy-csv">CSV</div>
      <div class="db-ctx-item" data-action="copy-tsv">TSV</div>
      <div class="db-ctx-item" data-action="copy-markdown">Markdown</div>
    </div>
  </div>
  <div class="db-ctx-sep"></div>
  <div class="db-ctx-item" data-action="filter-value">Filter by this value</div>
  <div class="db-ctx-item" data-action="exclude-value">Exclude this value</div>
  <div class="db-ctx-sep"></div>
  <div class="db-ctx-item" data-action="toggle-panel">Toggle side panel</div>
</div>

<!-- ═══ Column Filter Dropdown (shared, repositioned per column) ═══ -->
<div class="db-col-filter" id="{table_id}_col_filter">
  <div class="db-col-filter-search"><input placeholder="Search values…" id="{table_id}_cf_search"/></div>
  <div class="db-col-filter-selectall" id="{table_id}_cf_selall">
    <input type="checkbox" checked/> <span>Select All</span>
  </div>
  <div class="db-col-filter-body" id="{table_id}_cf_body"></div>
  <div class="db-col-filter-actions">
    <button id="{table_id}_cf_clear">Clear</button>
    <button class="primary" id="{table_id}_cf_apply">Apply</button>
  </div>
</div>

<!-- ═══ Column Selector Dropdown ═══ -->
<div class="db-col-selector" id="{table_id}_col_selector">
  <div class="db-col-selector-header">
    <input placeholder="Search columns…" id="{table_id}_cs_search"/>
  </div>
  <div class="db-col-selector-body" id="{table_id}_cs_body"></div>
  <div class="db-col-selector-actions">
    <button id="{table_id}_cs_none">None</button>
    <button id="{table_id}_cs_all">All</button>
  </div>
</div>

<!-- ═══ Side Panel ═══ -->
<div class="db-side-panel" id="{table_id}_panel">
  <div class="db-side-header">
    <span>Row Details</span>
    <span class="db-side-close" id="{table_id}_panel_close">{close_icon}</span>
  </div>
  <div class="db-side-body" id="{table_id}_panel_body"></div>
</div>

<!-- ═══ Toast ═══ -->
<div class="db-toast" id="{table_id}_toast"></div>

<script>
(function() {{
  "use strict";
  const TID = "{table_id}";
  const COLS = {col_meta_json};
  const DATA = {records_json};
  const ROOT = document.getElementById(TID);

  const $ = (id) => document.getElementById(id);
  const $$ = (sel) => ROOT.querySelectorAll(sel);

  /* ─── State ─── */
  let filteredData = DATA.slice();
  let sortCol = null, sortDir = 0;
  let activeFilters = [];       // {{col, value, mode:'include'|'exclude'}}
  let columnFilters = {{}};       // {{colName: Set of allowed values}} — per-column filter
  let visibleCols = new Set(COLS.map(c => c.name));
  let panelOpen = false, panelRowIdx = null;

  /* Selection state */
  let selAnchor = null;  // {{r, c}}
  let selEnd = null;     // {{r, c}}
  let isSelecting = false;

  /* Tab state */
  let activeView = 'table';
  let addedTabs = new Set();  // 'viz', 'profile'

  const TYPE_ICONS = {json.dumps(type_icons)};

  /* ─── Helpers ─── */
  function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}
  function toast(msg) {{
    const t = $(TID + '_toast');
    t.textContent = msg; t.classList.add('show');
    clearTimeout(t._tid); t._tid = setTimeout(() => t.classList.remove('show'), 2000);
  }}
  function copyText(text) {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(() => toast('Copied to clipboard'));
    }} else {{
      const ta = document.createElement('textarea'); ta.value = text;
      ta.style.cssText = 'position:fixed;opacity:0'; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); document.body.removeChild(ta); toast('Copied to clipboard');
    }}
  }}

  function getVisibleCols() {{ return COLS.filter(c => visibleCols.has(c.name)); }}

  /* ─── Sorting ─── */
  function doSort() {{
    if (!sortCol || sortDir === 0) return;
    const ci = COLS.findIndex(c => c.name === sortCol);
    if (ci < 0) return;
    const isNum = COLS[ci].dtype_category === 'integer' || COLS[ci].dtype_category === 'float';
    filteredData.sort((a, b) => {{
      let va = a[sortCol], vb = b[sortCol];
      if (va === 'null' || va === undefined) va = null;
      if (vb === 'null' || vb === undefined) vb = null;
      if (va === null && vb === null) return 0;
      if (va === null) return 1; if (vb === null) return -1;
      if (isNum) {{
        va = parseFloat(va); vb = parseFloat(vb);
        if (isNaN(va)) return 1; if (isNaN(vb)) return -1;
        return sortDir * (va - vb);
      }}
      return sortDir * String(va).localeCompare(String(vb));
    }});
  }}

  function handleSort(colName, thEl) {{
    $$('thead th').forEach(t => t.classList.remove('sorted-asc', 'sorted-desc'));
    if (sortCol === colName) {{
      sortDir = sortDir === 1 ? -1 : (sortDir === -1 ? 0 : 1);
    }} else {{ sortCol = colName; sortDir = 1; }}
    if (sortDir === 0) {{ sortCol = null; applyAllFilters(); return; }}
    thEl.classList.add(sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
    doSort();
    buildBody();
  }}

  /* ─── Filtering ─── */
  function applyAllFilters() {{
    let data = DATA.slice();
    // Column filters (per-column value selection)
    Object.keys(columnFilters).forEach(col => {{
      const allowed = columnFilters[col];
      if (allowed) data = data.filter(r => allowed.has(String(r[col] !== undefined ? r[col] : 'null')));
    }});
    // Active context-menu filters
    activeFilters.forEach(f => {{
      if (f.mode === 'include') data = data.filter(r => String(r[f.col]) === String(f.value));
      else data = data.filter(r => String(r[f.col]) !== String(f.value));
    }});
    // Global search
    const q = ($(TID + '_search').value || '').toLowerCase().trim();
    if (q) {{
      // Search column names too
      const matchingColNames = COLS.filter(c => c.name.toLowerCase().includes(q)).map(c => c.name);
      data = data.filter(row => {{
        // Match if any visible column name matches OR any cell value matches
        if (matchingColNames.length > 0) return true;
        return COLS.some(c => {{
          const v = row[c.name];
          return v !== undefined && String(v).toLowerCase().includes(q);
        }});
      }});
    }}
    filteredData = data;
    doSort();
    buildBody();
    renderFilterPills();
    updateSummary();
  }}

  function addFilter(col, value, mode) {{
    if (activeFilters.find(f => f.col === col && f.value === value && f.mode === mode)) return;
    activeFilters.push({{ col, value, mode }});
    applyAllFilters();
  }}
  function removeFilter(idx) {{ activeFilters.splice(idx, 1); applyAllFilters(); }}

  function renderFilterPills() {{
    const container = $(TID + '_filters');
    container.innerHTML = '';
    // Column filter pills
    Object.keys(columnFilters).forEach(col => {{
      const pill = document.createElement('span');
      pill.className = 'db-filter-pill';
      const n = columnFilters[col].size;
      const total = new Set(DATA.map(r => String(r[col] !== undefined ? r[col] : 'null'))).size;
      pill.innerHTML = esc(col) + ': ' + n + '/' + total + ' <span class="db-pill-close" data-cfcol="' + esc(col) + '">{close_icon}</span>';
      pill.querySelector('.db-pill-close').addEventListener('click', () => {{
        delete columnFilters[col];
        // Update header
        $$('thead th').forEach(th => {{ if (th.dataset.col === col) th.classList.remove('has-filter'); }});
        applyAllFilters();
      }});
      container.appendChild(pill);
    }});
    // Context-menu filter pills
    activeFilters.forEach((f, idx) => {{
      const pill = document.createElement('span');
      pill.className = 'db-filter-pill';
      const label = f.mode === 'include' ? (f.col + ' = ' + f.value) : (f.col + ' ≠ ' + f.value);
      pill.innerHTML = esc(label) + ' <span class="db-pill-close">{close_icon}</span>';
      pill.querySelector('.db-pill-close').addEventListener('click', () => removeFilter(idx));
      container.appendChild(pill);
    }});
    // Update toolbar button state
    const btn = $(TID + '_col_vis_btn');
    if (visibleCols.size < COLS.length) btn.classList.add('has-active'); else btn.classList.remove('has-active');
  }}

  function updateSummary() {{
    const s = $(TID + '_summary');
    const total = DATA.length, shown = filteredData.length;
    if (shown !== total) s.textContent = 'Showing ' + shown.toLocaleString() + ' of ' + total.toLocaleString() + ' rows';
    else s.textContent = '{row_summary}';
  }}

  /* ─── Rendering ─── */
  function buildHeader() {{
    const tr = $(TID + '_thead_tr');
    tr.innerHTML = '';
    const thIdx = document.createElement('th');
    thIdx.className = 'db-row-idx'; thIdx.textContent = '';
    tr.appendChild(thIdx);
    getVisibleCols().forEach((col, ci) => {{
      const th = document.createElement('th');
      th.dataset.col = col.name; th.dataset.ci = ci;
      if (columnFilters[col.name]) th.classList.add('has-filter');
      if (sortCol === col.name) th.classList.add(sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
      th.innerHTML = '<div class="db-th-content">'
        + '<span class="db-th-inner">'
        + (TYPE_ICONS[col.name] || '') + ' <span>' + esc(col.name) + '</span> '
        + '{sort_icon}'
        + '</span>'
        + '<span class="db-th-filter-btn" data-col="' + esc(col.name) + '" title="Filter">'
        + '<svg viewBox="0 0 16 16" width="12" height="12" fill="none"><path d="M2 3H14L10 8.5V12L6 14V8.5L2 3Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>'
        + '</span>'
        + '</div>'
        + '<div class="db-resize-handle"></div>';
      // Sort on click (on the inner area, not filter btn)
      th.querySelector('.db-th-inner').addEventListener('click', () => handleSort(col.name, th));
      // Filter btn
      th.querySelector('.db-th-filter-btn').addEventListener('click', (e) => {{
        e.stopPropagation();
        openColumnFilter(col.name, th);
      }});
      // Resize handle
      initResize(th.querySelector('.db-resize-handle'), th);
      tr.appendChild(th);
    }});
  }}

  function buildBody() {{
    const tbody = $(TID + '_tbody');
    tbody.innerHTML = '';
    const visCols = getVisibleCols();
    filteredData.forEach((row, ri) => {{
      const tr = document.createElement('tr');
      const tdIdx = document.createElement('td');
      tdIdx.className = 'db-row-idx'; tdIdx.textContent = ri + 1;
      tr.appendChild(tdIdx);
      visCols.forEach((col, ci) => {{
        const td = document.createElement('td');
        const val = row[col.name];
        td.textContent = val !== undefined ? val : '';
        td.dataset.ri = ri; td.dataset.ci = ci; td.dataset.col = col.name;
        td.dataset.val = val !== undefined ? val : '';
        if (val === 'null' || val === '' || val === undefined) td.classList.add('db-null');
        else if (col.dtype_category === 'boolean') td.classList.add(val === 'true' ? 'db-bool-true' : 'db-bool-false');
        else if (col.dtype_category === 'integer' || col.dtype_category === 'float') td.classList.add('db-number');
        tr.appendChild(td);
      }});
      tbody.appendChild(tr);
    }});
    clearSelection();
    updateSummary();
  }}

  /* ─── Search ─── */
  $(TID + '_search').addEventListener('input', () => applyAllFilters());

  /* ─── Column Filter Dropdown ─── */
  let cfCol = null; // currently open filter column
  let cfSelected = new Set();

  function openColumnFilter(colName, thEl) {{
    const cf = $(TID + '_col_filter');
    // If same column already open, close
    if (cf.classList.contains('open') && cfCol === colName) {{ cf.classList.remove('open'); return; }}
    cfCol = colName;
    // Position below the header
    const rect = thEl.getBoundingClientRect();
    const rootRect = ROOT.getBoundingClientRect();
    cf.style.left = (rect.left - rootRect.left) + 'px';
    cf.style.top = (rect.bottom - rootRect.top) + 'px';
    // Compute unique values and counts
    const valCounts = {{}};
    DATA.forEach(r => {{
      const v = String(r[colName] !== undefined ? r[colName] : 'null');
      valCounts[v] = (valCounts[v] || 0) + 1;
    }});
    const sortedVals = Object.keys(valCounts).sort((a, b) => valCounts[b] - valCounts[a]);
    // Initialize selection from existing filter or all
    if (columnFilters[colName]) cfSelected = new Set(columnFilters[colName]);
    else cfSelected = new Set(sortedVals);
    // Render
    renderCfBody(sortedVals, valCounts, '');
    $(TID + '_cf_search').value = '';
    $(TID + '_cf_selall').querySelector('input').checked = cfSelected.size === sortedVals.length;
    cf.classList.add('open');
    $(TID + '_cf_search').focus();
  }}

  function renderCfBody(vals, valCounts, query) {{
    const body = $(TID + '_cf_body');
    body.innerHTML = '';
    const filtered = query ? vals.filter(v => v.toLowerCase().includes(query.toLowerCase())) : vals;
    filtered.forEach(v => {{
      const item = document.createElement('div');
      item.className = 'db-col-filter-item';
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = cfSelected.has(v);
      const sp = document.createElement('span'); sp.textContent = v; sp.title = v;
      const cnt = document.createElement('span'); cnt.className = 'val-count'; cnt.textContent = valCounts[v];
      cb.addEventListener('change', () => {{
        if (cb.checked) cfSelected.add(v); else cfSelected.delete(v);
        $(TID + '_cf_selall').querySelector('input').checked = cfSelected.size === vals.length;
      }});
      item.addEventListener('click', (e) => {{ if (e.target !== cb) cb.click(); }});
      item.appendChild(cb); item.appendChild(sp); item.appendChild(cnt);
      body.appendChild(item);
    }});
  }}

  // Search within column filter
  $(TID + '_cf_search').addEventListener('input', function() {{
    const valCounts = {{}};
    DATA.forEach(r => {{
      const v = String(r[cfCol] !== undefined ? r[cfCol] : 'null');
      valCounts[v] = (valCounts[v] || 0) + 1;
    }});
    const sortedVals = Object.keys(valCounts).sort((a, b) => valCounts[b] - valCounts[a]);
    renderCfBody(sortedVals, valCounts, this.value);
  }});

  // Select All
  $(TID + '_cf_selall').addEventListener('click', function() {{
    const cb = this.querySelector('input');
    const valCounts = {{}};
    DATA.forEach(r => {{
      const v = String(r[cfCol] !== undefined ? r[cfCol] : 'null');
      valCounts[v] = (valCounts[v] || 0) + 1;
    }});
    if (cb.checked) {{
      cfSelected = new Set(Object.keys(valCounts));
    }} else {{
      cfSelected = new Set();
    }}
    const sortedVals = Object.keys(valCounts).sort((a, b) => valCounts[b] - valCounts[a]);
    renderCfBody(sortedVals, valCounts, $(TID + '_cf_search').value);
  }});

  // Apply
  $(TID + '_cf_apply').addEventListener('click', function() {{
    const allVals = new Set(DATA.map(r => String(r[cfCol] !== undefined ? r[cfCol] : 'null')));
    if (cfSelected.size === allVals.size) {{
      delete columnFilters[cfCol];
      $$('thead th').forEach(th => {{ if (th.dataset.col === cfCol) th.classList.remove('has-filter'); }});
    }} else {{
      columnFilters[cfCol] = new Set(cfSelected);
      $$('thead th').forEach(th => {{ if (th.dataset.col === cfCol) th.classList.add('has-filter'); }});
    }}
    $(TID + '_col_filter').classList.remove('open');
    applyAllFilters();
  }});

  // Clear
  $(TID + '_cf_clear').addEventListener('click', function() {{
    delete columnFilters[cfCol];
    $$('thead th').forEach(th => {{ if (th.dataset.col === cfCol) th.classList.remove('has-filter'); }});
    $(TID + '_col_filter').classList.remove('open');
    applyAllFilters();
  }});

  /* ─── Column Visibility ─── */
  const colVisBtn = $(TID + '_col_vis_btn');
  const colSel = $(TID + '_col_selector');

  colVisBtn.addEventListener('click', (e) => {{
    e.stopPropagation();
    if (colSel.classList.contains('open')) {{ colSel.classList.remove('open'); return; }}
    const rect = colVisBtn.getBoundingClientRect();
    const rootRect = ROOT.getBoundingClientRect();
    colSel.style.left = (rect.left - rootRect.left) + 'px';
    colSel.style.top = (rect.bottom - rootRect.top + 4) + 'px';
    renderColSelector('');
    $(TID + '_cs_search').value = '';
    colSel.classList.add('open');
  }});

  function renderColSelector(query) {{
    const body = $(TID + '_cs_body');
    body.innerHTML = '';
    const cols = query ? COLS.filter(c => c.name.toLowerCase().includes(query.toLowerCase())) : COLS;
    cols.forEach(col => {{
      const item = document.createElement('div');
      item.className = 'db-col-selector-item';
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = visibleCols.has(col.name);
      const sp = document.createElement('span'); sp.textContent = col.name;
      cb.addEventListener('change', () => {{
        if (cb.checked) visibleCols.add(col.name); else visibleCols.delete(col.name);
        buildHeader(); buildBody(); renderFilterPills();
      }});
      item.addEventListener('click', (e) => {{ if (e.target !== cb) cb.click(); }});
      item.appendChild(cb); item.appendChild(sp);
      body.appendChild(item);
    }});
  }}

  $(TID + '_cs_search').addEventListener('input', function() {{ renderColSelector(this.value); }});
  $(TID + '_cs_all').addEventListener('click', () => {{
    visibleCols = new Set(COLS.map(c => c.name));
    buildHeader(); buildBody(); renderColSelector($(TID + '_cs_search').value); renderFilterPills();
  }});
  $(TID + '_cs_none').addEventListener('click', () => {{
    visibleCols = new Set();
    buildHeader(); buildBody(); renderColSelector($(TID + '_cs_search').value); renderFilterPills();
  }});

  /* ─── Excel-like Selection ─── */
  function getCellCoords(td) {{
    const ri = parseInt(td.dataset.ri), ci = parseInt(td.dataset.ci);
    return isNaN(ri) || isNaN(ci) ? null : {{r: ri, c: ci}};
  }}

  function clearSelection() {{ $$('tbody td.db-sel, tbody td.db-sel-border-top, tbody td.db-sel-border-bottom, tbody td.db-sel-border-left, tbody td.db-sel-border-right').forEach(td => {{ td.classList.remove('db-sel', 'db-sel-border-top', 'db-sel-border-bottom', 'db-sel-border-left', 'db-sel-border-right'); }}); selAnchor = null; selEnd = null; }}

  function paintSelection() {{
    $$('tbody td.db-sel, tbody td.db-sel-border-top, tbody td.db-sel-border-bottom, tbody td.db-sel-border-left, tbody td.db-sel-border-right').forEach(td => {{ td.classList.remove('db-sel', 'db-sel-border-top', 'db-sel-border-bottom', 'db-sel-border-left', 'db-sel-border-right'); }});
    if (!selAnchor || !selEnd) return;
    const r1 = Math.min(selAnchor.r, selEnd.r), r2 = Math.max(selAnchor.r, selEnd.r);
    const c1 = Math.min(selAnchor.c, selEnd.c), c2 = Math.max(selAnchor.c, selEnd.c);
    const tbody = $(TID + '_tbody');
    const rows = tbody.querySelectorAll('tr');
    for (let r = r1; r <= r2 && r < rows.length; r++) {{
      const tds = rows[r].querySelectorAll('td:not(.db-row-idx)');
      for (let c = c1; c <= c2 && c < tds.length; c++) {{
        tds[c].classList.add('db-sel');
        if (r === r1) tds[c].classList.add('db-sel-border-top');
        if (r === r2) tds[c].classList.add('db-sel-border-bottom');
        if (c === c1) tds[c].classList.add('db-sel-border-left');
        if (c === c2) tds[c].classList.add('db-sel-border-right');
      }}
    }}
    // Update status
    const count = (r2 - r1 + 1) * (c2 - c1 + 1);
    $(TID + '_status_left').textContent = count > 1 ? count + ' cells selected' : '';

    // Compute sum/avg for numeric selections
    if (count > 1) {{
      let sum = 0, numCount = 0;
      const visCols = getVisibleCols();
      for (let r = r1; r <= r2; r++) {{
        for (let c = c1; c <= c2; c++) {{
          const col = visCols[c];
          if (col && (col.dtype_category === 'integer' || col.dtype_category === 'float')) {{
            const v = parseFloat(filteredData[r][col.name]);
            if (!isNaN(v)) {{ sum += v; numCount++; }}
          }}
        }}
      }}
      if (numCount > 0) {{
        $(TID + '_status_right').textContent = 'Sum: ' + sum.toLocaleString(undefined, {{maximumFractionDigits: 4}}) + '  Avg: ' + (sum / numCount).toLocaleString(undefined, {{maximumFractionDigits: 4}}) + '  Count: ' + numCount;
      }} else {{
        $(TID + '_status_right').textContent = '';
      }}
    }} else {{
      $(TID + '_status_right').textContent = '';
    }}
  }}

  function getSelectedText(sep) {{
    if (!selAnchor || !selEnd) return '';
    const r1 = Math.min(selAnchor.r, selEnd.r), r2 = Math.max(selAnchor.r, selEnd.r);
    const c1 = Math.min(selAnchor.c, selEnd.c), c2 = Math.max(selAnchor.c, selEnd.c);
    const visCols = getVisibleCols();
    let lines = [];
    for (let r = r1; r <= r2; r++) {{
      let cells = [];
      for (let c = c1; c <= c2; c++) {{
        const col = visCols[c];
        cells.push(col ? (filteredData[r][col.name] || '') : '');
      }}
      lines.push(cells.join(sep));
    }}
    return lines.join('\\n');
  }}

  // Mouse events for selection
  ROOT.addEventListener('mousedown', (e) => {{
    const td = e.target.closest('#' + TID + ' tbody td:not(.db-row-idx)');
    if (!td) return;
    const coords = getCellCoords(td);
    if (!coords) return;
    if (e.shiftKey && selAnchor) {{
      selEnd = coords;
    }} else {{
      selAnchor = coords;
      selEnd = coords;
    }}
    isSelecting = true;
    paintSelection();
  }});

  ROOT.addEventListener('mousemove', (e) => {{
    if (!isSelecting) return;
    const td = e.target.closest('#' + TID + ' tbody td:not(.db-row-idx)');
    if (!td) return;
    const coords = getCellCoords(td);
    if (!coords) return;
    selEnd = coords;
    paintSelection();
  }});

  document.addEventListener('mouseup', () => {{ isSelecting = false; }});

  /* ─── Context Menu ─── */
  const ctx = $(TID + '_ctx');
  ROOT.addEventListener('contextmenu', (e) => {{
    const td = e.target.closest('#' + TID + ' tbody td:not(.db-row-idx)');
    if (!td) return;
    e.preventDefault();
    const coords = getCellCoords(td);
    if (coords && (!selAnchor || !selEnd || coords.r < Math.min(selAnchor.r, selEnd.r) || coords.r > Math.max(selAnchor.r, selEnd.r) || coords.c < Math.min(selAnchor.c, selEnd.c) || coords.c > Math.max(selAnchor.c, selEnd.c))) {{
      selAnchor = coords; selEnd = coords; paintSelection();
    }}
    ctx.style.left = e.clientX + 'px'; ctx.style.top = e.clientY + 'px';
    ctx.classList.add('open');
    ctx._col = td.dataset.col; ctx._val = td.dataset.val; ctx._ri = parseInt(td.dataset.ri);
  }});

  document.addEventListener('click', (e) => {{
    if (!e.target.closest('#' + TID + '_ctx')) ctx.classList.remove('open');
    if (!e.target.closest('#' + TID + '_col_filter') && !e.target.closest('.db-th-filter-btn')) $(TID + '_col_filter').classList.remove('open');
    if (!e.target.closest('#' + TID + '_col_selector') && !e.target.closest('#' + TID + '_col_vis_btn')) colSel.classList.remove('open');
    if (!e.target.closest('#' + TID + '_tab_dd') && !e.target.closest('#' + TID + '_tab_table')) $(TID + '_tab_dd').classList.remove('open');
    if (!e.target.closest('#' + TID + '_plus_dd') && !e.target.closest('#' + TID + '_plus_btn')) $(TID + '_plus_dd').classList.remove('open');
  }});

  ctx.addEventListener('click', (e) => {{
    const item = e.target.closest('.db-ctx-item');
    if (!item) return;
    const action = item.dataset.action;
    if (action === 'copy') {{ copyText(getSelectedText('\\t') || ctx._val); }}
    else if (action === 'copy-csv') {{ copyAsFormat('csv'); }}
    else if (action === 'copy-tsv') {{ copyAsFormat('tsv'); }}
    else if (action === 'copy-markdown') {{ copyAsFormat('markdown'); }}
    else if (action === 'filter-value') {{ addFilter(ctx._col, ctx._val, 'include'); }}
    else if (action === 'exclude-value') {{ addFilter(ctx._col, ctx._val, 'exclude'); }}
    else if (action === 'toggle-panel') {{ togglePanel(ctx._ri); }}
    ctx.classList.remove('open');
  }});

  /* ─── Copy/Export ─── */
  function copyAsFormat(fmt) {{
    const colNames = getVisibleCols().map(c => c.name);
    let text = '';
    if (fmt === 'csv') {{
      text = colNames.join(',') + '\\n';
      filteredData.forEach(r => {{
        text += colNames.map(c => {{ let v = r[c] || ''; if (v.includes(',') || v.includes('"') || v.includes('\\n')) v = '"' + v.replace(/"/g, '""') + '"'; return v; }}).join(',') + '\\n';
      }});
    }} else if (fmt === 'tsv') {{
      text = colNames.join('\\t') + '\\n';
      filteredData.forEach(r => {{ text += colNames.map(c => (r[c] || '').replace(/\\t/g, ' ')).join('\\t') + '\\n'; }});
    }} else if (fmt === 'markdown') {{
      text = '| ' + colNames.join(' | ') + ' |\\n';
      text += '| ' + colNames.map(() => '---').join(' | ') + ' |\\n';
      filteredData.forEach(r => {{ text += '| ' + colNames.map(c => (r[c] || '').replace(/\\|/g, '\\\\|')).join(' | ') + ' |\\n'; }});
    }}
    copyText(text);
  }}

  function downloadFile(fmt) {{
    const colNames = getVisibleCols().map(c => c.name);
    let content, mime, ext;
    if (fmt === 'csv') {{
      content = colNames.join(',') + '\\n';
      filteredData.forEach(r => {{ content += colNames.map(c => {{ let v = r[c] || ''; if (v.includes(',') || v.includes('"') || v.includes('\\n')) v = '"' + v.replace(/"/g, '""') + '"'; return v; }}).join(',') + '\\n'; }});
      mime = 'text/csv;charset=utf-8;'; ext = 'csv';
    }} else {{
      content = '\\uFEFF' + colNames.join(',') + '\\n';
      filteredData.forEach(r => {{ content += colNames.map(c => {{ let v = r[c] || ''; if (v.includes(',') || v.includes('"') || v.includes('\\n')) v = '"' + v.replace(/"/g, '""') + '"'; return v; }}).join(',') + '\\n'; }});
      mime = 'application/vnd.ms-excel'; ext = 'xls';
    }}
    const blob = new Blob([content], {{ type: mime }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'data.' + ext; a.click();
    URL.revokeObjectURL(url); toast('Downloaded as ' + ext.toUpperCase());
  }}

  /* ─── Keyboard ─── */
  ROOT.setAttribute('tabindex', '0'); ROOT.style.outline = 'none';
  ROOT.addEventListener('keydown', (e) => {{
    if ((e.metaKey || e.ctrlKey) && e.key === 'c') {{
      const sel = getSelectedText('\\t');
      if (sel) {{ e.preventDefault(); copyText(sel); }}
    }}
    if ((e.metaKey || e.ctrlKey) && e.key === 'a') {{
      e.preventDefault();
      selAnchor = {{r: 0, c: 0}};
      selEnd = {{r: filteredData.length - 1, c: getVisibleCols().length - 1}};
      paintSelection();
    }}
  }});

  /* ─── Side Panel ─── */
  function togglePanel(ri) {{
    const panel = $(TID + '_panel');
    if (panelOpen && panelRowIdx === ri) {{ panel.classList.remove('open'); panelOpen = false; panelRowIdx = null; }}
    else showPanel(ri != null ? ri : 0);
  }}
  function showPanel(ri) {{
    const panel = $(TID + '_panel');
    const body = $(TID + '_panel_body');
    const row = filteredData[ri]; if (!row) return;
    panelRowIdx = ri; panelOpen = true; body.innerHTML = '';
    COLS.forEach(col => {{
      const div = document.createElement('div'); div.className = 'db-side-row';
      div.innerHTML = '<div class="db-side-label">' + esc(col.name) + '</div><div class="db-side-value">' + esc(row[col.name] || '') + '</div>';
      body.appendChild(div);
    }});
    panel.classList.add('open');
  }}
  $(TID + '_panel_close').addEventListener('click', () => {{ $(TID + '_panel').classList.remove('open'); panelOpen = false; panelRowIdx = null; }});

  /* ─── Tab System ─── */
  $(TID + '_tab_table').addEventListener('click', (e) => {{
    e.stopPropagation();
    const dd = $(TID + '_tab_dd');
    if (e.target.closest('.db-tab-chevron')) {{
      dd.classList.toggle('open');
      const rect = $(TID + '_tab_table').getBoundingClientRect();
      const rootRect = ROOT.getBoundingClientRect();
      dd.style.left = Math.max(0, rect.left - rootRect.left) + 'px';
      dd.style.top = '38px';
      return;
    }}
    switchView('table');
  }});

  $(TID + '_tab_dd').addEventListener('click', (e) => {{
    const item = e.target.closest('.db-dropdown-item');
    if (!item) return;
    const action = item.dataset.action;
    if (action === 'download-csv') downloadFile('csv');
    if (action === 'download-excel') downloadFile('excel');
    if (action === 'copy-all') copyAsFormat('csv');
    $(TID + '_tab_dd').classList.remove('open');
  }});

  // Plus button
  $(TID + '_plus_btn').addEventListener('click', (e) => {{
    e.stopPropagation();
    const dd = $(TID + '_plus_dd');
    dd.classList.toggle('open');
    const rect = $(TID + '_plus_btn').getBoundingClientRect();
    const rootRect = ROOT.getBoundingClientRect();
    dd.style.left = Math.max(0, Math.min(rect.left - rootRect.left, rootRect.width - 220)) + 'px';
    dd.style.top = '38px';
  }});

  $(TID + '_plus_dd').addEventListener('click', (e) => {{
    const item = e.target.closest('.db-dropdown-item');
    if (!item) return;
    const action = item.dataset.action;
    if (action === 'add-viz') {{ addTab('viz', '📊 Visualization'); }}
    if (action === 'add-profile') {{ addTab('profile', '📋 Data Profile'); }}
    $(TID + '_plus_dd').classList.remove('open');
  }});

  function addTab(viewName, label) {{
    if (addedTabs.has(viewName)) {{ switchView(viewName); return; }}
    addedTabs.add(viewName);
    const tab = document.createElement('div');
    tab.className = 'db-tab'; tab.dataset.view = viewName;
    tab.innerHTML = label + ' <span class="db-tab-close" data-view="' + viewName + '">{close_icon}</span>';
    tab.addEventListener('click', (e) => {{
      if (e.target.closest('.db-tab-close')) {{
        removeTab(viewName); return;
      }}
      switchView(viewName);
    }});
    $(TID + '_plus_btn').before(tab);
    switchView(viewName);
    if (viewName === 'profile') buildProfile();
    if (viewName === 'viz') buildVizControls();
  }}

  function removeTab(viewName) {{
    addedTabs.delete(viewName);
    const tab = ROOT.querySelector('.db-tab[data-view="' + viewName + '"]');
    if (tab) tab.remove();
    if (activeView === viewName) switchView('table');
  }}

  function switchView(viewName) {{
    activeView = viewName;
    ROOT.querySelectorAll('.db-tab').forEach(t => t.classList.toggle('active', t.dataset.view === viewName));
    ROOT.querySelectorAll('.db-view').forEach(v => v.classList.remove('active'));
    const view = $(TID + '_view_' + viewName);
    if (view) view.classList.add('active');
  }}

  /* ─── Profile Modal ─── */
  const modal = $(TID + '_modal');
  const modalClose = $(TID + '_modal_close');
  modalClose.addEventListener('click', () => modal.classList.remove('open'));
  modal.addEventListener('click', (e) => {{ if (e.target === modal) modal.classList.remove('open'); }});

  function openProfileModal(colName) {{
    const titleEl = $(TID + '_modal_title');
    const bodyEl = $(TID + '_modal_body');
    const col = COLS.find(c => c.name === colName);
    if (!col) return;

    titleEl.textContent = '📊 Distribution: ' + colName + ' (' + col.dtype_category + ')';
    const vals = DATA.map(r => r[colName]);
    const nonNull = vals.filter(v => v !== 'null' && v !== undefined && v !== '');
    const isNum = col.dtype_category === 'integer' || col.dtype_category === 'float';

    let html = '<div style="display:flex;gap:20px;margin-bottom:16px;flex-wrap:wrap;background:#f8f9fb;padding:12px;border-radius:6px;font-size:12px;">';
    html += '<div><strong>Total Rows:</strong> ' + vals.length + '</div>';
    html += '<div><strong>Non-Null:</strong> ' + nonNull.length + '</div>';
    html += '<div><strong>Nulls:</strong> ' + (vals.length - nonNull.length) + '</div>';
    html += '<div><strong>Unique:</strong> ' + new Set(nonNull).size + '</div>';

    if (isNum) {{
      const nums = nonNull.map(Number).filter(n => !isNaN(n));
      if (nums.length) {{
        const sum = nums.reduce((a, b) => a + b, 0);
        const mean = sum / nums.length;
        const min = Math.min(...nums), max = Math.max(...nums);
        const sorted = [...nums].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        html += '<div><strong>Min:</strong> ' + min + '</div>';
        html += '<div><strong>Max:</strong> ' + max + '</div>';
        html += '<div><strong>Mean:</strong> ' + mean.toFixed(4) + '</div>';
        html += '<div><strong>Median:</strong> ' + median + '</div>';
      }}
    }}
    html += '</div>';

    // Chart SVG
    const chartW = 560, chartH = 260, padL = 60, padB = 40, padT = 20;
    if (isNum) {{
      const nums = nonNull.map(Number).filter(n => !isNaN(n));
      const mn = Math.min(...nums), mx = Math.max(...nums);
      const range = mx - mn || 1;
      const buckets = 15;
      const counts = new Array(buckets).fill(0);
      nums.forEach(n => {{ let b = Math.floor((n - mn) / range * buckets); if (b >= buckets) b = buckets - 1; counts[b]++; }});
      const maxC = Math.max(...counts) || 1;
      const barW = (chartW - padL) / buckets;

      let svg = '<svg viewBox="0 0 ' + (chartW + 20) + ' ' + (chartH + padB + padT) + '" style="width:100%;height:auto;">';
      counts.forEach((c, i) => {{
        const h = (c / maxC) * (chartH - padT);
        const x = padL + i * barW;
        const y = chartH - h;
        const bStart = (mn + (i / buckets) * range).toFixed(2);
        const bEnd = (mn + ((i + 1) / buckets) * range).toFixed(2);
        svg += '<rect x="' + (x + 1) + '" y="' + y + '" width="' + (barW - 2) + '" height="' + h + '" rx="2" fill="#1a73e8" opacity="0.85"><title>Range: ' + bStart + ' - ' + bEnd + '\\nCount: ' + c + '</title></rect>';
        if (c > 0) svg += '<text x="' + (x + barW / 2) + '" y="' + (y - 4) + '" text-anchor="middle" font-size="10" fill="#444">' + c + '</text>';
      }});
      // Axes
      svg += '<line x1="' + padL + '" y1="' + chartH + '" x2="' + chartW + '" y2="' + chartH + '" stroke="#ccc"/>';
      svg += '<line x1="' + padL + '" y1="10" x2="' + padL + '" y2="' + chartH + '" stroke="#ccc"/>';
      // X labels
      for (let i = 0; i <= buckets; i += 3) {{
        const v = (mn + (i / buckets) * range).toFixed(1);
        svg += '<text x="' + (padL + i * barW) + '" y="' + (chartH + 16) + '" text-anchor="middle" font-size="10" fill="#666">' + v + '</text>';
      }}
      svg += '</svg>';
      html += svg;
    }} else {{
      const freqs = {{}};
      nonNull.forEach(v => {{ freqs[v] = (freqs[v] || 0) + 1; }});
      const entries = Object.entries(freqs).sort((a, b) => b[1] - a[1]).slice(0, 20);
      const maxC = entries.length ? Math.max(...entries.map(e => e[1])) : 1;
      const barH = 22, gap = 6, labelW = 140, drawW = 380;
      const svgH = entries.length * (barH + gap) + 20;

      let svg = '<svg viewBox="0 0 ' + (labelW + drawW + 60) + ' ' + svgH + '" style="width:100%;height:auto;">';
      entries.forEach(([label, count], i) => {{
        const y = i * (barH + gap) + 10;
        const w = (count / maxC) * drawW;
        const shortLabel = label.length > 20 ? label.substring(0, 18) + '…' : label;
        svg += '<text x="' + (labelW - 6) + '" y="' + (y + barH / 2 + 4) + '" text-anchor="end" font-size="11" fill="#333">' + esc(shortLabel) + '</text>';
        svg += '<rect x="' + labelW + '" y="' + y + '" width="' + w + '" height="' + barH + '" rx="3" fill="#1a73e8" opacity="0.85"><title>' + esc(label) + ': ' + count + '</title></rect>';
        svg += '<text x="' + (labelW + w + 6) + '" y="' + (y + barH / 2 + 4) + '" font-size="11" fill="#555">' + count + '</text>';
      }});
      svg += '</svg>';
      html += svg;
    }}

    bodyEl.innerHTML = html;
    modal.classList.add('open');
  }}

  /* ─── Data Profile ─── */
  function buildProfile() {{
    const body = $(TID + '_profile_body');
    body.innerHTML = '';
    const table = document.createElement('table');
    table.style.width = '100%';
    const thead = document.createElement('thead');
    thead.innerHTML = '<tr><th>Column</th><th>Type</th><th>Count</th><th>Nulls</th><th>Unique</th><th>Min</th><th>Max</th><th>Mean</th><th>Distribution (Click to pop out)</th></tr>';
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    COLS.forEach(col => {{
      const vals = DATA.map(r => r[col.name]);
      const nonNull = vals.filter(v => v !== 'null' && v !== undefined && v !== '');
      const unique = new Set(nonNull);
      const isNum = col.dtype_category === 'integer' || col.dtype_category === 'float';
      let minV = '', maxV = '', meanV = '';
      if (isNum) {{
        const nums = nonNull.map(Number).filter(n => !isNaN(n));
        if (nums.length) {{
          minV = Math.min(...nums).toLocaleString(undefined, {{maximumFractionDigits: 4}});
          maxV = Math.max(...nums).toLocaleString(undefined, {{maximumFractionDigits: 4}});
          meanV = (nums.reduce((a, b) => a + b, 0) / nums.length).toLocaleString(undefined, {{maximumFractionDigits: 4}});
        }}
      }} else {{
        const sorted = [...nonNull].sort();
        if (sorted.length) {{ minV = sorted[0]; maxV = sorted[sorted.length - 1]; }}
      }}

      let sparkSvg = '';
      if (isNum) {{
        const nums = nonNull.map(Number).filter(n => !isNaN(n));
        if (nums.length > 1) {{
          const mn = Math.min(...nums), mx = Math.max(...nums);
          const range = mx - mn || 1;
          const buckets = 10; const counts = new Array(buckets).fill(0);
          nums.forEach(n => {{ let b = Math.floor((n - mn) / range * buckets); if (b >= buckets) b = buckets - 1; counts[b]++; }});
          const maxC = Math.max(...counts);
          const bw = 80 / buckets;
          sparkSvg = '<svg class="db-spark" viewBox="0 0 80 20">';
          counts.forEach((c, i) => {{
            const h = maxC ? (c / maxC) * 18 : 0;
            sparkSvg += '<rect x="' + (i * bw) + '" y="' + (20 - h) + '" width="' + (bw - 1) + '" height="' + h + '"/>';
          }});
          sparkSvg += '</svg>';
        }}
      }} else {{
        const freqs = {{}};
        nonNull.forEach(v => {{ freqs[v] = (freqs[v] || 0) + 1; }});
        const top = Object.entries(freqs).sort((a, b) => b[1] - a[1]).slice(0, 5);
        const maxC = top.length ? top[0][1] : 1;
        const bw = 80 / Math.max(top.length, 1);
        sparkSvg = '<svg class="db-spark" viewBox="0 0 80 20">';
        top.forEach(([v, c], i) => {{
          const h = (c / maxC) * 18;
          sparkSvg += '<rect x="' + (i * bw) + '" y="' + (20 - h) + '" width="' + (bw - 1) + '" height="' + h + '"/>';
        }});
        sparkSvg += '</svg>';
      }}

      const tr = document.createElement('tr');
      tr.innerHTML = '<td><strong>' + esc(col.name) + '</strong></td>'
        + '<td>' + esc(col.dtype_category) + '</td>'
        + '<td>' + nonNull.length + '</td>'
        + '<td>' + (vals.length - nonNull.length) + '</td>'
        + '<td>' + unique.size + '</td>'
        + '<td>' + esc(String(minV)) + '</td>'
        + '<td>' + esc(String(maxV)) + '</td>'
        + '<td>' + esc(String(meanV)) + '</td>'
        + '<td><button class="db-spark-btn" data-col="' + esc(col.name) + '">' + sparkSvg + ' 🔍</button></td>';

      tr.querySelector('.db-spark-btn').addEventListener('click', () => openProfileModal(col.name));
      tbody.appendChild(tr);
    }});
    table.appendChild(tbody);
    body.appendChild(table);
  }}

  /* ─── Visualization ─── */
  function buildVizControls() {{
    const xSel = $(TID + '_viz_x_col');
    const ySel = $(TID + '_viz_y_col');
    xSel.innerHTML = ''; ySel.innerHTML = '';

    COLS.forEach(col => {{
      const opt1 = document.createElement('option');
      opt1.value = col.name; opt1.textContent = col.name;
      xSel.appendChild(opt1);
    }});

    const optRowCnt = document.createElement('option');
    optRowCnt.value = '__row_count__'; optRowCnt.textContent = '(Row count)';
    ySel.appendChild(optRowCnt);

    COLS.forEach(col => {{
      const opt2 = document.createElement('option');
      opt2.value = col.name; opt2.textContent = col.name;
      ySel.appendChild(opt2);
    }});

    xSel.addEventListener('change', renderChart);
    ySel.addEventListener('change', renderChart);
    $(TID + '_viz_agg').addEventListener('change', renderChart);
    $(TID + '_viz_type').addEventListener('change', renderChart);
    renderChart();
  }}

  function renderChart() {{
    const xCol = $(TID + '_viz_x_col').value;
    const yCol = $(TID + '_viz_y_col').value;
    const aggFunc = $(TID + '_viz_agg').value;
    const chartType = $(TID + '_viz_type').value;
    const area = $(TID + '_chart_area');

    if (!xCol) {{ area.innerHTML = '<p>Select an X axis column</p>'; return; }}

    // Grouping & Aggregation
    const groups = {{}};
    filteredData.forEach(r => {{
      const xVal = r[xCol] !== undefined && r[xCol] !== null && r[xCol] !== '' ? String(r[xCol]) : 'null';
      if (!groups[xVal]) groups[xVal] = [];
      if (yCol !== '__row_count__') {{
        const yVal = parseFloat(r[yCol]);
        if (!isNaN(yVal)) groups[xVal].push(yVal);
      }} else {{
        groups[xVal].push(1);
      }}
    }});

    const xEntries = Object.keys(groups);
    if (!xEntries.length) {{ area.innerHTML = '<p>No data to display</p>'; return; }}

    const aggResults = [];
    xEntries.forEach(xVal => {{
      const yVals = groups[xVal];
      let res = 0;
      if (yCol === '__row_count__' || aggFunc === 'COUNT') {{
        res = yVals.length;
      }} else if (yVals.length) {{
        if (aggFunc === 'SUM') res = yVals.reduce((a, b) => a + b, 0);
        if (aggFunc === 'AVG') res = yVals.reduce((a, b) => a + b, 0) / yVals.length;
        if (aggFunc === 'MIN') res = Math.min(...yVals);
        if (aggFunc === 'MAX') res = Math.max(...yVals);
      }}
      aggResults.push({{ x: xVal, y: res }});
    }});

    const yLabel = yCol === '__row_count__' ? 'Count' : aggFunc + '(' + yCol + ')';

    if (chartType === 'line') {{
      // Line Chart
      const chartW = 540, chartH = 260, padL = 60, padB = 40, padT = 20;
      const maxY = Math.max(...aggResults.map(d => d.y)) || 1;
      const stepX = (chartW - padL) / Math.max(1, aggResults.length - 1);
      let pts = [];
      let svg = '<svg viewBox="0 0 ' + (chartW + 40) + ' ' + (chartH + padB + padT) + '" style="width:100%;height:auto;">';
      // Axis lines
      svg += '<line x1="' + padL + '" y1="' + chartH + '" x2="' + chartW + '" y2="' + chartH + '" stroke="#ccc"/>';
      svg += '<line x1="' + padL + '" y1="10" x2="' + padL + '" y2="' + chartH + '" stroke="#ccc"/>';

      aggResults.forEach((d, i) => {{
        const cx = padL + i * stepX;
        const cy = chartH - (d.y / maxY) * (chartH - padT);
        pts.push(cx + ',' + cy);
        svg += '<circle cx="' + cx + '" cy="' + cy + '" r="4" fill="#1a73e8"><title>' + esc(d.x) + ': ' + d.y.toFixed(2) + '</title></circle>';
      }});
      svg += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="#1a73e8" stroke-width="2"/>';
      // Axis labels
      svg += '<text x="' + (chartW / 2) + '" y="' + (chartH + 34) + '" text-anchor="middle" font-size="11" font-weight="600" fill="#555">X: ' + esc(xCol) + '</text>';
      svg += '<text x="15" y="' + (chartH / 2) + '" text-anchor="middle" font-size="11" font-weight="600" fill="#555" transform="rotate(-90 15,' + (chartH / 2) + ')">' + esc(yLabel) + '</text>';
      svg += '</svg>';
      area.innerHTML = svg;
    }} else if (chartType === 'scatter') {{
      // Scatter Plot
      const chartW = 540, chartH = 260, padL = 60, padB = 40, padT = 20;
      const maxY = Math.max(...aggResults.map(d => d.y)) || 1;
      let svg = '<svg viewBox="0 0 ' + (chartW + 40) + ' ' + (chartH + padB + padT) + '" style="width:100%;height:auto;">';
      svg += '<line x1="' + padL + '" y1="' + chartH + '" x2="' + chartW + '" y2="' + chartH + '" stroke="#ccc"/>';
      svg += '<line x1="' + padL + '" y1="10" x2="' + padL + '" y2="' + chartH + '" stroke="#ccc"/>';

      aggResults.forEach((d, i) => {{
        const cx = padL + (i / Math.max(1, aggResults.length - 1)) * (chartW - padL);
        const cy = chartH - (d.y / maxY) * (chartH - padT);
        svg += '<circle cx="' + cx + '" cy="' + cy + '" r="5" fill="#4285f4" opacity="0.75"><title>' + esc(d.x) + ': ' + d.y.toFixed(2) + '</title></circle>';
      }});
      svg += '<text x="' + (chartW / 2) + '" y="' + (chartH + 34) + '" text-anchor="middle" font-size="11" font-weight="600" fill="#555">X: ' + esc(xCol) + '</text>';
      svg += '<text x="15" y="' + (chartH / 2) + '" text-anchor="middle" font-size="11" font-weight="600" fill="#555" transform="rotate(-90 15,' + (chartH / 2) + ')">' + esc(yLabel) + '</text>';
      svg += '</svg>';
      area.innerHTML = svg;
    }} else {{
      // Bar Chart (default)
      const topEntries = aggResults.slice(0, 25);
      const maxY = Math.max(...topEntries.map(e => e.y)) || 1;
      const barH = 22, gap = 5, labelW = 140, drawW = 380;
      const svgH = topEntries.length * (barH + gap) + 30;

      let svg = '<svg viewBox="0 0 ' + (labelW + drawW + 70) + ' ' + svgH + '" style="max-height:' + Math.min(svgH, 500) + 'px">';
      topEntries.forEach((d, i) => {{
        const y = i * (barH + gap) + 10;
        const w = (d.y / maxY) * drawW;
        const shortLabel = d.x.length > 20 ? d.x.substring(0, 18) + '…' : d.x;
        svg += '<text x="' + (labelW - 6) + '" y="' + (y + barH / 2 + 4) + '" text-anchor="end" font-size="11" fill="#444">' + esc(shortLabel) + '</text>';
        svg += '<rect x="' + labelW + '" y="' + y + '" width="' + w + '" height="' + barH + '" rx="3" fill="#1a73e8" opacity="0.85"><title>' + esc(d.x) + '\\n' + yLabel + ': ' + d.y.toFixed(2) + '</title></rect>';
        svg += '<text x="' + (labelW + w + 6) + '" y="' + (y + barH / 2 + 4) + '" font-size="11" fill="#555">' + (Number.isInteger(d.y) ? d.y : d.y.toFixed(2)) + '</text>';
      }});
      svg += '</svg>';
      area.innerHTML = svg;
    }}
  }}

  /* ─── Column Resize ─── */
  function initResize(handle, th) {{
    let startX, startW;
    function onDown(e) {{
      e.preventDefault(); e.stopPropagation();
      startX = e.clientX; startW = th.offsetWidth;
      handle.classList.add('active');
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    }}
    function onMove(e) {{
      const w = Math.max(50, startW + e.clientX - startX);
      th.style.width = w + 'px'; th.style.minWidth = w + 'px';
      const ci = th.dataset.ci;
      $(TID + '_tbody').querySelectorAll('tr').forEach(tr => {{
        const td = tr.children[parseInt(ci) + 1];
        if (td) {{ td.style.width = w + 'px'; td.style.minWidth = w + 'px'; td.style.maxWidth = w + 'px'; }}
      }});
    }}
    function onUp() {{
      handle.classList.remove('active');
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }}
    handle.addEventListener('mousedown', onDown);
  }}

  /* ─── Init ─── */
  buildHeader();
  buildBody();
}})();
</script>
</div>
"""
    return html
