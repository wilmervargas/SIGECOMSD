import requests

def obtener_tasas_bcv():
    url = "https://pydolarve.org/api/v1/dollar?page=bcv"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Verifica si hubo error en la petición
        data = response.json()
        
        # Accediendo a los datos (la estructura puede variar según la API)
        monedas = data.get('monedas', {})
        usd = monedas.get('usd', 'No disponible')
        eur = monedas.get('eur', 'No disponible')
        fecha = data.get('fecha', 'No disponible')

        print(f"--- Tasas Oficiales BCV ({fecha}) ---")
        print(f"Dólar (USD): {usd} VES")
        print(f"Euro (EUR): {eur} VES")
        
    except Exception as e:
        print(f"Error al conectar con la API: {e}")

if __name__ == "__main__":
    obtener_tasas_bcv()