"""
Add Discord Notifications to settings menu
This should be inserted into menus/settings_menu.py

Find this section:
    _option("10", "Reset Settings")
    _option("11", "Export Settings")
    _option("12", "Import Settings")
    _option("13", "Back")

Replace with:
"""

# Add Discord Notifications option
def add_discord_option_to_menu():
    """Code to add to settings menu"""
    
    code = """
    _option("10", "Reset Settings")
    
    _option("11", "Discord Notifications")  # ← NEW
    
    _option("12", "Export Settings")
    
    _option("13", "Import Settings")
    
    _option("14", "Back")
    """
    
    # And in the choice handling, add:
    
    handler = """
    elif choice == "11":
        _show_discord_menu()  # ← NEW
    
    elif choice == "12":
        path = input(...)
        # Export code
    
    elif choice == "13":
        path = input(...)
        # Import code
    
    elif choice == "14":
        return
    """
    
    return code, handler

# Function to add to settings_menu.py
def _show_discord_menu():
    """Show Discord settings menu"""
    from discord_settings import show_discord_menu
    show_discord_menu()

