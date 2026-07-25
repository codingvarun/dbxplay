"""
Generate a standalone HTML file to visually verify the Databricks-style table UI
without needing a running Jupyter notebook.

Usage:
    python generate_demo_html.py
    open demo_output.html
"""

import sys
import os

# Add parent dir to path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dbxplay.core import _convert_to_records, _safe_str
from dbxplay.templates import render_table_html

import json
import uuid


def main():
    # Sample data mimicking the wine quality dataset from the Databricks screenshots
    data = [
        {"fixed_acidity": 7.4, "volatile_acidity": 0.70, "citric_acid": 0.00, "residual_sugar": 1.9, "chlorides": 0.076, "free_sulfur_dioxide": 11, "total_sulfur_dioxide": 34, "density": 0.9978, "pH": 3.51, "sulphates": 0.56, "alcohol": 9.4, "quality": 5, "season": "winter"},
        {"fixed_acidity": 7.8, "volatile_acidity": 0.88, "citric_acid": 0.00, "residual_sugar": 2.6, "chlorides": 0.098, "free_sulfur_dioxide": 25, "total_sulfur_dioxide": 67, "density": 0.9968, "pH": 3.20, "sulphates": 0.68, "alcohol": 9.8, "quality": 5, "season": "spring"},
        {"fixed_acidity": 7.8, "volatile_acidity": 0.76, "citric_acid": 0.04, "residual_sugar": 2.3, "chlorides": 0.092, "free_sulfur_dioxide": 15, "total_sulfur_dioxide": 54, "density": 0.9970, "pH": 3.26, "sulphates": 0.65, "alcohol": 9.8, "quality": 5, "season": "summer"},
        {"fixed_acidity": 11.2, "volatile_acidity": 0.28, "citric_acid": 0.56, "residual_sugar": 1.9, "chlorides": 0.075, "free_sulfur_dioxide": 17, "total_sulfur_dioxide": 60, "density": 0.9980, "pH": 3.16, "sulphates": 0.58, "alcohol": 9.8, "quality": 6, "season": "fall"},
        {"fixed_acidity": 7.4, "volatile_acidity": 0.70, "citric_acid": 0.00, "residual_sugar": 1.9, "chlorides": 0.076, "free_sulfur_dioxide": 11, "total_sulfur_dioxide": 34, "density": 0.9978, "pH": 3.51, "sulphates": 0.56, "alcohol": 9.4, "quality": 5, "season": "winter"},
        {"fixed_acidity": 7.4, "volatile_acidity": 0.66, "citric_acid": 0.00, "residual_sugar": 1.8, "chlorides": 0.075, "free_sulfur_dioxide": 13, "total_sulfur_dioxide": 40, "density": 0.9978, "pH": 3.51, "sulphates": 0.56, "alcohol": 9.4, "quality": 5, "season": "spring"},
        {"fixed_acidity": 7.9, "volatile_acidity": 0.60, "citric_acid": 0.06, "residual_sugar": 1.6, "chlorides": 0.069, "free_sulfur_dioxide": 15, "total_sulfur_dioxide": 59, "density": 0.9964, "pH": 3.30, "sulphates": 0.46, "alcohol": 9.4, "quality": 5, "season": "summer"},
        {"fixed_acidity": 7.3, "volatile_acidity": 0.65, "citric_acid": 0.00, "residual_sugar": 1.2, "chlorides": 0.065, "free_sulfur_dioxide": 15, "total_sulfur_dioxide": 21, "density": 0.9946, "pH": 3.39, "sulphates": 0.47, "alcohol": 10.0, "quality": 7, "season": "fall"},
        {"fixed_acidity": 7.8, "volatile_acidity": 0.58, "citric_acid": 0.02, "residual_sugar": 2.0, "chlorides": 0.073, "free_sulfur_dioxide": 9, "total_sulfur_dioxide": 18, "density": 0.9968, "pH": 3.36, "sulphates": 0.57, "alcohol": 9.5, "quality": 7, "season": "winter"},
        {"fixed_acidity": 7.5, "volatile_acidity": 0.50, "citric_acid": 0.36, "residual_sugar": 6.1, "chlorides": 0.071, "free_sulfur_dioxide": 17, "total_sulfur_dioxide": 102, "density": 0.9978, "pH": 3.35, "sulphates": 0.80, "alcohol": 10.5, "quality": 5, "season": "spring"},
        {"fixed_acidity": 6.7, "volatile_acidity": 0.58, "citric_acid": 0.08, "residual_sugar": 1.8, "chlorides": 0.097, "free_sulfur_dioxide": 15, "total_sulfur_dioxide": 65, "density": 0.9959, "pH": 3.28, "sulphates": 0.54, "alcohol": 9.2, "quality": 5, "season": "summer"},
        {"fixed_acidity": 6.3, "volatile_acidity": 0.30, "citric_acid": 0.34, "residual_sugar": 1.6, "chlorides": 0.049, "free_sulfur_dioxide": 14, "total_sulfur_dioxide": 132, "density": 0.9940, "pH": 3.30, "sulphates": 0.49, "alcohol": 9.5, "quality": 6, "season": "fall"},
        {"fixed_acidity": 8.1, "volatile_acidity": 0.28, "citric_acid": 0.40, "residual_sugar": 6.9, "chlorides": 0.050, "free_sulfur_dioxide": 30, "total_sulfur_dioxide": 97, "density": 0.9951, "pH": 3.26, "sulphates": 0.44, "alcohol": 10.1, "quality": 6, "season": "winter"},
        {"fixed_acidity": 8.1, "volatile_acidity": 0.28, "citric_acid": 0.40, "residual_sugar": 6.9, "chlorides": 0.050, "free_sulfur_dioxide": 30, "total_sulfur_dioxide": 97, "density": 0.9951, "pH": 3.26, "sulphates": 0.44, "alcohol": 10.1, "quality": 6, "season": "spring"},
        {"fixed_acidity": 7.2, "volatile_acidity": 0.23, "citric_acid": 0.32, "residual_sugar": 8.5, "chlorides": 0.058, "free_sulfur_dioxide": 47, "total_sulfur_dioxide": 186, "density": 0.9956, "pH": 3.19, "sulphates": 0.40, "alcohol": 9.9, "quality": 6, "season": "summer"},
        {"fixed_acidity": 7.2, "volatile_acidity": 0.23, "citric_acid": 0.32, "residual_sugar": 8.5, "chlorides": 0.058, "free_sulfur_dioxide": 47, "total_sulfur_dioxide": 186, "density": 0.9956, "pH": 3.19, "sulphates": 0.40, "alcohol": 9.9, "quality": 6, "season": "fall"},
        {"fixed_acidity": 6.2, "volatile_acidity": 0.32, "citric_acid": 0.16, "residual_sugar": 7.0, "chlorides": 0.045, "free_sulfur_dioxide": 30, "total_sulfur_dioxide": 136, "density": 0.9949, "pH": 3.18, "sulphates": 0.47, "alcohol": 9.6, "quality": 6, "season": "winter"},
        {"fixed_acidity": None, "volatile_acidity": 0.45, "citric_acid": None, "residual_sugar": 3.0, "chlorides": 0.060, "free_sulfur_dioxide": None, "total_sulfur_dioxide": 88, "density": 0.9970, "pH": 3.40, "sulphates": 0.52, "alcohol": 9.0, "quality": None, "season": None},
        {"fixed_acidity": 5.9, "volatile_acidity": 0.29, "citric_acid": 0.25, "residual_sugar": 13.4, "chlorides": 0.067, "free_sulfur_dioxide": 72, "total_sulfur_dioxide": 160, "density": 0.9991, "pH": 3.28, "sulphates": 0.60, "alcohol": 8.8, "quality": 5, "season": "spring"},
        {"fixed_acidity": 6.3, "volatile_acidity": 0.39, "citric_acid": 0.08, "residual_sugar": 1.7, "chlorides": 0.066, "free_sulfur_dioxide": 3, "total_sulfur_dioxide": 20, "density": 0.9954, "pH": 3.34, "sulphates": 0.58, "alcohol": 10.5, "quality": 6, "season": "summer"},
    ]

    records, columns, total_rows, truncated = _convert_to_records(data, limit=1000)
    safe_records = [{k: _safe_str(v) for k, v in row.items()} for row in records]

    table_id = "db_demo_" + uuid.uuid4().hex[:8]
    html = render_table_html(
        table_id=table_id,
        records=safe_records,
        columns=columns,
        total_rows=total_rows,
        truncated=truncated,
        limit=1000,
        title="Table",
    )

    # Wrap in a full HTML page
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Databricks Display Demo</title>
<style>
  body {{
    margin: 40px auto;
    max-width: 1200px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f7fa;
    color: #333;
  }}
  h1 {{
    font-size: 20px;
    color: #1b1f23;
    margin-bottom: 16px;
  }}
  .demo-note {{
    font-size: 13px;
    color: #666;
    margin-bottom: 24px;
    line-height: 1.6;
  }}
</style>
</head>
<body>
<h1>📊 databricks_display — Demo</h1>
<p class="demo-note">
  This is a self-contained demo of the Databricks-style <code>display()</code> table.<br>
  Try: <strong>sorting columns</strong>, <strong>right-clicking cells</strong> (context menu),
  <strong>searching</strong>, <strong>filtering</strong>, <strong>downloading CSV/Excel</strong>,
  and <strong>resizing columns</strong>.
</p>
{html}
</body>
</html>"""

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_output.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ Demo HTML written to: {output_path}")
    print("   Open it in your browser to verify the UI.")


if __name__ == "__main__":
    main()
