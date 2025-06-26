from typing import Optional, List
import pandas as pd
from core.data_utils import filter_dataframe, sort_dataframe, prepare_export, calculate_summaries
from core.data_processor import get_category_summary, load_keywords, save_keywords, load_categories

class Controller:
    """
    Service/controller layer for coordinating data operations between the GUI and core logic.
    """
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.selected_df: Optional[pd.DataFrame] = None
        self.keywords_map = load_keywords()
        self.categories = load_categories()
        self.currently_selected_row_index = None

    def load_data(self, filepath: str) -> None:
        self.df = pd.read_excel(filepath, skiprows=7)
        self.selected_df = self.df.copy()

    def filter_data(self, category: Optional[str], search_term: Optional[str], value_filter: Optional[str]) -> pd.DataFrame:
        return filter_dataframe(self.selected_df, category, search_term, value_filter)

    def sort_data(self, column: str, ascending: bool = True) -> None:
        if self.selected_df is not None:
            self.selected_df = sort_dataframe(self.selected_df, column, ascending)

    def get_summary(self, df: Optional[pd.DataFrame]) -> pd.DataFrame:
        return get_category_summary(df)

    def export_data(self, df: pd.DataFrame, filepath: str) -> None:
        df.to_excel(filepath, index=False)

    def calculate_summaries(self, df: Optional[pd.DataFrame]):
        return calculate_summaries(df)

    def update_keywords(self, description: str, category: str) -> None:
        self.keywords_map[description] = category
        save_keywords(self.keywords_map)

    def save_keywords_map(self, keywords_map: dict) -> None:
        """Save the entire keywords map."""
        self.keywords_map = keywords_map
        save_keywords(self.keywords_map)

    def get_categories(self) -> List[str]:
        return self.categories 

    # These methods will be called from the filter frame but need to delegate to the main app
    def apply_filters(self, event=None) -> None:
        """Delegate to main app's apply_filters method."""
        # This will be overridden by the main app
        pass

    def clear_filters(self) -> None:
        """Delegate to main app's clear_filters method."""
        # This will be overridden by the main app
        pass 