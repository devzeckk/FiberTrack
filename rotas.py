import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# --- CONFIGURAÇÕES ---
ENDERECO_ESCRITORIO = 'R. Leão Santos Neto, 2 - Arari, MA, 65480-000'

servicos_pendentes = [
    'Av. Dr. João da Silva Lima, 1-133 - Arari, MA',
    'Rua Pedro Leandro Fernandes, 48 - Arari, MA',
    'R. das Flores, Arari - MA',
    'R. da Piçarreira, Arari - MA'
]

def otimizar_lista_enderecos(inicio, destinos):
    print("🧠 Otimizando rota para economia de combustível...")
    geolocator = Nominatim(user_agent="fibertrack_optimizer_v3", timeout=15)
    
    def buscar_com_retry(endereco):
        # Tentativa 1: Endereço completo
        # Tentativa 2: Apenas Rua e Cidade (remove número da casa que costuma dar erro)
        # Tentativa 3: Apenas a Cidade
        tentativas = [
            endereco,
            ", ".join(endereco.split(",")[0:1] + endereco.split(",")[-2:]), # Tira o número
            "Arari, MA, Brasil"
        ]
        
        for tentativa in tentativas:
            try:
                sleep(1.5)
                loc = geolocator.geocode(tentativa)
                if loc:
                    return loc
            except:
                continue
        return None

    # Tenta localizar o escritório
    loc_inicio = buscar_com_retry(inicio)
    
    if not loc_inicio:
        print("⚠️ Escritório não fixado com precisão. Usando centro de Arari como base.")
        from collections import namedtuple
        Location = namedtuple('Location', ['latitude', 'longitude'])
        loc_inicio = Location(latitude=-3.4536, longitude=-44.7806)

    pontos = []
    for d in destinos:
        loc = buscar_com_retry(d)
        if loc: 
            pontos.append({'endereco': d, 'coord': (loc.latitude, loc.longitude)})
        else:
            print(f"❓ Não localizei {d}, mas vou incluir na rota final mesmo assim.")
            # Adiciona com coord do escritório só para não perder o endereço na lista
            pontos.append({'endereco': d, 'coord': (loc_inicio.latitude, loc_inicio.longitude)})
    
    # Algoritmo de vizinho mais próximo (Graph logic)
    rota_otimizada = []
    ponto_atual = (loc_inicio.latitude, loc_inicio.longitude)
    
    while pontos:
        proximo = min(pontos, key=lambda p: geodesic(ponto_atual, p['coord']).km)
        rota_otimizada.append(proximo['endereco'])
        ponto_atual = proximo['coord']
        pontos.remove(proximo)
    
    print("✅ Rota organizada!")
    return rota_otimizada

# --- INÍCIO DO SCRIPT SELENIUM ---
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

def montar_logistica_os(origem, destinos_crus):
    # 1. Otimiza a lista antes de abrir o Maps
    destinos = otimizar_lista_enderecos(origem, destinos_crus)
    
    wait = WebDriverWait(driver, 20)
    driver.get("https://www.google.com/maps/dir///@-3.4539137,-44.7811197,15z?entry=ttu")
    
    try:
        # Preencher Origem
        campo_origem = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-0']//input")))
        campo_origem.send_keys(origem)

        # Preencher Destinos Otimizados
        for i, destino in enumerate(destinos, start=1):
            campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='directions-searchbox-{i}']//input")))
            campo.send_keys(destino)
            campo.send_keys(Keys.ENTER)
            sleep(2)
            if i < len(destinos):
                add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Adicionar destino')]")))
                add_btn.click()
                sleep(1)

        # Configura Visualização Final
        sleep(3)
        try:
            # Ativar Satélite
            driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Camadas')]").click()
            sleep(1)
            driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Satélite')]").click()
            # Abrir Detalhes
            detalhes = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Detalhes')] | //button[contains(@data-value, 'Detalhes')]")))
            detalhes.click()
        except: pass

        print(f"\n🚀 ROTA OTIMIZADA PARA O TÉCNICO:\n{driver.current_url}")

    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    montar_logistica_os(ENDERECO_ESCRITORIO, servicos_pendentes)
    sleep(900)
    driver.quit()
