# new file: gui/frames/bottom_frame.py
import customtkinter as ctk
from config.constants import CATEGORY_SELECT


class BottomFrame(ctk.CTkFrame):
    """
    Frame for editing and summarizing selected data.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.main_app = master  # Reference to the main app

        self.grid_columnconfigure(1, weight=1)

        # --- Edit Controls ---
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(self.control_frame, text="Edit Selected:").pack(
            side="left", padx=(10, 5)
        )

        self.category_edit_box = ctk.CTkComboBox(
            self.control_frame,
            values=self.controller.get_categories(),
            state="disabled",
        )
        self.category_edit_box.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(
            self.control_frame,
            text="Update",
            command=lambda: self.main_app.update_row_category(),
            state="disabled",
        )
        self.update_button.pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(
            self.control_frame,
            text="Delete",
            command=lambda: self.main_app.delete_selected_row(),
            state="disabled",
            fg_color="#C0392B",
            hover_color="#E74C3C",
        )
        self.delete_button.pack(side="left", padx=5)

        # --- Overall Summary Labels ---
        self.overall_summary_frame = ctk.CTkFrame(self, fg_color="transparent")
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

    def update_row_category(self):
        if self.controller.currently_selected_row_index is None:
            return
        chosen_category = self.category_edit_box.get()
        if not chosen_category or chosen_category == CATEGORY_SELECT:
            return
