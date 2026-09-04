"""Small WebDriver-compatible simulator for framework and menu testing."""


class MockElement:
    def __init__(self, name):
        self.name = name
        self.clicked = False
        self.value = ""

    def click(self):
        self.clicked = True

    def send_keys(self, text):
        self.value += str(text)

    def clear(self):
        self.value = ""

    def get_attribute(self, name):
        if name == "value":
            return self.value
        return f"mock_{name}"

    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    @property
    def text(self):
        return f"Mock text from {self.name}"


class HeadlessDriver:
    """Deterministic browser double that records simulated interactions."""

    def __init__(self, instance_name):
        self.instance_name = instance_name
        self.current_url = "about:blank"
        self.title = "Headless Mode"
        self.page_source = "<html><body>Headless Mode</body></html>"
        self.closed = False
        self.actions = []

    def get(self, url):
        self.current_url = url
        self.actions.append(("get", url))

    def find_element(self, by, value):
        self.actions.append(("find_element", by, value))
        return MockElement(value)

    def find_elements(self, by, value):
        self.actions.append(("find_elements", by, value))
        return []

    def execute_script(self, script, *args):
        self.actions.append(("execute_script", script))
        if "document.readyState" in script:
            return "complete"
        return None

    def set_page_load_timeout(self, timeout):
        self.page_load_timeout = timeout

    def quit(self):
        self.closed = True


def create_headless_driver(instance_name):
    print("\n  HEADLESS MODE - browser actions will be simulated.")
    print(f"  Account: {instance_name}")
    return HeadlessDriver(instance_name)
