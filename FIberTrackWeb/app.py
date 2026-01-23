from flask import Flask, render_template, request
import threading
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

app = Flask(__name__)

# Configuração Central
ESCRITORIO = 'R. Leão Santos Neto, 2 - Arari, MA, 65480-000'

def realizar_automacao(lista_os):
    # --- PARTE 1: OTIMIZAÇÃO GEOGRÁFICA ---
    geolocator = Nominatim(user_agent="fibertrack_app", timeout=15)
    
    def get_coords(end):
        try:
            loc = geolocator.geocode(f"{end}, Arari, MA")
            return (loc.latitude, loc.longitude) if loc else None
        except: return None

    # Lógica de Grafos (Vizinho mais próximo)
    coord_atual = get_coords(ESCRITORIO) or (-3.4536, -44.7806)
    ordenados = []
    temp_lista = lista_os.copy()

    while temp_lista:
        proximo = min(temp_lista, key=lambda x: geodesic(coord_atual, get_coords(x) or coord_atual).km)
        ordenados.append(proximo)
        coord_atual = get_coords(proximo) or coord_atual
        temp_lista.remove(proximo)

    # --- PARTE 2: SELENIUM ---
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    
    driver.get("https://www.google.com.br/maps/dir/")
    sleep(3)
    
    # Preenchimento automático (sua lógica já validada)
    campo_0 = driver.find_element(By.XPATH, "//div[@id='directions-searchbox-0']//input")
    campo_0.send_keys(ESCRITORIO)
    campo_0.send_keys(Keys.ENTER)

    for i, destino in enumerate(ordenados, start=1):
        campo = driver.find_element(By.XPATH, f"//div[@id='directions-searchbox-{i}']//input")
        campo.send_keys(destino)
        campo.send_keys(Keys.ENTER)
        sleep(1.5)
        if i < len(ordenados):
            driver.find_element(By.XPATH, "//span[contains(text(), 'Adicionar destino')]").click()
            sleep(0.5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/executar', methods=['POST'])
def executar():
    texto = request.form.get('lista_os')
    enderecos = [l.strip() for l in texto.split('\n') if l.strip()]
    
    if enderecos:
        # Roda o Selenium em segundo plano
        threading.Thread(target=realizar_automacao, args=(enderecos,)).start()
        return "<h1>Sucesso!</h1><p>A rota está sendo gerada no servidor. Pode fechar esta aba.</p><a href='/'>Voltar</a>"
    return "Erro: Lista vazia."

if __name__ == '__main__':
    # host='0.0.0.0' permite que outros PCs da empresa acessem pelo seu IP
    app.run(host='0.0.0.0', port=5000, debug=True)