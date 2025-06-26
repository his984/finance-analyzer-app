# file: core/data_processor.py
import json
import sys
import os
from pathlib import Path
import pandas as pd

def get_config_path():
    """Get config path that works in both development and frozen executable."""
    if getattr(sys, 'frozen', False):
        # Running in a bundle (executable)
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, 'config')

# This creates a path that works in both development and frozen executable
CONFIG_DIR = get_config_path()
KEYWORDS_FILE = os.path.join(CONFIG_DIR, "keywords.json")
CATEGORIES_FILE = os.path.join(CONFIG_DIR, "categories_list.txt")


def load_keywords():
    """Loads the keywords dictionary from the config directory."""
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_keywords(keywords):
    """Saves the updated keywords dictionary to the config directory."""
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as file:
        json.dump(keywords, file, indent=4, ensure_ascii=False)


def load_categories():
    """Loads the category list from the config directory."""
    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []


# --- UPDATED AND SAFER FUNCTION ---
def get_category_summary(dataframe):
    """
    Calculates the sum of 'Amount' for each 'Category', sorts them,
    and returns a summary DataFrame.
    """
    # First, check if the dataframe or the required columns exist.
    if (
        dataframe is None
        or "Category" not in dataframe.columns
        or "Amount" not in dataframe.columns
    ):
        return pd.DataFrame(columns=["Category", "Total"])

    # Now that we know the 'Category' column exists, check if it's all empty.
    if dataframe["Category"].eq("").all():
        return pd.DataFrame(columns=["Category", "Total"])

    # Filter out uncategorized items for the summary table
    categorized_df = dataframe[dataframe["Category"] != ""].copy()
    if categorized_df.empty:
        return pd.DataFrame(columns=["Category", "Total"])

    # Group by 'Category', sum the 'Amount', and make it a DataFrame again
    amounts = pd.to_numeric(categorized_df["Amount"], errors="coerce").fillna(0)
    summary = (
        categorized_df.groupby("Category").agg(Total=("Amount", "sum")).reset_index()
    )

    # Round the Total column to two decimal places
    summary["Total"] = summary["Total"].round(2)

    # Sort by amount to see the biggest items first
    summary = summary.sort_values(by="Total", ascending=True)

    # Do NOT format 'Total' as string here; keep as float for charting
    return summary
