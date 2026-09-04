"""
Headless Mode - Test bot framework without browser

Useful for testing on mobile or when no browser is available.
"""


class HeadlessDriver:
    """Mock WebDriver for testing without browser."""

    def __init__(self, instance_name):
        self.instance_name = instance_name
        self.current_url = "about:blank"
        self.title = "Headless Mode"
        self.closed = False

    def get(self, url):
        """Navigate to URL (simulated)."""
        self.current_url = url
        print(f"  [HEADLESS] Would navigate to: {url}")
        return True

    def find_element(self, by, value):
        """Find element (simulated)."""
        print(f"  [HEADLESS] Would find element by {by}: {value}")
        return MockElement(value)

    def execute_script(self, script, *args):
        """Execute JavaScript (simulated)."""
        print(f"  [HEADLESS] Would execute: {script[:50]}...")
        return "test_result"

    def quit(self):
        """Close driver."""
        self.closed = True
        print(f"  [HEADLESS] Driver closed")

    def set_page_load_timeout(self, timeout):
        """Set timeout (simulated)."""
        pass


class MockElement:
    """Mock WebElement for testing."""

    def __init__(self, name):
        self.name = name

    def click(self):
        """Click element (simulated)."""
        print(f"  [HEADLESS] Would click: {self.name}")

    def send_keys(self, text):
        """Type text (simulated)."""
        print(f"  [HEADLESS] Would type: {text}")

    def get_attribute(self, attr):
        """Get attribute (simulated)."""
        return f"mock_{attr}"

    @property
    def text(self):
        """Get element text (simulated)."""
        return f"Mock text from {self.name}"


def create_headless_driver(instance_name):
    """Create headless driver for testing."""
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           HEADLESS MODE - NO BROWSER REQUIRED                 ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Account: {instance_name}")
    print("  Status: Testing framework without browser")
    print("  Browser actions will be simulated")
    print()

    return HeadlessDriver(instance_name)

