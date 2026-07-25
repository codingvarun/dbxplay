"""
dbxplay — A Databricks-like interactive display() function
for Jupyter Notebooks, AWS Glue, Google Colab, and VS Code.

Usage:
    from dbxplay import display
    display(df)
"""

from dbxplay.core import display

__version__ = "0.1.0"
__all__ = ["display"]
