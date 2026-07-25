"""
core.py — Main display() function and DataFrame type detection/conversion.
"""

import json
import uuid
import html as html_module
import math
from typing import Any, Dict, List, Optional, Union

from dbxplay.templates import render_table_html


def _is_pyspark_dataframe(obj: Any) -> bool:
    """Check if the object is a PySpark DataFrame without importing PySpark."""
    cls_name = type(obj).__name__
    module = type(obj).__module__ or ""
    return cls_name == "DataFrame" and "pyspark" in module


def _is_pandas_dataframe(obj: Any) -> bool:
    """Check if the object is a Pandas DataFrame."""
    cls_name = type(obj).__name__
    module = type(obj).__module__ or ""
    return cls_name == "DataFrame" and "pandas" in module


def _is_polars_dataframe(obj: Any) -> bool:
    """Check if the object is a Polars DataFrame."""
    cls_name = type(obj).__name__
    module = type(obj).__module__ or ""
    return cls_name == "DataFrame" and "polars" in module


def _infer_dtype_category(values: list, col_name: str = "") -> str:
    """Infer a human-readable dtype category from a sample of Python values.

    Returns one of: 'string', 'integer', 'float', 'boolean', 'datetime', 'complex'
    """
    import datetime as dt

    non_none = [v for v in values if v is not None]
    if not non_none:
        return "string"

    sample = non_none[:50]

    # Check boolean first (bool is subclass of int in Python)
    if all(isinstance(v, bool) for v in sample):
        return "boolean"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in sample):
        return "integer"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in sample):
        return "float"
    if all(isinstance(v, (dt.datetime, dt.date)) for v in sample):
        return "datetime"
    if all(isinstance(v, (dict, list)) for v in sample):
        return "complex"

    # Try to detect string-encoded timestamps
    str_vals = [v for v in sample if isinstance(v, str)]
    if str_vals and len(str_vals) == len(sample):
        ts_count = sum(1 for s in str_vals[:10] if len(s) >= 10 and s[4:5] == "-")
        if ts_count >= len(str_vals[:10]) * 0.8:
            return "datetime"

    return "string"


def _pandas_dtype_to_category(dtype) -> str:
    """Convert a pandas dtype to our category string."""
    dtype_str = str(dtype).lower()
    if "bool" in dtype_str:
        return "boolean"
    if "int" in dtype_str:
        return "integer"
    if "float" in dtype_str or "double" in dtype_str:
        return "float"
    if "datetime" in dtype_str or "timestamp" in dtype_str:
        return "datetime"
    if "object" in dtype_str or "string" in dtype_str or "str" in dtype_str:
        return "string"
    if "category" in dtype_str:
        return "string"
    return "string"


def _spark_dtype_to_category(dtype_str: str) -> str:
    """Convert a PySpark dtype string to our category string."""
    dtype_str = dtype_str.lower()
    if "bool" in dtype_str:
        return "boolean"
    if "int" in dtype_str or "long" in dtype_str or "short" in dtype_str or "byte" in dtype_str:
        return "integer"
    if "float" in dtype_str or "double" in dtype_str or "decimal" in dtype_str:
        return "float"
    if "timestamp" in dtype_str or "date" in dtype_str:
        return "datetime"
    if "struct" in dtype_str or "array" in dtype_str or "map" in dtype_str:
        return "complex"
    return "string"


def _polars_dtype_to_category(dtype) -> str:
    """Convert a Polars dtype to our category string."""
    dtype_str = str(dtype).lower()
    if "bool" in dtype_str:
        return "boolean"
    if "int" in dtype_str or "uint" in dtype_str:
        return "integer"
    if "float" in dtype_str or "decimal" in dtype_str:
        return "float"
    if "date" in dtype_str or "time" in dtype_str or "duration" in dtype_str:
        return "datetime"
    if "struct" in dtype_str or "list" in dtype_str:
        return "complex"
    return "string"


