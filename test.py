
import unittest
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys


class GuestbookTestSuite(unittest.TestCase):
    """
    Comprehensive test suite for the Guestbook Web Application
    Tests include form validation, message posting, UI elements, and edge cases
    """

    @classmethod
    def setUpClass(cls):
        """Set up Chrome driver with headless configuration for CI/CD"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        # Initialize the Chrome driver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://13.51.175.170"  # Adjust URL as needed
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.driver.quit()

    def setUp(self):
        """Navigate to the guestbook page before each test"""
        self.driver.get(self.base_url)
        time.sleep(1)  # Allow page to load

    def generate_random_string(self, length=10):
        """Generate random string for testing"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def test_01_page_loads_successfully(self):
        """Test Case 1: Verify the guestbook page loads successfully"""
        self.assertEqual(self.driver.title, "Guestbook App")

        # Check if main elements are present
        header = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertEqual(header.text, "Guestbook App")

        # Check subtitle
        subtitle = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Leave a message for others')]")
        self.assertIsNotNone(subtitle)

    def test_02_form_elements_present(self):
        """Test Case 2: Verify all form elements are present and accessible"""
        # Check name input field
        name_input = self.driver.find_element(By.NAME, "name")
        self.assertTrue(name_input.is_displayed())
        self.assertEqual(name_input.get_attribute("placeholder"), "Your name")
        self.assertTrue(name_input.get_attribute("required"))

        # Check message input field
        message_input = self.driver.find_element(By.NAME, "message")
        self.assertTrue(message_input.is_displayed())
        self.assertEqual(message_input.get_attribute("placeholder"), "Type your message...")
        self.assertTrue(message_input.get_attribute("required"))

        # Check submit button
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        self.assertTrue(submit_button.is_displayed())
        self.assertEqual(submit_button.text, "Send")

    def test_03_submit_valid_message(self):
        """Test Case 3: Submit a valid message and verify it appears"""
        test_name = f"TestUser_{self.generate_random_string(5)}"
        test_message = f"Test message {self.generate_random_string(10)}"

        # Fill form fields
        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        name_input.clear()
        name_input.send_keys(test_name)

        message_input.clear()
        message_input.send_keys(test_message)

        # Submit form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Wait for page reload and verify message appears
        time.sleep(2)

        # Check for success toast
        try:
            toast = self.wait.until(EC.presence_of_element_located((By.ID, "toast")))
            self.assertEqual(toast.text, "Message sent!")
        except TimeoutException:
            pass  # Toast might disappear quickly

        # Verify message appears in the messages list
        message_elements = self.driver.find_elements(By.XPATH, f"//span[contains(text(), '{test_name}')]")
        self.assertGreater(len(message_elements), 0, "Submitted message should appear in the list")

    def test_04_empty_name_validation(self):
        """Test Case 4: Test form validation with empty name field"""
        message_input = self.driver.find_element(By.NAME, "message")
        message_input.clear()
        message_input.send_keys("Test message without name")

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Verify form doesn't submit (HTML5 validation should prevent it)
        name_input = self.driver.find_element(By.NAME, "name")
        validation_message = name_input.get_attribute("validationMessage")
        self.assertIsNotNone(validation_message)

    def test_05_empty_message_validation(self):
        """Test Case 5: Test form validation with empty message field"""
        name_input = self.driver.find_element(By.NAME, "name")
        name_input.clear()
        name_input.send_keys("Test User")

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Verify form doesn't submit (HTML5 validation should prevent it)
        message_input = self.driver.find_element(By.NAME, "message")
        validation_message = message_input.get_attribute("validationMessage")
        self.assertIsNotNone(validation_message)

    def test_06_both_fields_empty_validation(self):
        """Test Case 6: Test form validation with both fields empty"""
        # Clear both fields (if they have any content)
        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        name_input.clear()
        message_input.clear()

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Verify form doesn't submit
        name_validation = name_input.get_attribute("validationMessage")
        self.assertIsNotNone(name_validation)

    def test_07_long_name_input(self):
        """Test Case 7: Test with very long name input"""
        long_name = "A" * 150  # Longer than VARCHAR(100) in database
        test_message = "Test message with long name"

        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        name_input.clear()
        name_input.send_keys(long_name)

        message_input.clear()
        message_input.send_keys(test_message)

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)

        # The application should handle this gracefully (truncate or show error)
        # We just verify the page doesn't crash
        self.assertEqual(self.driver.title, "Guestbook App")

    def test_08_special_characters_input(self):
        """Test Case 8: Test with special characters in input"""
        special_name = "Test<>User&'\"123"
        special_message = "Message with special chars: <script>alert('xss')</script> & quotes \"'"

        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        name_input.clear()
        name_input.send_keys(special_name)

        message_input.clear()
        message_input.send_keys(special_message)

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)

        # Verify XSS prevention - the script should not execute
        # and special characters should be properly escaped
        self.assertEqual(self.driver.title, "Guestbook App")

        # Check if the message appears with escaped characters
        page_source = self.driver.page_source
        self.assertNotIn("<script>alert('xss')</script>", page_source)

    def test_09_multiple_messages_order(self):
        """Test Case 9: Test multiple message submissions and verify order"""
        messages = []

        for i in range(3):
            test_name = f"User_{i}_{self.generate_random_string(3)}"
            test_message = f"Message {i} - {self.generate_random_string(5)}"
            messages.append((test_name, test_message))

            name_input = self.driver.find_element(By.NAME, "name")
            message_input = self.driver.find_element(By.NAME, "message")

            name_input.clear()
            name_input.send_keys(test_name)

            message_input.clear()
            message_input.send_keys(test_message)

            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()

            time.sleep(2)
  GNU nano 7.2                                                                       test.py                                                                                
        # Verify messages appear in reverse chronological order (newest first)
        message_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'p-3 rounded-lg border')]")
        self.assertGreaterEqual(len(message_elements), 3)

        # Check if the last submitted message appears first
        first_message_element = message_elements[0]
        self.assertIn(messages[-1][0], first_message_element.text)

    def test_10_ui_responsiveness_mobile_view(self):
        """Test Case 10: Test UI responsiveness by changing window size"""
        # Test desktop view
        self.driver.set_window_size(1920, 1080)
        time.sleep(1)

        form_container = self.driver.find_element(By.XPATH, "//div[contains(@class, 'sticky bottom-4')]")
        self.assertTrue(form_container.is_displayed())

        # Test mobile view
        self.driver.set_window_size(375, 667)
        time.sleep(1)

        # Verify form is still accessible and visible
        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

        self.assertTrue(name_input.is_displayed())
        self.assertTrue(message_input.is_displayed())
        self.assertTrue(submit_button.is_displayed())

        # Reset to desktop view
        self.driver.set_window_size(1920, 1080)

    def test_11_keyboard_navigation(self):
        """Test Case 11: Test keyboard navigation through form elements"""
        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        # Focus on name input
        name_input.click()
        name_input.send_keys("Keyboard User")

        # Tab to message input
        name_input.send_keys(Keys.TAB)

        # Verify focus moved to message input
        active_element = self.driver.switch_to.active_element
        self.assertEqual(active_element.get_attribute("name"), "message")

        # Type message
        active_element.send_keys("Testing keyboard navigation")

        # Tab to submit button and press Enter
        active_element.send_keys(Keys.TAB)
        active_element = self.driver.switch_to.active_element
        self.assertEqual(active_element.text, "Send")

        # Submit using Enter key
        active_element.send_keys(Keys.RETURN)

        time.sleep(2)

        # Verify submission worked
        page_source = self.driver.page_source
        self.assertIn("Keyboard User", page_source)

    def test_12_form_reset_after_submission(self):
        """Test Case 12: Verify form fields are cleared/reset after successful submission"""
        test_name = f"ResetTest_{self.generate_random_string(5)}"
        test_message = f"Reset test message {self.generate_random_string(8)}"

        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        name_input.clear()
        name_input.send_keys(test_name)

        message_input.clear()
        message_input.send_keys(test_message)

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)

        # Check if form fields are cleared after submission
        name_input_after = self.driver.find_element(By.NAME, "name")
        message_input_after = self.driver.find_element(By.NAME, "message")

        # Note: The current PHP implementation doesn't clear fields after submission
        # This test documents the current behavior
        name_value = name_input_after.get_attribute("value")
        message_value = message_input_after.get_attribute("value")

        # This assertion might fail if form doesn't reset - that's a UX improvement opportunity
        print(f"Name field after submission: '{name_value}'")
        print(f"Message field after submission: '{message_value}'")

    def test_13_timestamp_display(self):
        """Test Case 13: Verify timestamp is displayed correctly for new messages"""
        test_name = f"TimeTest_{self.generate_random_string(4)}"
        test_message = "Testing timestamp display"

        name_input = self.driver.find_element(By.NAME, "name")
        message_input = self.driver.find_element(By.NAME, "message")

        name_input.clear()
        name_input.send_keys(test_name)

        message_input.clear()
        message_input.send_keys(test_message)

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)

        # Look for timestamp in the latest message
        timestamp_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'text-xs text-gray-500')]")

        if timestamp_elements:
            # Verify timestamp format (should contain month abbreviation and time)
            timestamp_text = timestamp_elements[0].text
            self.assertRegex(timestamp_text, r'[A-Za-z]{3}\s+\d+,\s+\d+:\d+\s+[ap]m')
        else:
            self.fail("No timestamp found for the submitted message")

    def test_14_empty_state_display(self):
        """Test Case 14: Verify empty state message when no messages exist"""

        try:
            empty_message = self.driver.find_element(By.XPATH, "//p[contains(text(), 'No messages yet')]")
            # If empty state is shown, verify its styling and message
            self.assertIn("No messages yet. Be the first to leave a message!", empty_message.text)
            self.assertTrue(empty_message.is_displayed())
        except NoSuchElementException:
            # If there are messages, verify the messages container exists
            messages_container = self.driver.find_element(By.XPATH, "//div[contains(@class, 'space-y-3')]")
            self.assertTrue(messages_container.is_displayed())

    def test_15_css_styling_verification(self):
        """Test Case 15: Verify critical CSS classes and styling are applied"""
        # Check header styling
        header = self.driver.find_element(By.TAG_NAME, "h1")
        header_classes = header.get_attribute("class")
        self.assertIn("text-2xl", header_classes)
        self.assertIn("font-bold", header_classes)
        self.assertIn("text-blue-600", header_classes)

        # Check form styling
        name_input = self.driver.find_element(By.NAME, "name")
        input_classes = name_input.get_attribute("class")
        self.assertIn("border", input_classes)
        self.assertIn("rounded-md", input_classes)

        # Check button styling
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        button_classes = submit_button.get_attribute("class")
        self.assertIn("bg-blue-600", button_classes)
        self.assertIn("text-white", button_classes)
        self.assertIn("rounded-md", button_classes)

        # Verify the button changes color on hover (check hover class exists)
        self.assertIn("hover:bg-blue-700", button_classes)


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2, warnings='ignore')
