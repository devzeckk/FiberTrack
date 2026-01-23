import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
    print("🧠 1. Iniciando otimização geográfica (Grafos)...")
    geolocator = Nominatim(user_agent="fibertrack_optimizer_v3", timeout=15)
    
    def buscar_com_retry(endereco):
        tentativas = [
            endereco,
            ", ".join(endereco.split(",")[0:1] + endereco.split(",")[-2:]),
            "Arari, MA, Brasil"
        ]
        for tentativa in tentativas:
            try:
                sleep(1.2) # Delay para evitar bloqueio do servidor
                loc = geolocator.geocode(tentativa)
                if loc: return loc
            except: continue
        return None

    loc_inicio = buscar_com_retry(inicio)
    if not loc_inicio:
        from collections import namedtuple
        Location = namedtuple('Location', ['latitude', 'longitude'])
        loc_inicio = Location(latitude=-3.4536, longitude=-44.7806)

    pontos = []
    for d in destinos:
        loc = buscar_com_retry(d)
        if loc: 
            pontos.append({'endereco': d, 'coord': (loc.latitude, loc.longitude)})
        else:
            pontos.append({'endereco': d, 'coord': (loc_inicio.latitude, loc_inicio.longitude)})
    
    rota_otimizada = []
    ponto_atual = (loc_inicio.latitude, loc_inicio.longitude)
    
    while pontos:
        proximo = min(pontos, key=lambda p: geodesic(ponto_atual, p['coord']).km)
        rota_otimizada.append(proximo['endereco'])
        ponto_atual = proximo['coord']
        pontos.remove(proximo)
    
    print("✅ Rota organizada com sucesso!")
    return rota_otimizada

def montar_logistica_os(origem, destinos_crus):
    # PASSO 1: OTIMIZAÇÃO (O Python trabalha aqui antes de abrir o Chrome)
    destinos = otimizar_lista_enderecos(origem, destinos_crus)
    
    # PASSO 2: INICIALIZAÇÃO DO NAVEGADOR (Só abre após a rota estar pronta)
    print("🌐 2. Abrindo navegador Chrome...")
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--log-level=3") # Remove mensagens de erro inúteis
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 20)
    # Vai direto para a URL de rotas
    driver.get("https://www.google.com.br/maps/dir/")
    
    try:
        # Preencher Origem
        print("✍️ Preenchendo endereços no Maps...")
        campo_origem = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-0']//input")))
        campo_origem.send_keys(origem)
        campo_origem.send_keys(Keys.ENTER)

        # Preencher Destinos Otimizados
        for i, destino in enumerate(destinos, start=1):
            campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='directions-searchbox-{i}']//input")))
            campo.send_keys(destino)
            campo.send_keys(Keys.ENTER)
            sleep(1.5)
            if i < len(destinos):
                add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Adicionar destino')]")))
                add_btn.click()
                sleep(0.5)

        # Configura Visualização Final
        sleep(2)
        try:
            driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Camadas')]").click()
            sleep(1)
            driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Satélite')]").click()
            detalhes = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Detalhes')] | //button[contains(@data-value, 'Detalhes')]")))
            detalhes.click()
        except: pass

        print(f"\n🚀 TUDO PRONTO! Rota enviada para o navegador.")

    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    montar_logistica_os(ENDERECO_ESCRITORIO, servicos_pendentes)