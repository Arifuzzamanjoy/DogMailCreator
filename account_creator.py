"""
Main account creator module for Gmail Creator
Coordinates all components to automate Gmail account creation
"""
import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import Config, Selectors
from browser_manager import BrowserManager
from user_manager import UserManager
from phone_verification import PhoneVerificationManager

class AccountCreator:
    """
    Main class that coordinates the Gmail account creation process
    Combines all component managers to create accounts
    """
    
    def __init__(self, auto_generate=True, user_count=10, use_proxy=True, browser_type="chrome"):
        """
        Initialize the account creator
        
        Args:
            auto_generate (bool): Whether to auto-generate user info
            user_count (int): Number of accounts to create
            use_proxy (bool): Whether to use proxies
            browser_type (str): Type of browser to use
        """
        self._setup_logging()
        self.logger = logging.getLogger('gmail_creator.main')
        
        self.logger.info("Initializing Gmail Account Creator")
        
        # Initialize component managers
        self.user_manager = UserManager(auto_generate=auto_generate, user_count=user_count)
        self.browser_manager = BrowserManager(use_proxy=use_proxy, browser_type=browser_type)
        self.phone_manager = PhoneVerificationManager()
        
        # Track status
        self.current_index = 0
        self.successful_accounts = 0
        self.failed_accounts = 0
        
    def _setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("gmail_creator.log"),
                logging.StreamHandler()
            ]
        )
    
    def create_accounts(self):
        """
        Main method to create the specified number of accounts
        
        Returns:
            int: Number of successfully created accounts
        """
        user_count = self.user_manager.get_user_count()
        self.logger.info(f"Starting creation of {user_count} accounts")
        
        while self.current_index < user_count:
            try:
                self.logger.info(f"Processing account {self.current_index + 1} of {user_count}")
                
                # Get user data for current index
                user_data = self.user_manager.get_user_data(self.current_index)
                if not user_data:
                    self.logger.error(f"Failed to get user data for index {self.current_index}")
                    self.failed_accounts += 1
                    self.current_index += 1
                    continue
                    
                # Initialize browser
                driver = self.browser_manager.initialize_driver()
                
                # Create the account
                success = self._create_single_account(driver, user_data)
                
                if success:
                    self.successful_accounts += 1
                else:
                    self.failed_accounts += 1
                
                # Close browser
                self.browser_manager.close()
                
                # Track progress
                self.current_index += 1
                
                # Random delay between accounts to avoid detection
                delay = random.uniform(5, 15)
                self.logger.info(f"Waiting {delay:.2f} seconds before next account")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                self.failed_accounts += 1
                self.current_index += 1
                
                # Close browser if it's still open
                self.browser_manager.close()
                
                # Longer delay after error
                time.sleep(random.uniform(10, 30))
                
        self.logger.info(f"Account creation complete: {self.successful_accounts} successful, {self.failed_accounts} failed")
        return self.successful_accounts
    
    def _create_single_account(self, driver, user_data):
        """
        Create a single Gmail account
        
        Args:
            driver (WebDriver): Initialized WebDriver
            user_data (dict): User data for account creation
            
        Returns:
            bool: True if account created successfully, False otherwise
        """
        try:
            # Navigate to account creation page using one of several methods
            self._navigate_to_account_creation(driver)
            
            # Fill out first step (name)
            self._fill_first_step(driver, user_data)
            
            # Fill out second step (birthday and gender)
            self._fill_second_step(driver, user_data)
            
            # Fill out third step (username)
            username = self._fill_username_step(driver, user_data)
            
            # Fill out fourth step (password)
            self._fill_password_step(driver, user_data)
            
            # Handle phone verification if required
            phone_number = ""
            if self._requires_phone_verification(driver):
                success, phone_number = self._handle_phone_verification(driver)
                if not success:
                    self.logger.error("Phone verification failed")
                    return False
            
            # Complete final steps (agree to terms)
            if not self._complete_final_steps(driver):
                self.logger.error("Failed to complete final steps")
                return False
            
            # Save the created account
            self.user_manager.save_created_account(
                username=username,
                password=user_data['password'],
                birthday=user_data['birthday'],
                phone_number=phone_number
            )
            
            self.logger.info(f"Successfully created account: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating account: {str(e)}")
            # Take screenshot for debugging
            self.browser_manager.take_screenshot(f"error_create_account_{self.current_index}")
            return False
    
    def _navigate_to_account_creation(self, driver):
        """Navigate to the account creation page using one of several methods"""
        self.logger.info("Navigating to account creation page")
        
        # Simulate realistic browsing behavior
        self.browser_manager.mouse_movement_simulation()
        
        # Random referrer to bypass detection
        if Config.INCLUDE_REFER_URL:
            random_url = random.choice(Config.SITE_LIST)
            driver.get(random_url)
            self.browser_manager.human_like_delay()
            
            # Random scrolling behavior
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
            self.browser_manager.human_like_delay()
        
        # Choose one of 4 random ways to reach account creation
        approach = random.randint(1, 4)
        self.logger.info(f"Using approach {approach} to access account creation")
        
        if approach == 1:
            # Via Google account help article
            driver.get(Selectors.URLS["support"])
            self.browser_manager.wait_for_element(
                Selectors.GOOGLE_ACCOUNT_ARTICLE_LINK, clickable=True
            ).click()
            
        elif approach == 2:
            # Direct via accounts.google.com
            driver.get(Selectors.URLS["accounts"])
            self.browser_manager.human_like_delay()
            
            # Click "Create account"
            for selector in Selectors.CREATE_ACCOUNT:
                try:
                    self.browser_manager.wait_for_element(selector, clickable=True).click()
                    break
                except Exception:
                    continue
            
            self.browser_manager.human_like_delay()
            
            # Click "For my personal use"
            for selector in Selectors.FOR_PERSONAL_USE:
                try:
                    self.browser_manager.wait_for_element(selector, clickable=True).click()
                    break
                except Exception:
                    continue
                    
        elif approach == 3:
            # Direct signup URL
            driver.get(Selectors.URLS["direct"])
            
        else:
            # Via Gmail help article
            driver.get(Selectors.URLS["mail_help"])
            self.browser_manager.wait_for_element(
                Selectors.MAIL_ARTICLE_LINK, clickable=True
            ).click()
            
        self.browser_manager.human_like_delay()
    
    def _fill_first_step(self, driver, user_data):
        """Fill out the first step of creation (name)"""
        self.logger.info("Filling out first step: name fields")
        
        # Get first name field and fill with human-like typing
        first_name_field = self.browser_manager.wait_for_element(Selectors.FIRST_NAME)
        first_name_field.clear()
        self.browser_manager.human_like_typing(first_name_field, user_data['first_name'])
        
        # Random pause between fields
        self.browser_manager.human_like_delay()
        
        # Fill last name with human-like typing
        last_name_field = self.browser_manager.wait_for_element(Selectors.LAST_NAME)
        last_name_field.clear()
        self.browser_manager.human_like_typing(last_name_field, user_data['last_name'])
        
        # Random mouse movement
        self.browser_manager.mouse_movement_simulation()
        
        # Click next button
        self._click_next_button(driver)
        
        self.logger.info("First step completed")
    
    def _fill_second_step(self, driver, user_data):
        """Fill out the second step (birthday and gender)"""
        self.logger.info("Filling out second step: birthday and gender")
        
        # Take a longer pause before filling out this step
        self.browser_manager.human_like_delay(2.0, 3.0)
        
        # Wait longer for page transition and take screenshot for debugging
        time.sleep(3)  
        self.browser_manager.take_screenshot(f"before_birthday_{self.current_index}")
        
        try:
            # Parse birthday
            parts = user_data['birthday'].split('/')
            month = parts[0]
            day = parts[1]
            year = parts[2]
            
            # Day field
            day_field = self.browser_manager.wait_for_element(Selectors.ACC_DAY, wait_time=8)
            day_field.clear()
            self.browser_manager.human_like_typing(day_field, day)
            self.logger.info("Day field filled")
            
            # Random delay
            self.browser_manager.human_like_delay()
            
            # Month dropdown
            month_select = self.browser_manager.wait_for_element(Selectors.ACC_MONTH)
            from selenium.webdriver.support.ui import Select
            Select(month_select).select_by_value(month)
            self.logger.info("Month field filled")
            
            # Random delay
            self.browser_manager.human_like_delay()
            
            # Year field
            year_field = self.browser_manager.wait_for_element(Selectors.ACC_YEAR)
            year_field.clear()
            self.browser_manager.human_like_typing(year_field, year)
            self.logger.info("Year field filled")
            
            # Random delay
            self.browser_manager.human_like_delay()
            
            # Gender dropdown
            gender_select = self.browser_manager.wait_for_element(Selectors.ACC_GENDER)
            Select(gender_select).select_by_value('1')  # '1' is male in the Google form
            self.logger.info("Gender field filled")
            
            # Random mouse movement
            self.browser_manager.mouse_movement_simulation()
            
            # Click next
            self._click_next_button(driver)
            
            self.logger.info("Second step completed")
            
        except Exception as e:
            self.logger.error(f"Error in birthday step: {str(e)}")
            # Take screenshot for debugging
            self.browser_manager.take_screenshot(f"error_birthday_{self.current_index}")
            
            # Try direct JavaScript approach as last resort
            try:
                self.logger.info("Attempting JavaScript fallback for birthday fields")
                driver.execute_script("""
                    // Try to set values directly via JS
                    document.querySelector('input[name="day"]').value = arguments[0];
                    document.querySelector('select#month').value = arguments[1];
                    document.querySelector('input[name="year"]').value = arguments[2];
                    document.querySelector('select#gender').value = '1';
                """, day, month, year)
                
                # Click next with JavaScript
                driver.execute_script("""
                    document.querySelector('button[type="button"]').click();
                """)
                
                # Wait to see if we advance
                time.sleep(3)
                self.logger.info("JavaScript form fill attempt completed")
            except Exception as js_error:
                self.logger.error(f"JavaScript fallback also failed: {str(js_error)}")
                raise
    
    def _fill_username_step(self, driver, user_data):
        """
        Fill out the username step
        
        Returns:
            str: The username that was successfully entered
        """
        self.logger.info("Filling out username step")
        self.browser_manager.human_like_delay()
        
        # Determine username
        username = ""
        if user_data.get('manual_username'):
            username = user_data['manual_username']
        else:
            # Generate username based on first/last name
            username = self.user_manager.generate_username(
                user_data['first_name'], 
                user_data['last_name']
            )
        
        # Sometimes Google has a "username_select" step first
        try:
            self.browser_manager.wait_for_element(
                Selectors.USERNAME_SELECT, wait_time=3, clickable=True
            ).click()
        except:
            self.logger.info("No username selection step, continuing")
        
        # Fill username field
        username_field = self.browser_manager.wait_for_element(Selectors.USERNAME)
        username_field.clear()
        self.browser_manager.human_like_typing(username_field, username)
        self.logger.info(f"Username entered: {username}")
        
        # Click next button
        self._click_next_button(driver)
        
        # Check for username warning
        try:
            self.browser_manager.wait_for_element(
                Selectors.USERNAME_WARNING, wait_time=3
            )
            self.logger.warning("Username was invalid or already taken")
            return self._fill_username_step(driver, {**user_data, 'manual_username': ""})
        except:
            self.logger.info("Username accepted")
        
        return username
    
    def _fill_password_step(self, driver, user_data):
        """Fill out the password step"""
        self.logger.info("Filling out password step")
        
        # Fill password field
        password_field = self.browser_manager.wait_for_element(Selectors.PASSWORD)
        password_field.clear()
        self.browser_manager.human_like_typing(password_field, user_data['password'])
        
        # Random delay between fields
        self.browser_manager.human_like_delay()
        
        # Fill confirm password field
        confirm_field = self.browser_manager.wait_for_element(Selectors.CONFIRM_PASSWORD)
        confirm_field.clear()
        self.browser_manager.human_like_typing(confirm_field, user_data['password'])
        
        # Click next button
        self._click_next_button(driver)
        
        self.logger.info("Password step completed")
    
    def _requires_phone_verification(self, driver):
        """Check if phone verification is required"""
        self.logger.info("Checking if phone verification is required")
        
        try:
            # If we're still on the birthday step, verification was skipped
            self.browser_manager.wait_for_element(
                Selectors.ACC_DAY, wait_time=3
            )
            self.logger.info("Phone verification not required")
            return False
        except:
            # If we can't find the day field, we're on the phone verification page
            try:
                self.browser_manager.wait_for_element(
                    Selectors.PHONE_NUMBER, wait_time=5
                )
                self.logger.info("Phone verification is required")
                return True
            except:
                # If we can't find the phone field either, something else is happening
                self.logger.warning("Could not determine verification requirement")
                return False
    
    def _handle_phone_verification(self, driver):
        """
        Handle the phone verification process
        
        Returns:
            tuple: (success, phone_number)
        """
        self.logger.info("Handling phone verification")
        
        # Get phone number from service
        success, phone_number = self.phone_manager.get_phone_number()
        if not success:
            self.logger.error("Failed to get phone number")
            return False, ""
        
        # Enter phone number
        phone_field = self.browser_manager.wait_for_element(Selectors.PHONE_NUMBER)
        self.browser_manager.human_like_typing(phone_field, phone_number)
        
        # Click next button
        self._click_next_button(driver)
        
        # Wait for SMS code
        success, code = self.phone_manager.get_verification_code()
        if not success:
            self.logger.error("Failed to get verification code")
            self.phone_manager.cancel_current_activation()
            return False, phone_number
        
        # Enter verification code
        code_field = self.browser_manager.wait_for_element(Selectors.CODE)
        self.browser_manager.human_like_typing(code_field, code)
        
        # Click verify button
        self._click_next_button(driver)
        
        # Report success to SMS service
        self.phone_manager.report_success()
        
        self.logger.info("Phone verification completed successfully")
        return True, phone_number
    
    def _complete_final_steps(self, driver):
        """Complete the final steps of account creation"""
        self.logger.info("Completing final steps")
        
        try:
            # Click next button to continue
            self._click_next_button(driver)
            
            # Random delay
            self.browser_manager.human_like_delay()
            
            # Scroll down for terms of service
            driver.execute_script("window.scrollTo(0, 800)")
            self.browser_manager.human_like_delay()
            
            # Click I agree
            self._click_next_button(driver)
            
            # Wait for completion
            time.sleep(3)  # Give it time to complete
            
            self.logger.info("Account creation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in final steps: {str(e)}")
            return False
    
    def _click_next_button(self, driver):
        """Click the next button, trying different selectors if necessary"""
        self.logger.info("Clicking next button")
        
        for selector in Selectors.NEXT_BUTTONS:
            try:
                button = self.browser_manager.wait_for_element(
                    selector, wait_time=5, clickable=True
                )
                button.click()
                self.browser_manager.human_like_delay()
                return True
            except Exception:
                continue
                
        # If all selectors fail, try JavaScript approach
        try:
            self.logger.warning("All next button selectors failed, trying JavaScript")
            driver.execute_script("""
                // Try to click the first button found
                document.querySelector('button[type="button"]').click();
            """)
            self.browser_manager.human_like_delay()
            return True
        except Exception as e:
            self.logger.error(f"JavaScript button click also failed: {str(e)}")
            raise ValueError("Could not click next button")