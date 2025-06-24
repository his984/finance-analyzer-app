import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import json
import math # Import the math library for calculating total pages
from CTkTable import CTkTable
from CTkMessagebox import CTkMessagebox

from core.data_processor import load_keywords, save_keywords, load_categories

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Analyzer")
        self.geometry("1200x800")

        # --- Data Storage & State ---
        self.df = None
        self.selected_df = None
        self.displayed_df = None
        self.keywords_map = load_keywords()
        self.categories_list = load_categories()
        self.currently_selected_row_index = None
        self.sort_column = None
        self.sort_ascending = True
        
        # NEW: Pagination State
        self.page_size = 50
        self.current_page = 0
        self.total_pages = 0
        
        # --- WIDGETS ---
        # ... (Top frame and Control Frame are the same) ...
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=10)
        self.top_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.load_button = ctk.CTkButton(self.top_frame, text="1. Load Excel File", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        self.analyze_button = ctk.CTkButton(self.top_frame, text="2. Analyze File", command=self.analyze_data, state="disabled")
        self.analyze_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_button = ctk.CTkButton(self.top_frame, text="3. Save Learned Keywords", command=self.save_learned_keywords, state="disabled")
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=20, pady=10)
        self.desc_label = ctk.CTkLabel(self.control_frame, text="Load and then analyze a file to begin.", font=ctk.CTkFont(size=14))
        self.desc_label.grid(row=0, column=0, padx=10, pady=10)
        self.category_combobox = ctk.CTkComboBox(self.control_frame, values=self.categories_list, state="disabled")
        self.category_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.update_button = ctk.CTkButton(self.control_frame, text="Update Category", command=self.update_row_category, state="disabled")
        self.update_button.grid(row=0, column=2, padx=10, pady=10)

        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Container for the table
        self.table_container = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True)
        self.table = None

        # NEW: Pagination Frame and Controls
        self.pagination_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=5)
        self.prev_button = ctk.CTkButton(self.pagination_frame, text="< Previous", command=self.previous_page, state="disabled")
        self.prev_button.pack(side="left", padx=10)
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Page - of -")
        self.page_label.pack(side="left", padx=10)
        self.next_button = ctk.CTkButton(self.pagination_frame, text="Next >", command=self.next_page, state="disabled")
        self.next_button.pack(side="left", padx=10)
        
        # Filter switch is moved to be beside pagination controls for better layout
        self.filter_switch_var = ctk.StringVar(value="off")
        self.filter_switch = ctk.CTkSwitch(self.pagination_frame, text="Show Uncategorized Only", command=self.filter_table, variable=self.filter_switch_var, onvalue="on", offvalue="off", state="disabled")
        self.filter_switch.pack(side="right", padx=10)
        
        self.update_table_display()

    # --- Methods for Pagination ---
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_table_display(is_interactive=True)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table_display(is_interactive=True)

    # --- Modified Methods ---
    def load_file(self):
        # ... same as before, but resets page number
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath: return
        try:
            self.df = pd.read_excel(filepath, skiprows=7)
            self.selected_df = self.df.copy()
            self.current_page = 0 # Reset to first page
            self.update_table_display(is_interactive=False)
            self.analyze_button.configure(state="normal")
            self.save_button.configure(state="disabled")
            self.filter_switch.configure(state="disabled")
            self.reset_control_panel()
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load file:\n{e}", icon="cancel")
    
    def filter_table(self):
        self.current_page = 0 # Reset to first page when filter changes
        self.update_table_display(is_interactive=True)

    def sort_table(self, column_name):
        # ... same as before, but resets page number
        if self.selected_df is None: return
        if self.sort_column == column_name: self.sort_ascending = not self.sort_ascending
        else: self.sort_ascending = True
        self.sort_column = column_name
        self.selected_df = self.selected_df.sort_values(by=column_name, ascending=self.sort_ascending)
        self.current_page = 0 # Reset to first page after sorting
        self.update_table_display(is_interactive=True)

    def update_table_display(self, is_interactive=False):
        if self.table: self.table.destroy()
        
        self.displayed_df = self.selected_df
        
        if self.filter_switch_var.get() == "on" and self.selected_df is not None and 'Category' in self.selected_df.columns:
            self.displayed_df = self.selected_df[self.selected_df['Category'] == '']

        if self.displayed_df is not None and not self.displayed_df.empty:
            # --- PAGINATION LOGIC ---
            self.total_pages = math.ceil(len(self.displayed_df) / self.page_size)
            start_index = self.current_page * self.page_size
            end_index = start_index + self.page_size
            df_page = self.displayed_df.iloc[start_index:end_index]
            
            values = [df_page.columns.tolist()] + df_page.values.tolist()
            
            # Update pagination controls
            self.page_label.configure(text=f"Page {self.current_page + 1} of {self.total_pages}")
            self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
            self.next_button.configure(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        else:
            values = [["No data to display."]]
            self.page_label.configure(text="Page - of -")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

        table_command = self.table_row_selected if is_interactive else None
        self.table = CTkTable(self.table_container, values=values, header_color="#565B5E", corner_radius=8, command=table_command)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Other methods (analyze_data, table_row_selected, etc.) are mostly the same ---
    # ... (Copy the rest of the methods from the previous version) ...
    def analyze_data(self):
        if self.selected_df is None: return
        self.current_page = 0
        columns_to_show = ['Accounting date', 'Description', 'Amount', 'Category']
        self.selected_df['Category'] = ''
        self.selected_df = self.selected_df.reindex(columns=columns_to_show, fill_value='')

        for keyword, category in self.keywords_map.items():
            mask = self.selected_df['Description'].str.contains(keyword, case=False, na=False)
            self.selected_df.loc[mask, 'Category'] = category
        
        self.filter_switch.configure(state="normal")
        self.save_button.configure(state="normal")
        self.update_table_display(is_interactive=True)
        self.reset_control_panel()
        
        uncategorized_count = len(self.selected_df[self.selected_df['Category'] == ''])
        if uncategorized_count == 0:
            CTkMessagebox(title="Analysis Complete", message="All transactions have been successfully categorized!", icon="check")
        else:
             CTkMessagebox(title="Analysis Complete", message=f"Automatic categorization is complete. Found {uncategorized_count} items to review.", icon="info")

    def table_row_selected(self, event):
        selected_row_position = event['row']
        if selected_row_position == 0:
            column_name = self.table.get_value(row=0, column=event['column'])
            self.sort_table(column_name)
            return
        
        if self.displayed_df is None or self.displayed_df.empty: return

        try:
            # We need to calculate the original index based on the page
            start_index = self.current_page * self.page_size
            actual_position_in_displayed_df = start_index + (selected_row_position - 1)
            
            item_data = self.displayed_df.iloc[actual_position_in_displayed_df]
            self.currently_selected_row_index = item_data.name

            self.desc_label.configure(text=f"Editing: {item_data['Description']}")
            self.category_combobox.configure(state="readonly", values=self.categories_list)
            self.category_combobox.set(item_data['Category'] or "Select Category")
            self.update_button.configure(state="normal")
        except IndexError:
            print(f"IndexError: Clicked row {selected_row_position} is out of bounds for the current view.")

    def update_row_category(self):
        if self.currently_selected_row_index is None: return
        chosen_category = self.category_combobox.get()
        if not chosen_category or chosen_category == "Select Category":
            CTkMessagebox(title="Warning", message="Please select a valid category.", icon="warning")
            return
        item_description = self.selected_df.loc[self.currently_selected_row_index, 'Description']
        
        self.selected_df.loc[self.currently_selected_row_index, 'Category'] = chosen_category
        self.keywords_map[item_description] = chosen_category
        
        self.update_table_display(is_interactive=True)
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