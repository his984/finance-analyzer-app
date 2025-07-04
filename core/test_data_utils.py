import pandas as pd
from core.data_utils import filter_dataframe, sort_dataframe, prepare_export, calculate_summaries


def sample_df():
    """Return a sample DataFrame for testing with a mix of categories and values."""
    return pd.DataFrame([
        {"Description": "Salary", "Amount": 1000, "Category": "Income"},
        {"Description": "Groceries", "Amount": -200, "Category": "Food"},
        {"Description": "Bonus", "Amount": 500, "Category": "Income"},
        {"Description": "Rent", "Amount": -800, "Category": "Housing"},
        {"Description": "", "Amount": -50, "Category": ""},
    ])


def test_filter_category():
    """Test filtering by a specific category returns only matching rows."""
    df = sample_df()
    filtered = filter_dataframe(df, category="Income")
    assert len(filtered) == 2
    assert all(filtered["Category"] == "Income")


def test_filter_uncategorized():
    """Test filtering for uncategorized rows returns only those with empty category."""
    df = sample_df()
    filtered = filter_dataframe(df, category="Uncategorized")
    assert len(filtered) == 1
    assert filtered.iloc[0]["Category"] == ""


def test_filter_search():
    """Test searching by description substring returns correct row(s)."""
    df = sample_df()
    filtered = filter_dataframe(df, search_term="rent")
    assert len(filtered) == 1
    assert filtered.iloc[0]["Description"] == "Rent"


def test_filter_value_positive():
    """Test filtering for positive values returns only positive amounts."""
    df = sample_df()
    filtered = filter_dataframe(df, value_filter="Positive")
    assert all(filtered["Amount"] > 0)


def test_filter_value_negative():
    """Test filtering for negative values returns only negative amounts."""
    df = sample_df()
    filtered = filter_dataframe(df, value_filter="Negative")
    assert all(filtered["Amount"] < 0)


def test_sort_dataframe():
    """Test sorting by amount in descending order returns the largest value first."""
    df = sample_df()
    sorted_df = sort_dataframe(df, "Amount", ascending=False)
    assert sorted_df.iloc[0]["Amount"] == 1000


def test_prepare_export():
    """Test prepare_export applies category filtering correctly."""
    df = sample_df()
    export_df = prepare_export(df, category="Food")
    assert len(export_df) == 1
    assert export_df.iloc[0]["Category"] == "Food"


def test_calculate_summaries():
    """Test calculation of income, expenses, and net balance from the sample data."""
    df = sample_df()
    income, expenses, net = calculate_summaries(df)
    assert income == 1500
    assert expenses == -1050
    assert net == 450
