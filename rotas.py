import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

# --- ENDEREÇO FIXO ---
ENDERECO_ESCRITORIO = 'R. Leão Santos Neto, 45-1 - Arari, MA, 65480-000'

# Lista de OS (Ordens de Serviço) do dia
# Dica: Coloque na ordem que você acredita ser a melhor para testar a otimização
servicos_pendentes = [
    'Rua Pedro Leandro Fernandes, 48 - Arari, MA',
    'Av. Dr. João da Silva Lima, 1-133 - Arari, MA',
    'R. das Flores, Arari - MA' # Exemplo de ponto adicional
]

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

def configurar_visualizacao_otimizada():
    """Ativa satélite e abre painel de detalhes para o técnico"""
    wait = WebDriverWait(driver, 10)
    try:
        # 1. Ativar Satélite
        botao_camadas = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Camadas')]")))
        botao_camadas.click()
        sleep(1)
        opcao_satelite = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Satélite')]")))
        opcao_satelite.click()
        
        # 2. Abrir Detalhes do Trajeto (Lista de ruas)
        # O Google Maps geralmente mostra um botão "Detalhes" ou o tempo da rota
        detalhes = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Detalhes')] | //button[contains(@data-value, 'Detalhes')]")))
        detalhes.click()
        print("✅ Visualização detalhada e Satélite ativados.")
    except:
        print("⚠️ Aviso: Não foi possível ativar todos os detalhes visuais automaticamente.")

def montar_logistica_os(origem, destinos):
    wait = WebDriverWait(driver, 20)
    # Abre direto na interface de rotas
    driver.get("https://www.google.com/maps/dir///@-3.4539137,-44.7811197,15z?entry=ttu")
    
    try:
        # Preencher Origem
        campo_origem = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-0']//input")))
        campo_origem.send_keys(origem)

        # Preencher Destinos (Múltiplas Paradas)
        for i, destino in enumerate(destinos, start=1):
            campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='directions-searchbox-{i}']//input")))
            campo.send_keys(destino)
            campo.send_keys(Keys.ENTER)
            sleep(2)
            
            # Se houver mais destinos, clica em "Adicionar"
            if i < len(destinos):
                add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Adicionar destino')]")))
                add_btn.click()
                sleep(1)

        # Finaliza a rota e otimiza visualmente
        sleep(3)
        configurar_visualizacao_otimizada()
        
        # Extrair link para o WhatsApp
        link_rota = driver.current_url
        print("\n" + "="*50)
        print("🚀 ROTA DE MANUTENÇÃO PRONTA")
        print(f"🔗 Copie este link para o técnico:\n{link_rota}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"Erro ao montar logística: {e}")

if __name__ == '__main__':
    try:
        montar_logistica_os(ENDERECO_ESCRITORIO, servicos_pendentes)
        # Mantém aberto para conferência da equipe antes de sair para o campo
        print("Interface pronta. O navegador ficará aberto por 15 minutos.")
        sleep(900)
    finally:
        driver.quit()
