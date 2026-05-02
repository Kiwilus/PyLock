import argparse
import getpass
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Generate a secure key from a password using PBKDF2 with salt.
def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16) # 16 bytes salt is standard and secure

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000, # High iterations make brute-force attacks much harder
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

# Check if a file is likely a PyLock encrypted file.
# Returns True only if it has .pylock extension and sufficient size.
def is_pylock_file(file_path: Path) -> bool:
    if not file_path.exists() or file_path.is_dir():
        return False

    # Must have .pylock extension
    if file_path.suffix.lower() != ".pylock":
        return False

    try:
        size = file_path.stat().st_size
        return size >= 48
    except Exception:
        return False

# Encrypt a file and save it with .pylock extension.
def encrypt_file(file_path: Path, password: str):
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found!")
        sys.exit(1)

    # Prevent encrypting an already encrypted file
    if is_pylock_file(file_path):
        print(f"Error: The file '{file_path.name}' is already encrypted (.pylock).")
        print("   Use --decrypt to decrypt it instead.")
        sys.exit(1)

    print(f"Encrypting {file_path.name} ...")

    # Derive key and salt
    key, salt = derive_key(password)
    fernet = Fernet(key)

    # Read the original file
    data = file_path.read_bytes()

    # Encrypt the data
    encrypted = fernet.encrypt(data)

    # Create output filename: original.ext.pylock
    output_path = file_path.with_suffix(file_path.suffix + ".pylock")

    # Prepend salt to the encrypted data
    output_path.write_bytes(salt + encrypted)

    print(f"Successfully encrypted → {output_path.name}")
    print("   You can now safely share this file.")

# Decrypt a .pylock file and restore the original.
def decrypt_file(file_path: Path, password: str):
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found!")
        sys.exit(1)

    # Prevent trying to decrypt a non-encrypted file
    if not is_pylock_file(file_path):
        print(
            f"Error: The file '{file_path.name}' does not appear to be a PyLock encrypted file."
        )
        print("   Only files with the .pylock extension can be decrypted.")
        print("   Use --encrypt to encrypt a file first.")
        sys.exit(1)

    print(f"Decrypting {file_path.name} ...")

    # Read the encrypted file
    data = file_path.read_bytes()

    # Extract salt (first 16 bytes) and encrypted content
    salt = data[:16]
    encrypted = data[16:]

    key, _ = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted)
    except InvalidToken:
        print("Wrong password or corrupted file!")
        return False
    except Exception as e:
        print(f"Decryption failed: {e}")
        return False

    # Create output filename by removing .pylock extension
    if file_path.name.endswith(".pylock"):
        output_path = file_path.with_suffix("")
    else:
        output_path = file_path.with_name(file_path.stem)

    if output_path.exists():
        output_path = file_path.with_name(
            file_path.stem + "_decrypted" + file_path.suffix.replace(".pylock", "")
        )

    output_path.write_bytes(decrypted)

    print(f"Successfully decrypted → {output_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="PyLock - Securely encrypt and decrypt files with a password"
    )
    parser.add_argument("file", type=Path, help="Path to the file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--encrypt", "-e", action="store_true", help="Encrypt the file")
    group.add_argument("--decrypt", "-d", action="store_true", help="Decrypt the file")

    parser.add_argument(
        "--password",
        "-p",
        type=str,
        help="Password (not recommended - visible in shell history)",
    )

    args = parser.parse_args()

    # Get password
    if args.password:
        password = args.password
        print(
            "⚠ Warning: Using password via command line is insecure (visible in history)!"
        )
    else:
        if args.encrypt:
            password = getpass.getpass("Enter a strong password: ")
            password2 = getpass.getpass("Repeat the password: ")
            if password != password2:
                print("Passwords do not match!")
                sys.exit(1)
        else:
            while True:
                password = getpass.getpass("Enter the password to decrypt: ")

                if decrypt_file(args.file, password):
                    return
                else:
                    print("Try again!\n")

    if args.encrypt:
        encrypt_file(args.file, password)
    else:
        decrypt_file(args.file, password)


if __name__ == "__main__":
    main()

