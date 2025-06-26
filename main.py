import sys
import traceback
from gui.app_ui import App

def main():
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Application failed to start:\n{str(e)}")
        except:
            print(f"Error: {e}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()