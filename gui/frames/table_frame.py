# new file: gui/frames/table_frame.py
import customtkinter as ctk
from tkinter import ttk


class TableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Style for the Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            borderwidth=0,
            rowheight=25,
        )
        style.map("Treeview", background=[("selected", "#22559b")])
        style.configure(
            "Treeview.Heading",
            background="#565B5E",
            foreground="white",
            relief="flat",
            font=("Calibri", 10, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", "#3484F0")])

        # Create the Treeview widget
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Add tags for row colors
        self.tree.tag_configure("oddrow", background="#343638")
        self.tree.tag_configure("evenrow", background="#2a2d2e")

        # Add a scrollbar
        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
