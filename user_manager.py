"""
User management module for Gmail Creator
Handles user data generation, loading, and storage
"""
import random
import string
import csv
import os
import logging
from datetime import datetime
from config import Config

class UserManager:
    """
    Manages user data for Gmail account creation
    Can generate random user info or load from CSV files
    """
    
    def __init__(self, auto_generate=True, user_count=10):
        """
        Initialize the user manager
        
        Args:
            auto_generate (bool): Whether to auto-generate user info or load from file
            user_count (int): Number of users to generate if auto-generating
        """
        self.logger = logging.getLogger('gmail_creator.user')
        self.auto_generate = auto_generate
        self.user_count = user_count
        
        # Data storage
        self.first_names = []
        self.last_names = []
        self.user_infos = []
        self.created_accounts = []
        
        # Load necessary data based on mode
        self._load_data()
    
    def _load_data(self):
        """Load required data files based on configuration"""
        if self.auto_generate:
            self._load_name_files()
        else:
            self._load_user_info_file()
    
    def _load_name_files(self):
        """Load first and last name databases from CSV files"""
        try:
            self.logger.info(f"Loading first names from {Config.FIRST_NAMES_PATH}")
            with open(Config.FIRST_NAMES_PATH, 'r') as first_name_file:
                reader = csv.reader(first_name_file)
                self.first_names = list(reader)
                
            self.logger.info(f"Loaded {len(self.first_names)} first names")
            
            if not self.first_names:
                raise ValueError("First name file is empty")
                
        except Exception as e:
            self.logger.error(f"Error loading first names: {str(e)}")
            raise ValueError("Failed to load first name database. Please check if First_Name_DB.csv exists.")
        
        try:
            self.logger.info(f"Loading last names from {Config.LAST_NAMES_PATH}")
            with open(Config.LAST_NAMES_PATH, 'r') as last_name_file:
                reader = csv.reader(last_name_file)
                self.last_names = list(reader)
                
            self.logger.info(f"Loaded {len(self.last_names)} last names")
            
            if not self.last_names:
                raise ValueError("Last name file is empty")
                
        except Exception as e:
            self.logger.error(f"Error loading last names: {str(e)}")
            raise ValueError("Failed to load last name database. Please check if Last_Name_DB.csv exists.")
    
    def _load_user_info_file(self):
        """Load user information from CSV file"""
        try:
            self.logger.info(f"Loading user info from {Config.USER_INFO_PATH}")
            with open(Config.USER_INFO_PATH, 'r') as user_info_file:
                reader = csv.reader(user_info_file)
                self.user_infos = list(reader)
                
            self.logger.info(f"Loaded {len(self.user_infos)} user records")
            
            # Skip header row if it exists
            if self.user_infos and "Firstname" in self.user_infos[0][0]:
                self.user_infos = self.user_infos[1:]
                
            self.user_count = len(self.user_infos)
            
            if not self.user_infos:
                raise ValueError("User info file is empty")
                
        except Exception as e:
            self.logger.error(f"Error loading user info: {str(e)}")
            raise ValueError(f"Failed to load user information. Please check if {Config.USER_INFO_PATH} exists.")
    
    def generate_password(self, min_length=None, max_length=None):
        """
        Generate a random secure password
        
        Args:
            min_length (int): Minimum length of password
            max_length (int): Maximum length of password
            
        Returns:
            str: Randomly generated password
        """
        if min_length is None:
            min_length = Config.PASSWORD_MIN_LENGTH
        if max_length is None:
            max_length = Config.PASSWORD_MAX_LENGTH
            
        size = random.randint(min_length, max_length)
        chars = Config.PASSWORD_CHARS
        
        # Ensure password has at least one of each character type
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice(string.punctuation)
        ]
        
        # Fill remaining length with random characters
        password.extend(random.choice(chars) for _ in range(size - 4))
        
        # Shuffle for randomness
        random.shuffle(password)
        
        return ''.join(password)
    
    def generate_random_birthday(self, min_year=1980, max_year=1999):
        """
        Generate a random birthday string
        
        Returns:
            str: Birthday in format MM/DD/YYYY
        """
        month = random.randint(1, 12)
        
        # Adjust day based on month
        if month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        elif month == 2:
            day = random.randint(1, 28)
        else:
            day = random.randint(1, 31)
            
        year = random.randint(min_year, max_year)
        
        return f"{month}/{day}/{year}"
    
    def generate_username(self, first_name, last_name, existing_usernames=None):
        """
        Generate a username based on first and last name
        
        Args:
            first_name (str): First name
            last_name (str): Last name
            existing_usernames (list): List of existing usernames to avoid duplicates
            
        Returns:
            str: Generated username
        """
        # Basic format: firstname.lastname + random digits
        base = f"{first_name.lower()}.{last_name.lower()}"
        
        # Remove non-alphanumeric characters
        base = ''.join(c for c in base if c.isalnum() or c == '.')
        
        # Add random digits
        rand_digits = random.randint(10000, 99999)
        username = f"{base}{rand_digits}"
        
        # Check for duplicates if a list was provided
        if existing_usernames and username in existing_usernames:
            # Try again with different digits
            return self.generate_username(first_name, last_name, existing_usernames)
            
        return username
    
    def get_user_data(self, index):
        """
        Get user data for a specific index
        
        Args:
            index (int): User index
            
        Returns:
            dict: User data including firstname, lastname, password, etc.
        """
        if index >= self.user_count:
            self.logger.error(f"Requested user index {index} exceeds available user count {self.user_count}")
            return None
            
        user_data = {}
        
        if self.auto_generate:
            # Generate random user data
            first_name = random.choice(self.first_names)[0]
            last_name = random.choice(self.last_names)[0]
            password = self.generate_password()
            birthday = self.generate_random_birthday()
            
            existing_usernames = [account['username'] for account in self.created_accounts]
            username = self.generate_username(first_name, last_name, existing_usernames)
            
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'password': password,
                'birthday': birthday,
                'username': username,
                'manual_username': ""
            }
        else:
            # Load from pre-defined user info
            try:
                row = self.user_infos[index]
                user_data = {
                    'first_name': row[0],
                    'last_name': row[1],
                    'password': row[2],
                    'birthday': row[3],
                    'manual_username': row[4] if len(row) > 4 else ""
                }
            except IndexError:
                self.logger.error(f"Error accessing user data at index {index}")
                return None
                
        self.logger.info(f"Generated/loaded user data: {user_data['first_name']} {user_data['last_name']}")
        return user_data
    
    def save_created_account(self, username, password, birthday, phone_number=""):
        """
        Save created account details to file
        
        Args:
            username (str): Gmail username
            password (str): Account password
            birthday (str): Account birthday
            phone_number (str): Phone number used for verification
        """
        # Create account data structure
        account_data = {
            'username': username,
            'password': password,
            'birthday': birthday,
            'phone_number': phone_number,
            'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to in-memory list
        self.created_accounts.append(account_data)
        
        # Save to file
        try:
            with open(Config.CREATED_ACCOUNTS_PATH, 'a') as f:
                f.write(f"{username}\t{password}\t{birthday}\t{phone_number}\n")
            self.logger.info(f"Saved created account: {username}")
        except Exception as e:
            self.logger.error(f"Failed to save created account {username}: {str(e)}")
    
    def get_user_count(self):
        """Get the total number of users to process"""
        return self.user_count