"""
Phone verification module for Gmail Creator
Handles interactions with SMS verification services (sms-activate.org)
"""
import requests
import time
import logging
from config import Config

class PhoneVerificationManager:
    """
    Manages phone verification process using SMS services
    Handles obtaining phone numbers and verification codes
    """
    
    def __init__(self, api_key=None, country_code=None):
        """
        Initialize phone verification manager
        
        Args:
            api_key (str): API key for SMS service, defaults to Config value
            country_code (str): Country code for phone numbers, defaults to Config value
        """
        self.logger = logging.getLogger('gmail_creator.phone')
        self.api_key = api_key or Config.API_KEY
        self.country_code = country_code or Config.COUNTRY_CODE
        self.api_url = Config.SMS_ACTIVATE_URL
        
        self.current_activation_id = None
        self.current_number = None
    
    def get_phone_number(self, max_attempts=None):
        """
        Get a phone number from the SMS service
        
        Args:
            max_attempts (int): Maximum number of attempts to get a number
            
        Returns:
            tuple: (successful, phone_number)
        """
        if max_attempts is None:
            max_attempts = Config.REQUEST_MAX_TRY
            
        self.logger.info(f"Getting phone number from SMS service with {max_attempts} max attempts")
        
        params = {
            "api_key": self.api_key,
            "action": "getNumber",
            "country": self.country_code,
            "service": "go",  # service code for Google
        }
        
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            self.logger.info(f"Phone number request attempt {attempt}/{max_attempts}")
            
            try:
                response = requests.get(self.api_url, params=params, timeout=10)
                data = response.text
                self.logger.debug(f"API response: {data}")
                
                if "ACCESS_NUMBER" in data:
                    # Format: ACCESS_NUMBER:12345:71234567890
                    parts = data.split(':')
                    if len(parts) >= 3:
                        self.current_activation_id = parts[1]
                        self.current_number = parts[2]
                        formatted_number = f"+{self.current_number}"
                        
                        self.logger.info(f"Successfully obtained phone number: {formatted_number}")
                        return True, formatted_number
                    else:
                        self.logger.warning(f"Invalid API response format: {data}")
                elif "NO_NUMBERS" in data:
                    self.logger.warning("No numbers available, retrying...")
                    time.sleep(2)  # Wait before retrying
                elif "NO_BALANCE" in data:
                    self.logger.error("Insufficient balance in SMS-Activate account")
                    return False, "Insufficient balance in SMS-Activate account"
                elif "BAD_KEY" in data:
                    self.logger.error("Invalid API key provided")
                    return False, "Invalid API key"
                else:
                    self.logger.warning(f"Unexpected API response: {data}")
                
            except requests.RequestException as e:
                self.logger.error(f"Request failed: {str(e)}")
            
            time.sleep(3)  # Wait between attempts
        
        self.logger.error(f"Failed to get phone number after {max_attempts} attempts")
        return False, None
    
    def get_verification_code(self, max_attempts=None, polling_interval=5):
        """
        Get verification code for the current phone number
        
        Args:
            max_attempts (int): Maximum number of attempts to get the code
            polling_interval (int): Time in seconds between polling attempts
            
        Returns:
            tuple: (successful, verification_code)
        """
        if not self.current_activation_id:
            self.logger.error("No active phone number session - call get_phone_number first")
            return False, "No active phone number"
            
        if max_attempts is None:
            max_attempts = Config.REQUEST_MAX_TRY
            
        self.logger.info(f"Waiting for verification code for activation ID: {self.current_activation_id}")
        
        params = {
            "api_key": self.api_key,
            "action": "getStatus",
            "id": self.current_activation_id
        }
        
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            self.logger.info(f"Verification code check attempt {attempt}/{max_attempts}")
            
            try:
                response = requests.get(self.api_url, params=params, timeout=10)
                data = response.text
                self.logger.debug(f"API response: {data}")
                
                if "STATUS_OK" in data:
                    # Format: STATUS_OK:123456
                    parts = data.split(':')
                    if len(parts) >= 2:
                        code = parts[1]
                        self.logger.info(f"Successfully received verification code: {code}")
                        return True, code
                    else:
                        self.logger.warning(f"Invalid STATUS_OK response format: {data}")
                elif "STATUS_WAIT_CODE" in data:
                    self.logger.info("SMS not received yet, waiting...")
                elif "STATUS_CANCEL" in data:
                    self.logger.warning("Activation was cancelled")
                    return False, "Activation cancelled"
                else:
                    self.logger.warning(f"Unexpected API response: {data}")
                
            except requests.RequestException as e:
                self.logger.error(f"Request failed: {str(e)}")
            
            # Don't count waiting for SMS as a failure attempt
            if "STATUS_WAIT_CODE" in data:
                attempt -= 1
                
            time.sleep(polling_interval)  # Wait between polling attempts
        
        self.logger.error(f"Failed to get verification code after {max_attempts} attempts")
        return False, None
    
    def cancel_current_activation(self):
        """
        Cancel the current phone number activation
        
        Returns:
            bool: True if cancelled successfully, False otherwise
        """
        if not self.current_activation_id:
            self.logger.warning("No active phone number to cancel")
            return True
            
        self.logger.info(f"Cancelling activation ID: {self.current_activation_id}")
        
        params = {
            "api_key": self.api_key,
            "action": "setStatus",
            "id": self.current_activation_id,
            "status": 8  # Status code for cancellation
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            data = response.text
            self.logger.debug(f"API response: {data}")
            
            if "ACCESS_CANCEL" in data or "ACCESS_ACTIVATION_CANCEL" in data:
                self.logger.info("Activation cancelled successfully")
                self.current_activation_id = None
                self.current_number = None
                return True
            else:
                self.logger.warning(f"Failed to cancel activation: {data}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return False
    
    def report_success(self):
        """
        Report successful use of the phone number
        
        Returns:
            bool: True if reported successfully, False otherwise
        """
        if not self.current_activation_id:
            self.logger.warning("No active phone number to report success for")
            return False
            
        self.logger.info(f"Reporting success for activation ID: {self.current_activation_id}")
        
        params = {
            "api_key": self.api_key,
            "action": "setStatus",
            "id": self.current_activation_id,
            "status": 6  # Status code for reporting success
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            data = response.text
            self.logger.debug(f"API response: {data}")
            
            if "ACCESS_ACTIVATION_SUCCESS" in data:
                self.logger.info("Successfully reported activation success")
                self.current_activation_id = None
                self.current_number = None
                return True
            else:
                self.logger.warning(f"Failed to report success: {data}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return False
    
    def check_balance(self):
        """
        Check balance on the SMS service
        
        Returns:
            float: Account balance or None if request failed
        """
        self.logger.info("Checking SMS service balance")
        
        params = {
            "api_key": self.api_key,
            "action": "getBalance",
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            data = response.text
            
            if "ACCESS_BALANCE" in data:
                # Format: ACCESS_BALANCE:10.50
                balance = float(data.split(':')[1])
                self.logger.info(f"Current balance: {balance}")
                return balance
            else:
                self.logger.warning(f"Failed to check balance: {data}")
                return None
                
        except (requests.RequestException, ValueError) as e:
            self.logger.error(f"Balance check failed: {str(e)}")
            return None