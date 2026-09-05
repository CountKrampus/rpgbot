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
        self.form_data = {}  # Track form fields
        
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
            
            # Extract CSRF token and other hidden fields
            token_input = soup.find('input', {'name': 'token'})
            if token_input:
                token_value = token_input.get('value')
                if token_value:
                    self.form_data['token'] = token_value
                    print(f"  [HTTP] Extracted CSRF token")
            
            submit_input = soup.find('input', {'name': 'L_Submit'})
            if submit_input:
                submit_value = submit_input.get('value', '1')
                self.form_data['L_Submit'] = submit_value
                print(f"  [HTTP] Extracted L_Submit={submit_value}")
            
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
                mock_elem = MockElement(element, self.session)
                mock_elem._driver = self  # Pass driver reference for navigation
                return mock_elem
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
            return "complete"
        if "return document.title" in script:
            return self.title
        if "return window.location" in script:
            return {"href": self.current_url}
        
        # Handle click simulation
        if "arguments[0].click()" in script or "click();" in script:
            print(f"  [JS] Click detected")
            # Check if we have form data to submit
            if self.form_data:
                print(f"  [JS] Submitting form with data: {list(self.form_data.keys())}")
                try:
                    # POST to login endpoint
                    response = self.session.post(
                        "https://eclipserpg.com/login",
                        data=self.form_data,
                        timeout=10
                    )
                    self.current_url = response.url
                    self.html_content = response.text
                    
                    # Update title
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('title')
                    self.title = title_tag.text if title_tag else "No Title"
                    
                    print(f"  [JS] Form submitted (Status: {response.status_code}, URL: {response.url})")
                    self.form_data = {}  # Clear form data
                    return True
                except Exception as e:
                    print(f"  [JS] Form submission failed: {e}")
                    return True
            else:
                # No form data, just navigate to login
                print(f"  [JS] No form data, navigating to login page")
                try:
                    login_url = "https://eclipserpg.com/login"
                    response = self.session.get(login_url, timeout=10)
                    self.current_url = login_url
                    self.html_content = response.text
                    
                    # Update title
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('title')
                    self.title = title_tag.text if title_tag else "No Title"
                    
                    # Extract CSRF token
                    token_input = soup.find('input', {'name': 'token'})
                    if token_input:
                        token_value = token_input.get('value')
                        if token_value:
                            self.form_data['token'] = token_value
                            print(f"  [JS] Extracted CSRF token")
                    
                    submit_input = soup.find('input', {'name': 'L_Submit'})
                    if submit_input:
                        submit_value = submit_input.get('value', '1')
                        self.form_data['L_Submit'] = submit_value
                        print(f"  [JS] Extracted L_Submit={submit_value}")
                    
                    print(f"  [JS] Navigated to login page (Status: {response.status_code})")
                    return True
                except Exception as e:
                    print(f"  [JS] Navigation failed: {e}")
                    return True
        
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

    @property
    def page_source(self):
        """Get current page HTML source."""
        return self.html_content


class MockElement:
    """Real HTML element from BeautifulSoup."""

    def __init__(self, element, session):
        self.element = element
        self.session = session

    def click(self):
        """Click element (follow link if available)."""
        href = self.element.get('href')
        if href:
            print(f"  [CLICK] Following link: {href}")
            # Navigate using the session
            try:
                from urllib.parse import urljoin
                full_url = urljoin(self._driver.current_url, href)
                response = self._driver.session.get(full_url, timeout=10)
                self._driver.current_url = full_url
                self._driver.html_content = response.text
                
                # Update title
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('title')
                self._driver.title = title_tag.text if title_tag else "No Title"
                
                print(f"  [CLICK] Navigated (Status: {response.status_code})")
                return True
            except Exception as e:
                print(f"  [CLICK] Navigation failed: {str(e)[:50]}")
                return False
        print(f"  [CLICK] Element has no link")
        return False

    def send_keys(self, text):
        """Type text (simulate form input)."""
        print(f"  [TYPE] Would type: {text}")
        # Track form data
        input_name = self.element.get('name') or self.element.get('id')
        if input_name and hasattr(self, '_driver'):
            self._driver.form_data[input_name] = text
        return True

    def get_attribute(self, attr):
        """Get element attribute."""
        value = self.element.get(attr)
        print(f"  [ATTR] {attr}={value}")
        return value

    def is_displayed(self):
        """Check if element is displayed."""
        return True

    def is_enabled(self):
        """Check if element is enabled."""
        return True

    def submit(self):
        """Submit form."""
        print(f"  [SUBMIT] Would submit form")
        return True

    def clear(self):
        """Clear element value."""
        print(f"  [CLEAR] Would clear element")
        return True

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

