import sys
import os
import ast
import argparse
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# Get key from .env (returns None if not found)
KEY_STRING = os.getenv('SECRET_KEY')

if not KEY_STRING:
    print("❌ Error: SECRET_KEY not found in .env file.")
    sys.exit(1)

# Ensure the key is bytes
SECRET_KEY = KEY_STRING.encode() if isinstance(KEY_STRING, str) else KEY_STRING
cipher = Fernet(SECRET_KEY)

def curse(filepath):
    """Turns your beautiful code into a nightmare."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'rb') as f:
        original_code = f.read()
    
    encrypted = cipher.encrypt(original_code)
    
    # We construct a payload that DOES NOT hardcode the key.
    # The runner must also have access to the .env or env vars to run this.
    payload = f"""# Cursed Script
import os
import cryptography.fernet as f
from dotenv import load_dotenv

load_dotenv()
k = os.getenv('SECRET_KEY')
if not k: raise ValueError("Key missing")
if isinstance(k, str): k = k.encode()

c = f.Fernet(k)
# The encrypted blob is stored as a literal bytes object here
encrypted_data = {encrypted!r}
exec(c.decrypt(encrypted_data))"""
    
    with open(filepath, 'w') as f:
        f.write(payload)
    print(f"💀 {filepath} has been obfuscated!")

def bless(filepath):
    """Restores the code so you can actually work on it."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        content = f.read()
    
    try:
        # Extract the literal bytes. We look for the variable assignment in the payload.
        # We look for "encrypted_data = " and the newline after it.
        start_marker = "encrypted_data = "
        start_index = content.find(start_marker) + len(start_marker)
        # Find the end of the line (where the bytes literal ends)
        end_index = content.find('\n', start_index)
        
        encrypted_repr = content[start_index:end_index]
        
        # ast.literal_eval safely converts the string "b'...'" back to bytes
        encrypted_data = ast.literal_eval(encrypted_repr)
        
        decrypted = cipher.decrypt(encrypted_data)
        
        with open(filepath, 'wb') as f:
            f.write(decrypted)
        print(f"✨ {filepath} is back to normal. Happy coding!")
    except Exception as e:
        print(f"❌ Failed to deobfuscate. Is the file actually cursed? Error: {e}")

if __name__ == "__main__":
    # 2. Add Argument Parsing
    parser = argparse.ArgumentParser(description="Obfuscate or de-obfuscate a python file.")
    parser.add_argument("file", help="The file to process")
    parser.add_argument("mode", choices=["curse", "bless"], help="Mode: curse (hide) or bless (reveal)")
    
    args = parser.parse_args()
    
    if args.mode == 'curse':
        curse(args.file)
    elif args.mode == 'bless':
        bless(args.file)