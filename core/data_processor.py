# file: core/data_processor.py
import json
from pathlib import Path
import pandas as pd

# This creates a path relative to the current file to find the config directory.
CONFIG_DIR = Path(__file__).parent.parent / "config"
KEYWORDS_FILE = CONFIG_DIR / "keywords.json"
CATEGORIES_FILE = CONFIG_DIR / "categories_list.txt"


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

    # Sort by amount to see the biggest items first
    summary = summary.sort_values(by="Total", ascending=True)

    # Format the 'Total' column as a string with 2 decimal places and a comma
    summary["Total"] = summary["Total"].apply(lambda x: f"{x:,.2f}")

    return summary
