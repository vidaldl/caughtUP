import os
from cryptography.fernet import Fernet
import requests
import logging
from tkinter import simpledialog, messagebox
import sys
from platform_utils import get_app_data_dir, get_resource_path

class TokenManager:
    def __init__(self, token_file="token.enc", key_file="key.key"):
        # Get the platform-appropriate application data directory
        self.app_data_dir = get_app_data_dir()
        self.resources_dir = os.path.join(self.app_data_dir, "resources")
        os.makedirs(self.resources_dir, exist_ok=True)
        
        # Set file paths using the app data directory
        self.token_file = os.path.join(self.resources_dir, token_file)
        self.key_file = os.path.join(self.resources_dir, key_file)
        self.config_file = os.path.join(self.resources_dir, "config.txt")
        
        logging.info(f"Resources directory: {self.resources_dir}")
        logging.info(f"Token file path: {self.token_file}")
        logging.info(f"Key file path: {self.key_file}")
        logging.info(f"Config file path: {self.config_file}")
        
        self.base_url = None
        self.token = None
        
        # CORRECT ORDER: Base URL first, then token
        self.load_or_request_base_url()
        self.load_or_request_token()
        logging.info(f"Initialized TokenManager with base_url: {self.base_url}, token_file: {self.token_file}, key_file: {self.key_file}")
    
    def is_connection_valid(self):
        """
        Validates the connection using current token and base_url.
        Returns: (is_valid: bool, error_type: str, status_code: int)
        """
        if not self.base_url:
            return False, "missing_base_url", 0
        if not self.token:
            return False, "missing_token", 0
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/api/v1/accounts", headers=headers, timeout=5)
            
            if response.status_code == 200:
                logging.info("Connection is valid.")
                return True, "success", 200
            elif response.status_code == 401:
                logging.warning("Token is unauthorized.")
                return False, "unauthorized", 401
            elif response.status_code == 404:
                logging.warning("API endpoint not found - likely wrong base URL.")
                return False, "invalid_url", 404
            else:
                logging.error(f"Unexpected status code: {response.status_code}")
                return False, "other_error", response.status_code
                
        except requests.ConnectionError:
            logging.error("Cannot connect to server - check base URL.")
            return False, "connection_error", 0
        except requests.Timeout:
            logging.error("Connection timed out.")
            return False, "timeout", 0
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return False, "request_error", 0

    def generate_key(self):
        if not os.path.exists(self.key_file):
            logging.info("Key file not found. Generating a new encryption key.")
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)
            logging.info(f"Encryption key generated and saved to {self.key_file}.")
        else:
            logging.info("Encryption key already exists.")

    def encrypt_token(self, token: str):
        logging.info("Encrypting token.")
        self.generate_key()
        with open(self.key_file, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(token.encode())
        with open(self.token_file, "wb") as f:
            f.write(encrypted_token)
        logging.info(f"Token encrypted and saved to {self.token_file}.")
    
    def decrypt_token(self) -> str:
        if not os.path.exists(self.token_file) or not os.path.exists(self.key_file):
            logging.info("Token or key file is missing. Cannot decrypt.")
            raise FileNotFoundError("Token or key file is missing.")
        with open(self.key_file, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        with open(self.token_file, "rb") as f:
            encrypted_token = f.read()
        return fernet.decrypt(encrypted_token).decode()
    
    def reset_token(self):
        logging.info("Resetting token.")
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
    
    def get_token(self):
        if self.token is None:
            self.token = self.load_token()
        return self.token
    
    def load_token(self):
        if os.path.exists(self.token_file) and os.path.exists(self.key_file):
            with open(self.key_file, "rb") as key_file:
                key = key_file.read()
            fernet = Fernet(key)
            with open(self.token_file, "rb") as token_file:
                encrypted_token = token_file.read()
            return fernet.decrypt(encrypted_token).decode()
        else:
            raise FileNotFoundError("Token or key file not found. Please set the token first.")
    
    def load_or_request_base_url(self):
        """Load existing base_url or request new one. Must be valid before token validation."""
        # Try to load existing base_url
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    for line in f:
                        if line.startswith("base_url="):
                            self.base_url = line.strip().split("=", 1)[1]
                            
                            # Test if base_url is reachable (without token)
                            if self._test_base_url_reachability():
                                logging.info(f"Base URL loaded and is reachable: {self.base_url}")
                                return
                            else:
                                logging.warning("Saved base URL is not reachable.")
                                
            except Exception as e:
                logging.warning(f"Failed to read base_url from config: {e}")
        
        # Request new base_url with validation
        while True:
            self.base_url = simpledialog.askstring(
                "Base URL Required", 
                "Enter the Canvas API base URL\n(e.g., https://institution.instructure.com):"
            )
            
            if not self.base_url:
                messagebox.showerror("Error", "A valid base URL is required.")
                raise ValueError("No base URL provided.")
            
            if not self.base_url.startswith("https://"):
                messagebox.showerror("Error", "Base URL must start with https://")
                continue
                
            # Test base URL reachability
            if self._test_base_url_reachability():
                logging.info(f"Base URL validated: {self.base_url}")
                self._save_base_url()
                return
            else:
                messagebox.showerror(
                    "Connection Error", 
                    "Cannot reach the specified URL. Please check the address and try again."
                )
                continue

    def _test_base_url_reachability(self):
        """Test if base_url is reachable without requiring a valid token."""
        try:
            # Try to reach a public endpoint or just test connectivity
            response = requests.get(f"{self.base_url}/api/v1/accounts", timeout=5)
            # We expect 401 (unauthorized) which means the URL is reachable
            # We also accept 200, 403, or other responses that indicate the server is responding
            if response.status_code in [200, 401, 403]:
                return True
            elif response.status_code == 404:
                # 404 might mean wrong URL structure
                return False
            else:
                # Other status codes might still indicate a reachable server
                logging.warning(f"Base URL test returned status {response.status_code}, assuming reachable")
                return True
                
        except requests.ConnectionError:
            logging.error("Cannot connect to base URL")
            return False
        except requests.Timeout:
            logging.error("Base URL connection timed out")
            return False
        except requests.RequestException as e:
            logging.error(f"Error testing base URL: {e}")
            return False

    def load_or_request_token(self):
        """Load existing token or request new one. Requires valid base_url first."""
        if not self.base_url:
            raise ValueError("Base URL must be set before loading token")
            
        # Try to load existing token
        try:
            self.token = self.load_token()
            logging.info("Token loaded from file.")
            
            # Validate token with the base_url
            is_valid, error_type, _ = self.is_connection_valid()
            if is_valid:
                logging.info("Existing token is valid.")
                return
            elif error_type == "unauthorized":
                logging.warning("Existing token is unauthorized, requesting new one.")
            else:
                logging.warning(f"Token validation failed: {error_type}")
                    
        except FileNotFoundError:
            logging.warning("No existing token found.")
        except Exception as e:
            logging.error(f"Error loading token: {e}")
        
        # Request new token with validation loop
        max_attempts = 3
        for attempt in range(max_attempts):
            self.token = simpledialog.askstring(
                "API Token Required", 
                f"Enter your Canvas API Token (attempt {attempt + 1}/{max_attempts}):"
            ).strip()
            
            if not self.token:
                if attempt == max_attempts - 1:
                    messagebox.showerror("Error", "A valid API Token is required. Exiting.")
                    raise ValueError("No API Token provided.")
                continue
                
            # Validate new token with base_url
            is_valid, error_type, _ = self.is_connection_valid()
            if is_valid:
                self.encrypt_token(self.token)
                logging.info("New token validated and encrypted.")
                return
            elif error_type == "unauthorized":
                messagebox.showerror("Invalid Token", "The provided token is not authorized. Please try again.")
                continue
            else:
                messagebox.showerror("Error", f"Token validation failed: {error_type}")
                continue
        
        raise ValueError("Failed to get valid token after maximum attempts.")

    def _save_base_url(self):
        """Helper method to save base_url to config file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                f.write(f"base_url={self.base_url}\n")
            logging.info("Base URL saved to config file.")
        except Exception as e:
            logging.warning(f"Failed to save base_url to config: {e}")