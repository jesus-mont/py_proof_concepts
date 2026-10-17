import json
import google.auth
import google.auth.crypt
import google.auth.jwt
from google.oauth2 import service_account
import pywhatkit as pwk
import requests

# ==========================================
# CONFIGURACIÓN
# ==========================================
CREDENTIALS_FILE = "credentials.json"
ISSUER_ID = "xxxx"
DESTINATARIO = "+521234567890"

url_api = "https://pokeapi.co/api/v2/pokemon/pikachu"
respuesta = requests.get(url_api)

if respuesta.status_code == 200:
    data = respuesta.json()

    # Extraer la URL de la imagen (Sprite oficial)
    imagen_url = data["sprites"]["other"]["official-artwork"]["front_default"]


def generar_jwt_minimo_corregido():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/wallet_object.issuer"],
    )

    contenido_qr = {"a": 26, "v": 1, "t": 1}

    # Estructura corregida con cardTitle obligatorio
    pase_minimo = {
        "iss": credentials.service_account_email,
        "aud": "google",
        "typ": "savetowallet",
        "payload": {
            "genericObjects": [{
                "id": f"{ISSUER_ID}.=test_11",  # ID nuevo para evitar caché
                "classId": f"{ISSUER_ID}.test_pase_clase",
                "state": "ACTIVE",
                "hexBackgroundColor": "#1B3022",
                "cardTitle": {  # <--- Este campo era el que faltaba
                    "defaultValue": {"language": "es", "value": "PASE DE ACCESO"}
                },
                "header": {
                    "defaultValue": {"language": "es", "value": "Name"}
                },
                "subheader": {  # <--- Evaluando este nuevo campo
                    "defaultValue": {"language": "es", "value": "Matrícula: #x"}
                },
                "logo": {
                    "sourceUri": {
                        "uri": imagen_url
                    },
                    "contentDescription": {  # <--- Este campo suele ser obligatorio para las imágenes
                        "defaultValue": {
                            "language": "es",
                            "value": "Logo"
                        }
                    }
                },
                "heroImage": {
                    "sourceUri": {
                        "uri": imagen_url
                    }
                },
                "barcode": {
                    "type": "QR_CODE",
                    "value": json.dumps(contenido_qr, separators=(",", ":")),
                    "alternateText": "Matrícula #x",
                },
            }]
        },
    }

    signer = google.auth.crypt.RSASigner.from_service_account_file(
        CREDENTIALS_FILE
    )
    token = google.auth.jwt.encode(signer, pase_minimo)

    # Nos aseguramos de decodificar el token a string plano para evitar la 'b' inicial
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return f"https://pay.google.com/gp/v/save/{token}"


if __name__ == "__main__":
    print("Generando enlace mínimo corregido...")
    enlace_final = generar_jwt_minimo_corregido()
    print(f"Enlace generado: {enlace_final}")

    mensaje = f"Prueba de pase de Google Wallet corregido:\n{enlace_final}"

    print("Enviando por WhatsApp...")
    pwk.sendwhatmsg_instantly(
        phone_no=DESTINATARIO, message=mensaje, wait_time=15, tab_close=True
    )
    print("¡Listo! Revisa tu WhatsApp y abre el enlace.")