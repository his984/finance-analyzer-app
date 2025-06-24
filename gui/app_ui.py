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
        self.displayed_df = None # The dataframe that is currently shown in the treeview
        self.keywords_map = load_keywords()
        self.categories_list = load_categories()
        self.currently_selected_row_index = None # The original DataFrame index for the selected row
        self.sort_column = None
        self.sort_ascending = True
        
        # UI Structure
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

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

        # Control Frame
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.desc_label = ctk.CTkLabel(self.control_frame, text="Load and then analyze a file to begin.", font=ctk.CTkFont(size=14))
        self.desc_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.category_combobox = ctk.CTkComboBox(self.control_frame, values=self.categories_list, state="disabled")
        self.category_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.update_button = ctk.CTkButton(self.control_frame, text="Update Category", command=self.update_row_category, state="disabled")
        self.update_button.grid(row=0, column=2, padx=10, pady=10)

        # Bottom Frame
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview Style Configuration
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e", borderwidth=0, rowheight=25)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565B5E", foreground="white", relief="flat", font=('Calibri', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.tree = ttk.Treeview(self.bottom_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # CORRECTED: Configure tags directly on the tree widget
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
            # Use the original DataFrame index as the item id (iid)
            self.tree.insert("", "end", iid=index, values=row.tolist(), tags=(tag,))

    def table_row_selected(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return
        
        self.currently_selected_row_index = selected_items[0]
        
        try:
            item_data = self.selected_df.loc[self.currently_selected_row_index]
            self.desc_label.configure(text=f"Editing: {item_data['Description']}")
            self.category_combobox.configure(state="readonly", values=self.categories_list)
            self.category_combobox.set(item_data['Category'] or "Select Category")
            self.update_button.configure(state="normal")
        except KeyError:
            print(f"KeyError: Could not find index {self.currently_selected_row_index} in the main dataframe. This can happen after filtering.")
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
            self.reset_control_panel()
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
        self.populate_treeview(self.selected_df)
        self.reset_control_panel()
        
        uncategorized_count = len(self.selected_df[self.selected_df['Category'] == ''])
        if uncategorized_count == 0:
            CTkMessagebox(title="Analysis Complete", message="All transactions have been successfully categorized!", icon="check")
        else:
             CTkMessagebox(title="Analysis Complete", message=f"Automatic categorization is complete. Found {uncategorized_count} items to review.", icon="info")

    def sort_table(self, column_name):
        if self.selected_df is None: return
        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_ascending = True
        
        self.sort_column = column_name
        self.selected_df = self.selected_df.sort_values(by=column_name, ascending=self.sort_ascending)
        self.populate_treeview(self.selected_df)

    def update_row_category(self):
        if self.currently_selected_row_index is None: return
        chosen_category = self.category_combobox.get()
        if not chosen_category or chosen_category == "Select Category": return
            
        item_description = self.selected_df.loc[self.currently_selected_row_index, 'Description']
        
        self.selected_df.loc[self.currently_selected_row_index, 'Category'] = chosen_category
        self.keywords_map[item_description] = chosen_category
        
        self.populate_treeview(self.selected_df)
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

# We are not using filter functionality in this version to focus on performance and stability
# if __name__ == "__main__" block is in main.py