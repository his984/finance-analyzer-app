# new file: gui/frames/bottom_frame.py
import customtkinter as ctk


class BottomFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.grid_columnconfigure(1, weight=1)

        # --- Edit Controls ---
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(self.control_frame, text="Edit Selected:").pack(
            side="left", padx=(10, 5)
        )

        self.category_edit_box = ctk.CTkComboBox(
            self.control_frame,
            values=self.controller.categories_for_edit,
            state="disabled",
        )
        self.category_edit_box.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(
            self.control_frame,
            text="Update",
            command=lambda: self.controller.update_row_category(),
            state="disabled",
        )
        self.update_button.pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(
            self.control_frame,
            text="Delete",
            command=lambda: self.controller.delete_selected_row(),
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
