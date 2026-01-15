import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

# --- CONFIGURAÇÕES ---
ENDERECO_ESCRITORIO = 'R. Leão Santos Neto, 45-1 - Arari, MA, 65480-000'

# Lista de endereços para compor a rota completa
clientes = [
    'Rua Pedro Leandro Fernandes, 48 - Arari, MA',
    'Av. Dr. João da Silva Lima, 1-133 - Arari, MA, 65480-000',
    # Você pode adicionar mais endereços aqui
]

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

def montar_rota_multipla(origem, lista_destinos):
    print(f"--- Iniciando rota completa com {len(lista_destinos)} destinos...")
    wait = WebDriverWait(driver, 20)
    
    # Abre o Google Maps direto na tela de rotas
    driver.get("https://www.google.com/maps/dir///@-3.4539137,-44.7811197,15z?entry=ttu")
    
    try:
        # 1. Preenche a Origem (Escritório)
        campo_origem = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-0']//input")))
        campo_origem.send_keys(origem)
        sleep(1)

        # 2. Preenche o Primeiro Destino
        campo_destino = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-1']//input")))
        campo_destino.send_keys(lista_destinos[0])
        campo_destino.send_keys(Keys.ENTER)
        sleep(3)

        # 3. Adiciona os outros destinos
        for i, destino in enumerate(lista_destinos[1:], start=2):
            print(f"    Adicionando parada {i}: {destino}")
            
            # Clica no botão "Adicionar destino"
            # O seletor busca o botão que tem o texto ou o ícone de adicionar
            botao_adicionar = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Adicionar destino')] | //div[contains(@aria-label, 'Adicionar destino')]")))
            botao_adicionar.click()
            sleep(1)

            # Localiza o novo campo que apareceu (o índice aumenta conforme adicionamos)
            novo_campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='directions-searchbox-{i}']//input")))
            novo_campo.send_keys(destino)
            novo_campo.send_keys(Keys.ENTER)
            sleep(2)

        print("\nSUCESSO: Rota completa traçada!")
        
    except Exception as e:
        print(f"Erro ao montar rota múltipla: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    try:
        montar_rota_multipla(ENDERECO_ESCRITORIO, clientes)
        
        # Mantém aberto para analisar o trajeto total
        print("Mantendo o navegador aberto por 10 minutos para conferência.")
        sleep(600)

    except Exception as e:
        driver.save_screenshot("erro_rota_multipla.png")
    finally:
        driver.quit()
