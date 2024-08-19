import requests
import time

def fetch_dashboard():
    url = "http://banescoseguros.onrender.com"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta una excepción para códigos de error HTTP
        print("Solicitud exitosa:", response.status_code)
        print("Contenido:", response.text)  # Puedes ajustar esto según lo que necesites hacer con el contenido
    except requests.exceptions.RequestException as e:
        print(f"Error durante la solicitud: {e}")

def main():
    while True:
        fetch_dashboard()
        time.sleep(60)

if __name__ == "__main__":
    main()
