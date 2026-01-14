import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

# --- ENDEREÇO FIXO DO ESCRITORIO ---
ENDERECO_ESCRITORIO = 'R. Leão Santos Neto, 45-1 - Arari, MA, 65480-000'

# Lista de endereços dos clientes
clientes = [
    'Av. Dr. João da Silva Lima, 1-133 - Arari, MA, 65480-000',
    'Rua Pedro Leandro Fernandes, 48 - Arari, MA',
    # Adicione mais aqui...
]

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

def calcular_rota(origem, destino):
    print(f"\n--- Calculando: {destino}")
    wait = WebDriverWait(driver, 20)
    
    # URL direta de rotas para evitar cliques desnecessários
    driver.get("https://www.google.com/maps/dir///@-3.4539137,-44.7811197,15z?entry=ttu")
    
    try:
        # 1. Localiza o campo de ORIGEM (escritório)
        # No modo de rotas, o Google usa inputs específicos no painel lateral
        origem_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-0']//input")))
        origem_input.clear()
        origem_input.send_keys(origem)
        
        # 2. Localiza o campo de DESTINO (cliente)
        destino_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-1']//input")))
        destino_input.clear()
        destino_input.send_keys(destino)
        
        # Pressiona ENTER para calcular
        destino_input.send_keys(Keys.ENTER)
        
        # Espera um pouco para o Maps processar o caminho
        sleep(5)
        print(f"    Rota traçada com sucesso!")
        
    except Exception as e:
        print(f"    Erro ao preencher campos de rota: {e}")

if __name__ == '__main__':
    try:
        # Loop para processar cada cliente da lista
        for cliente in clientes:
            calcular_rota(ENDERECO_ESCRITORIO, cliente)
            
            # Pausa para você visualizar a rota na tela antes de ir para o próximo
            print("    Aguardando 10 segundos para visualização...")
            sleep(10)

        print("\n--- Todos os cálculos foram concluídos! ---")
        sleep(60) # Mantém aberto no último para conferência

    except Exception as e:
        traceback.print_exc()
        driver.save_screenshot("erro_rota.png")
    finally:
        driver.quit()
