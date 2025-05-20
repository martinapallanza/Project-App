import socket
import threading
import base64
import io
from PIL import Image
 
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8090
 
def start_server():
    """Avvia il server backend per gestire richieste."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((BACKEND_HOST, BACKEND_PORT))
        server.listen()
        print(f"🟢 Server backend in ascolto su {BACKEND_HOST}:{BACKEND_PORT}...")
 
        while True:
            conn, addr = server.accept()
            print(f"🔵 Connessione ricevuta da {addr}")
            thread = threading.Thread(target=handle_client_request, args=(conn,))
            thread.start()
 
 
def handle_client_request(conn):
    """Gestisce le richieste in arrivo dal client."""
    try:
        data = conn.recv(5 * 1024 * 1024).decode()
        command, payload = data.split("||")
 
        if command.startswith("analyze_image"):
            _, context = command.split(":")
            img_data = base64.b64decode(payload)
            image = Image.open(io.BytesIO(img_data))
            diagnosis = f"Analisi diagnostica eseguita per contesto: {context}"
            conn.sendall(f"diagnosis||{diagnosis}".encode())
 
        elif command == "chat_request":
            response_text = "Risposta simulata da ChatGPT per il payload: " + payload
            conn.sendall(f"chat_response||{response_text}".encode())
 
    except Exception as e:
        conn.sendall(f"error||{str(e)}".encode())
    finally:
        conn.close()
 
 
def send_to_backend(command, payload):
    """Invia una richiesta al backend e restituisce la risposta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((BACKEND_HOST, BACKEND_PORT))
            client.sendall(f"{command}||{payload}".encode())
            response = client.recv(5 * 1024 * 1024).decode()
            return response
    except Exception as e:
        return f"error||{str(e)}"