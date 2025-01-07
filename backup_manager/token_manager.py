import os
from cryptography.fernet import Fernet
import requests

class TokenManager:
    def __init__(self, base_url, token_file="resources/token.enc", key_file="resources/key.key"):
        self.base_url = base_url
        self.token_file = token_file
        self.key_file = key_file

    def generate_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)

    def encrypt_token(self, token: str):
        self.generate_key()
        with open(self.key_file, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(token.encode())
        with open(self.token_file, "wb") as f:
            f.write(encrypted_token)

    def decrypt_token(self) -> str:
        if not os.path.exists(self.token_file) or not os.path.exists(self.key_file):
            raise FileNotFoundError("Token or key file is missing.")
        with open(self.key_file, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        with open(self.token_file, "rb") as f:
            encrypted_token = f.read()
        try:
            return fernet.decrypt(encrypted_token).decode()
        except Exception as e:
            raise ValueError("Failed to decrypt the token. It might be corrupted or tampered with.") from e

    def validate_token(self, token: str) -> bool:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{self.base_url}/api/v1/users/self", headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            return False

    def reset_token(self):
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
