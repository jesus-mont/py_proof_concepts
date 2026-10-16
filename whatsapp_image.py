import os
import time
import pywhatkit as kit
import requests

# 1. Obtener los datos de Pikachu desde PokéAPI
url_api = "https://pokeapi.co/api/v2/pokemon/pikachu"
respuesta = requests.get(url_api)

if respuesta.status_code == 200:
    data = respuesta.json()

    # Extraer la URL de la imagen (Sprite oficial)
    imagen_url = data["sprites"]["other"]["official-artwork"]["front_default"]

    # 2. Descargar la imagen y guardarla localmente
    nombre_archivo = "pikachu.png"
    img_data = requests.get(imagen_url).content

    with open(nombre_archivo, "wb") as f:
        f.write(img_data)

    print("✅ Imagen de Pikachu descargada correctamente.")

    # 3. Configurar el envío por WhatsApp
    # Formato internacional del número: +[Código de país][Número de teléfono]
    numero_destino = "+521234567890"  # Reemplaza con el número real
    mensaje_texto = "¡Hola! Aquí tienes la imagen oficial de Pikachu desde PokéAPI ⚡"

    # Obtener la ruta absoluta de la imagen (requerido por pywhatkit)
    ruta_absoluta = os.path.abspath(nombre_archivo)

    print("⏳ Abriendo WhatsApp Web para enviar el mensaje...")

    # Enviar la imagen
    # pywhatkit abrirá el navegador y enviará la imagen después del tiempo indicado
    kit.sendwhats_image(
        receiver=numero_destino,
        img_path=ruta_absoluta,
        caption=mensaje_texto,
        wait_time=15,  # Tiempo en segundos para esperar a que cargue WhatsApp Web
        tab_close=True,  # Cierra la pestaña del navegador al terminar
    )

    print("🚀 Mensaje procesado con éxito.")
else:
    print(f"❌ Error al consultar PokéAPI: {respuesta.status_code}")