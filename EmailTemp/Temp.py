import random
import time
import requests
import os
import base64
import re
from colorama import Fore, Style, init

init(autoreset=True)

API_URL = "https://api.mail.tm"
processed_message_ids = set()

def print_header(text):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + text.center(50))
    print(Fore.CYAN + Style.BRIGHT + "=" * 50 + "\n")

def print_success(text):
    print(Fore.GREEN + Style.BRIGHT + "[✓] " + text)

def print_error(text):
    print(Fore.RED + Style.BRIGHT + "[✗] " + text)

def print_info(text):
    print(Fore.BLUE + Style.BRIGHT + "[i] " + text)

def create_temp_email():
    try:
        response = requests.get(f"{API_URL}/domains", timeout=10)
        response.raise_for_status()
        domains = response.json()["hydra:member"]
        if not domains:
            raise Exception("No hay dominios disponibles.")
        domain = domains[0]["domain"]
        email = f"user{int(time.time())}{random.randint(1000, 9999)}@{domain}"
        password = "password123"
        account_data = {"address": email, "password": password}
        response = requests.post(f"{API_URL}/accounts", json=account_data, timeout=10)
        response.raise_for_status()
        print_success(f"Tu basura a llegado: {email}")
        return email, password
    except Exception as e:
        print_error(f"Error al crear el correo temporal: {e}")
        return None, None

def login_temp_email(email, password):
    try:
        response = requests.post(f"{API_URL}/token", json={"address": email, "password": password}, timeout=10)
        response.raise_for_status()
        return response.json()["token"]
    except Exception as e:
        print_error(f"Error al iniciar sesión: {e}")
        return None

def download_attachments(message_data, headers):
    attachments = message_data.get("attachments", [])
    for attach in attachments:
        attachment_id = attach["id"]
        filename = attach.get("filename", f"adjunto_{attachment_id}")
        download_url = attach.get("downloadUrl")

        if download_url:
            full_download_url = f"{API_URL}{download_url}"
            try:
                print_info(f"Descargando adjunto: {filename}")
                file_data = requests.get(full_download_url, headers=headers, stream=True, timeout=10)
                file_data.raise_for_status()
                with open(os.path.join(os.getcwd(), filename), "wb") as f:
                    for chunk in file_data.iter_content(chunk_size=8192):
                        f.write(chunk)
                print_success(f"Archivo '{filename}' descargado correctamente.")
            except Exception as e:
                print_error(f"Error al descargar el adjunto '{filename}': {e}")
        else:
            print_error(f"El adjunto '{filename}' no tiene una URL de descarga disponible.")

def extract_and_save_inline_images(html_content):
    img_tags = re.findall(r'<img[^>]+src="data:image/[^"]+"', html_content)
    for i, img_tag in enumerate(img_tags):
        match = re.search(r'data:image/([^;]+);base64,([^"+]+)', img_tag)
        if match:
            image_type = match.group(1)
            image_data = match.group(2)
            image_bytes = base64.b64decode(image_data)
            filename = f"inline_image_{i}.{image_type}"
            with open(filename, 'wb') as image_file:
                image_file.write(image_bytes)
            print_success(f"Imagen incrustada guardada como {filename}")

def check_inbox(token):
    headers = {"Authorization": f"Bearer {token}"}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/messages", headers=headers, timeout=30)
            response.raise_for_status()
            messages = response.json()["hydra:member"]
            break
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print_error(f"Error al conectar (intento {attempt+1}/{max_retries}). Reintentando en 5s...")
                time.sleep(5)
            else:
                print_error(f"Error al revisar la bandeja de entrada: {e}")
                return []

    new_messages = [msg for msg in messages if msg["id"] not in processed_message_ids]

    for message in new_messages:
        message_id = message["id"]
        try:
            response = requests.get(f"{API_URL}/messages/{message_id}", headers=headers, timeout=10)
            response.raise_for_status()
            detailed_data = response.json()

            processed_message_ids.add(message_id)

            sender = detailed_data["from"]["address"]
            subject = detailed_data.get("subject", "(Sin asunto)")
            text_content = detailed_data.get("text", "Sin contenido disponible.")

            print_header("Nuevo mensaje recibido")
            print(Fore.YELLOW + Style.BRIGHT + f"De: {sender}")
            print(Fore.YELLOW + Style.BRIGHT + f"Asunto: {subject}")
            if text_content.strip():
                print(Fore.WHITE + Style.NORMAL + f"Contenido:\n{text_content.strip()}\n")

            html_content = detailed_data.get("html", "")
            if isinstance(html_content, list):
                html_content = ''.join(html_content)

            if html_content and isinstance(html_content, str):
                extract_and_save_inline_images(html_content)

            download_attachments(detailed_data, headers)

        except Exception as e:
            print_error(f"Error al procesar el mensaje {message_id}: {e}")

    return new_messages

def main():
    print_header("TrashMail by Kovax00")
    print_info("Creando correo temporal...\n")
    email, password = create_temp_email()

    if not email or not password:
        print_error("No se pudo crear el correo temporal. Saliendo...")
        return

    print_info("Iniciando sesión...\n")
    token = login_temp_email(email, password)

    if not token:
        print_error("No se pudo iniciar sesión. Saliendo...")
        return

    print_success("Sesión iniciada correctamente.")
    print_info("Esperando mensajes en el buzón... (Presiona Ctrl + C para salir)")

    try:
        while True:
            messages = check_inbox(token)
            if messages:
                print_info("Esperando más mensajes...")
            time.sleep(10)
    except KeyboardInterrupt:
        print_error("A la mierda x.x")

if __name__ == "__main__":
    main()