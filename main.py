import re
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração de Regex
CAMPOS_RE = {
    "processo": r"Nº Processo:\s*(.*?)(?=Inexigibilidade|Contratante:)",
    "contratante": r"Contratante:\s*(.*?)(?=Contratado:)",
    "contratado": r"Contratado:\s*(.*?)(?=Objeto:)",
    "objeto": r"Objeto:\s*(.*?)(?=Fundamento Legal:|Vigência:)",
    "vigencia": r"Vigência:\s*(.*?)(?=Valor Total:)",
    "valor_total": r"Valor Total:\s*(.*?)(?=Data de Assinatura:)",
    "data_assinatura": r"Data de Assinatura:\s*(.*?)(?=\(|$)"
}

# Funções de Interação e Extração

def esperar_e_clicar(wait, by, locator):
    """Aguarda o elemento ficar clicável e clica."""
    elemento = wait.until(EC.element_to_be_clickable((by, locator)))
    elemento.click()
    return elemento

def esperar_e_preencher(wait, by, locator, texto):
    """Aguarda o campo, limpa e digita o texto."""
    elemento = wait.until(EC.presence_of_element_located((by, locator)))
    elemento.clear()
    elemento.send_keys(texto)
    return elemento


def extrair_dados_texto(texto):
    """Aplica regex no texto bruto para extrair dicionário de dados."""
    dados = {}
    for campo, padrao in CAMPOS_RE.items():
        match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
        dados[campo] = match.group(1).strip().rstrip(".") if match else None
    return dados

def selecionar_data(driver, data_inicio, data_fim):
    """Injeta as datas diretamente via JavaScript para contornar o date picker do site."""
    driver.execute_script(f"""
        var dtInicio = document.getElementById('data-inicio');
        var dtFim = document.getElementById('data-fim');
        
        dtInicio.value = '{data_inicio}';
        dtFim.value = '{data_fim}';
        
        dtInicio.dispatchEvent(new Event('change'));
        dtFim.dispatchEvent(new Event('change'));
    """)

# Pesquisa e Extração

def realizar_pesquisa(driver, wait):
    """Centraliza as interações de preenchimento do formulário."""
    print("Preenchendo critérios de busca...")
    
    # Busca e filtros básicos
    esperar_e_preencher(wait, By.ID, "search-bar", "material didático")
    esperar_e_clicar(wait, By.ID, "toggle-search-advanced") # Expande opções avançadas
    esperar_e_clicar(wait, By.ID, "tipo-pesquisa-1") # Resultado Exato
    
    # Data personalizada
    esperar_e_clicar(wait, By.ID, "personalizado")
    selecionar_data(driver, "01/01/2025", "31/12/2025")

    # Seção 3 (contratos, licitações etc.)
    esperar_e_clicar(wait, By.ID, "do3") 
    esperar_e_clicar(wait, By.XPATH, "//button[normalize-space()='PESQUISAR']")

    # Filtros avançados pós-busca
    esperar_e_clicar(wait, By.ID, "orgPrinAction") # Filtro de Órgão Principal
    esperar_e_clicar(wait, By.XPATH, "//a[contains(text(), 'Ministério da Educação')]")

    esperar_e_clicar(wait, By.ID, "artTypeAction") # Filtro de Tipo de Documento
    esperar_e_clicar(wait, By.XPATH, "//a[contains(text(), 'Extrato de Contrato')]")


def raspar_pagina_atual(driver, wait):
    """Itera sobre os links da página de resultados e extrai os dados."""
    registros_pagina = []
    
    # Localiza todos os links de resultados
    selector_links = (By.XPATH, "//div[@class='resultados-wrapper']//a")
    wait.until(EC.presence_of_all_elements_located(selector_links))
    
    # Quantidade de links na página
    total_links = len(driver.find_elements(*selector_links))

    for i in range(total_links):
        # Re-localiza os links para evitar StaleElementReferenceException
        links = wait.until(EC.presence_of_all_elements_located(selector_links))
        link = links[i]
        
        # Abre o documento
        ActionChains(driver).move_to_element(link).pause(0.2).click().perform()
        
        # Extração
        paragrafos = driver.find_elements(By.CSS_SELECTOR, "p.dou-paragraph")
        texto_completo = " ".join(p.text for p in paragrafos)
        registros_pagina.append(extrair_dados_texto(texto_completo))
        
        # Volta e aguarda recarregar
        driver.back()
        wait.until(EC.presence_of_all_elements_located(selector_links))
        
    return registros_pagina

def executar(driver):
    """Agrega a lógica de execução principal: navegação, pesquisa, extração e salvamento."""
    wait = WebDriverWait(driver, 15)
    driver.get("https://in.gov.br/acesso-a-informacao/dados-abertos/base-de-dados")
    
    realizar_pesquisa(driver, wait)
    
    # Paginação
    todos_registros = []
    try:
        btn_ultima_pg = wait.until(EC.presence_of_element_located((By.ID, "lastPage")))
        total_paginas = int(btn_ultima_pg.text)
    except Exception as e:
        total_paginas = 1

    for pagina in range(1, total_paginas + 1):
        print(f"Processando página {pagina} de {total_paginas}...")
        dados_pg = raspar_pagina_atual(driver, wait)
        todos_registros.extend(dados_pg)
        
        if pagina < total_paginas:
            esperar_e_clicar(wait, By.ID, "rightArrow")
            # Aguarda a transição de página
            wait.until(EC.staleness_of(btn_ultima_pg)) 

    # Salvar Dados
    df = pd.DataFrame(todos_registros)
    df.to_csv('dados/contratos_mec_2025.csv', index=False, encoding='utf-8')
    print(f"Sucesso! {len(todos_registros)} registros salvos.")

def main():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor='http://chrome:4444/wd/hub',
        options=options
    )

    os.makedirs('dados', exist_ok=True)

    try:
        executar(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()