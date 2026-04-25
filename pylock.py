import argparse
import getpass
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Generates a secure key from a password (using salt)
def derive_key(password: str, salt: bytes = None) -> bytes:
    if salt is None:
        salt = os.urandom(16)  # 16 bytes salt is standard and secure

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,  # high iterations = safer against brute force
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

# Encrypts a file and saves it as .pylock
def encrypt_file(file_path: Path, password: str):
    if not file_path.exists():
        print(f"Error: file {file_path} not found!")
        sys.exit(1)

    print(f"Encrypting {file_path} ...")

    # Deriving Salt + Key
    key, salt = derive_key(password)
    fernet = Fernet(key)

    # read file
    data = file_path.read_bytes()

    # encrypt
    encrypted = fernet.encrypt(data)

    # Output file: originalname.pylock
    output_path = file_path.with_suffix(file_path.suffix + ".pylock")

    # Append salt to the front (so the recipient can use it when decrypting)
    output_path.write_bytes(salt + encrypted)

    print(f"Encrypted saved as: {output_path}")
    print("   your file is now encrypted")

# decrypts a .pylock file
def decrypt_file(file_path: Path, password: str):
    if not file_path.exists():
        print(f"Error: file {file_path} not found!")
        sys.exit(1)

    print(f"Decrypting {file_path} ...")

    data = file_path.read_bytes()

    # first 16 Bytes = Salt
    salt = data[:16]
    encrypted = data[16:]

    # Derive Key from Password + Salt
    key, _ = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception:
        print("Wrong password or corrupted file!")
        sys.exit(1)

    # Ausgabedatei ohne .pylock-Endung
    if file_path.suffix == ".pylock":
        output_path = file_path.with_suffix("")
    else:
        output_path = file_path.with_name(file_path.name + ".decrypted")

    output_path.write_bytes(decrypted)

    print(f"Decrypted saved as: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="PyLock - Securely encrypt and decrypt files with password"
    )
    parser.add_argument("file", type=Path, help="path to file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--encrypt", "-e", action="store_true", help="Encrypt file")
    group.add_argument("--decrypt", "-d", action="store_true", help="decrypt file")

    # Passwort kann über Kommandozeile kommen (nicht empfohlen) oder interaktiv
    parser.add_argument("--password", "-p", type=str, help="Password (unsafe in the history!)")

    args = parser.parse_args()

    # Passwort holen
    if args.password:
        password = args.password
        print("⚠Warning: Password via command line is insecure (appears in the shell history)!")
    else:
        if args.encrypt:
            password = getpass.getpass("Enter a strong password: ")
            password2 = getpass.getpass("repeat the password: ")
            if password != password2:
                print("password do not match!")
                sys.exit(1)
        else:
            password = getpass.getpass("Enter the password to decrypt: ")

    if args.encrypt:
        encrypt_file(args.file, password)
    else:
        decrypt_file(args.file, password)


if __name__ == "__main__":
    main()