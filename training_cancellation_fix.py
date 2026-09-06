"""
Training cancellation fix - checks for cancellation more frequently
Add these checks to training.py
"""

# Add to imports:
# from immediate_cancel import is_immediate_cancel_requested

# Replace wait_for_battle_to_finish with this version that checks cancellation:

def wait_for_battle_to_finish_with_cancel(driver, timeout_seconds=60):
    """
    Wait for battle to finish, with cancellation check
    """
    from immediate_cancel import is_immediate_cancel_requested
    
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        # ✅ CHECK CANCELLATION FREQUENTLY
        if is_immediate_cancel_requested():
            print("\n  ⚠️  Cancel requested - stopping battle wait")
            return "cancelled"
        
        # Check if battle finished
        try:
            button = get_battle_button(driver)
            if button and battle_has_ended(driver):
                return "success"
        except:
            pass
        
        time.sleep(0.5)
    
    return None

# Also add cancellation checks in the main loop:

def train(
    driver,
    account_name,
    max_battles=None,
    duration_seconds=None,
    difficulty_level=None,
):
    """
    Train with improved cancellation handling
    """
    from immediate_cancel import is_immediate_cancel_requested, reset_immediate_cancel
    
    reset_immediate_cancel()  # Clear any previous cancel
    
    cancelled = False
    battles_completed = 0
    total_exp_gained = 0
    
    while battles_completed < max_battles:
        # ✅ CHECK CANCELLATION AT START OF LOOP
        if is_immediate_cancel_requested():
            print("\n⚠️  TRAINING STOPPED BY USER")
            cancelled = True
            break
        
        # Start battle
        battle_result = wait_for_battle_to_finish_with_cancel(driver)
        
        # ✅ CHECK IF CANCELLED DURING BATTLE
        if battle_result == "cancelled":
            print("\n⚠️  TRAINING STOPPED BY USER (during battle)")
            cancelled = True
            break
        
        # Rest of battle handling...
        battles_completed += 1
        
        # ✅ CHECK AFTER EACH BATTLE
        if is_immediate_cancel_requested():
            print("\n⚠️  TRAINING STOPPED BY USER (after battle)")
            cancelled = True
            break
    
    return cancelled, battles_completed, total_exp_gained

# Usage in main training function:
"""
Instead of:
    if is_cancel_requested():
        print("Training cancelled. Finishing the current result summary.")
        cancelled = True
        break

Use:
    if is_immediate_cancel_requested():
        print("\\n⚠️  TRAINING STOPPED IMMEDIATELY")
        cancelled = True
        break
"""
