# STEP 1: Install Required Packages
# Run these in your terminal/command prompt (not inside the Python script)
# ------------------------------------------------------------
# Linux/macOS: sudo apt install gnupg
# Windows: Install GPG from https://www.gnupg.org/download/
# Then install the Python package:
# pip install python-gnupg
# ------------------------------------------------------------

# STEP 2: Prompt for encrypted file path
import os
import gnupg
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Use a file picker dialog to select the .gpg file
Tk().withdraw()
encrypted_filename = askopenfilename(title="Select Encrypted .gpg File", filetypes=[("GPG files", "*.gpg")])

if not encrypted_filename:
    print("❌ No file selected.")
    exit()

print(f"✅ File selected: {encrypted_filename}")

# STEP 3: Decrypt the File using python-gnupg
# Set GPG home if needed; otherwise, use default
gpg = gnupg.GPG()  # Optionally: gnupg.GPG(gnupghome='/path/to/.gnupg')
gpg.encoding = 'utf-8'

# Prompt for passphrase
passphrase = input("🔐 Enter the passphrase used during encryption: ")

# Output filename
decrypted_filename = encrypted_filename.replace(".gpg", "")

# Perform decryption
with open(encrypted_filename, "rb") as f:
    result = gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_filename)

if result.ok:
    print(f"✅ Decryption successful. File saved as: {decrypted_filename}")
else:
    print(f"❌ Decryption failed: {result.stderr}")

# STEP 4 (Optional): Open image if it's a visual file
try:
    from PIL import Image
    img = Image.open(decrypted_filename)
    img.show()
except Exception as e:
    print(f"ℹ️ Decrypted file not displayed (not an image or not supported): {e}")