def _safe_str(val: Any) -> str:
    """Convert a value to a display-safe string."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, float):
        if val != val:  # NaN check
            return "NaN"
        if val == float("inf"):
            return "Infinity"
        if val == float("-inf"):
            return "-Infinity"
    return str(val)


def _convert_to_records(
    data: Any,
    limit: int = 1000,
) -> tuple:
    """Convert various DataFrame types to a list of dicts and column metadata.

    Returns:
        (records: List[Dict], columns: List[Dict], total_rows: int, truncated: bool)
        Each column dict has keys: 'name', 'dtype_category'
    """

    if _is_pyspark_dataframe(data):
        total_rows = None
        limited = data.limit(limit)
        pdf = limited.toPandas()
        records = pdf.to_dict("records")
        columns = []
        for field in data.schema.fields:
            columns.append({
                "name": field.name,
                "dtype_category": _spark_dtype_to_category(str(field.dataType)),
            })
        truncated = len(records) >= limit
        return records, columns, total_rows, truncated

    if _is_pandas_dataframe(data):
        total_rows = len(data)
        truncated = total_rows > limit
        df_sample = data.head(limit) if truncated else data
        records = json.loads(df_sample.to_json(orient="records", date_format="iso", default_handler=str))
        columns = []
        for col_name in data.columns:
            columns.append({
                "name": str(col_name),
                "dtype_category": _pandas_dtype_to_category(data[col_name].dtype),
            })
        return records, columns, total_rows, truncated

    if _is_polars_dataframe(data):
        total_rows = data.height
        truncated = total_rows > limit
        df_sample = data.head(limit) if truncated else data
        records = df_sample.to_dicts()
        columns = []
        for col_name in data.columns:
            columns.append({
                "name": col_name,
                "dtype_category": _polars_dtype_to_category(data[col_name].dtype),
            })
        return records, columns, total_rows, truncated

    if isinstance(data, list):
        if not data:
            return [], [], 0, False
        total_rows = len(data)
        truncated = total_rows > limit
        sample = data[:limit]

        if isinstance(sample[0], dict):
            records = sample
            all_keys = []
            seen = set()
            for row in sample:
                for k in row:
                    if k not in seen:
                        all_keys.append(k)
                        seen.add(k)
            columns = []
            for k in all_keys:
                vals = [row.get(k) for row in sample]
                columns.append({
                    "name": str(k),
                    "dtype_category": _infer_dtype_category(vals, str(k)),
                })
            return records, columns, total_rows, truncated
        else:
            records = [{"value": v} for v in sample]
            columns = [{"name": "value", "dtype_category": _infer_dtype_category(sample)}]
            return records, columns, total_rows, truncated

    if isinstance(data, dict):
        col_names = list(data.keys())
        max_len = max((len(v) if isinstance(v, list) else 1) for v in data.values()) if data else 0
        total_rows = max_len
        truncated = total_rows > limit
        actual_len = min(max_len, limit)
        records = []
        for i in range(actual_len):
            row = {}
            for c in col_names:
                vals = data[c]
                if isinstance(vals, list):
                    row[c] = vals[i] if i < len(vals) else None
                else:
                    row[c] = vals
            records.append(row)
        columns = []
        for c in col_names:
            vals = data[c] if isinstance(data[c], list) else [data[c]]
            columns.append({
                "name": str(c),
                "dtype_category": _infer_dtype_category(vals[:50], str(c)),
            })
        return records, columns, total_rows, truncated

    raise TypeError(
        f"display() does not support type '{type(data).__name__}'. "
        "Supported types: PySpark DataFrame, Pandas DataFrame, Polars DataFrame, list, dict."
    )


def display(
    data: Any,
    limit: int = 1000,
    title: str = "Table",
    height: Optional[int] = None,
) -> None:
    """Display a DataFrame or data structure in an interactive Databricks-style table.

    Args:
        data: A PySpark, Pandas, or Polars DataFrame, or a list of dicts / dict of lists.
        limit: Maximum number of rows to display (default 1000). PySpark DataFrames
               are automatically limited to avoid OOM.
        title: The tab title shown in the top bar (default "Table").
        height: Optional fixed height in pixels for the table container. If None,
                the table auto-sizes up to ~500px then scrolls.
    """
    from IPython.display import display as ipy_display, HTML

    records, columns, total_rows, truncated = _convert_to_records(data, limit=limit)

    # Sanitize all record values for safe JSON embedding
    safe_records = []
    for row in records:
        safe_row = {}
        for k, v in row.items():
            safe_row[k] = _safe_str(v)
        safe_records.append(safe_row)

    table_id = "db_table_" + uuid.uuid4().hex[:12]

    html_str = render_table_html(
        table_id=table_id,
        records=safe_records,
        columns=columns,
        total_rows=total_rows,
        truncated=truncated,
        limit=limit,
        title=title,
        height=height,
    )

    ipy_display(HTML(html_str))
