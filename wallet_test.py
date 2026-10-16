import json
import google.auth
import google.auth.crypt
import google.auth.jwt
from google.oauth2 import service_account
import pywhatkit as pwk

# ==========================================
# CONFIGURACIÓN
# ==========================================
CREDENTIALS_FILE = "credentials.json"  # Tu archivo de credenciales de Google Cloud
ISSUER_ID = "3388000000000000000"  # Tu Issuer ID de Google Wallet
DESTINATARIO = "+521234567890"  # Número de teléfono del destinatario con código de país

URL_LOGO_GITHUB = "https://raw.githubusercontent.com/jesus-mont/py_proof_concepts/main/logo_andora.png"
URL_HERO_GITHUB = "https://raw.githubusercontent.com/jesus-mont/py_proof_concepts/main/avatar_j_andora.png"
def firmar_json_a_jwt():
    # 1. Cargar las credenciales de servicio de Google Cloud
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/wallet_object.issuer"],
    )

    # Tu JSON específico que se codificará dentro del código QR
    contenido_qr = {"a": 26, "v": 1, "t": 1}

    # 2. Estructura del pase personalizado con tu diseño y el QR integrado
    tu_json_personalizado = {
        "iss": credentials.service_account_email,
        "aud": "google",
        "typ": "savetowallet",
        "payload": {
            "genericObjects": [{
                "id": f"{ISSUER_ID}.andora_jesus_22",
                "classId": f"{ISSUER_ID}.andora_pase_clase",
                "state": "ACTIVE",
                "hexBackgroundColor": "#1B3022",  # Fondo verde oscuro de tu diseño
                "logo": {
                    "sourceUri": {
                        "uri": "https://tuservidor.com/images/logo_andora.png"
                    },
                    "contentDescription": {
                        "defaultValue": {
                            "language": "es",
                            "value": "Logo Andora",
                        }
                    },
                },
                "heroImage": {
                    "sourceUri": {
                        "uri": "https://tuservidor.com/images/avatar_j_andora.png"
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
                    # Se convierte tu diccionario JSON a una cadena compacta de texto
                    "value": json.dumps(contenido_qr, separators=(",", ":")),
                    "alternateText": "Matrícula #22",
                },
            }]
        },
    }

    # 3. Firmar digitalmente el JSON para convertirlo en JWT
    signer = google.auth.crypt.RSASigner.from_service_account_file(
        CREDENTIALS_FILE
    )
    token = google.auth.jwt.encode(signer, tu_json_personalizado)

    # Crear el enlace final de Google Wallet
    enlace_wallet = f"https://pay.google.com/gp/v/save/{token}"
    return enlace_wallet


if __name__ == "__main__":
    print("Firmando tu JSON personalizado y generando el enlace de Wallet...")
    enlace_final = firmar_json_a_jwt()
    print(f"Enlace generado con éxito: {enlace_final}")

    # Mensaje que se enviará por WhatsApp
    mensaje = (
        "¡Hola Jesus! Aquí tienes tu pase de acceso exclusivo de Andora.\n\n"
        "Haz clic en el siguiente enlace para agregarlo a tu Google Wallet:\n"
        f"{enlace_final}"
    )

    print(
        "Lanzando WhatsApp Web mediante pywhatkit para enviar el mensaje con tu"
        " diseño..."
    )

    # Envía el mensaje de forma inmediata
    pwk.sendwhatmsg_instantly(
        phone_no=DESTINATARIO, message=mensaje, wait_time=15, tab_close=True
    )

    print(
        "¡Proceso finalizado! Revisa que WhatsApp Web haya enviado el mensaje con"
        " tu pase personalizado y el QR configurado."
    )