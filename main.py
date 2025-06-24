import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import json
from CTkTable import CTkTable
from CTkMessagebox import CTkMessagebox

# --- Helper Functions (No changes here) ---
def load_keywords(filepath="keywords.json"):
    try:
        with open(filepath, 'r', encoding='utf-8') as file: return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def save_keywords(keywords, filepath="keywords.json"):
    with open(filepath, 'w', encoding='utf-8') as file: json.dump(keywords, file, indent=4, ensure_ascii=False)

def load_categories(filepath="categories_list.txt"):
    try:
        with open(filepath, 'r', encoding='utf-8') as file: return [line.strip() for line in file if line.strip()]
    except FileNotFoundError: return []

# --- Main Application Class ---
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
        
        # --- WIDGETS ---
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

        self.filter_switch_var = ctk.StringVar(value="off")
        self.filter_switch = ctk.CTkSwitch(self.bottom_frame, text="Show Uncategorized Only", command=self.filter_table, variable=self.filter_switch_var, onvalue="on", offvalue="off", state="disabled")
        self.filter_switch.pack(pady=5, padx=10, anchor="w")

        self.table_container = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True)
        self.table = None
        self.update_table_display()
        
    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel Files", "*.xlsx"),))
        if not filepath: return

        try:
            self.df = pd.read_excel(filepath, skiprows=7)
            self.selected_df = self.df.copy()
            
            # --- UPDATED STATE CONTROL ---
            self.update_table_display(is_interactive=False) # Display raw data, not interactive
            self.analyze_button.configure(state="normal") # Enable analyze button
            self.save_button.configure(state="disabled") # Ensure save is disabled
            self.filter_switch.configure(state="disabled") # Ensure filter is disabled
            self.reset_control_panel()
            print("File loaded successfully. Ready to analyze.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load file:\n{e}", icon="cancel")

    def analyze_data(self):
        if self.selected_df is None: return
        print("Analyzing data...")
        # ... (Analysis logic is the same) ...
        columns_to_show = ['Accounting date', 'Description', 'Amount', 'Category']
        self.selected_df['Category'] = ''
        self.selected_df = self.selected_df.reindex(columns=columns_to_show)
        for keyword, category in self.keywords_map.items():
            mask = self.selected_df['Description'].str.contains(keyword, case=False, na=False)
            self.selected_df.loc[mask, 'Category'] = category
        
        # --- UPDATED STATE CONTROL ---
        self.update_table_display(is_interactive=True) # Now table is interactive
        self.save_button.configure(state="normal") # Enable saving
        self.filter_switch.configure(state="normal") # Enable filtering
        self.reset_control_panel() # Reset control panel text
        
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
            item_data = self.displayed_df.iloc[selected_row_position - 1]
            self.currently_selected_row_index = item_data.name
            self.desc_label.configure(text=f"Editing: {item_data['Description']}")
            self.category_combobox.configure(state="readonly", values=self.categories_list)
            self.category_combobox.set(item_data['Category'] or "Select Category")
            self.update_button.configure(state="normal")
        except IndexError:
            print(f"IndexError: Clicked row {selected_row_position} is out of bounds for the current view.")

    def sort_table(self, column_name):
        if self.selected_df is None: return
        if self.sort_column == column_name: self.sort_ascending = not self.sort_ascending
        else: self.sort_ascending = True
        self.sort_column = column_name
        self.selected_df = self.selected_df.sort_values(by=column_name, ascending=self.sort_ascending)
        self.update_table_display(is_interactive=True)

    def filter_table(self):
        self.update_table_display(is_interactive=True)

    def update_table_display(self, is_interactive=False):
        if self.table: self.table.destroy()
        
        self.displayed_df = self.selected_df
        if self.filter_switch_var.get() == "on" and self.selected_df is not None and 'Category' in self.selected_df.columns:
            self.displayed_df = self.selected_df[self.selected_df['Category'] == '']

        if self.displayed_df is not None and not self.displayed_df.empty:
            values = [self.displayed_df.columns.tolist()] + self.displayed_df.values.tolist()
            # Link the click command only if the table is interactive
            table_command = self.table_row_selected if is_interactive else None
            self.table = CTkTable(self.table_container, values=values, header_color="#565B5E", corner_radius=8, command=table_command)
        else:
            values = [["Load a file to see data"]]
            self.table = CTkTable(self.table_container, values=values, header_color="#565B5E", corner_radius=8)
        
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

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