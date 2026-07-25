"""
Tests for databricks_display — verifies core conversion logic and HTML output.
"""

import json
import datetime
import pytest


def test_display_pandas_basic():
    """Test display() with a basic Pandas DataFrame."""
    import pandas as pd
    from dbxplay.core import _convert_to_records

    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [30, 25, 35],
        "score": [9.5, 8.3, 7.1],
        "active": [True, False, True],
    })
    records, columns, total_rows, truncated = _convert_to_records(df, limit=100)

    assert len(records) == 3
    assert total_rows == 3
    assert truncated is False
    assert len(columns) == 4

    col_map = {c["name"]: c["dtype_category"] for c in columns}
    assert col_map["name"] == "string"
    assert col_map["age"] == "integer"
    assert col_map["score"] == "float"
    assert col_map["active"] == "boolean"


def test_display_pandas_with_nulls():
    """Test display() handles None / NaN values in Pandas."""
    import pandas as pd
    from dbxplay.core import _convert_to_records

    df = pd.DataFrame({
        "x": [1.0, None, 3.0],
        "y": ["a", None, "c"],
    })
    records, columns, total_rows, truncated = _convert_to_records(df, limit=100)
    assert len(records) == 3
    # None should be converted to None in JSON
    assert records[1]["y"] is None


def test_display_pandas_truncation():
    """Test that display() truncates when limit is exceeded."""
    import pandas as pd
    from dbxplay.core import _convert_to_records

    df = pd.DataFrame({"val": list(range(500))})
    records, columns, total_rows, truncated = _convert_to_records(df, limit=100)

    assert len(records) == 100
    assert total_rows == 500
    assert truncated is True


def test_display_pandas_datetime():
    """Test datetime columns are detected correctly."""
    import pandas as pd
    from dbxplay.core import _convert_to_records

    df = pd.DataFrame({
        "ts": pd.to_datetime(["2024-01-01", "2024-06-15", "2024-12-31"]),
        "val": [10, 20, 30],
    })
    records, columns, total_rows, truncated = _convert_to_records(df, limit=100)
    col_map = {c["name"]: c["dtype_category"] for c in columns}
    assert col_map["ts"] == "datetime"
    assert col_map["val"] == "integer"


def test_display_list_of_dicts():
    """Test display() with a list of dicts."""
    from dbxplay.core import _convert_to_records

    data = [
        {"city": "NYC", "pop": 8000000},
        {"city": "LA", "pop": 4000000},
        {"city": "Chicago", "pop": 2700000},
    ]
    records, columns, total_rows, truncated = _convert_to_records(data, limit=100)

    assert len(records) == 3
    assert total_rows == 3
    assert truncated is False
    col_names = [c["name"] for c in columns]
    assert "city" in col_names
    assert "pop" in col_names


def test_display_dict_of_lists():
    """Test display() with a column-oriented dict of lists."""
    from dbxplay.core import _convert_to_records

    data = {
        "name": ["Alice", "Bob"],
        "score": [95.5, 88.0],
    }
    records, columns, total_rows, truncated = _convert_to_records(data, limit=100)

    assert len(records) == 2
    assert records[0]["name"] == "Alice"
    assert records[1]["score"] == 88.0


def test_display_empty_list():
    """Test display() handles an empty list gracefully."""
    from dbxplay.core import _convert_to_records

    records, columns, total_rows, truncated = _convert_to_records([], limit=100)
    assert records == []
    assert columns == []
    assert total_rows == 0
    assert truncated is False


def test_display_unsupported_type():
    """Test that an unsupported type raises TypeError."""
    from dbxplay.core import _convert_to_records

    with pytest.raises(TypeError, match="does not support type"):
        _convert_to_records("a plain string", limit=100)


def test_html_output_contains_key_elements():
    """Test that the rendered HTML contains expected Databricks UI elements."""
    import pandas as pd
    from dbxplay.core import _convert_to_records, _safe_str
    from dbxplay.templates import render_table_html

    df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    records, columns, total_rows, truncated = _convert_to_records(df, limit=100)
    safe_records = [{k: _safe_str(v) for k, v in row.items()} for row in records]

    html = render_table_html(
        table_id="test_tbl",
        records=safe_records,
        columns=columns,
        total_rows=total_rows,
        truncated=truncated,
        limit=100,
    )

    # Check essential UI elements exist
    assert "db-display-root" in html
    assert "db-topbar" in html
    assert "db-context-menu" in html
    assert "Download all rows" in html
    assert "Copy results to clipboard" in html
    assert "Filter by this value" in html
    assert "Exclude this value" in html
    assert "Toggle side panel" in html
    assert "Copy as" in html
    assert "CSV" in html
    assert "TSV" in html
    assert "Markdown" in html
    assert "db-search-input" in html
    assert "db-side-panel" in html


def test_safe_str():
    """Test the _safe_str helper for edge cases."""
    from dbxplay.core import _safe_str

    assert _safe_str(None) == "null"
    assert _safe_str(True) == "true"
    assert _safe_str(False) == "false"
    assert _safe_str(float("nan")) == "NaN"
    assert _safe_str(float("inf")) == "Infinity"
    assert _safe_str(float("-inf")) == "-Infinity"
    assert _safe_str(42) == "42"
    assert _safe_str("hello") == "hello"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
