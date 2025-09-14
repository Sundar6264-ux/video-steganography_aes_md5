"""
MD5_Utils.py — Utility functions for generating and verifying MD5 checksums.

⚠️ Note: MD5 is cryptographically broken and should not be used for
      security-sensitive applications. Here it is used only for
      simple integrity verification.
"""

import hashlib


def md5_checksum(text: str) -> str:
    """
    Generate the MD5 checksum for a given text string.

    Args:
        text (str): Input string.

    Returns:
        str: 32-character hexadecimal MD5 checksum.
    """
    hash_object = hashlib.md5()
    hash_object.update(text.encode("utf-8"))
    return hash_object.hexdigest()


def verify_md5_checksum(text: str, original_checksum: str) -> bool:
    """
    Verify whether the MD5 checksum of the given text matches the original.

    Args:
        text (str): Input string to verify.
        original_checksum (str): Expected MD5 checksum.

    Returns:
        bool: True if checksum matches, False otherwise.
    """
    current_checksum = md5_checksum(text)
    return current_checksum == original_checksum


def main() -> None:
    """Demonstration of MD5 checksum generation and verification."""
    text = "Hello, world!"

    original_checksum = md5_checksum(text)
    #print("MD5 checksum:", original_checksum)
    #print("Length:", len(original_checksum))

    # Verification with same text
    print("Verification passed:", verify_md5_checksum(text, original_checksum))

    # Verification with changed text
    print(
        "Verification passed after text change:",
        verify_md5_checksum("Hello, World!", original_checksum),
    )


if __name__ == "__main__":
    main()
