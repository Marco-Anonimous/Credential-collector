import smtplib
import os
import time
import sys
from colorama import *

init(autoreset=True)

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.0001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def input_typewriter(prompt, delay=0.001):
    for char in prompt:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    return input(Fore.GREEN)

tag = """ [====================================-byCipherX-==================================]
"""

logo = """
[====================================-byCipherX-==================================]

███████╗███╗   ███╗ █████╗ ██╗██╗         ███████╗██████╗  █████╗ ███╗   ███╗
██╔════╝████╗ ████║██╔══██╗██║██║         ██╔════╝██╔══██╗██╔══██╗████╗ ████║
█████╗  ██╔████╔██║███████║██║██║         ███████╗██████╔╝███████║██╔████╔██║
██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║
███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ███████║██║     ██║  ██║██║ ╚═╝ ██║
╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝

[====================================-byCipherX-==================================]
"""

# Solo Gmail y Yandex
smtp_proveedores = {
    "1": {"nombre": "Gmail", "servidor": "smtp.gmail.com", "puerto": 587, "nota": "Usa contraseña de aplicación"},
    "2": {"nombre": "Yandex", "servidor": "smtp.yandex.com", "puerto": 587, "nota": "Usa contraseña normal"},
}

def mostrar_menu_proveedores():
    print(logo)
    print(Fore.CYAN + "Selecciona el proveedor que deseas usar:\n")
    for key, value in smtp_proveedores.items():
        print(f"[{key}] {value['nombre']} - {value['nota']}")
    print()

# Selección del proveedor
limpiar_pantalla()
mostrar_menu_proveedores()
opcion = input(Fore.GREEN + "[==> ")

if opcion not in smtp_proveedores:
    typewriter(tag + "[ERROR] Opción no válida. Cerrando...")
    sys.exit()

proveedor = smtp_proveedores[opcion]

# Ingreso de datos
limpiar_pantalla()
email = input_typewriter(logo + f"USANDO SMTP DE {proveedor['nombre'].upper()}\n\nINGRESA TU CORREO :) :\n[==> ")
limpiar_pantalla()

vers = input_typewriter(tag + "AHORA INGRESA EL CORREO DESTINO :) :\n[==> ")
limpiar_pantalla()

subject = input_typewriter(tag + "INGRESA EL ASUNTO DEL CORREO :) :\n[==> ")
limpiar_pantalla()

message = input_typewriter(tag +"INGRESA EL MENSAJE O LINK :) :\n[==> ")
limpiar_pantalla()

nombre = int(input_typewriter(tag +"INTRODUCE EL NUMERO DE CORREOS A ENVIAR :\n[==> "))
limpiar_pantalla()

text = f"Subject: {subject}\n\n{message}"

token = input_typewriter(tag + f"INGRESA TU CONTRASEÑA ({proveedor['nota']}) :\n[==> ")
limpiar_pantalla()

# Envío de correos
try:
    server = smtplib.SMTP(proveedor["servidor"], proveedor["puerto"])
    server.starttls()
    server.login(email, token)

    for i in range(nombre):
        server.sendmail(email, vers, text)
        print(Fore.YELLOW + f"[+] Correo {i+1} enviado a {vers}")

    typewriter(tag + f"TODOS LOS CORREOS SE ENVIARON EXITOSAMENTE.")
    server.quit()

except Exception as e:
    typewriter(tag + f"[ERROR] ALGO SALIÓ MAL : {e}")