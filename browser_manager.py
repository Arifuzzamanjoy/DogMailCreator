"""
Browser management module for Gmail Creator
Handles browser initialization, anti-detection, and human simulation
"""
import random
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from fake_useragent import UserAgent
import logging

from config import Config
from proxy_manager import ProxyManager


class BrowserManager:
    """
    Manages browser initialization and interactions
    Implements anti-detection measures and human-like behavior
    """
    
    def __init__(self, use_proxy=True, browser_type="chrome"):
        """
        Initialize the browser manager
        
        Args:
            use_proxy (bool): Whether to use proxy for browser
            browser_type (str): Type of browser to use ('chrome' or 'firefox')
        """
        self.logger = logging.getLogger('gmail_creator.browser')
        self.browser_type = browser_type.lower()
        self.use_proxy = use_proxy
        self.driver = None
        self.proxy_manager = ProxyManager() if use_proxy else None
        self.user_agent = self._get_random_user_agent()
    
    def _get_random_user_agent(self):
        """Get a random user agent string"""
        try:
            return UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36").random
        except Exception as e:
            self.logger.warning(f"Error getting random user agent: {str(e)}")
            # Default modern user agents if fake_useragent fails
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
            ]
            return random.choice(user_agents)
    
    def initialize_driver(self):
        """
        Initialize and configure WebDriver with anti-detection measures
        
        Returns:
            WebDriver: Configured Selenium WebDriver instance
        """
        self.logger.info(f"Initializing {self.browser_type} driver")
        
        # Set up seleniumwire options
        seleniumwire_options = {
            'exclude_hosts': ['google-analytics.com', 'analytics.google.com', 'googletagmanager.com']
        }
        
        # Add proxy if enabled
        if self.use_proxy and self.proxy_manager:
            seleniumwire_options['proxy'] = self.proxy_manager.get_proxy_options()
            self.logger.info(f"Using proxy: {self.proxy_manager.current_proxy}")
        
        # Configure browser options
        if self.browser_type == 'chrome':
            options = self._setup_chrome_options()
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options, 
                seleniumwire_options=seleniumwire_options
            )
        elif self.browser_type == 'firefox':
            options = self._setup_firefox_options()
            driver = webdriver.Firefox(
                service=Service(GeckoDriverManager().install()), 
                options=options, 
                seleniumwire_options=seleniumwire_options
            )
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # Apply additional anti-detection measures
        self._apply_anti_detection(driver)
        self.driver = driver
        return driver
    
    def _setup_chrome_options(self):
        """Set up Chrome-specific options with anti-detection measures"""
        options = ChromeOptions()
        
        # Anti-bot detection settings
        prefs = {
            "profile.password_manager_enabled": False, 
            "credentials_enable_service": False, 
            "useAutomationExtension": False,
            "profile.default_content_setting_values.notifications": 2
        }
        
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Additional anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        
        # Add timezone to match IP location if using a proxy
        timezone = random.choice(["America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"])
        options.add_argument(f"--timezone={timezone}")
        
        # Random language preferences to appear more natural
        langs = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "es-ES,es;q=0.9,en;q=0.7"]
        options.add_argument(f"--lang={random.choice(langs)}")
        
        # Set user agent
        options.add_argument(f"user-agent={self.user_agent}")
        
        return options
    
    def _setup_firefox_options(self):
        """Set up Firefox-specific options with anti-detection measures"""
        options = FirefoxOptions()
        
        # Common options
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("general.useragent.override", self.user_agent)
        
        # Additional preferences
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        
        return options
    
    def _apply_anti_detection(self, driver):
        """Apply additional runtime anti-detection measures to the browser"""
        try:
            # Hide WebDriver flag
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Random window size to avoid detection
            width = random.randint(Config.BROWSER_WIDTH_MIN, Config.BROWSER_WIDTH_MAX)
            height = random.randint(Config.BROWSER_HEIGHT_MIN, Config.BROWSER_HEIGHT_MAX)
            driver.set_window_size(width, height)
            
            # Additional spoofing for Chrome
            if self.browser_type == 'chrome':
                driver.execute_script("""
                    // Overwrite the 'navigator.chrome' property to undefined
                    Object.defineProperty(window, 'chrome', {
                        enumerable: true,
                        configurable: false,
                        writable: false,
                        value: {
                            app: {
                                isInstalled: false,
                            },
                            webstore: {
                                onInstallStageChanged: {},
                                onDownloadProgress: {},
                            },
                            runtime: {
                                PlatformOs: {
                                    MAC: 'mac',
                                    WIN: 'win',
                                    ANDROID: 'android',
                                    CROS: 'cros',
                                    LINUX: 'linux',
                                    OPENBSD: 'openbsd',
                                },
                                PlatformArch: {
                                    ARM: 'arm',
                                    X86_32: 'x86-32',
                                    X86_64: 'x86-64',
                                },
                                PlatformNaclArch: {
                                    ARM: 'arm',
                                    X86_32: 'x86-32',
                                    X86_64: 'x86-64',
                                },
                                RequestUpdateCheckStatus: {
                                    THROTTLED: 'throttled',
                                    NO_UPDATE: 'no_update',
                                    UPDATE_AVAILABLE: 'update_available',
                                }
                            }
                        }
                    });
                """)
            
        except Exception as e:
            self.logger.warning(f"Error applying anti-detection measures: {str(e)}")
    
    def human_like_delay(self, min_time=0.5, max_time=2.0):
        """Simulate human-like delay between actions"""
        base_delay = random.uniform(min_time, max_time)
        time.sleep(base_delay * Config.WAIT)
    
    def human_like_typing(self, element, text):
        """Type text like a human with random delays between keystrokes"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))  # Random delay between keystrokes
    
    def mouse_movement_simulation(self):
        """Simulate random mouse movements to appear more human-like"""
        if not self.driver:
            return
            
        try:
            # Get window size
            window_size = self.driver.get_window_size()
            width, height = window_size['width'], window_size['height']
            
            # Execute JavaScript to move mouse randomly
            for _ in range(3):
                x, y = random.randint(0, width), random.randint(0, height)
                self.driver.execute_script(
                    f"document.elementFromPoint({x}, {y}).scrollIntoView({{behavior: 'smooth', block: 'center'}});"
                )
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.logger.debug(f"Mouse movement simulation failed: {str(e)}")
    
    def wait_for_element(self, selector, by=By.XPATH, wait_time=None, clickable=False):
        """
        Wait for an element to be available with enhanced retry logic
        
        Args:
            selector (str): Element selector
            by (selenium.webdriver.common.by.By): Selector type
            wait_time (int): Custom wait time or None for default
            clickable (bool): Whether to wait for element to be clickable
            
        Returns:
            WebElement: The found element
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized. Call initialize_driver() first.")
            
        if wait_time is None:
            wait_time = Config.WAIT
            
        try:
            wait = WebDriverWait(self.driver, wait_time)
            if clickable:
                return wait.until(EC.element_to_be_clickable((by, selector)))
            else:
                return wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            # Try JavaScript injection as fallback for difficult elements
            try:
                self.logger.warning(f"Element not found with normal wait: {selector}, trying JavaScript fallback")
                element = self.driver.find_element(by, selector)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
                if clickable:
                    self.driver.execute_script("arguments[0].click();", element)
                return element
            except Exception as e:
                self.logger.error(f"JavaScript fallback also failed: {str(e)}")
                # Take screenshot for debugging
                self.take_screenshot("element_not_found")
                raise
    
    def take_screenshot(self, name_prefix):
        """Take a screenshot for debugging purposes"""
        if not self.driver:
            return
            
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name_prefix}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
    
    def close(self):
        """Close the WebDriver safely"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error closing driver: {str(e)}")
            finally:
                self.driver = None