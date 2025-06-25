import logging
import sys
import traceback
from gui.app_ui import App

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """Main application entry point with error handling."""
    try:
        logging.info("Starting Finance Analyzer application")
        
        # Create an instance of our main application window.
        app = App()
        
        logging.info("Application window created successfully")
        
        # Start the GUI event loop.
        app.mainloop()
        
        logging.info("Application closed successfully")
        
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Show error message to user
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Application failed to start:\n{str(e)}")
        except:
            print(f"Error: {e}")
            input("Press Enter to exit...")

# This condition checks if the script is executed directly.
if __name__ == "__main__":
    main()