import json
import time
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
import requests

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES Y DATOS
# ==========================================
# Ruta a tu archivo de credenciales de Google Cloud Service Account
CREDENTIALS_FILE = "credentials.json"

# Tu ID de cuenta de emisor de Google Wallet (lo obtienes en la consola de Google Business)
ISSUER_ID = "3388000000000000000"  # Reemplaza con tu Issuer ID real

# Datos de WhatsApp (puedes usar tu proveedor o la API de Meta)
WHATSAPP_API_URL = "https://api.tu-proveedor-whatsapp.com/v1/messages"
WHATSAPP_TOKEN = "TU_TOKEN_DE_WHATSAPP"
DESTINATARIO = "+521234567890"  # Número de teléfono con código de país


def generar_jwt_google_wallet():
    # 1. Cargar credenciales de la cuenta de servicio
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/wallet_object.issuer"],
    )

    # 2. Definir la estructura del pase genérico (inspirado en tu imagen)
    object_id = f"{ISSUER_ID}.andora_jesus_22"
    class_id = f"{ISSUER_ID}.andora_pase_clase"

    pase_data = {
        "iss": credentials.service_account_email,
        "aud": "google",
        "typ": "savetowallet",
        "payload": {
            "genericObjects": [{
                "id": object_id,
                "classId": class_id,
                "state": "ACTIVE",
                "hexBackgroundColor": (  # Verde oscuro de la imagen
                    "#1B3022"
                ),
                "logo": {
                    "sourceUri": {
                        "uri": "https://tuservidor.com/images/logo_andora.png"
                    },
                    "contentDescription": {
                        "defaultValue": {
                            "language": "es",
                            "value": "Andora Logo",
                        }
                    },
                },
                "heroImage": {
                    "sourceUri": {
                        "uri": (  # Aquí puedes colocar la imagen con la letra "J"
                            "https://tuservidor.com/images/avatar_j_andora.png"
                        )
                    },
                    "contentDescription": {
                        "defaultValue": {
                            "language": "es",
                            "value": "Avatar Jesus",
                        }
                    },
                },
                "header": {
                    "defaultValue": {"language": "es", "value": "Jesus Montaño"}
                },
                "subheader": {
                    "defaultValue": {
                        "language": "es",
                        "value": "Matrícula: #22",
                    }
                },
                "textModulesData": [{
                    "header": "INSTRUCCIÓN",
                    "body": "Presenta este pase al ingresar",
                    "id": "instruccion_ingreso",
                }],
                "barcode": {
                    "type": "QR_CODE",
                    "value": "MATRICULA_22_JESUS_MONTAÑO",
                    "alternateText": "Matrícula #22",
                },
            }]
        },
    }

    # 3. Firmar el JWT utilizando la librería de Google Auth
    signer = google.auth.crypt.RSASigner.from_service_account_file(
        CREDENTIALS_FILE
    )
    payload_bytes = json.dumps(pase_data).encode("utf-8")
    token = google.auth.jwt.encode(signer, pase_data)

    # El enlace oficial para añadir a Google Wallet
    save_url = f"https://pay.google.com/gp/v/save/{token}"
    return save_url


def enviar_whatsapp(enlace_wallet):
    # 4. Enviar el enlace generado a través de WhatsApp
    payload = {
        "to": DESTINATARIO,
        "message": (
            "¡Hola Jesus! Aquí tienes tu pase de acceso exclusivo de Andora.\n\n"
            "Haz clic en el siguiente enlace para agregarlo a tu Google"
            f" Wallet:\n{enlace_wallet}"
        ),
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        print("¡Pase generado y enviado con éxito por WhatsApp!")
    else:
        print(f"Error al enviar por WhatsApp: {response.text}")


# Ejecución principal
if __name__ == "__main__":
    print("Generando enlace de Google Wallet...")
    enlace = generar_jwt_google_wallet()
    print(f"Enlace generado: {enlace}")

    print("Enviando mensaje por WhatsApp...")
    enviar_whatsapp(enlace)