# new file: gui/frames/summary_panel.py
import customtkinter as ctk
from tkinter import ttk


class SummaryPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title for the panel
        self.title_label = ctk.CTkLabel(
            self, text="Category Summary", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=10)

        # Container for the treeview itself
        tree_container = ctk.CTkFrame(self, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Create the treeview for the summary
        self.summary_tree = self.create_treeview_in_frame(tree_container)

    def create_treeview_in_frame(self, parent_frame):
        # We include the style here so this component is self-contained
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Summary.Treeview",
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            borderwidth=0,
            rowheight=25,
        )
        style.map("Summary.Treeview", background=[("selected", "#22559b")])
        style.configure(
            "Summary.Treeview.Heading",
            background="#565B5E",
            foreground="white",
            relief="flat",
            font=("Calibri", 10, "bold"),
        )
        style.map("Summary.Treeview.Heading", background=[("active", "#3484F0")])

        tree = ttk.Treeview(parent_frame, show="headings", style="Summary.Treeview")
        tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(parent_frame, command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.tag_configure("oddrow", background="#343638")
        tree.tag_configure("evenrow", background="#2a2d2e")

        return tree
