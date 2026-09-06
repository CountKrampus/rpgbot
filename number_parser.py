"""
Parse human-friendly number formats
300k -> 300000
350k -> 350000
1m -> 1000000
2.5m -> 2500000
1b -> 1000000000
"""

import re

class NumberParser:
    """Convert human-friendly numbers to integers"""
    
    MULTIPLIERS = {
        'k': 1_000,
        'm': 1_000_000,
        'b': 1_000_000_000,
        't': 1_000_000_000_000,
    }
    
    @staticmethod
    def parse(value):
        """
        Parse number from string.
        
        Examples:
            "300000" -> 300000
            "300k" -> 300000
            "1.5k" -> 1500
            "2m" -> 2000000
            "1.2m" -> 1200000
            "5b" -> 5000000000
        
        Args:
            value: String representation of number
        
        Returns:
            Integer, or None if invalid
        """
        if value is None:
            return None
        
        # Convert to string and strip whitespace
        value = str(value).strip().lower()
        
        if not value:
            return None
        
        # If it's just a number, parse directly
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try to parse with suffix (k, m, b, t)
        match = re.match(r'^([\d.]+)\s*([kmbt])$', value)
        if match:
            number_str, suffix = match.groups()
            
            try:
                number = float(number_str)
                multiplier = NumberParser.MULTIPLIERS.get(suffix, 1)
                result = int(number * multiplier)
                return result
            except (ValueError, KeyError):
                return None
        
        # Invalid format
        return None
    
    @staticmethod
    def format_number(number):
        """
        Format large numbers in human-readable format.
        
        Examples:
            300000 -> "300k"
            1500000 -> "1.5m"
            5000000000 -> "5b"
        """
        if number is None:
            return "0"
        
        number = int(number)
        
        for suffix, multiplier in sorted(NumberParser.MULTIPLIERS.items(), 
                                         key=lambda x: x[1], reverse=True):
            if abs(number) >= multiplier:
                value = number / multiplier
                # Remove decimal if it's .0
                if value == int(value):
                    return f"{int(value)}{suffix}"
                else:
                    return f"{value:.1f}{suffix}"
        
        return str(number)
    
    @staticmethod
    def validate_input(prompt, min_val=0, max_val=None):
        """
        Get user input with number parsing.
        
        Args:
            prompt: Input prompt text
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            Parsed integer, or None if cancelled
        """
        while True:
            user_input = input(prompt).strip()
            
            if user_input.lower() in ['q', 'quit', 'cancel', 'exit']:
                return None
            
            parsed = NumberParser.parse(user_input)
            
            if parsed is None:
                print(f"  ❌ Invalid input. Use format: 300000 or 300k or 1.5m")
                continue
            
            if parsed < min_val:
                print(f"  ❌ Value must be at least {NumberParser.format_number(min_val)}")
                continue
            
            if max_val is not None and parsed > max_val:
                print(f"  ❌ Value cannot exceed {NumberParser.format_number(max_val)}")
                continue
            
            # Confirm large numbers
            if parsed >= 1_000_000:
                formatted = NumberParser.format_number(parsed)
                confirm = input(f"  Confirm: {formatted}? (y/n): ").strip().lower()
                if confirm == 'y':
                    return parsed
                else:
                    continue
            
            return parsed

# Test the parser
if __name__ == "__main__":
    test_cases = [
        ("300000", 300000),
        ("300k", 300000),
        ("1.5k", 1500),
        ("2m", 2000000),
        ("1.2m", 1200000),
        ("5b", 5000000000),
        ("1", 1),
        ("invalid", None),
    ]
    
    print("Testing NumberParser:")
    for input_val, expected in test_cases:
        result = NumberParser.parse(input_val)
        status = "✅" if result == expected else "❌"
        print(f"  {status} parse('{input_val}') = {result} (expected {expected})")
    
    print("\nTesting format_number:")
    format_tests = [
        (300000, "300k"),
        (1500000, "1.5m"),
        (5000000000, "5b"),
    ]
    for number, expected in format_tests:
        result = NumberParser.format_number(number)
        status = "✅" if result == expected else "❌"
        print(f"  {status} format_number({number}) = {result} (expected {expected})")
