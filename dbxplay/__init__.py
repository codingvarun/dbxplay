"""
dbxplay — A Databricks-like interactive display() function
for Jupyter Notebooks, AWS Glue, Google Colab, and VS Code.

Usage:
    from dbxplay import display
    display(df)
"""

from dbxplay.core import display, init, set_theme, get_theme

__version__ = "0.2.3"
__all__ = ["display", "init", "set_theme", "get_theme"]
