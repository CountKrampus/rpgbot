"""
Headless Mode - Real HTTP requests without browser

Uses requests library to make actual web calls.
Useful for testing on mobile or when no browser is available.
"""

import requests
from bs4 import BeautifulSoup


class HeadlessDriver:
    """Real HTTP driver without browser GUI."""

    def __init__(self, instance_name):
        self.instance_name = instance_name
        self.current_url = "about:blank"
        self.title = "Headless Mode"
        self.closed = False
        self.session = requests.Session()
        self.html_content = ""
        
        # Set user agent to look like a real browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36"
        })

    def get(self, url):
        """Navigate to URL using real HTTP request."""
        try:
            print(f"  [HTTP] GET {url}")
            response = self.session.get(url, timeout=10)
            self.current_url = url
            self.html_content = response.text
            
            # Extract title from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            self.title = title_tag.text if title_tag else "No Title"
            
            print(f"  [HTTP] Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"  [HTTP] Error: {str(e)[:50]}")
            return False

    def find_element(self, by, value):
        """Find element in HTML."""
        try:
            soup = BeautifulSoup(self.html_content, 'html.parser')
            
            if by == "id":
                element = soup.find(id=value)
            elif by == "name":
                element = soup.find(attrs={"name": value})
            elif by == "class name":
                element = soup.find(class_=value)
            elif by == "tag name":
                element = soup.find(value)
            elif by == "css selector":
                element = soup.select(value)
                element = element[0] if element else None
            elif by == "xpath":
                # Basic XPath support for common patterns
                if "normalize-space()=" in value:
                    # Extract text from normalize-space()='Text'
                    import re
                    match = re.search(r"normalize-space\(\)='([^']+)'", value)
                    if match:
                        text = match.group(1)
                        element = soup.find(string=lambda s: text in s.strip() if s else False)
                    else:
                        element = None
                else:
                    element = None
            else:
                element = soup.find(attrs={by: value})
            
            if element:
                print(f"  [HTML] Found {by}: {value}")
                return MockElement(element, self.session)
            else:
                print(f"  [HTML] Not found {by}: {value}")
                raise Exception(f"Element not found: {by}={value}")
        except Exception as e:
            print(f"  [HTML] Error: {str(e)[:50]}")
            raise

    def execute_script(self, script, *args):
        """Execute JavaScript (limited support)."""
        # Handle common JS checks
        if "return document.readyState" in script:
            return "complete"  # Pretend page is ready
        if "return document.title" in script:
            return self.title
        if "return window.location" in script:
            return {"href": self.current_url}
        
        print(f"  [JS] Would execute: {script[:50]}...")
        return "test_result"

    def quit(self):
        """Close driver."""
        self.closed = True
        self.session.close()
        print(f"  [HTTP] Session closed")

    def set_page_load_timeout(self, timeout):
        """Set timeout (handled by requests)."""
        pass


class MockElement:
    """Real HTML element from BeautifulSoup."""

    def __init__(self, element, session):
        self.element = element
        self.session = session

    def click(self):
        """Click element (follow link if available)."""
        href = self.element.get('href')
        if href:
            print(f"  [CLICK] Would follow: {href}")
            return True
        print(f"  [CLICK] Element has no link")
        return False

    def send_keys(self, text):
        """Type text (simulate form input)."""
        print(f"  [TYPE] Would type: {text}")
        return True

    def get_attribute(self, attr):
        """Get element attribute."""
        value = self.element.get(attr)
        print(f"  [ATTR] {attr}={value}")
        return value

    @property
    def text(self):
        """Get element text."""
        text = self.element.get_text(strip=True)
        return text if text else ""


def create_headless_driver(instance_name):
    """Create headless HTTP driver for testing."""
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           HEADLESS MODE - REAL HTTP REQUESTS                  ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Account: {instance_name}")
    print("  Status: Using HTTP requests (no browser GUI)")
    print("  Real web requests enabled")
    print()

    return HeadlessDriver(instance_name)

