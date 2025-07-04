import pandas as pd
from typing import Optional, Tuple


def filter_dataframe(
    df: Optional[pd.DataFrame],
    category: Optional[str] = None,
    search_term: Optional[str] = None,
    value_filter: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Filter the DataFrame by category, search term, and value (positive/negative/all).
    Args:
        df: The DataFrame to filter.
        category: Category filter ('All Categories', 'Uncategorized', or specific category).
        search_term: Substring to search for in the 'Description' column.
        value_filter: 'All', 'Positive', or 'Negative'.
    Returns:
        Filtered DataFrame or None if input is None.
    """
    if df is None:
        return df
    filtered = df
    if category == "Uncategorized":
        filtered = filtered[filtered["Category"] == ""]
    elif category and category != "All Categories":
        filtered = filtered[filtered["Category"] == category]
    if search_term:
        filtered = filtered[filtered["Description"].str.contains(search_term, case=False, na=False)]
    if value_filter == "Positive":
        filtered = filtered[pd.to_numeric(filtered["Amount"], errors="coerce") > 0]
    elif value_filter == "Negative":
        filtered = filtered[pd.to_numeric(filtered["Amount"], errors="coerce") < 0]
    return filtered.reset_index(drop=True)


def sort_dataframe(df: Optional[pd.DataFrame], column: str, ascending: bool = True) -> Optional[pd.DataFrame]:
    """
    Sort the DataFrame by the given column and order.
    Args:
        df: The DataFrame to sort.
        column: Column name to sort by.
        ascending: Sort order.
    Returns:
        Sorted DataFrame or None if input is None or column not found.
    """
    if df is None or column not in df.columns:
        return df
    return df.sort_values(by=column, ascending=ascending)


def prepare_export(
    df: Optional[pd.DataFrame],
    category: Optional[str] = None,
    search_term: Optional[str] = None,
    value_filter: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Prepare the DataFrame for export, applying the same filters as the UI.
    Args:
        df: The DataFrame to filter for export.
        category: Category filter.
        search_term: Search filter.
        value_filter: Value filter.
    Returns:
        Filtered DataFrame or None if input is None.
    """
    return filter_dataframe(df, category, search_term, value_filter)


def calculate_summaries(df: Optional[pd.DataFrame]) -> Tuple[float, float, float]:
    """
    Calculate total income, expenses, and net balance from the DataFrame.
    Args:
        df: The DataFrame to summarize.
    Returns:
        Tuple of (income, expenses, net balance).
    """
    if df is None or "Amount" not in df.columns:
        return 0.0, 0.0, 0.0
    amounts = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    total_income = amounts[amounts > 0].sum()
    total_expenses = amounts[amounts < 0].sum()
    net_balance = amounts.sum()
    return total_income, total_expenses, net_balance
