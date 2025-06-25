import json
from pathlib import Path

# This creates a path relative to the current file to find the config directory.
# It ensures the app works no matter where you run it from.
CONFIG_DIR = Path(__file__).parent.parent / "config"
KEYWORDS_FILE = CONFIG_DIR / "keywords.json"
CATEGORIES_FILE = CONFIG_DIR / "categories_list.txt"


def load_keywords():
    """Loads the keywords dictionary from the config directory."""
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file not found or is invalid, start with an empty dictionary.
        return {}


def save_keywords(keywords):
    """Saves the updated keywords dictionary to the config directory."""
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as file:
        # indent=4 makes the JSON file human-readable.
        json.dump(keywords, file, indent=4, ensure_ascii=False)


def load_categories():
    """Loads the category list from the config directory."""
    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as file:
            # Read each line, strip whitespace/newlines, and return as a list.
            # It also filters out empty lines.
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        # If file not found, return an empty list.
        return []


def calculate_category_summary(dataframe):
    """
    Calculates the sum of 'Amount' for each 'Category'.

    Args:
        dataframe (pd.DataFrame): The dataframe to analyze.

    Returns:
        pd.DataFrame: A new dataframe with 'Category' and summed 'Amount'.
    """
    if (
        dataframe is None
        or "Category" not in dataframe.columns
        or dataframe["Category"].eq("").all()
    ):
        return pd.DataFrame(columns=["Category", "Total Amount"])

    # Group by 'Category', calculate the sum of 'Amount' for each, and reset index to make it a dataframe
    summary = dataframe.groupby("Category")["Amount"].sum().reset_index()

    # Sort by amount
    summary = summary.sort_values(by="Amount", ascending=True)

    # Rename columns for clarity
    summary.columns = ["Category", "Total Amount"]

    return summary


def get_category_summary(dataframe):
    """Calculates the sum of 'Amount' for each 'Category' and returns a summary DataFrame."""
    if (
        dataframe is None
        or "Category" not in dataframe.columns
        or dataframe["Category"].eq("").all()
    ):
        return pd.DataFrame(columns=["Category", "Total"])

    # Filter out uncategorized items for the summary table
    categorized_df = dataframe[dataframe["Category"] != ""].copy()

    if categorized_df.empty:
        return pd.DataFrame(columns=["Category", "Total"])

    # Group by 'Category', sum the 'Amount', and make it a DataFrame again
    summary = categorized_df.groupby("Category")["Amount"].sum().reset_index()

    # Sort by amount to see the biggest items first
    summary = summary.sort_values(by="Amount", ascending=True)

    # Format the amount to 2 decimal places
    summary["Amount"] = summary["Amount"].round(2)

    return summary
