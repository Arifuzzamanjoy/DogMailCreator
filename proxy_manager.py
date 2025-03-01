"""
Proxy management module for Gmail Creator
Handles proxy acquisition, verification, and rotation
"""
import random
import requests
from fp.fp import FreeProxy
from config import Config
import logging

class ProxyManager:
    """
    Manages proxies for automated browsing
    Provides methods to obtain and verify working proxies
    """
    
    def __init__(self):
        self.logger = logging.getLogger('gmail_creator.proxy')
        self.max_retries = Config.PROXY_RETRIES
        self.timeout = Config.PROXY_TIMEOUT
        self._current_proxy = None
    
    @property
    def current_proxy(self):
        """Return the current working proxy"""
        if not self._current_proxy:
            self._current_proxy = self.get_working_proxy()
        return self._current_proxy
    
    def reset_proxy(self):
        """Reset the current proxy and get a new one"""
        self._current_proxy = None
        return self.current_proxy
    
    def get_working_proxy(self):
        """
        Obtain a working proxy with retry logic
        
        Returns:
            str: Working proxy URL or None if no working proxy found
        """
        self.logger.info(f"Attempting to get proxy from FreeProxy service (max attempts: {self.max_retries})")
        
        for attempt in range(self.max_retries):
            try:
                proxy = FreeProxy(rand=True, timeout=self.timeout).get()
                
                if not proxy:
                    self.logger.warning(f"FreeProxy returned None (attempt {attempt+1}/{self.max_retries})")
                    continue
                
                self.logger.info(f"Testing proxy: {proxy} (attempt {attempt+1}/{self.max_retries})")
                
                if self.verify_proxy(proxy):
                    self.logger.info(f"Found working proxy: {proxy}")
                    return proxy
                else:
                    self.logger.warning(f"Proxy verification failed for: {proxy}")
            except Exception as e:
                self.logger.error(f"Error getting proxy (attempt {attempt+1}/{self.max_retries}): {str(e)}")
        
        self.logger.warning("All proxy attempts failed - proceeding without proxy")
        return None
    
    def verify_proxy(self, proxy, test_url="https://accounts.google.com", timeout=3):
        """
        Test if the proxy works specifically with Google domains
        
        Args:
            proxy (str): Proxy URL to test
            test_url (str): URL to test against
            timeout (int): Connection timeout in seconds
            
        Returns:
            bool: True if proxy works, False otherwise
        """
        try:
            proxies = {
                "http": proxy,
                "https": proxy
            }
            
            response = requests.get(
                test_url, 
                proxies=proxies, 
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
            )
            
            if response.status_code == 200:
                self.logger.info(f"Proxy verified working with {test_url}")
                return True
            else:
                self.logger.warning(f"Proxy returned status code {response.status_code} for {test_url}")
                return False
                
        except requests.RequestException as e:
            self.logger.warning(f"Proxy verification failed: {str(e)}")
            return False
            
    def get_proxy_options(self):
        """
        Get proxy configuration for selenium-wire
        
        Returns:
            dict: Proxy configuration dictionary or empty dict if no proxy
        """
        proxy_options = {'no_proxy': 'localhost,127.0.0.1'}
        
        if self.current_proxy:
            proxy_options['http'] = self.current_proxy
            proxy_options['https'] = self.current_proxy
            
        return proxy_options