import customtkinter as ctk
from tkinter import filedialog, ttk
import pandas as pd
import json
import math
from CTkMessagebox import CTkMessagebox

from core.data_processor import load_keywords, save_keywords, load_categories

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Analyzer")
        self.geometry("1400x800")

        # --- Data Storage & State ---
        self.df = None
        self.selected_df = None
        self.keywords_map = load_keywords()
        self.categories_for_filter = ["All Categories", "Uncategorized"] + load_categories()
        self.categories_for_edit = load_categories()
        self.currently_selected_row_index = None
        self.sort_column = None
        self.sort_ascending = True
        
        # --- WIDGETS ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Top Action Frame
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.load_button = ctk.CTkButton(self.top_frame, text="1. Load Excel File", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        self.analyze_button = ctk.CTkButton(self.top_frame, text="2. Analyze File", command=self.analyze_data, state="disabled")
        self.analyze_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_button = ctk.CTkButton(self.top_frame, text="3. Save Learned Keywords", command=self.save_learned_keywords, state="disabled")
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        self.export_button = ctk.CTkButton(self.top_frame, text="4. Export to Excel", command=self.export_to_excel, state="disabled")
        self.export_button.grid(row=0, column=3, padx=5, pady=5)
        
        # --- UPDATED: Filter & Search Frame ---
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        self.filter_frame.grid_columnconfigure(3, weight=1) # Allow search entry to expand
        ctk.CTkLabel(self.filter_frame, text="Filter by Category:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.category_filter_box = ctk.CTkComboBox(self.filter_frame, values=self.categories_for_filter, command=self.apply_filters, state="disabled")
        self.category_filter_box.grid(row=0, column=1, padx=5, pady=10)
        ctk.CTkLabel(self.filter_frame, text="Search Description:").grid(row=0, column=2, padx=(20, 5), pady=10)
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Type to search...", state="disabled")
        self.search_entry.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        # Bind the key release event to the apply_filters function
        self.search_entry.bind("<KeyRelease>", self.apply_filters)
        # The search button is no longer needed
        self.clear_button = ctk.CTkButton(self.filter_frame, text="Clear Filters", command=self.clear_filters, state="disabled")
        self.clear_button.grid(row=0, column=4, padx=(5, 10), pady=10)

        # Main Data Table Frame
        # ... (No changes in this section) ...
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e", borderwidth=0, rowheight=25)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565B5E", foreground="white", relief="flat", font=('Calibri', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])
        self.tree = ttk.Treeview(self.table_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure('oddrow', background='#343638')
        self.tree.tag_configure('evenrow', background='#2a2d2e')
        scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", lambda event: self.table_row_selected(event))

        # Bottom Control & Summary Frame
        # ... (No changes in this section) ...
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.control_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.control_frame, text="Edit Selected:").pack(side="left", padx=(10,5))
        self.category_edit_box = ctk.CTkComboBox(self.control_frame, values=self.categories_for_edit, state="disabled")
        self.category_edit_box.pack(side="left", padx=5)
        self.update_button = ctk.CTkButton(self.control_frame, text="Update", command=self.update_row_category, state="disabled")
        self.update_button.pack(side="left", padx=5)
        self.delete_button = ctk.CTkButton(self.control_frame, text="Delete", command=self.delete_selected_row, state="disabled", fg_color="#C0392B", hover_color="#E74C3C")
        self.delete_button.pack(side="left", padx=5)
        self.summary_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.summary_frame.grid(row=0, column=1, sticky="e")
        font_summary = ctk.CTkFont(size=16, weight="bold")
        self.income_label = ctk.CTkLabel(self.summary_frame, text="Income: -", font=font_summary, text_color="#27AE60")
        self.income_label.pack(side="left", padx=10)
        self.expense_label = ctk.CTkLabel(self.summary_frame, text="Expenses: -", font=font_summary, text_color="#C0392B")
        self.expense_label.pack(side="left", padx=10)
        self.net_label = ctk.CTkLabel(self.summary_frame, text="Net: -", font=font_summary)
        self.net_label.pack(side="left", padx=10)
        
        self.populate_treeview(None)

    # --- All methods are the same, no logic changes needed ---
    def populate_treeview(self, dataframe):
        self.tree.delete(*self.tree.get_children())
        if dataframe is None or dataframe.empty:
            self.tree["columns"] = ("1")
            self.tree.heading("1", text="No data to display. Please load a file.", anchor="center")
            self.tree.column("1", anchor="center")
            return
        self.tree["columns"] = dataframe.columns.tolist()
        for col in dataframe.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_table(c), anchor="center")
            self.tree.column(col, anchor="center", width=150)
        for i, (index, row) in enumerate(dataframe.iterrows()):
            tag = 'oddrow' if i % 2 != 0 else 'evenrow'
            self.tree.insert("", "end", iid=index, values=row.tolist(), tags=(tag,))
    def calculate_and_display_summaries(self, dataframe):
        if dataframe is None or 'Amount' not in dataframe.columns:
            self.income_label.configure(text="Income: -")
            self.expense_label.configure(text="Expenses: -")
            self.net_label.configure(text="Net: -")
            return
        amounts = pd.to_numeric(dataframe['Amount'], errors='coerce').fillna(0)
        total_income = amounts[amounts > 0].sum()
        total_expenses = amounts[amounts < 0].sum()
        net_balance = amounts.sum()
        self.income_label.configure(text=f"Income: {total_income:,.2f}")
        self.expense_label.configure(text=f"Expenses: {total_expenses:,.2f}")
        self.net_label.configure(text=f"Net: {net_balance:,.2f}")
    def apply_filters(self, event=None):
        if self.selected_df is None: return
        df_to_display = self.selected_df
        selected_category = self.category_filter_box.get()
        if selected_category == "Uncategorized":
            df_to_display = df_to_display[df_to_display['Category'] == '']
        elif selected_category != "All Categories":
            df_to_display = df_to_display[df_to_display['Category'] == selected_category]
        search_term = self.search_entry.get()
        if search_term:
            df_to_display = df_to_display[df_to_display['Description'].str.contains(search_term, case=False, na=False)]
        self.populate_treeview(df_to_display)
        self.calculate_and_display_summaries(df_to_display)
        self.reset_control_panel()
    def clear_filters(self):
        if self.selected_df is None: return
        self.search_entry.delete(0, 'end')
        self.category_filter_box.set("All Categories")
        self.populate_treeview(self.selected_df)
        self.calculate_and_display_summaries(self.selected_df)
        self.reset_control_panel()
    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath: return
        try:
            self.df = pd.read_excel(filepath, skiprows=7)
            self.selected_df = self.df.copy()
            self.populate_treeview(self.selected_df)
            self.analyze_button.configure(state="normal")
            self.save_button.configure(state="disabled")
            self.export_button.configure(state="disabled")
            self.clear_filters()
            self.category_filter_box.configure(state="disabled")
            self.search_entry.configure(state="disabled")
            self.clear_button.configure(state="disabled")
            self.calculate_and_display_summaries(None)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load file:\n{e}", icon="cancel")
    def analyze_data(self):
        if self.selected_df is None: return
        columns_to_show = ['Accounting date', 'Description', 'Amount', 'Category']
        self.selected_df['Category'] = ''
        self.selected_df = self.selected_df.reindex(columns=columns_to_show, fill_value='')
        for keyword, category in self.keywords_map.items():
            mask = self.selected_df['Description'].str.contains(keyword, case=False, na=False)
            self.selected_df.loc[mask, 'Category'] = category
        self.save_button.configure(state="normal")
        self.export_button.configure(state="normal")
        self.category_filter_box.configure(state="readonly")
        self.search_entry.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.clear_filters()
        uncategorized_count = self.selected_df['Category'].eq('').sum()
        if uncategorized_count == 0:
            CTkMessagebox(title="Analysis Complete", message="All transactions have been successfully categorized!", icon="check")
        else:
             CTkMessagebox(title="Analysis Complete", message=f"Automatic categorization is complete. Found {uncategorized_count} items to review.", icon="info")
    def sort_table(self, column_name):
        if self.selected_df is None: return
        if self.sort_column == column_name: self.sort_ascending = not self.sort_ascending
        else: self.sort_ascending = True
        self.sort_column = column_name
        self.selected_df = self.selected_df.sort_values(by=column_name, ascending=self.sort_ascending)
        self.apply_filters()
    def table_row_selected(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return
        selected_iid_str = selected_items[0]
        if self.selected_df is None: return
        try:
            index_type = self.selected_df.index.dtype.type
            self.currently_selected_row_index = index_type(selected_iid_str)
            item_data = self.selected_df.loc[self.currently_selected_row_index]
            self.category_edit_box.configure(state="readonly")
            self.category_edit_box.set(item_data['Category'] or "Select Category")
            self.update_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        except (KeyError, ValueError) as e:
            print(f"Error selecting row: {e}")
            self.reset_control_panel()
    def update_row_category(self):
        if self.currently_selected_row_index is None: return
        chosen_category = self.category_edit_box.get()
        if not chosen_category or chosen_category == "Select Category": return
        item_description = self.selected_df.loc[self.currently_selected_row_index, 'Description']
        self.selected_df.loc[self.currently_selected_row_index, 'Category'] = chosen_category
        self.keywords_map[item_description] = chosen_category
        self.apply_filters()
        self.calculate_and_display_summaries(self.selected_df)
        self.reset_control_panel()
    def delete_selected_row(self):
        if self.currently_selected_row_index is None: return
        msg = CTkMessagebox(title="Confirm Deletion", message=f"Are you sure you want to permanently delete this row?", icon="question", option_1="Cancel", option_2="Delete")
        if msg.get() == "Delete":
            try:
                self.selected_df.drop(self.currently_selected_row_index, inplace=True)
                self.apply_filters()
                self.reset_control_panel()
            except KeyError:
                CTkMessagebox(title="Error", message="Could not delete the row.", icon="cancel")
    def save_learned_keywords(self):
        save_keywords(self.keywords_map)
        CTkMessagebox(title="Saved", message="Learned keywords have been saved successfully.")
    def reset_control_panel(self):
        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.category_edit_box.set("")
        self.category_edit_box.configure(state="disabled")
        self.currently_selected_row_index = None
    def export_to_excel(self):
        if self.selected_df is None or self.selected_df.empty:
            CTkMessagebox(title="Warning", message="No data available to export.", icon="warning")
            return
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel Workbook", "*.xlsx"), ("All Files", "*.*")],
                title="Save Processed Data As..."
            )
            if not filepath: return
            self.selected_df.to_excel(filepath, index=False)
            CTkMessagebox(title="Success", message=f"Data successfully exported to:\n{filepath}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to export file:\n{e}", icon="cancel")

if __name__ == "__main__":
    app = App()
    app.mainloop()