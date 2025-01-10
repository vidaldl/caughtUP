import tkinter as tk
from backup_manager.token_manager import TokenManager
from gui.menu_bar import MenuBar

# Replace with your Canvas LMS base URL
BASE_URL = "https://byui.instructure.com:443"  

def test_menu_bar():
    # Initialize TokenManager with a test base URL
    token_manager = TokenManager(base_url=BASE_URL)

    # Create the main test window
    root = tk.Tk()
    root.title("Menu Bar Test")

    # Attach the MenuBar to the test window
    MenuBar(root, token_manager)

    # Run the Tkinter main loop
    root.geometry("400x300")
    root.mainloop()

if __name__ == "__main__":
    test_menu_bar()
