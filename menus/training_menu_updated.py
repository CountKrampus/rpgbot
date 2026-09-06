"""
Updated training menu with number parser support
300k, 1.5m, 5b formats now work!
"""

from number_parser import NumberParser

def get_training_target():
    """Get training target from user with number parsing"""
    print("\n" + "="*60)
    print("  TRAINING TARGET")
    print("="*60)
    print("  Enter number of battles to train")
    print("  Formats: 300000, 300k, 1.5m, 5b")
    print("  (Type 'q' to cancel)")
    print("="*60)
    
    result = NumberParser.validate_input("\n  Enter battles: ", min_val=1000)
    return result

def get_searching_target():
    """Get searching target from user"""
    print("\n" + "="*60)
    print("  SEARCHING TARGET")
    print("="*60)
    print("  Enter number of searches to perform")
    print("  Formats: 100000, 100k, 1m, 2.5m")
    print("="*60)
    
    result = NumberParser.validate_input("\n  Enter searches: ", min_val=100)
    return result

def get_mining_target():
    """Get mining target from user"""
    print("\n" + "="*60)
    print("  MINING TARGET")
    print("="*60)
    print("  Enter number of mines to perform")
    print("  Formats: 50000, 50k, 500k, 1m")
    print("="*60)
    
    result = NumberParser.validate_input("\n  Enter mines: ", min_val=100)
    return result

# Example usage in main menu:
def show_automation_menu():
    """Show automation options"""
    print("\n" + "="*60)
    print("  AUTOMATION")
    print("="*60)
    print("  [1] Training (battles)")
    print("  [2] Searching (items)")
    print("  [3] Mining (ore)")
    print("  [0] Back")
    
    choice = input("\n  Select: ").strip()
    
    if choice == "1":
        target = get_training_target()
        if target:
            print(f"\n  ✅ Training {NumberParser.format_number(target)} battles")
            # Run training...
    
    elif choice == "2":
        target = get_searching_target()
        if target:
            print(f"\n  ✅ Searching {NumberParser.format_number(target)} times")
            # Run searching...
    
    elif choice == "3":
        target = get_mining_target()
        if target:
            print(f"\n  ✅ Mining {NumberParser.format_number(target)} times")
            # Run mining...

if __name__ == "__main__":
    show_automation_menu()
