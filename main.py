"""
Main entry point for Gmail Creator Application
Provides command-line interface and execution control
"""
import os
import sys
import logging
import argparse
import traceback
from datetime import datetime

from account_creator import AccountCreator
from phone_verification import PhoneVerificationManager
from config import Config


def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration with file and console output
    
    Args:
        log_level: Logging level to use
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"gmail_creator_{timestamp}.log"
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/{log_filename}"),
            logging.StreamHandler()
        ]
    )


def parse_arguments():
    """
    Parse command-line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Gmail Account Creator')
    
    # Operation mode options
    parser.add_argument('--auto-generate', action='store_true', default=Config.AUTO_GENERATE_USERINFO,
                        help='Auto-generate user information instead of using CSV file')
    parser.add_argument('--count', type=int, default=Config.AUTO_GENERATE_NUMBER,
                        help='Number of accounts to create when auto-generating')
    
    # Browser options
    parser.add_argument('--browser', choices=['chrome', 'firefox'], default='chrome',
                        help='Browser to use for automation')
    parser.add_argument('--no-proxy', action='store_true', 
                        help='Disable proxy usage')
    
    # File paths
    parser.add_argument('--csv-file', type=str, default=None,
                        help='Path to CSV file with user information')
    parser.add_argument('--output-file', type=str, default=Config.CREATED_ACCOUNTS_PATH,
                        help='Path to file for saving created accounts')
    
    # Advanced options
    parser.add_argument('--check-balance', action='store_true',
                        help='Check SMS service balance and exit')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    return parser.parse_args()


def check_prerequisites():
    """Check if all prerequisites are met before running"""
    logger = logging.getLogger('gmail_creator.main')
    
    # Check if data directory exists
    if not os.path.exists('./data'):
        logger.warning("Data directory not found - creating it")
        os.makedirs('./data', exist_ok=True)
    
    # Check for name databases if in auto-generate mode
    if Config.AUTO_GENERATE_USERINFO:
        if not os.path.exists(Config.FIRST_NAMES_PATH):
            logger.error(f"First name database not found at {Config.FIRST_NAMES_PATH}")
            return False
            
        if not os.path.exists(Config.LAST_NAMES_PATH):
            logger.error(f"Last name database not found at {Config.LAST_NAMES_PATH}")
            return False
    else:
        # Check for user info CSV
        if not os.path.exists(Config.USER_INFO_PATH):
            logger.error(f"User info CSV not found at {Config.USER_INFO_PATH}")
            return False
    
    return True


def check_sms_balance():
    """
    Check SMS service balance
    
    Returns:
        float: Account balance or None if check failed
    """
    logger = logging.getLogger('gmail_creator.main')
    logger.info("Checking SMS service balance")
    
    phone_manager = PhoneVerificationManager()
    balance = phone_manager.check_balance()
    
    if balance is not None:
        logger.info(f"Current SMS service balance: ${balance:.2f}")
        if balance < 1.0:
            logger.warning("Low balance! You may not have enough funds for verification.")
    else:
        logger.error("Failed to check SMS service balance")
    
    return balance


def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(log_level=logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger('gmail_creator.main')
    
    logger.info("Starting Gmail Creator")
    logger.info(f"Arguments: {args}")
    
    # Handle special command: check balance
    if args.check_balance:
        check_sms_balance()
        return
    
    # Override config with command-line arguments
    if args.csv_file:
        Config.USER_INFO_PATH = args.csv_file
    
    if args.output_file:
        Config.CREATED_ACCOUNTS_PATH = args.output_file
    
    # Validate prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed. Cannot continue.")
        return 1
    
    # Check SMS balance before starting
    balance = check_sms_balance()
    if balance is not None and balance < 0.5:
        logger.error("SMS service balance too low. Please add funds and try again.")
        return 1
    
    try:
        # Initialize account creator
        creator = AccountCreator(
            auto_generate=args.auto_generate,
            user_count=args.count,
            use_proxy=not args.no_proxy,
            browser_type=args.browser
        )
        
        # Start account creation
        start_time = datetime.now()
        success_count = creator.create_accounts()
        end_time = datetime.now()
        
        # Output summary
        duration = (end_time - start_time).total_seconds() / 60.0  # in minutes
        logger.info(f"Account creation completed in {duration:.2f} minutes")
        logger.info(f"Successfully created {success_count} accounts")
        logger.info(f"Created accounts saved to {Config.CREATED_ACCOUNTS_PATH}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())