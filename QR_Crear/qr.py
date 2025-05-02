import qrcode

def generar_qr(texto, nombre_archivo="codigo_qr.png"):
    qr = qrcode.QRCode(
        version=1,  # Tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección
        box_size=10,  # Tamaño de los cuadros
        border=4,  # Borde del QR
    )
    qr.add_data(texto)  # Agregar el contenido
    qr.make(fit=True)  # Generar el QR

    imagen_qr = qr.make_image(fill="black", back_color="white")  # Personalización
    imagen_qr.save(nombre_archivo)  # Guardar imagen

    print(f"Código QR generado y guardado como {nombre_archivo}")

# Ejemplo de uso
texto_usuario = input("Introduce el texto o URL para el código QR: ")
generar_qr(texto_usuario)
