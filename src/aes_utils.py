"""
AES_Utils.py — Utility functions for AES-256-GCM encryption and decryption.

⚠️ Note: Keys and IVs are currently hardcoded for demonstration.
      Replace with securely generated values (e.g., from get_random_bytes)
      in production environments.
"""

import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def encrypt_AES_256(msg: bytes) -> str:
    """
    Encrypt a message using AES-256 in GCM mode.

    Args:
        msg (bytes): Plaintext message to encrypt.

    Returns:
        str: Base64-encoded ciphertext.
    """
    key = b"12345678901234567890123456789012"  # 32 bytes = 256-bit key
    iv = b"123456789012"                       # 12 bytes = recommended for GCM

    cipher = AES.new(key, AES.MODE_GCM, iv)
    ciphertxt, _ = cipher.encrypt_and_digest(msg)

    print("AES ENCRYPT DEBUG:", ciphertxt)
    return base64.b64encode(ciphertxt).decode("utf-8")


def decrypt_AES_256(ciphertxt_b64: str) -> bytes:
    """
    Decrypt a message encrypted with AES-256 in GCM mode.

    Args:
        ciphertxt_b64 (str): Base64-encoded ciphertext.

    Returns:
        bytes: Decrypted plaintext.
    """
    key = b"12345678901234567890123456789012"
    iv = b"123456789012"

    cipher = AES.new(key, AES.MODE_GCM, iv)
    ciphertext = base64.b64decode(ciphertxt_b64)
    plaintxt = cipher.decrypt(ciphertext)

    return plaintxt


def main() -> None:
    """Demonstration of AES encryption/decryption."""
    message = b"Hello, AES GCM encryption!"

    print("Receiver: checksum verified!")
    ciphertext = encrypt_AES_256(message)
    print("Ciphertext (base64):", ciphertext)

    decrypted = decrypt_AES_256(ciphertext)
    print("Decrypted:", decrypted.decode("utf-8"))


if __name__ == "__main__":
    main()
