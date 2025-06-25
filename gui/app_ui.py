import customtkinter as ctk
from tkinter import filedialog, ttk
import pandas as pd
import json
import math
from CTkMessagebox import CTkMessagebox

from core.data_processor import (
    load_keywords,
    save_keywords,
    load_categories,
    get_category_summary,
)
from .frames.top_actions_frame import TopActionsFrame
from .frames.filter_frame import FilterFrame
from .frames.table_frame import TableFrame
from .frames.bottom_frame import BottomFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Analyzer")
        self.geometry("1600x900")

        # Data Storage & State
        self.df = None
        self.selected_df = None
        self.keywords_map = load_keywords()
        self.categories_for_filter = [
            "All Categories",
            "Uncategorized",
        ] + load_categories()
        self.categories_for_edit = load_categories()
        self.currently_selected_row_index = None
        self.sort_column = None
        self.sort_ascending = True

        # UI Structure
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create and grid all the main frames
        self.top_frame = TopActionsFrame(self, controller=self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.filter_frame = FilterFrame(self, controller=self)
        self.filter_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=1)

        self.table_frame = TableFrame(self.content_frame)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.tree = self.table_frame.tree
        self.tree.bind(
            "<<TreeviewSelect>>", lambda event: self.table_row_selected(event)
        )

        self.summary_panel = TableFrame(self.content_frame)
        self.summary_panel.grid(row=0, column=1, sticky="nsew")
        self.summary_tree = self.summary_panel.tree

        self.bottom_frame = BottomFrame(self, controller=self)
        self.bottom_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Initial population
        self.populate_treeview(self.tree, None)
        self.populate_treeview(self.summary_tree, None)

    def populate_treeview(self, tree, dataframe, is_interactive=False):
        """
        A robust method to populate a treeview. It clears the tree,
        sets columns, and inserts data. It conditionally adds sort commands.
        """
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

    def apply_filters(self, event=None):
        if self.selected_df is None:
            return

        df_to_display = self.selected_df
        selected_category = self.filter_frame.category_filter_box.get()
        if selected_category == "Uncategorized":
            df_to_display = df_to_display[df_to_display["Category"] == ""]
        elif selected_category != "All Categories":
            df_to_display = df_to_display[
                df_to_display["Category"] == selected_category
            ]

        search_term = self.filter_frame.search_entry.get()
        if search_term:
            df_to_display = df_to_display[
                df_to_display["Description"].str.contains(
                    search_term, case=False, na=False
                )
            ]

        # Value filter logic
        value_filter = self.filter_frame.value_filter_box.get()
        if value_filter == "Positive":
            df_to_display = df_to_display[pd.to_numeric(df_to_display["Amount"], errors="coerce") > 0]
        elif value_filter == "Negative":
            df_to_display = df_to_display[pd.to_numeric(df_to_display["Amount"], errors="coerce") < 0]

        self.populate_treeview(self.tree, df_to_display, is_interactive=True)
        self.populate_treeview(
            self.summary_tree, get_category_summary(df_to_display), is_interactive=False
        )
        self.calculate_and_display_summaries(df_to_display)
        self.reset_control_panel()

    def calculate_and_display_summaries(self, dataframe):
        if dataframe is None or "Amount" not in dataframe.columns:
            self.bottom_frame.income_label.configure(text="Income: -")
            self.bottom_frame.expense_label.configure(text="Expenses: -")
            self.bottom_frame.net_label.configure(text="Net: -")
            return
        amounts = pd.to_numeric(dataframe["Amount"], errors="coerce").fillna(0)
        total_income = amounts[amounts > 0].sum()
        total_expenses = amounts[amounts < 0].sum()
        net_balance = amounts.sum()
        self.bottom_frame.income_label.configure(text=f"Income: {total_income:,.2f}")
        self.bottom_frame.expense_label.configure(
            text=f"Expenses: {total_expenses:,.2f}"
        )
        self.bottom_frame.net_label.configure(text=f"Net: {net_balance:,.2f}")

    def load_file(self):
        """Loads the Excel file, displays its raw content, and enables the Analyze button."""
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath:
            return

        try:
            self.df = pd.read_excel(filepath, skiprows=7)
            self.selected_df = self.df.copy()

            # --- CRITICAL CHANGE: Only display raw data. Do NOT call any filter/summary functions ---
            self.populate_treeview(self.tree, self.selected_df, is_interactive=False)
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

    def analyze_data(self):
        """Analyzes data, then sets the filter to 'All Categories' and refreshes the view."""
        if self.selected_df is None:
            return

        # --- Analysis Logic (Stays the same) ---
        columns_to_show = ["Accounting date", "Description", "Amount", "Category"]
        self.selected_df["Category"] = ""
        self.selected_df = self.selected_df.reindex(
            columns=columns_to_show, fill_value=""
        )
        for keyword, category in self.keywords_map.items():
            mask = self.selected_df["Description"].str.contains(
                keyword, case=False, na=False
            )
            self.selected_df.loc[mask, "Category"] = category

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
        # Set the default filter value before applying it
        self.filter_frame.category_filter_box.set("All Categories")
        self.apply_filters()  # Now this will use the correct default filter

        # --- Display completion message (Stays the same) ---
        uncategorized_count = self.selected_df["Category"].eq("").sum()
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

    def clear_filters(self, reset_ui_controls=False):
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
        self.filter_frame.category_filter_box.set("All Categories")
        self.filter_frame.value_filter_box.set("All")
        if self.selected_df is not None:
            self.apply_filters()
        self.reset_control_panel()

    def sort_table(self, column_name):
        if self.selected_df is None:
            return
        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_ascending = True
        self.sort_column = column_name
        self.selected_df = self.selected_df.sort_values(
            by=column_name, ascending=self.sort_ascending
        )
        self.apply_filters()

    def table_row_selected(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        selected_iid_str = selected_items[0]
        try:
            index_type = self.selected_df.index.dtype.type
            self.currently_selected_row_index = index_type(selected_iid_str)
            item_data = self.selected_df.loc[self.currently_selected_row_index]
            self.bottom_frame.category_edit_box.configure(state="readonly")
            self.bottom_frame.category_edit_box.set(
                item_data["Category"] or "Select Category"
            )
            self.bottom_frame.update_button.configure(state="normal")
            self.bottom_frame.delete_button.configure(state="normal")
        except (KeyError, ValueError) as e:
            print(f"Error selecting row: {e}")
            self.reset_control_panel()

    def update_row_category(self):
        if self.currently_selected_row_index is None:
            return
        chosen_category = self.bottom_frame.category_edit_box.get()
        if not chosen_category or chosen_category == "Select Category":
            return
        item_description = self.selected_df.loc[
            self.currently_selected_row_index, "Description"
        ]
        self.selected_df.loc[self.currently_selected_row_index, "Category"] = (
            chosen_category
        )
        self.keywords_map[item_description] = chosen_category
        self.apply_filters()
        self.reset_control_panel()

    def delete_selected_row(self):
        if self.currently_selected_row_index is None:
            return
        msg = CTkMessagebox(
            title="Confirm Deletion",
            message=f"Are you sure you want to permanently delete this row?",
            icon="question",
            option_1="Cancel",
            option_2="Delete",
        )
        if msg.get() == "Delete":
            try:
                self.selected_df.drop(self.currently_selected_row_index, inplace=True)
                self.apply_filters()
                self.reset_control_panel()
            except KeyError:
                CTkMessagebox(
                    title="Error", message="Could not delete the row.", icon="cancel"
                )

    def save_learned_keywords(self):
        save_keywords(self.keywords_map)
        CTkMessagebox(
            title="Saved", message="Learned keywords have been saved successfully."
        )

    def reset_control_panel(self):
        self.bottom_frame.update_button.configure(state="disabled")
        self.bottom_frame.delete_button.configure(state="disabled")
        self.bottom_frame.category_edit_box.set("")
        self.bottom_frame.category_edit_box.configure(state="disabled")
        self.currently_selected_row_index = None

    def export_to_excel(self):
        if self.selected_df is None:
            return
        # Logic to get currently displayed data for export
        df_to_export = self.selected_df.copy()  # Start with a copy
        selected_category = self.filter_frame.category_filter_box.get()
        if selected_category == "Uncategorized":
            df_to_export = df_to_export[df_to_export["Category"] == ""]
        elif selected_category != "All Categories":
            df_to_export = df_to_export[df_to_export["Category"] == selected_category]
        search_term = self.filter_frame.search_entry.get()
        if search_term:
            df_to_export = df_to_export[
                df_to_export["Description"].str.contains(
                    search_term, case=False, na=False
                )
            ]

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
            df_to_export.to_excel(filepath, index=False)
            CTkMessagebox(
                title="Success", message=f"Data successfully exported to:\n{filepath}"
            )
        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Failed to export file:\n{e}", icon="cancel"
            )


if __name__ == "__main__":
    app = App()
    app.mainloop()
