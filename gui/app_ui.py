import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import json
from CTkMessagebox import CTkMessagebox

from .frames.top_actions_frame import TopActionsFrame
from .frames.filter_frame import FilterFrame
from .frames.table_frame import TableFrame
from .frames.bottom_frame import BottomFrame
from .frames.summary_chart_frame import SummaryChartFrame
from core.controller import Controller
from config.constants import APP_TITLE, COLOR_INCOME, COLOR_EXPENSE, CATEGORY_ALL, CATEGORY_UNCATEGORIZED


class App(ctk.CTk):
    """
    Main application window for the Finance Analyzer.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.attributes('-fullscreen', True)  # True fullscreen mode
        # self.state('zoomed')
        self.controller = Controller()
        # Override controller methods to point to main app methods
        self.controller.apply_filters = self.apply_filters
        self.controller.clear_filters = self.clear_filters
        self.sort_column: str | None = None
        self.sort_ascending: bool = True
        self.current_displayed_df = None  # Track currently displayed DataFrame

        # UI Structure
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create and grid all the main frames
        self.top_frame = TopActionsFrame(self, controller=self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.filter_frame = FilterFrame(self, controller=self.controller)
        self.filter_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=1)

        self.table_frame = TableFrame(self.content_frame)
        self.table_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        self.tree = self.table_frame.tree
        self.tree.bind(
            "<<TreeviewSelect>>", lambda event: self.table_row_selected(event)
        )

        self.summary_panel = TableFrame(self.content_frame)
        self.summary_panel.grid(row=0, column=1, sticky="nsew")
        self.summary_tree = self.summary_panel.tree

        # Add the summary chart frame below the summary panel
        self.summary_chart_frame = SummaryChartFrame(self.content_frame)
        self.summary_chart_frame.grid(row=1, column=1, sticky="nsew", pady=(10, 0))
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.bottom_frame = BottomFrame(self, controller=self.controller)
        self.bottom_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Initial population
        self.populate_treeview(self.tree, None)
        self.populate_treeview(self.summary_tree, None)

    def populate_treeview(self, tree, dataframe: pd.DataFrame | None, is_interactive: bool = False) -> None:
        """Populate a treeview with the given DataFrame."""
        # Clear previous contents and columns
        tree.delete(*tree.get_children())
        tree["columns"] = ()

        if dataframe is None or dataframe.empty:
            tree["columns"] = "1"
            tree.heading("1", text="No Data")
            tree.column("1")
            return

        # Define new columns
        tree["columns"] = dataframe.columns.tolist()

        # Configure each column
        for col in dataframe.columns:
            # Prepare options for the heading
            heading_options = {"text": col}
            # Add the sort command ONLY if the table is interactive
            if is_interactive:
                heading_options["command"] = lambda c=col: self.sort_table(c)

            # Apply the options using dictionary unpacking
            tree.heading(col, **heading_options)
            tree.column(col, width=150, anchor="center")

        # Insert data rows
        for i, (index, row) in enumerate(dataframe.iterrows()):
            tag = "oddrow" if i % 2 != 0 else "evenrow"
            iid = index if is_interactive else i
            tree.insert("", "end", iid=iid, values=row.tolist(), tags=(tag,))

    def apply_filters(self, event=None) -> None:
        """Apply all filters and update the UI accordingly."""
        if self.controller.selected_df is None:
            return
        selected_category = self.filter_frame.category_filter_box.get()
        search_term = self.filter_frame.search_entry.get()
        value_filter = self.filter_frame.value_filter_box.get()
        df_to_display = self.controller.filter_data(selected_category, search_term, value_filter)
        self.current_displayed_df = df_to_display  # Store currently displayed DataFrame
        summary_df = self.controller.get_summary(df_to_display)
        self.populate_treeview(self.tree, df_to_display, is_interactive=True)
        self.populate_treeview(self.summary_tree, summary_df, is_interactive=False)
        self.summary_chart_frame.update_chart(summary_df)
        self.calculate_and_display_summaries(df_to_display)
        self.reset_control_panel()

    def calculate_and_display_summaries(self, dataframe: pd.DataFrame | None) -> None:
        """Calculate and display income, expenses, and net balance."""
        income, expenses, net = self.controller.calculate_summaries(dataframe)
        self.bottom_frame.income_label.configure(text=f"Income: {income:,.2f}", text_color=COLOR_INCOME)
        self.bottom_frame.expense_label.configure(text=f"Expenses: {expenses:,.2f}", text_color=COLOR_EXPENSE)
        self.bottom_frame.net_label.configure(text=f"Net: {net:,.2f}")

    def load_file(self) -> None:
        """Load an Excel file and initialize the data."""
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath:
            return

        try:
            self.controller.load_data(filepath)
            self.current_displayed_df = self.controller.selected_df  # Initialize current displayed DataFrame
            self.populate_treeview(self.tree, self.controller.selected_df, is_interactive=False)
            self.populate_treeview(self.summary_tree, None)

            # --- CRITICAL CHANGE: Only enable the Analyze button ---
            self.top_frame.analyze_button.configure(state="normal")

            # --- Disable all other controls to enforce workflow ---
            self.top_frame.save_button.configure(state="disabled")
            self.top_frame.export_button.configure(state="disabled")
            self.filter_frame.category_filter_box.configure(state="disabled")
            self.filter_frame.search_entry.configure(state="disabled")
            self.filter_frame.clear_button.configure(state="disabled")
            self.filter_frame.value_filter_box.set("All")
            self.filter_frame.value_filter_box.configure(state="disabled")
            self.reset_control_panel()
            self.calculate_and_display_summaries(None)

            print("File loaded successfully. Waiting for analysis.")

        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Failed to load file:\n{e}", icon="cancel"
            )

    def analyze_data(self) -> None:
        """Analyze the loaded data and categorize transactions using two-pass logic (exact, then contains)."""
        if self.controller.selected_df is None:
            return

        columns_to_show = ["Accounting date", "Description", "Amount", "Category"]
        self.controller.selected_df["Category"] = ""
        self.controller.selected_df = self.controller.selected_df.reindex(
            columns=columns_to_show, fill_value=""
        )
        keywords_map = self.controller.keywords_map
        df = self.controller.selected_df

        # --- Pass 1: Exact Matching ---
        for category, rules in keywords_map.items():
            exact_list = rules.get("exact", [])
            if exact_list:
                mask = df["Description"].isin(exact_list)
                df.loc[mask, "Category"] = category

        # --- Pass 2: Contains Matching (only for uncategorized rows) ---
        uncategorized_mask = df["Category"] == ""
        for category, rules in keywords_map.items():
            contains_list = rules.get("contains", [])
            if contains_list:
                for keyword in contains_list:
                    # Only apply to still-uncategorized rows
                    contains_mask = df.loc[uncategorized_mask, "Description"].str.contains(keyword, case=False, na=False)
                    # Get the indices in the main DataFrame
                    indices = df.loc[uncategorized_mask].index[contains_mask]
                    df.loc[indices, "Category"] = category
                    # Update uncategorized_mask for next iterations
                    uncategorized_mask = df["Category"] == ""

        # --- Enable Controls ---
        self.tree.bind(
            "<<TreeviewSelect>>", lambda event: self.table_row_selected(event)
        )
        self.top_frame.save_button.configure(state="normal")
        self.top_frame.export_button.configure(state="normal")
        self.filter_frame.category_filter_box.configure(state="readonly")
        self.filter_frame.search_entry.configure(state="normal")
        self.filter_frame.clear_button.configure(state="normal")
        self.filter_frame.value_filter_box.set("All")
        self.filter_frame.value_filter_box.configure(state="readonly")

        # --- THE FIX YOU SUGGESTED ---
        self.refresh_category_filter()  # Refresh category filter with current categories
        self.bottom_frame.category_edit_box.configure(values=self.controller.get_categories())
        self.filter_frame.category_filter_box.set("All Categories")
        self.current_displayed_df = self.controller.selected_df  # Initialize current displayed DataFrame
        self.apply_filters()  # Now this will use the correct default filter

        # --- Display completion message (Stays the same) ---
        uncategorized_count = self.controller.selected_df["Category"].eq("").sum()
        if uncategorized_count == 0:
            CTkMessagebox(
                title="Analysis Complete",
                message="All transactions have been successfully categorized!",
                icon="check",
            )
        else:
            CTkMessagebox(
                title="Analysis Complete",
                message=f"Analysis complete. Found {uncategorized_count} items to review.",
                icon="info",
            )

    def clear_filters(self, reset_ui_controls: bool = False) -> None:
        """Clear all filters and reset the UI."""
        if reset_ui_controls:
            self.top_frame.save_button.configure(state="disabled")
            self.top_frame.export_button.configure(state="disabled")
            self.filter_frame.category_filter_box.configure(state="disabled")
            self.filter_frame.search_entry.configure(state="disabled")
            self.filter_frame.clear_button.configure(state="disabled")
            self.filter_frame.value_filter_box.configure(state="disabled")
        else:
            self.top_frame.save_button.configure(state="normal")
            self.top_frame.export_button.configure(state="normal")
            self.filter_frame.category_filter_box.configure(state="readonly")
            self.filter_frame.search_entry.configure(state="normal")
            self.filter_frame.clear_button.configure(state="normal")
            self.filter_frame.value_filter_box.configure(state="readonly")
        self.filter_frame.search_entry.delete(0, "end")
        self.refresh_category_filter()  # Refresh category filter with current categories
        self.bottom_frame.category_edit_box.configure(values=self.controller.get_categories())
        self.filter_frame.category_filter_box.set("All Categories")
        self.filter_frame.value_filter_box.set("All")
        if self.controller.selected_df is not None:
            self.apply_filters()
        self.reset_control_panel()

    def sort_table(self, column_name: str) -> None:
        """Sort the table by the given column."""
        if self.controller.selected_df is None:
            return
        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_ascending = True
        self.sort_column = column_name
        self.controller.sort_data(column_name, ascending=self.sort_ascending)
        self.apply_filters()

    def table_row_selected(self, event) -> None:
        """Handle row selection in the table."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        selected_iid_str = selected_items[0]
        try:
            # Use the currently displayed DataFrame instead of the original
            if self.current_displayed_df is not None:
                index_type = self.current_displayed_df.index.dtype.type
                self.controller.currently_selected_row_index = index_type(selected_iid_str)
                item_data = self.current_displayed_df.loc[self.controller.currently_selected_row_index]
            else:
                # Fallback to original DataFrame if no filtered data
                index_type = self.controller.selected_df.index.dtype.type
                self.controller.currently_selected_row_index = index_type(selected_iid_str)
                item_data = self.controller.selected_df.loc[self.controller.currently_selected_row_index]

            self.bottom_frame.category_edit_box.configure(state="readonly")
            # Refresh the category edit box with current categories
            self.bottom_frame.category_edit_box.configure(values=self.controller.get_categories())
            self.bottom_frame.category_edit_box.set(
                item_data["Category"] or "Select Category"
            )
            # Set and enable the amount entry
            self.bottom_frame.amount_edit_entry.configure(state="normal")
            self.bottom_frame.amount_edit_entry.delete(0, "end")
            self.bottom_frame.amount_edit_entry.insert(0, str(item_data["Amount"]))
            # Set and enable the description entry
            self.bottom_frame.description_edit_entry.configure(state="normal")
            self.bottom_frame.description_edit_entry.delete(0, "end")
            self.bottom_frame.description_edit_entry.insert(0, str(item_data["Description"]))
            self.bottom_frame.update_button.configure(state="normal")
            self.bottom_frame.delete_button.configure(state="normal")
        except (KeyError, ValueError) as e:
            print(f"Error selecting row: {e}")
            self.reset_control_panel()

    def update_row_data(self) -> None:
        """Update the description, category, and amount of the selected row and learn the new description as an exact match."""
        if self.controller.currently_selected_row_index is None:
            return
        chosen_category = self.bottom_frame.category_edit_box.get()
        amount_str = self.bottom_frame.amount_edit_entry.get()
        new_description = self.bottom_frame.description_edit_entry.get().strip()
        if not chosen_category or chosen_category == "Select Category":
            return
        if not new_description:
            CTkMessagebox(title="Error", message="Description cannot be empty.", icon="cancel")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            CTkMessagebox(title="Error", message="Amount must be a valid number.", icon="cancel")
            return
        try:
            if self.current_displayed_df is not None:
                selected_row_data = self.current_displayed_df.loc[self.controller.currently_selected_row_index]
                mask = True
                for col in selected_row_data.index:
                    if col in self.controller.selected_df.columns:
                        mask = mask & (self.controller.selected_df[col] == selected_row_data[col])
                matching_indices = self.controller.selected_df[mask].index
                if len(matching_indices) > 0:
                    original_index = matching_indices[0]
                    old_description = selected_row_data["Description"]
                    self.controller.selected_df.loc[original_index, "Category"] = chosen_category
                    self.controller.selected_df.loc[original_index, "Amount"] = amount
                    self.controller.selected_df.loc[original_index, "Description"] = new_description
                else:
                    raise KeyError("Could not find matching row in original DataFrame")
            else:
                old_description = self.controller.selected_df.loc[
                    self.controller.currently_selected_row_index, "Description"
                ]
                self.controller.selected_df.loc[self.controller.currently_selected_row_index, "Category"] = (
                    chosen_category
                )
                self.controller.selected_df.loc[self.controller.currently_selected_row_index, "Amount"] = amount
                self.controller.selected_df.loc[self.controller.currently_selected_row_index, "Description"] = new_description

            # --- Update the keywords map for the new structure ---
            keywords_map = self.controller.keywords_map
            # Remove old description from all categories' exact lists
            for cat, rules in keywords_map.items():
                if "exact" in rules and old_description in rules["exact"]:
                    rules["exact"].remove(old_description)
            # Add new description to the chosen category's exact list
            if chosen_category not in keywords_map:
                keywords_map[chosen_category] = {"exact": [], "contains": []}
            if new_description not in keywords_map[chosen_category]["exact"]:
                keywords_map[chosen_category]["exact"].append(new_description)
            self.controller.keywords_map = keywords_map
            self.apply_filters()
            self.reset_control_panel()
        except (KeyError, ValueError) as e:
            print(f"Error updating row data: {e}")
            CTkMessagebox(
                title="Error", message="Could not update the row.", icon="cancel"
            )

    def delete_selected_row(self) -> None:
        """Delete the selected row from the data."""
        if self.controller.currently_selected_row_index is None:
            return

        # Get the description of the selected row for the confirmation message
        try:
            if self.current_displayed_df is not None:
                # Get description from the currently displayed DataFrame
                selected_row_data = self.current_displayed_df.loc[self.controller.currently_selected_row_index]
                item_description = selected_row_data["Description"]
            else:
                # Get description from the original DataFrame
                item_description = self.controller.selected_df.loc[
                    self.controller.currently_selected_row_index, "Description"
                ]
        except (KeyError, ValueError) as e:
            print(f"Error getting row description: {e}")
            item_description = "Unknown"

        msg = CTkMessagebox(
            title="Confirm Deletion",
            message=f"Are you sure you want to permanently delete this row?\n\n{item_description}",
            icon="question",
            option_1="Cancel",
            option_2="Delete",
        )
        if msg.get() == "Delete":
            try:
                # Get the correct index for the original DataFrame
                if self.current_displayed_df is not None:
                    # Find the corresponding index in the original DataFrame
                    # We need to find the row in the original DataFrame that matches the selected row
                    selected_row_data = self.current_displayed_df.loc[self.controller.currently_selected_row_index]

                    # Find the matching row in the original DataFrame
                    # We'll match by all columns to ensure we get the right row
                    mask = True
                    for col in selected_row_data.index:
                        if col in self.controller.selected_df.columns:
                            mask = mask & (self.controller.selected_df[col] == selected_row_data[col])

                    # Get the index of the matching row in the original DataFrame
                    matching_indices = self.controller.selected_df[mask].index
                    if len(matching_indices) > 0:
                        original_index = matching_indices[0]
                        # Delete from the original DataFrame using the correct index
                        self.controller.selected_df.drop(original_index, inplace=True)
                    else:
                        raise KeyError("Could not find matching row in original DataFrame")
                else:
                    # If no filtered data, delete directly from original DataFrame
                    self.controller.selected_df.drop(self.controller.currently_selected_row_index, inplace=True)

                self.apply_filters()
                self.reset_control_panel()
            except (KeyError, ValueError) as e:
                print(f"Error deleting row: {e}")
                CTkMessagebox(
                    title="Error", message="Could not delete the row.", icon="cancel"
                )

    def save_learned_keywords(self) -> None:
        """Save the learned keywords to the config."""
        self.controller.save_keywords_map(self.controller.keywords_map)
        CTkMessagebox(
            title="Saved", message="Learned keywords have been saved successfully."
        )

    def reset_control_panel(self) -> None:
        """Reset the control panel to its default state."""
        self.bottom_frame.update_button.configure(state="disabled")
        self.bottom_frame.delete_button.configure(state="disabled")
        self.bottom_frame.category_edit_box.set("")
        self.bottom_frame.category_edit_box.configure(state="disabled")
        self.bottom_frame.amount_edit_entry.delete(0, "end")
        self.bottom_frame.amount_edit_entry.configure(state="disabled")
        self.bottom_frame.description_edit_entry.delete(0, "end")
        self.bottom_frame.description_edit_entry.configure(state="disabled")
        # Refresh the category edit box with current categories
        self.bottom_frame.category_edit_box.configure(values=self.controller.get_categories())
        self.controller.currently_selected_row_index = None

    def export_to_excel(self) -> None:
        """Export the currently displayed data to an Excel file."""
        if self.controller.selected_df is None:
            return
        selected_category = self.filter_frame.category_filter_box.get()
        search_term = self.filter_frame.search_entry.get()
        value_filter = self.filter_frame.value_filter_box.get()
        df_to_export = self.controller.filter_data(selected_category, search_term, value_filter)
        if df_to_export.empty:
            CTkMessagebox(
                title="Warning",
                message="No data in the current view to export.",
                icon="warning",
            )
            return
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Workbook", "*.xlsx"), ("All Files", "*.*")],
                title="Save Processed Data As...",
            )
            if not filepath:
                return
            self.controller.export_data(df_to_export, filepath)
            CTkMessagebox(
                title="Success", message=f"Data successfully exported to:\n{filepath}"
            )
        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Failed to export file:\n{e}", icon="cancel"
            )

    def export_keywords(self) -> None:
        """Export the content of keywords.json to a user-specified location."""
        try:
            keywords = self.controller.keywords_map
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Export Keywords As...",
            )
            if not filepath:
                return
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(keywords, f, indent=4, ensure_ascii=False)
            CTkMessagebox(title="Success", message=f"Keywords exported to:\n{filepath}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to export keywords:\n{e}", icon="cancel")

    def refresh_category_filter(self) -> None:
        """Refresh the category filter box with current categories."""
        current_categories = self.controller.get_categories()
        self.filter_frame.category_filter_box.configure(
            values=[CATEGORY_ALL, CATEGORY_UNCATEGORIZED] + current_categories
        )

    def exit_fullscreen(self):
        self.attributes('-fullscreen', False)


if __name__ == "__main__":
    app = App()
    app.mainloop()
