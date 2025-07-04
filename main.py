"""
Main entry point for the Finance Analyzer application.
Handles application startup and error reporting.
"""
from gui.app_ui import App


def main():
    """Start the Finance Analyzer GUI application and handle startup errors."""
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Application failed to start:\n{str(e)}")
        except Exception:
            print(f"Error: {e}")
            input("Press Enter to exit...")


if __name__ == "__main__":
    main()
