from typing import Optional, List
import pandas as pd
from core.data_utils import filter_dataframe, sort_dataframe, calculate_summaries
from core.data_processor import get_category_summary, load_keywords, save_keywords, load_categories


class Controller:
    """
    Coordinates data operations between the GUI and core logic, acting as the service/controller layer.
    Handles data loading, filtering, sorting, exporting, and keyword/category management.
    """
    def __init__(self):
        """Initialize the Controller with empty dataframes and load keywords/categories from config."""
        self.df: Optional[pd.DataFrame] = None
        self.selected_df: Optional[pd.DataFrame] = None
        self.keywords_map = load_keywords()
        self.categories = load_categories()
        self.currently_selected_row_index = None

    def load_data(self, filepath: str) -> None:
        """Load Excel data from the given filepath, skipping the first 7 rows."""
        self.df = pd.read_excel(filepath, skiprows=7)
        self.selected_df = self.df.copy()

    def filter_data(self, category: Optional[str], search_term: Optional[str], value_filter: Optional[str]) -> pd.DataFrame:
        """Filter the selected DataFrame by category, search term, and value filter."""
        return filter_dataframe(self.selected_df, category, search_term, value_filter)

    def sort_data(self, column: str, ascending: bool = True) -> None:
        """Sort the selected DataFrame by the given column and order."""
        if self.selected_df is not None:
            self.selected_df = sort_dataframe(self.selected_df, column, ascending)

    def get_summary(self, df: Optional[pd.DataFrame]) -> pd.DataFrame:
        """Return a summary DataFrame with totals by category for the given DataFrame."""
        return get_category_summary(df)

    def export_data(self, df: pd.DataFrame, filepath: str) -> None:
        """Export the given DataFrame to Excel, starting at row 8 (index 7)."""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=7)

    def calculate_summaries(self, df: Optional[pd.DataFrame]):
        """Calculate total income, expenses, and net balance for the given DataFrame."""
        return calculate_summaries(df)

    def update_keywords(self, description: str, category: str) -> None:
        """Add a description to the exact match list for a category and save the updated keywords map."""
        if category not in self.keywords_map:
            self.keywords_map[category] = {"exact": [], "contains": []}
        if description not in self.keywords_map[category]["exact"]:
            self.keywords_map[category]["exact"].append(description)
        save_keywords(self.keywords_map)

    def save_keywords_map(self, keywords_map: dict) -> None:
        """Replace and save the entire keywords map."""
        self.keywords_map = keywords_map
        save_keywords(self.keywords_map)

    def get_categories(self) -> List[str]:
        """Return the list of categories loaded from config."""
        return self.categories

    def apply_filters(self, event=None) -> None:
        """Delegate to main app's apply_filters method. Overridden by the main app."""
        pass

    def clear_filters(self) -> None:
        """Delegate to main app's clear_filters method. Overridden by the main app."""
        pass
