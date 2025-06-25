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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Analyzer")
        self.geometry("1600x900")

        # --- Data Storage & State ---
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

        # --- UI Structure ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Top Action Frame
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.load_button = ctk.CTkButton(
            self.top_frame, text="1. Load File", command=self.load_file
        )
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        self.analyze_button = ctk.CTkButton(
            self.top_frame,
            text="2. Analyze",
            command=self.analyze_data,
            state="disabled",
        )
        self.analyze_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_button = ctk.CTkButton(
            self.top_frame,
            text="3. Save Keywords",
            command=self.save_learned_keywords,
            state="disabled",
        )
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        self.export_button = ctk.CTkButton(
            self.top_frame,
            text="4. Export Excel",
            command=self.export_to_excel,
            state="disabled",
        )
        self.export_button.grid(row=0, column=3, padx=5, pady=5)

        # Filter Frame
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        self.filter_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(self.filter_frame, text="Filter Category:").grid(
            row=0, column=0, padx=(10, 5), pady=10
        )
        self.category_filter_box = ctk.CTkComboBox(
            self.filter_frame,
            values=self.categories_for_filter,
            command=self.apply_filters,
            state="disabled",
        )
        self.category_filter_box.grid(row=0, column=1, padx=5, pady=10)
        ctk.CTkLabel(self.filter_frame, text="Search Desc:").grid(
            row=0, column=2, padx=(20, 5), pady=10
        )
        self.search_entry = ctk.CTkEntry(
            self.filter_frame, placeholder_text="Type to search...", state="disabled"
        )
        self.search_entry.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.apply_filters)
        self.clear_button = ctk.CTkButton(
            self.filter_frame,
            text="Clear Filters",
            command=self.clear_filters,
            state="disabled",
        )
        self.clear_button.grid(row=0, column=4, padx=(5, 10), pady=10)

        # Main Content Frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Main Table Container
        self.main_table_container = ctk.CTkFrame(self.content_frame)
        self.main_table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.main_table_container.grid_rowconfigure(0, weight=1)
        self.main_table_container.grid_columnconfigure(0, weight=1)

        # Summary Panel Container
        self.summary_container = ctk.CTkFrame(self.content_frame)
        self.summary_container.grid(row=0, column=1, sticky="nsew")
        self.summary_container.grid_rowconfigure(1, weight=1)
        self.summary_container.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self.summary_container,
            text="Category Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=10)

        # Create Treeview widgets
        self.tree = self.create_treeview_in_frame(self.main_table_container)
        self.summary_tree = self.create_treeview_in_frame(self.summary_container)

        self.tree.bind(
            "<<TreeviewSelect>>", lambda event: self.table_row_selected(event)
        )

        # Bottom Control & Summary Frame
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        self.control_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.control_frame, text="Edit Selected:").pack(
            side="left", padx=(10, 5)
        )
        self.category_edit_box = ctk.CTkComboBox(
            self.control_frame, values=self.categories_for_edit, state="disabled"
        )
        self.category_edit_box.pack(side="left", padx=5)
        self.update_button = ctk.CTkButton(
            self.control_frame,
            text="Update",
            command=self.update_row_category,
            state="disabled",
        )
        self.update_button.pack(side="left", padx=5)
        self.delete_button = ctk.CTkButton(
            self.control_frame,
            text="Delete",
            command=self.delete_selected_row,
            state="disabled",
            fg_color="#C0392B",
            hover_color="#E74C3C",
        )
        self.delete_button.pack(side="left", padx=5)

        self.overall_summary_frame = ctk.CTkFrame(
            self.bottom_frame, fg_color="transparent"
        )
        self.overall_summary_frame.grid(row=0, column=1, sticky="e")
        font_summary = ctk.CTkFont(size=16, weight="bold")
        self.income_label = ctk.CTkLabel(
            self.overall_summary_frame,
            text="Income: -",
            font=font_summary,
            text_color="#27AE60",
        )
        self.income_label.pack(side="left", padx=10)
        self.expense_label = ctk.CTkLabel(
            self.overall_summary_frame,
            text="Expenses: -",
            font=font_summary,
            text_color="#C0392B",
        )
        self.expense_label.pack(side="left", padx=10)
        self.net_label = ctk.CTkLabel(
            self.overall_summary_frame, text="Net: -", font=font_summary
        )
        self.net_label.pack(side="left", padx=10)

        self.populate_treeview(self.tree, None)
        self.populate_treeview(self.summary_tree, None)

    def create_treeview_in_frame(self, parent_frame):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            borderwidth=0,
            rowheight=25,
        )
        style.map("Treeview", background=[("selected", "#22559b")])
        style.configure(
            "Treeview.Heading",
            background="#565B5E",
            foreground="white",
            relief="flat",
            font=("Calibri", 10, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", "#3484F0")])

        tree = ttk.Treeview(frame, show="headings", style="Treeview")
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ctk.CTkScrollbar(frame, command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.tag_configure("oddrow", background="#343638")
        tree.tag_configure("evenrow", background="#2a2d2e")

        return tree

    def populate_treeview(self, tree, dataframe, is_interactive=False):
        """Clears and populates a given treeview with a dataframe."""
        tree.delete(*self.tree.get_children())

        # Clear existing columns before setting new ones
        tree["columns"] = ()

        if dataframe is None or dataframe.empty:
            tree["columns"] = "1"
            tree.heading("1", text="No Data")
            tree.column("1", anchor="c")
            return

        tree["columns"] = dataframe.columns.tolist()
        for col in dataframe.columns:
            # --- THE DEFINITIVE FIX IS HERE ---
            heading_options = {"text": col, "anchor": "center"}
            if is_interactive:
                heading_options["command"] = lambda c=col: self.sort_table(c)

            tree.heading(col, **heading_options)
            tree.column(col, anchor="c", width=150)

        for i, (index, row) in enumerate(dataframe.iterrows()):
            tag = "oddrow" if i % 2 != 0 else "evenrow"
            iid = index if is_interactive else i
            tree.insert("", "end", iid=iid, values=row.tolist(), tags=(tag,))

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath:
            return
        try:
            self.df = pd.read_excel(filepath, skiprows=7)
            self.selected_df = self.df.copy()
            self.populate_treeview(self.tree, self.selected_df, is_interactive=False)
            self.populate_treeview(self.summary_tree, None)
            self.top_frame.analyze_button.configure(state="normal")
            self.clear_filters(reset_ui_controls=True)
            self.reset_control_panel()
            self.calculate_and_display_summaries(None)
        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Failed to load file:\n{e}", icon="cancel"
            )

    def analyze_data(self):
        if self.selected_df is None:
            return
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

        self.tree.bind(
            "<<TreeviewSelect>>", lambda event: self.table_row_selected(event)
        )
        self.clear_filters(reset_ui_controls=False)
        self.apply_filters()

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

        self.populate_treeview(self.tree, df_to_display, is_interactive=True)
        self.calculate_and_display_summaries(df_to_display)
        self.populate_treeview(
            self.summary_tree, get_category_summary(df_to_display), is_interactive=False
        )
        self.reset_control_panel()

    def clear_filters(self, reset_ui_controls=False):
        if reset_ui_controls:
            self.top_frame.save_button.configure(state="disabled")
            self.top_frame.export_button.configure(state="disabled")
            self.filter_frame.category_filter_box.configure(state="disabled")
            self.filter_frame.search_entry.configure(state="disabled")
            self.filter_frame.clear_button.configure(state="disabled")
        else:
            self.top_frame.save_button.configure(state="normal")
            self.top_frame.export_button.configure(state="normal")
            self.filter_frame.category_filter_box.configure(state="readonly")
            self.filter_frame.search_entry.configure(state="normal")
            self.filter_frame.clear_button.configure(state="normal")

        self.filter_frame.search_entry.delete(0, "end")
        self.filter_frame.category_filter_box.set("All Categories")
        if self.selected_df is not None:
            self.apply_filters()
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

        df_to_export = self.selected_df
        # ... (filter logic for export) ...
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
