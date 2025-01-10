from backup_manager.token_manager import TokenManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

BASE_URL = "https://<institution>.instructure.com:443"  # Replace with your Canvas instance base URL
VALID_TOKEN = "<your_api_token>"          # Replace with a valid Canvas API token
INVALID_TOKEN = "123123123123123123123"

if __name__ == "__main__":
    token_manager = TokenManager(base_url=BASE_URL)

    # Test 1: Encrypt and Decrypt Token
    print("Testing encryption and decryption...")
    token_manager.encrypt_token(VALID_TOKEN)
    try:
        decrypted_token = token_manager.decrypt_token()
        assert decrypted_token == VALID_TOKEN
        print("Encryption and decryption test passed!")
    except Exception as e:
        print(f"Encryption and decryption test failed: {e}")

    # Test 2: Validate Token
    print("Testing token validation...")
    if token_manager.validate_token(VALID_TOKEN):
        print("Token validation passed!")
    else:
        print("Token validation failed!")

    # Test 3: Validate Invalid Token
    print("Testing invalid token validation...")
    if not token_manager.validate_token(INVALID_TOKEN):
        print("Invalid token validation passed!")
    else:
        print("Invalid token validation failed!")

    # Test 4: Reset Token
    print("Testing token reset...")
    token_manager.reset_token()
    try:
        token_manager.decrypt_token()
        print("Token reset failed!")
    except FileNotFoundError:
        print("Token reset passed!")
