import os
from cryptography.fernet import Fernet
import requests
import logging

class TokenManager:
    def __init__(self, base_url, token_file="resources/token.enc", key_file="resources/key.key"):
        self.base_url = base_url
        self.token_file = token_file
        self.key_file = key_file
        self.token = None
        logging.info(f"Initialized TokenManager with base_url: {self.base_url}, token_file: {self.token_file}, key_file: {self.key_file}")

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
        logging.info("Decrypting token.")
        with open(self.key_file, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        with open(self.token_file, "rb") as f:
            encrypted_token = f.read()
        try:
            decrypted_token = fernet.decrypt(encrypted_token).decode()
            logging.info("Token successfully decrypted.")
            return decrypted_token
        except Exception as e:
            logging.info("Failed to decrypt the token. It might be corrupted or tampered with.")
            raise ValueError("Failed to decrypt the token. It might be corrupted or tampered with.") from e

    def validate_token(self, token: str) -> bool:
        logging.info("Validating token with Canvas LMS API.")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{self.base_url}/api/v1/users/self", headers=headers)
            response.raise_for_status()
            logging.info("Token validation successful.")
            return True
        except requests.exceptions.RequestException as e:
            logging.info(f"Token validation failed. Error: {e}")
            return False

    def reset_token(self):
        logging.info("Resetting token.")
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            logging.info(f"Token file {self.token_file} deleted.")
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
            logging.info(f"Key file {self.key_file} deleted.")

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
