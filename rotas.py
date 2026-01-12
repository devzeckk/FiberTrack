import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

# Configuração do Driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window() 

# 1. URL do Google maps
print("--- Abrindo Google Maps...")
driver.get("https://www.google.com/maps")

def lidar_com_cookies():
    """Tenta fechar o pop-up de cookies se ele aparecer"""
    try:
        wait = WebDriverWait(driver, 5)
        # Procura por botões que tenham "Aceitar" ou "Rejeitar" no texto
        # O XPath abaixo procura um botão que contenha o texto 'Aceitar tudo' ou 'Aceitar'
        botao_cookie = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Aceitar')]/ancestor::button | //button[contains(., 'Aceitar')]")
        ))
        botao_cookie.click()
        print("   Pop-up de cookies fechado.")
        sleep(2) # Espera o pop-up sumir
    except:
        print("   Nenhum pop-up de cookies encontrado (ou já aceito). Seguindo...")

def adiciona_destino(endereco):
    print("--- Tentando adicionar destino...")
    
    # Chama a função para limpar a tela antes de buscar
    lidar_com_cookies()
    
    wait = WebDriverWait(driver, 20) 
    
    try:
        # Tenta encontrar pelo ID padrão
        barra = wait.until(EC.element_to_be_clickable((By.ID, 'searchboxinput')))
    except:
        print("   ID 'searchboxinput' falhou. Tentando encontrar pelo input genérico...")
        # Fallback: procura o primeiro input de texto na tela
        barra = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='searchboxinput' or @name='q']")))

    print("   Caixa de busca encontrada.")
    barra.clear()
    barra.send_keys(endereco)
    sleep(1)
    barra.send_keys(Keys.RETURN)
    print("   Endereço enviado.")

def abre_rotas():
    print("--- Tentando encontrar botão de rotas...")
    wait = WebDriverWait(driver, 15)

    # Tenta vários seletores para garantir
    xpaths = [
        '//button[@data-value="Rotas"]',
        '//button[contains(@aria-label, "Rotas")]',
        '//button[contains(@aria-label, "Directions")]',
        '//*[@id="hArJGc"]' # ID do ícone de seta
    ]
    
    for xpath in xpaths:
        try:
            botao = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            botao.click()
            print(f"   Botão de rotas clicado usando: {xpath}")
            return
        except:
            continue # Tenta o próximo
            
    raise Exception("Não foi possível clicar no botão de rotas com nenhum seletor.")

if __name__ == '__main__':
    try:
        endereco = 'Av. Dr. João da Silva Lima, 1-133 - Arari, MA, 65480-000'
        
        adiciona_destino(endereco)
        
        # Espera o painel lateral carregar a info do local
        sleep(4) 
        
        abre_rotas()

        print("SUCESSO! Mantendo aberto por 10 minutos.")
        sleep(600)

    except Exception as e:
        print("\n\n!!! OCORREU UM ERRO !!!")
        traceback.print_exc()
        # Tira um print da tela para você ver o que o robô estava vendo na hora do erro
        driver.save_screenshot("erro_debug.png")

        print("Uma foto da tela (erro_debug.png) foi salva na pasta do projeto.")
