"""
Configuration module for Gmail Creator
Contains all settings, constants, and selectors used throughout the application
"""
import string

class Config:
    """Configuration class storing all settings and constants"""
    
    # Account generation settings
    AUTO_GENERATE_USERINFO = True
    AUTO_GENERATE_NUMBER = 10
    INCLUDE_REFER_URL = False
    
    # Timing settings
    WAIT = 4  # Base wait time in seconds
    REQUEST_MAX_TRY = 10  # Maximum retries for phone number requests
    
    # SMS API settings
    API_KEY = "8e49fdB90d0209c085dd1df56cedf00e"
    COUNTRY_CODE = "175"  # Australian country code
    SMS_ACTIVATE_URL = "https://sms-activate.org/stubs/handler_api.php"
    
    # File paths
    FIRST_NAMES_PATH = "./data/First_Name_DB.csv"
    LAST_NAMES_PATH = "./data/Last_Name_DB.csv"
    USER_INFO_PATH = r"G:\Python\Sujon\Auto-Gmail-Creator\user.csv"
    CREATED_ACCOUNTS_PATH = "Created.txt"
    
    # Password generation settings
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 12
    PASSWORD_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation
    
    # Referral sites for bypassing bot detection
    SITE_LIST = [
        'https://google.com',
        'https://wizardrytechnique.webflow.io/',
        'https://www.rachelbavaresco.com/',
        'https://lightning-bolt.webflow.io/'
    ]
    
    # Browser settings
    BROWSER_WIDTH_MIN = 1050
    BROWSER_WIDTH_MAX = 1200
    BROWSER_HEIGHT_MIN = 800
    BROWSER_HEIGHT_MAX = 900
    
    # Proxy settings
    PROXY_RETRIES = 3
    PROXY_TIMEOUT = 1
    
    @staticmethod
    def get_phone_request_params():
        """Return parameters for phone number request"""
        return {
            "api_key": Config.API_KEY,
            "action": "getNumber",
            "country": Config.COUNTRY_CODE,
            "service": "go",
        }
    
    @staticmethod
    def get_status_params():
        """Return parameters for status check request"""
        return {
            "api_key": Config.API_KEY,
            "action": "getStatus"
        }


class Selectors:
    """Class containing all XPath and CSS selectors for web elements"""
    
    CREATE_ACCOUNT = [
        "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-dgl2Hf ksBjEc lKxP2d LQeN7 FliLIb uRo0Xe TrZEUc Xf9GD']",
        "//*[@class='JnOM6e TrZEUc kTeh9 KXbQ4b']"
    ]
    
    FOR_PERSONAL_USE = [
        "//span[@class='VfPpkd-StrnGf-rymPhb-b9t22c']"
    ]
    
    FIRST_NAME = "//*[@name='firstName']"
    LAST_NAME = "//*[@name='lastName']"
    USERNAME = "//*[@name='Username']"
    PASSWORD = "//*[@name='Passwd']"
    CONFIRM_PASSWORD = "//*[@name='PasswdAgain']"
    
    NEXT_BUTTONS = [
        "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 qIypjc TrZEUc lw1w4b']",
        "//button[contains(text(),'Next')]",
        "//button[contains(text(),'I agree')]"
    ]
    
    PHONE_NUMBER = "//*[@id='phoneNumberId']"
    CODE = '//input[@name="code"]'
    
    # Account details fields
    ACC_PHONE_NUMBER = '//input[@id="phoneNumberId"]'
    ACC_DAY = '//input[@name="day"]'
    ACC_MONTH = '//select[@id="month"]'
    ACC_YEAR = '//input[@name="year"]'
    ACC_GENDER = '//select[@id="gender"]'
    
    USERNAME_WARNING = '//*[@class="jibhHc"]'
    USERNAME_SELECT = '//*[@aria-posinset="3"]'
    
    # Account creation entry points
    GOOGLE_ACCOUNT_ARTICLE_LINK = '//*[@id="hcfe-content"]/section/div/div[1]/article/section/div/div[1]/div/div[2]/a[1]'
    MAIL_ARTICLE_LINK = '//*[@id="hcfe-content"]/section/div/div[1]/article/section/div/div[1]/div/p[1]/a'
    
    # URLs for account creation
    URLS = {
        "support": "https://support.google.com/accounts/answer/27441?hl=en",
        "direct": "https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp",
        "accounts": "https://accounts.google.com",
        "mail_help": "https://support.google.com/mail/answer/56256?hl=en"
    }