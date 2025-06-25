# file: gui/frames/top_actions_frame.py
import customtkinter as ctk

class TopActionsFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        
        self.controller = controller

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # --- THE FIX IS HERE: We wrap each command in a lambda ---
        
        self.load_button = ctk.CTkButton(self, text="1. Load File", command=lambda: self.controller.load_file())
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.analyze_button = ctk.CTkButton(self, text="2. Analyze", command=lambda: self.controller.analyze_data(), state="disabled")
        self.analyze_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.save_button = ctk.CTkButton(self, text="3. Save Keywords", command=lambda: self.controller.save_learned_keywords(), state="disabled")
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.export_button = ctk.CTkButton(self, text="4. Export Excel", command=lambda: self.controller.export_to_excel(), state="disabled")
        self.export_button.grid(row=0, column=3, padx=5, pady=5)