from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('swiggy_automation.log'),
        logging.StreamHandler()
    ]
)

class SwiggyAutomation:
    def _init_(self, phone_number="9391496810", headless=False):
        self.phone_number = phone_number
        self.driver = None
        self.wait = None
        self.setup_driver(headless)
        
    def setup_driver(self, headless=False):
        """Initialize Chrome WebDriver with optimized settings"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Add performance and stability options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Suppress Chrome logging
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--silent")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 15)
            logging.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def safe_click(self, element, method="click"):
        """Safely click an element with multiple fallback methods"""
        try:
            if method == "click":
                element.click()
            elif method == "js":
                self.driver.execute_script("arguments[0].click();", element)
            elif method == "action":
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(element).click().perform()
            return True
        except Exception as e:
            logging.warning(f"Click method '{method}' failed: {e}")
            return False
    
    def find_and_click(self, locators, description, timeout=10):
        """Find element using multiple locators and click with fallback methods"""
        for locator_type, locator_value in locators:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((locator_type, locator_value))
                )
                
                # Try multiple click methods
                for method in ["click", "js", "action"]:
                    if self.safe_click(element, method):
                        logging.info(f"Successfully clicked {description}")
                        return True
                        
            except TimeoutException:
                continue
            except Exception as e:
                logging.warning(f"Error with locator {locator_value}: {e}")
                continue
        
        logging.error(f"Failed to find and click {description}")
        return False
    
    def open_swiggy(self):
        """Open Swiggy homepage"""
        try:
            self.driver.get("https://www.swiggy.com/")
            logging.info("Opened Swiggy homepage")
            time.sleep(3)
            return True
        except Exception as e:
            logging.error(f"Failed to open Swiggy: {e}")
            return False
    
    def debug_current_state(self):
        """Debug current page state"""
        try:
            logging.info(f"Current URL: {self.driver.current_url}")
            logging.info(f"Page Title: {self.driver.title}")
            
            # Check for common elements
            elements_to_check = [
                ("OTP input", "//input[@type='tel' and @maxlength='6']"),
                ("OTP input", "//input[@placeholder*='OTP' or @placeholder*='otp']"),
                ("Verify button", "//button[contains(text(),'Verify')]"),
                ("Continue button", "//button[contains(text(),'Continue')]"),
                ("Login form", "//form"),
                ("Error message", "//*[contains(@class, 'error') or contains(text(), 'error')]")
            ]
            
            for element_name, xpath in elements_to_check:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        logging.info(f"Found {len(elements)} {element_name} element(s)")
                        for i, elem in enumerate(elements):
                            if elem.is_displayed():
                                logging.info(f"  {element_name} {i+1}: visible, enabled={elem.is_enabled()}")
                            else:
                                logging.info(f"  {element_name} {i+1}: hidden")
                except Exception as e:
                    logging.warning(f"Error checking {element_name}: {e}")
                    
        except Exception as e:
            logging.error(f"Debug failed: {e}")
    
    def handle_login(self):
        """Handle login process with improved OTP handling"""
        # Multiple possible login button locators
        login_locators = [
            (By.XPATH, "//a[contains(text(),'Sign in')]"),
            (By.XPATH, "//span[contains(text(),'Sign In')]"),
            (By.XPATH, "//div[contains(text(),'Sign in')]"),
            (By.XPATH, "//button[contains(text(),'Login')]"),
            (By.XPATH, "//*[contains(@class, 'login') or contains(@class, 'sign-in')]"),
            (By.CSS_SELECTOR, "[data-testid='login-cta']")
        ]
        
        if not self.find_and_click(login_locators, "login button"):
            logging.error("Could not find login button")
            return False
        
        time.sleep(3)
        
        # Enter phone number
        phone_locators = [
            (By.XPATH, "//input[@type='tel']"),
            (By.XPATH, "//input[@id='mobile']"),
            (By.XPATH, "//input[@placeholder*='mobile' or @placeholder*='phone']"),
            (By.CSS_SELECTOR, "input[type='tel']"),
            (By.XPATH, "//input[@name='mobile']")
        ]
        
        phone_input = None
        for locator_type, locator_value in phone_locators:
            try:
                phone_input = self.wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
                if phone_input.is_displayed():
                    break
            except TimeoutException:
                continue
        
        if not phone_input:
            logging.error("Phone input field not found")
            return False
        
        try:
            phone_input.clear()
            phone_input.send_keys(self.phone_number)
            logging.info(f"Entered phone number: {self.phone_number}")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Failed to enter phone number: {e}")
            return False
        
        # Click login/continue after phone
        login_after_phone_locators = [
            (By.XPATH, "//button[contains(text(),'Login') or contains(text(),'Continue') or contains(text(),'Send OTP')]"),
            (By.XPATH, "//a[contains(text(),'Login') or contains(text(),'Continue') or contains(text(),'Send OTP')]"),
            (By.CSS_SELECTOR, "[data-testid='login-cta']"),
            (By.XPATH, "//button[contains(@class, 'login') or contains(@class, 'continue')]")
        ]
        
        if not self.find_and_click(login_after_phone_locators, "login after phone"):
            logging.error("Could not find login/continue button after phone entry")
            return False
        
        time.sleep(3)
        
        # Debug current state before OTP
        logging.info("=== DEBUG: Current state before OTP ===")
        self.debug_current_state()
        
        # Wait for OTP entry with better user interaction
        print("🔢 Please enter the OTP manually in the browser...")
        print("⏳ Waiting for OTP entry and automatic verification...")
        
        # Wait for either OTP completion or verify button to become available
        otp_completed = False
        for i in range(120):  # Wait up to 2 minutes
            try:
                # Check if we're already logged in (page changed)
                if "swiggy.com" in self.driver.current_url and "login" not in self.driver.current_url.lower():
                    otp_completed = True
                    logging.info("Login detected - OTP was successful")
                    break
                
                # Check if verify button exists and is clickable
                verify_locators = [
                    (By.XPATH, "//button[contains(text(),'Verify') or contains(text(),'Continue') or contains(text(),'Proceed')]"),
                    (By.XPATH, "//a[contains(text(),'Verify') or contains(text(),'Continue') or contains(text(),'Proceed')]"),
                    (By.CSS_SELECTOR, "[data-testid='verify-cta']"),
                    (By.XPATH, "//button[contains(@class, 'verify') or contains(@class, 'continue')]")
                ]
                
                for locator_type, locator_value in verify_locators:
                    try:
                        verify_button = self.driver.find_element(locator_type, locator_value)
                        if verify_button.is_displayed() and verify_button.is_enabled():
                            # Try to click verify button
                            if self.safe_click(verify_button, "click"):
                                logging.info("Clicked verify button")
                                time.sleep(3)
                                # Check if login was successful
                                if "login" not in self.driver.current_url.lower():
                                    otp_completed = True
                                break
                    except:
                        continue
                
                if otp_completed:
                    break
                    
                # Show countdown every 10 seconds
                if i % 10 == 0 and i > 0:
                    remaining = 120 - i
                    print(f"⏳ Still waiting... {remaining} seconds remaining")
                
                time.sleep(1)
                
            except Exception as e:
                logging.warning(f"Error during OTP wait: {e}")
                time.sleep(1)
                continue
        
        if not otp_completed:
            logging.error("OTP verification timed out or failed")
            return False
        
        # Additional wait for page to fully load after login
        time.sleep(5)
        logging.info("Login process completed successfully")
        return True
    
    def wait_for_location_handling(self):
        """Wait for manual location/address handling"""
        print("📍 Please handle location/address selection manually if prompted...")
        print("⏳ Waiting for you to complete location setup (60 seconds)...")
        time.sleep(60)
        logging.info("Location handling wait completed")
        return True
    
    def navigate_to_search_page(self):
        """Navigate to Swiggy search page"""
        try:
            search_url = "https://www.swiggy.com/search"
            self.driver.get(search_url)
            logging.info(f"Navigated to search page: {search_url}")
            time.sleep(5)  # Wait for page to load
            return True
        except Exception as e:
            logging.error(f"Failed to navigate to search page: {e}")
            return False
    
    def search_restaurant(self, restaurant_name="Chandrika Grand"):
        """Search for a restaurant on the search page"""
        # Multiple possible search input locators
        search_locators = [
            (By.XPATH, "//input[@placeholder*='Search']"),
            (By.XPATH, "//input[@placeholder*='restaurants']"),
            (By.XPATH, "//input[@placeholder*='dishes']"),
            (By.CSS_SELECTOR, "input[placeholder*='Search']"),
            (By.XPATH, "//*[contains(@class, 'search')]//input"),
            (By.XPATH, "//input[@type='text']"),
            (By.XPATH, "//input[@name='searchQuery']")
        ]
        
        search_input = None
        for attempt in range(10):  # Try for 10 seconds
            for locator_type, locator_value in search_locators:
                try:
                    search_input = self.driver.find_element(locator_type, locator_value)
                    if search_input.is_displayed() and search_input.is_enabled():
                        break
                except:
                    continue
            
            if search_input and search_input.is_displayed():
                break
            
            time.sleep(1)
        
        if not search_input:
            logging.error("Search input not found")
            return False
        
        try:
            # Clear and enter search term
            search_input.clear()
            search_input.send_keys(restaurant_name)
            logging.info(f"Entered search term: {restaurant_name}")
            time.sleep(2)
            
            # Press Enter or click search button
            search_input.send_keys(Keys.RETURN)
            logging.info(f"Searched for restaurant: {restaurant_name}")
            time.sleep(5)  # Wait for search results
            return True
        except Exception as e:
            logging.error(f"Failed to search for restaurant: {e}")
            return False
    
    def select_restaurant(self, restaurant_name="Chandrika Grand"):
        """Select restaurant from search results"""
        restaurant_locators = [
            (By.XPATH, f"//div[contains(text(),'{restaurant_name}')]"),
            (By.XPATH, f"//h3[contains(text(),'{restaurant_name}')]"),
            (By.XPATH, f"//span[contains(text(),'{restaurant_name}')]"),
            (By.XPATH, f"//*[contains(text(),'{restaurant_name}')]"),
            (By.XPATH, f"//a[contains(text(),'{restaurant_name}')]"),
            (By.XPATH, f"//div[contains(@class, 'restaurant') and contains(text(),'{restaurant_name}')]"),
            (By.XPATH, f"//div[contains(@class, 'RestaurantList')]//div[contains(text(),'{restaurant_name}')]")
        ]
        
        # Wait for search results to load
        time.sleep(5)
        
        if self.find_and_click(restaurant_locators, f"restaurant: {restaurant_name}"):
            logging.info(f"Selected restaurant: {restaurant_name}")
            time.sleep(5)  # Wait for restaurant page to load
            return True
        
        logging.error(f"Could not find restaurant: {restaurant_name}")
        return False
    
    def add_item_to_cart(self):
        """Add first available item to cart"""
        # Multiple possible add button locators
        add_button_locators = [
            (By.XPATH, "//button[contains(text(),'ADD') or contains(text(),'Add')]"),
            (By.XPATH, "//div[contains(text(),'ADD') or contains(text(),'Add')]"),
            (By.CSS_SELECTOR, "[data-testid='add-item-btn']"),
            (By.XPATH, "//*[contains(@class, 'add-btn') or contains(@class, 'add-button')]"),
            (By.XPATH, "//button[contains(@class, 'styles_base__') and contains(text(), 'ADD')]")
        ]
        
        try:
            # Wait for menu to load
            time.sleep(5)
            
            # Find first add button
            add_button = None
            for locator_type, locator_value in add_button_locators:
                try:
                    add_button = self.wait.until(
                        EC.element_to_be_clickable((locator_type, locator_value))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not add_button:
                logging.error("Add button not found")
                return False
            
            # Scroll to button and click to add first item
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
            time.sleep(2)
            
            if self.safe_click(add_button, "js"):
                logging.info("Added first item to cart")
                time.sleep(3)
                return True
            
        except Exception as e:
            logging.error(f"Failed to add item to cart: {e}")
            return False
    
    def view_cart_and_select_address(self):
        """View cart and select home address"""
        # View cart
        view_cart_locators = [
            (By.XPATH, "//span[contains(text(),'View Cart')]"),
            (By.XPATH, "//button[contains(text(),'View Cart')]"),
            (By.CSS_SELECTOR, "[data-testid='view-cart-btn']"),
            (By.XPATH, "//*[contains(@class, 'view-cart')]"),
            (By.XPATH, "//div[contains(text(),'View Cart')]"),
            (By.XPATH, "//a[contains(text(),'View Cart')]")
        ]
        
        if not self.find_and_click(view_cart_locators, "view cart button"):
            logging.error("Could not find view cart button")
            return False
        
        time.sleep(5)
        
        # Select home address
        if not self.select_home_address():
            logging.error("Could not select home address")
            return False
        
        logging.info("Successfully viewed cart and selected home address")
        return True
    
    def select_home_address(self):
        """Select home address from available addresses"""
        try:
            # Wait for address section to load
            time.sleep(3)
            
            # Multiple possible home address locators
            home_address_locators = [
                (By.XPATH, "//div[contains(text(),'Home') or contains(text(),'HOME')]"),
                (By.XPATH, "//span[contains(text(),'Home') or contains(text(),'HOME')]"),
                (By.XPATH, "//*[contains(@class, 'address') and contains(text(), 'Home')]"),
                (By.XPATH, "//label[contains(text(),'Home')]"),
                (By.XPATH, "//div[contains(@class, 'address-type') and contains(text(), 'Home')]"),
                (By.XPATH, "//button[contains(text(),'Home')]"),
                (By.XPATH, "//*[contains(@data-testid, 'address') and contains(text(), 'Home')]")
            ]
            
            # Try to find and click home address
            for locator_type, locator_value in home_address_locators:
                try:
                    home_address = self.wait.until(
                        EC.element_to_be_clickable((locator_type, locator_value))
                    )
                    
                    if home_address.is_displayed():
                        # Scroll to address and click
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", home_address)
                        time.sleep(1)
                        
                        if self.safe_click(home_address, "js"):
                            logging.info("Selected home address")
                            time.sleep(3)
                            return True
                            
                except TimeoutException:
                    continue
                except Exception as e:
                    logging.warning(f"Error with home address locator {locator_value}: {e}")
                    continue
            
            # If no specific "Home" address found, try to select first address
            logging.warning("Home address not found, trying to select first available address")
            return self.select_first_address()
            
        except Exception as e:
            logging.error(f"Failed to select home address: {e}")
            return False
    
    def select_first_address(self):
        """Select the first available address if home address not found"""
        try:
            # Generic address locators
            address_locators = [
                (By.XPATH, "//div[contains(@class, 'address-item')]"),
                (By.XPATH, "//div[contains(@class, 'address-card')]"),
                (By.XPATH, "//button[contains(@class, 'address')]"),
                (By.XPATH, "//*[contains(@class, 'address') and contains(@class, 'selectable')]"),
                (By.XPATH, "//label[contains(@class, 'address')]"),
                (By.XPATH, "//div[contains(@class, 'delivery-address')]")
            ]
            
            for locator_type, locator_value in address_locators:
                try:
                    address_element = self.wait.until(
                        EC.element_to_be_clickable((locator_type, locator_value))
                    )
                    
                    if address_element.is_displayed():
                        # Scroll to address and click
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", address_element)
                        time.sleep(1)
                        
                        if self.safe_click(address_element, "js"):
                            logging.info("Selected first available address")
                            time.sleep(3)
                            return True
                            
                except TimeoutException:
                    continue
                except Exception as e:
                    logging.warning(f"Error with address locator {locator_value}: {e}")
                    continue
            
            logging.warning("No address could be selected automatically")
            print("📍 Please select your delivery address manually within 30 seconds...")
            time.sleep(30)
            return True
            
        except Exception as e:
            logging.error(f"Failed to select address: {e}")
            return False
    
    def run_automation(self, restaurant_name="Chandrika Grand"):
        """Run complete automation workflow"""
        try:
            steps = [
                ("Opening Swiggy", self.open_swiggy),
                ("Handling login", self.handle_login),
                ("Waiting for location handling", self.wait_for_location_handling),
                ("Navigating to search page", self.navigate_to_search_page),
                ("Searching restaurant", lambda: self.search_restaurant(restaurant_name)),
                ("Selecting restaurant", lambda: self.select_restaurant(restaurant_name)),
                ("Adding item to cart", self.add_item_to_cart),
                ("Viewing cart and selecting address", self.view_cart_and_select_address)
            ]
            
            for step_name, step_function in steps:
                logging.info(f"Starting: {step_name}")
                if not step_function():
                    logging.error(f"Failed: {step_name}")
                    return False
                logging.info(f"Completed: {step_name}")
            
            logging.info("✅ Automation completed successfully!")
            print("🎉 Automation complete! The item has been added to cart and home address selected.")
            print("📋 You can now review the order and proceed with payment manually.")
            return True
            
        except Exception as e:
            logging.error(f"Automation failed with error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            logging.info("Closing browser...")
            # Don't quit immediately, let user review
            # self.driver.quit()


def main():
    """Main execution function"""
    # Configuration
    PHONE_NUMBER = "9XXXXXXXXX"  # Change this to your phone number
    RESTAURANT_NAME = "Chandrika Grand"  # Change this to your preferred restaurant
    
    automation = SwiggyAutomation(phone_number=PHONE_NUMBER)
    
    try:
        success = automation.run_automation(restaurant_name=RESTAURANT_NAME)
        if success:
            print("✅ Automation completed successfully!")
        else:
            print("❌ Automation failed. Check logs for details.")
    
    except KeyboardInterrupt:
        logging.info("Automation interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        # Keep browser open for manual review
        input("Press Enter to close the browser...")
        automation.cleanup()


if _name_ == "_main_":
    main()