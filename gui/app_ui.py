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
        self.geometry("1200x800")

        # Data Storage & State
        self.df = None
        self.selected_df = None
        self.keywords_map = load_keywords()
        self.categories_list = load_categories()
        self.currently_selected_row_index = None
        self.sort_column = None
        self.sort_ascending = True
        
        # UI Structure
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Row for the table will expand

        # Top Frame
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.load_button = ctk.CTkButton(self.top_frame, text="1. Load Excel File", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        self.analyze_button = ctk.CTkButton(self.top_frame, text="2. Analyze File", command=self.analyze_data, state="disabled")
        self.analyze_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_button = ctk.CTkButton(self.top_frame, text="3. Save Learned Keywords", command=self.save_learned_keywords, state="disabled")
        self.save_button.grid(row=0, column=2, padx=5, pady=5)

        # --- RE-ADDED: Summary Frame ---
        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1)

        font_summary = ctk.CTkFont(size=16, weight="bold")
        self.income_label = ctk.CTkLabel(self.summary_frame, text="Total Income: -", font=font_summary, text_color="#27AE60")
        self.income_label.grid(row=0, column=0, padx=10, pady=10)
        self.expense_label = ctk.CTkLabel(self.summary_frame, text="Total Expenses: -", font=font_summary, text_color="#C0392B")
        self.expense_label.grid(row=0, column=1, padx=10, pady=10)
        self.net_label = ctk.CTkLabel(self.summary_frame, text="Net Balance: -", font=font_summary)
        self.net_label.grid(row=0, column=2, padx=10, pady=10)

        # Control Frame for editing
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.desc_label = ctk.CTkLabel(self.control_frame, text="Load and then analyze a file to begin.", font=ctk.CTkFont(size=14))
        self.desc_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.category_combobox = ctk.CTkComboBox(self.control_frame, values=self.categories_list, state="disabled")
        self.category_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.update_button = ctk.CTkButton(self.control_frame, text="Update Category", command=self.update_row_category, state="disabled")
        self.update_button.grid(row=0, column=2, padx=10, pady=10)

        # Bottom Frame for the Treeview table
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e", borderwidth=0, rowheight=25)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565B5E", foreground="white", relief="flat", font=('Calibri', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.tree = ttk.Treeview(self.bottom_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        self.tree.tag_configure('oddrow', background='#343638')
        self.tree.tag_configure('evenrow', background='#2a2d2e')
        
        scrollbar = ctk.CTkScrollbar(self.bottom_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<<TreeviewSelect>>", self.table_row_selected)
        
        self.populate_treeview(None)

    def populate_treeview(self, dataframe):
        self.tree.delete(*self.tree.get_children())
        if dataframe is None or dataframe.empty:
            self.tree["columns"] = ("1")
            self.tree.heading("1", text="No data to display. Please load a file.", anchor="center")
            self.tree.column("1", width=500, anchor="center")
            return
        self.tree["columns"] = dataframe.columns.tolist()
        for col in dataframe.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_table(c), anchor="center")
            self.tree.column(col, anchor="center", width=150)
        for i, (index, row) in enumerate(dataframe.iterrows()):
            tag = 'oddrow' if i % 2 != 0 else 'evenrow'
            self.tree.insert("", "end", iid=index, values=row.tolist(), tags=(tag,))

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath: return
        try:
            self.df = pd.read_excel(filepath, skiprows=7)
            self.selected_df = self.df.copy()
            self.populate_treeview(self.selected_df)
            self.analyze_button.configure(state="normal")
            self.save_button.configure(state="disabled")
            self.reset_control_panel()
            # Reset summary labels on new file load
            self.income_label.configure(text="Total Income: -")
            self.expense_label.configure(text="Total Expenses: -")
            self.net_label.configure(text="Net Balance: -")
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
        
        self.calculate_and_display_summaries() # Calculate and show totals
        self.save_button.configure(state="normal")
        self.populate_treeview(self.selected_df)
        self.reset_control_panel()
        
        uncategorized_count = len(self.selected_df[self.selected_df['Category'] == ''])
        if uncategorized_count == 0:
            CTkMessagebox(title="Analysis Complete", message="All transactions have been successfully categorized!", icon="check")
        else:
             CTkMessagebox(title="Analysis Complete", message=f"Automatic categorization is complete. Found {uncategorized_count} items to review.", icon="info")

    # --- RE-ADDED: Method to calculate and display summaries ---
    def calculate_and_display_summaries(self):
        if self.selected_df is None or 'Amount' not in self.selected_df.columns:
            return

        amounts = pd.to_numeric(self.selected_df['Amount'], errors='coerce').fillna(0)
        total_income = amounts[amounts > 0].sum()
        total_expenses = amounts[amounts < 0].sum()
        net_balance = amounts.sum()

        self.income_label.configure(text=f"Total Income: {total_income:,.2f}")
        self.expense_label.configure(text=f"Total Expenses: {total_expenses:,.2f}")
        self.net_label.configure(text=f"Net Balance: {net_balance:,.2f}")

    def sort_table(self, column_name):
        if self.selected_df is None: return
        if self.sort_column == column_name: self.sort_ascending = not self.sort_ascending
        else: self.sort_ascending = True
        self.sort_column = column_name
        self.selected_df = self.selected_df.sort_values(by=column_name, ascending=self.sort_ascending)
        self.populate_treeview(self.selected_df)

    def table_row_selected(self, event=None):
        """Handles row selection with robust index type handling."""
        # This method is called when a row is selected in the treeview.
        selected_items = self.tree.selection()
        if not selected_items:
            # This can happen if the selection is cleared.
            return
        
        # The iid from the treeview is always a string.
        selected_iid_str = selected_items[0]
        
        if self.selected_df is None:
            # This check prevents errors if a click happens before data is loaded.
            return

        try:
            # --- THE DEFINITIVE FIX ---
            # 1. Get the data type of the pandas DataFrame index (e.g., int, str).
            index_type = self.selected_df.index.dtype.type
            
            # 2. Convert the string iid from the treeview to the correct pandas index type.
            self.currently_selected_row_index = index_type(selected_iid_str)
            
            # 3. Now, safely use .loc with the correctly-typed index to find the row.
            item_data = self.selected_df.loc[self.currently_selected_row_index]
            
            # 4. Update the control panel widgets with the correct data.
            self.desc_label.configure(text=f"Editing: {item_data['Description']}")
            self.category_combobox.configure(state="readonly", values=self.categories_list)
            self.category_combobox.set(item_data['Category'] or "Select Category")
            self.update_button.configure(state="normal")

        except (KeyError, ValueError) as e:
            # This block catches errors if the index somehow is not found
            # or the type conversion fails, preventing a crash.
            print(f"Error selecting row (index: {selected_iid_str}): {e}")
            self.reset_control_panel()

    def update_row_category(self):
        if self.currently_selected_row_index is None: return
        chosen_category = self.category_combobox.get()
        if not chosen_category or chosen_category == "Select Category": return
        item_description = self.selected_df.loc[self.currently_selected_row_index, 'Description']
        self.selected_df.loc[self.currently_selected_row_index, 'Category'] = chosen_category
        self.keywords_map[item_description] = chosen_category
        self.populate_treeview(self.selected_df)
        self.calculate_and_display_summaries() # Recalculate after a change
        self.reset_control_panel()

    def save_learned_keywords(self):
        save_keywords(self.keywords_map)
        CTkMessagebox(title="Saved", message="Learned keywords have been saved successfully.")
    
    def reset_control_panel(self):
        self.desc_label.configure(text="Select a row from the table to edit its category.")
        self.update_button.configure(state="disabled")
        self.category_combobox.set("")
        self.category_combobox.configure(state="disabled")
        self.currently_selected_row_index = None

if __name__ == "__main__":
    app = App()
    app.mainloop()