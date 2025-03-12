import os
from cryptography.fernet import Fernet
import requests
import logging
from tkinter import simpledialog, messagebox
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    result = os.path.join(base_path, relative_path)
    logging.info(f"Resource path for {relative_path}: {result}")
    return result

class TokenManager:
    def __init__(self, token_file="resources/token.enc", key_file="resources/key.key"):
        # Determine if running as an app bundle
        if getattr(sys, 'frozen', False):
            # Running as bundled app - use user's home directory for persistent files
            self.resources_dir = os.path.join(os.path.expanduser("~"), "CaughtUP", "resources")
            os.makedirs(self.resources_dir, exist_ok=True)
            
            self.token_file = os.path.join(self.resources_dir, os.path.basename(token_file))
            self.key_file = os.path.join(self.resources_dir, os.path.basename(key_file))
            self.config_file = os.path.join(self.resources_dir, "config.txt")
        else:
            # Running in development
            self.resources_dir = os.path.dirname(token_file)
            if not os.path.isabs(self.resources_dir):
                self.resources_dir = os.path.abspath(self.resources_dir)
                
            self.token_file = os.path.abspath(token_file)
            self.key_file = os.path.abspath(key_file)
            self.config_file = os.path.join(self.resources_dir, "config.txt")
        
        logging.info(f"Resources directory: {self.resources_dir}")
        logging.info(f"Token file path: {self.token_file}")
        logging.info(f"Key file path: {self.key_file}")
        logging.info(f"Config file path: {self.config_file}")
        
        os.makedirs(self.resources_dir, exist_ok=True)
        
        self.base_url = None
        self.token = None
        
        self.load_or_request_token()
        self.load_or_request_base_url()
        logging.info(f"Initialized TokenManager with base_url: {self.base_url}, token_file: {self.token_file}, key_file: {self.key_file}")
    
    def load_or_request_token(self):
        # Attempt to load token first
        try:
            self.token = self.load_token()
            logging.info("Token successfully loaded and validated.")
            return
        except FileNotFoundError:
            logging.warning("Token file not found. Requesting new token input.")
        except Exception as e:
            logging.error(f"Error loading token: {e}. Requesting new token input.")
        
        while True:
            self.token = simpledialog.askstring("API Token Required", "Enter your API Token:")
            if not self.token:
                messagebox.showerror("Error", "A valid API Token is required. Exiting.")
                raise ValueError("No API Token provided.")
            self.encrypt_token(self.token)
            logging.info("New token received and encrypted.")
            break
    
    def load_or_request_base_url(self):
        # Attempt to load base_url from config file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    for line in f:
                        if line.startswith("base_url="):
                            self.base_url = line.strip().split("=", 1)[1]
                            if self.is_base_url_valid():
                                logging.info(f"Base URL successfully loaded from config file: {self.base_url}")
                                return
                            else:
                                logging.warning("Base URL from config file is invalid, requesting new input.")
            except Exception as e:
                logging.warning(f"Failed to read base_url from config file: {e}")
        
        # Request input if base_url is missing or invalid
        while True:
            self.base_url = simpledialog.askstring("Base URL Required", "Enter the Canvas API base URL (must start with https://):")
            if not self.base_url:
                messagebox.showerror("Error", "A valid base URL is required. Exiting.")
                raise ValueError("No base URL provided.")
            
            if self.base_url.startswith("https://") and self.is_base_url_valid():
                logging.info(f"Base URL successfully validated: {self.base_url}")
                try:
                    with open(self.config_file, "w") as f:
                        f.write(f"base_url={self.base_url}\n")
                    logging.info("Base URL saved to config file.")
                except Exception as e:
                    logging.warning(f"Failed to save base_url to config file: {e}")
                break
            else:
                messagebox.showerror("Error", "Invalid or unreachable base URL. Please enter a valid URL.")
    
    def is_base_url_valid(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/api/v1/accounts", headers=headers, timeout=5)
            valid = response.status_code == 200
            if valid:
                logging.info("Base URL is reachable and valid.")
            else:
                logging.warning("Base URL validation failed.")
            return valid
        except requests.RequestException as e:
            logging.error(f"Request to validate base URL failed: {e}")
            return False
    
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