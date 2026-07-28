# dbxplay

A Databricks-like interactive `display()` function for **Jupyter Notebooks**, **AWS Glue**, **Google Colab**, and **VS Code**.

Brings the beautiful, interactive table UI from Databricks into any Python notebook environment — with sorting, filtering, searching, customizable X/Y charting, data profiling, context menus, column resizing, CSV/Excel export, and more.

## Installation

```bash
pip install dbxplay
```

Or install locally in editable mode:

```bash
pip install -e .
```

## Quick Start

```python
from dbxplay import display
import pandas as pd

df = pd.read_csv("your_data.csv")
display(df)
```

## Usage & Examples

```python
from dbxplay import display

# Basic usage
display(df)

# Stratified sampling across categories (PySpark, Pandas, Polars)
display(df, stratify_by="user_tier")

# Sample more rows (e.g. 5,000)
display(df, limit=5000)

# Display all rows without truncation
display(df, limit=None)

# With options
display(df, limit=500, title="My Data", height=400, stratify_by="country_code")
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `data` | DataFrame/list/dict | *(required)* | The data to display |
| `limit` | int / None | 1000 | Max rows to render (pass a higher int like `5000`, or `None` for unlimited) |
| `title` | str | "Table" | Tab title in the top bar |
| `height` | int | None | Fixed height in px (auto-sizes to ~520px) |
| `stratify_by` | str | None | Optional column name to perform stratified sampling across categories |

### Supported Data Types

- **Pandas DataFrames**
- **Polars DataFrames**
- **PySpark DataFrames** (auto-limited to prevent OOM)
- **Lists of dicts** — `[{"a": 1, "b": 2}, ...]`
- **Dicts of lists** — `{"a": [1, 2], "b": [3, 4]}`

## Features

| Feature | Description |
| :--- | :--- |
| 🔍 **Global Search** | Instant full-text search across all columns & values |
| ↕️ **Column Sorting** | Click column headers to sort ascending/descending |
| 🔽 **Column Filtering** | Per-column value checkbox dropdowns |
| 📊 **Custom Visualization** | Customizable X/Y axes & aggregations (COUNT, SUM, AVG, MIN, MAX) |
| 📋 **Data Profile** | Overview stats & pop-out closeable distribution charts |
| 🎯 **Filter by Value** | Right-click any cell → "Filter by this value" |
| 🚫 **Exclude Value** | Right-click → "Exclude this value" |
| 📋 **Copy as CSV/TSV/Markdown** | Right-click → Copy as → choose format |
| 📥 **Download CSV / Excel** | Top `Table ∨` dropdown → Download |
| 📐 **Column Resizing** | Drag column borders to resize |
| 📄 **Side Panel** | Row detail view panel |
| 🔢 **Data Type Icons** | Automatic type badges (ABC, #, 1.2, T/F, 📅, {}) |
| ✅ **Zero Dependencies** | Self-contained HTML/CSS/JS — works everywhere |

## Context Menu (Right-Click)

Right-click any cell to access:
- **Copy** (⌘C)
- **Copy as** → CSV, TSV, Markdown
- **Filter by this value**
- **Exclude this value**
- **Toggle side panel**

## License

MIT

