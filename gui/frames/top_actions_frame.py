# file: gui/frames/top_actions_frame.py
import customtkinter as ctk
from tkinter import PhotoImage

class TopActionsFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Create a sub-frame for the main buttons, aligned left
        self.button_row = ctk.CTkFrame(self, fg_color="transparent")
        self.button_row.grid(row=0, column=0, sticky="w")  # Align left

        button_style = {
            "height": 36,
            "width": 160,
            "corner_radius": 8,
            "font": ctk.CTkFont(size=14, weight="bold"),
        }

        self.load_button = ctk.CTkButton(
            self.button_row, text="Load File", command=lambda: self.controller.load_file(), **button_style
        )
        self.load_button.pack(side="left", padx=(0, 4), pady=10)
        
        self.analyze_button = ctk.CTkButton(
            self.button_row, text="Analyze", command=lambda: self.controller.analyze_data(), state="disabled", **button_style
        )
        self.analyze_button.pack(side="left", padx=4, pady=10)
        
        self.save_button = ctk.CTkButton(
            self.button_row, text="Save Keywords", command=lambda: self.controller.save_learned_keywords(), state="disabled", **button_style
        )
        self.save_button.pack(side="left", padx=4, pady=10)
        
        self.export_button = ctk.CTkButton(
            self.button_row, text="Export Excel", command=lambda: self.controller.export_to_excel(), state="disabled", **button_style
        )
        self.export_button.pack(side="left", padx=(4, 0), pady=10)

        # Red close button with 'X' icon at the far right
        self.close_button = ctk.CTkButton(
            self,
            text="✕",  # Unicode X
            width=36,
            height=36,
            fg_color="#C0392B",
            hover_color="#E74C3C",
            text_color="white",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=18,
            command=master.quit,
        )
        self.close_button.grid(row=0, column=1, padx=(15, 20), pady=10, sticky="e")