# new file: gui/frames/filter_frame.py
import customtkinter as ctk


class FilterFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller

        self.grid_columnconfigure(3, weight=1)

        # --- Category Filter ---
        ctk.CTkLabel(self, text="Filter Category:").grid(
            row=0, column=0, padx=(10, 5), pady=10
        )
        self.category_filter_box = ctk.CTkComboBox(
            self,
            values=self.controller.categories_for_filter,
            command=lambda value: self.controller.apply_filters(),
            state="disabled",
        )
        self.category_filter_box.grid(row=0, column=1, padx=5, pady=10)

        # --- Search Filter ---
        ctk.CTkLabel(self, text="Search Desc:").grid(
            row=0, column=2, padx=(20, 5), pady=10
        )
        self.search_entry = ctk.CTkEntry(
            self, placeholder_text="Type to search...", state="disabled"
        )
        self.search_entry.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.search_entry.bind(
            "<KeyRelease>", lambda event: self.controller.apply_filters(event)
        )

        self.clear_button = ctk.CTkButton(
            self,
            text="Clear Filters",
            command=lambda: self.controller.clear_filters(),
            state="disabled",
        )
        self.clear_button.grid(row=0, column=4, padx=(5, 10), pady=10)

        self.value_filter_box = ctk.CTkComboBox(
            self,
            values=["All", "Positive", "Negative"],
            command=lambda value: self.controller.apply_filters(),
            state="readonly",
        )
        self.value_filter_box.set("All")
        self.value_filter_box.grid(row=0, column=5, padx=(5, 10), pady=10)
