import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# Mudanças para o Edge
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions  # Renomeado para clareza
from webdriver_manager.microsoft import EdgeChromiumDriverManager  # Mudança aqui
# Fim das mudanças para o Edge
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from itertools import combinations

# --- Configurações ---
SEARCH_QUERY = 'ppgia unifor'
MAX_ARTICLES_TO_FETCH = 185  # Mantenha baixo para testes iniciais
BASE_URL = 'https://scholar.google.com/'
# XPath fornecido pelo usuário para o botão "Próxima Página"
NEXT_PAGE_BUTTON_XPATH = '//*[@id="gs_nm"]/button[2]'  # Adicionado aqui


# --- Métodos Anti-Bloqueio ---
def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        # Edge User Agent
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.73',
        # Edge User Agent
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
    ]
    return random.choice(user_agents)


def setup_driver():
    edge_options = EdgeOptions()
    edge_options.use_chromium = True  # Importante para usar com EdgeChromiumDriverManager
    edge_options.add_argument(f"user-agent={get_random_user_agent()}")
    # edge_options.add_argument("--headless") # Modo headless
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920x1080")
    edge_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    })
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option('useAutomationExtension', False)

    try:
        print("Configurando o WebDriver para Microsoft Edge...")
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)  # Mudança aqui para webdriver.Edge
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            """
        })
        print("WebDriver do Edge configurado com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o driver do Edge: {e}")
        print("Certifique-se de que o Microsoft Edge (baseado em Chromium) está instalado.")
        print("Se o problema persistir, tente instalar o msedgedriver manualmente e especificar o caminho.")
        return None
    return driver


def gentle_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))


def check_for_captcha(driver):
    title = driver.title.lower()
    if "google" in title and ("captcha" in title or "verificação" in title or "robot" in title):
        print("CAPTCHA detectado! Interrompendo o scraping.")
        return True
    try:
        # Tenta encontrar elementos comuns de CAPTCHA (ex: reCAPTCHA)
        if driver.find_elements(By.CSS_SELECTOR, 'iframe[title*="reCAPTCHA"]'):
            print("CAPTCHA (iframe reCAPTCHA) detectado! Interrompendo o scraping.")
            return True
        if driver.find_elements(By.ID, "recaptcha"):
            print("CAPTCHA (id=recaptcha) detectado! Interrompendo o scraping.")
            return True
    except:  # Ignora se os elementos não forem encontrados
        pass
    return False


# --- Funções de Scraping ---
def search_scholar(driver, query):
    print(f"1 - Entrando no site do Google Acadêmico: {BASE_URL}")
    driver.get(BASE_URL)
    gentle_delay()

    if check_for_captcha(driver): return False

    try:
        search_box = driver.find_element(By.NAME, 'q')
        print(f"2 - Pesquisando por '{query}'...")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        gentle_delay(3, 6)
        if check_for_captcha(driver): return False
        print("Pesquisa realizada.")
        return True
    except Exception as e:
        print(f"Erro ao realizar a pesquisa: {e}")
        return False


def extract_authors_from_page(driver):
    authors_list_per_article = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles_divs = soup.find_all('div', class_='gs_r')

    for article_div in articles_divs:
        authors_div = article_div.find('div', class_='gs_a')
        if authors_div:
            authors_text = authors_div.get_text(separator=' ').split(' - ')[0]
            authors = [author.strip() for author in authors_text.replace('...', '').split(',') if author.strip()]
            if authors:
                cleaned_authors = []
                for author in authors:
                    name_parts = []
                    for part in author.split():
                        if not any(char.isdigit() for char in part) or len(part) > 2:
                            name_parts.append(part)
                    cleaned_name = " ".join(name_parts)
                    if cleaned_name:
                        cleaned_authors.append(cleaned_name)
                if cleaned_authors:
                    authors_list_per_article.append(cleaned_authors)
    return authors_list_per_article


def scrape_articles_authors(driver, max_articles):
    print(f"\n3 - Iniciando WebScraper para puxar dados dos autores (máx {max_articles} artigos)...")
    all_coauthors = []
    articles_processed = 0
    page_count = 1

    while articles_processed < max_articles:
        print(f"--- Processando página {page_count} ---")
        if check_for_captcha(driver):
            print("CAPTCHA encontrado. Parando a coleta de dados.")
            break

        authors_on_page = extract_authors_from_page(driver)
        if not authors_on_page and page_count > 1:  # Se não houver autores e não for a primeira página, pode ser o fim.
            print("Nenhum autor encontrado nesta página ou fim dos resultados.")
            break
        elif not authors_on_page and page_count == 1:
            print("Nenhum autor encontrado na primeira página. Verifique a query ou a estrutura do site.")
            # Poderia adicionar uma pequena espera e tentar novamente uma vez aqui, caso seja um problema de carregamento.

        for coauthors in authors_on_page:
            if articles_processed < max_articles:
                all_coauthors.append(coauthors)
                articles_processed += 1
            else:
                break

        print(f"Artigos processados até agora: {articles_processed}/{max_articles}")
        print(f"Autores encontrados nesta página: {len(authors_on_page)}")
        if authors_on_page:
            print(f"Exemplo de autores do primeiro artigo: {authors_on_page[0]}")

        if articles_processed >= max_articles:
            print("Limite de artigos atingido.")
            break

        try:
            # Mudança aqui para usar o XPath fornecido
            print(f"Tentando encontrar o botão 'Próxima Página' com XPath: {NEXT_PAGE_BUTTON_XPATH}")
            next_button = driver.find_element(By.XPATH, NEXT_PAGE_BUTTON_XPATH)
            print("Clicando no botão 'Próxima Página'...")
            # Tentar scrollar para o botão ser clicável, se necessário
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.5)  # Pequena pausa após o scroll
            # driver.execute_script("arguments[0].click();", next_button) # Clique via JS
            next_button.click()  # Clique direto do Selenium
            page_count += 1
            gentle_delay(4, 7)
        except Exception as e:
            print(
                f"Não foi possível encontrar o botão 'Próxima Página' com o XPath '{NEXT_PAGE_BUTTON_XPATH}' ou erro ao clicar: {e}")
            print("Provavelmente chegamos ao fim dos resultados, o XPath está incorreto ou a página mudou.")
            break

    print(f"Total de {articles_processed} artigos processados.")
    return all_coauthors


# --- Funções de Grafo ---
def create_coauthorship_graph(all_coauthors_lists):
    print("\n4 - Criando o grafo de coautoria...")
    G = nx.Graph()
    edge_weights = defaultdict(int)

    for coauthors in all_coauthors_lists:
        for author in coauthors:
            if not G.has_node(author):
                G.add_node(author, count=0)
            G.nodes[author]['count'] += 1
        for author1, author2 in combinations(coauthors, 2):
            u, v = tuple(sorted((author1, author2)))
            edge_weights[(u, v)] += 1
    for (u, v), weight in edge_weights.items():
        G.add_edge(u, v, weight=weight)
        # print(f"  Adicionando/atualizando aresta: ({u}) --{weight}-- ({v})") # Descomente para debug detalhado

    print(f"Grafo criado com {G.number_of_nodes()} nós (autores) e {G.number_of_edges()} arestas (colaborações).")
    return G


def plot_and_save_graph(G, filename_prefix="coauthorship_graph"):
    if not G.nodes():
        print("Grafo vazio, não há nada para plotar ou salvar.")
        return

    print("\n5 - Plotando e salvando o grafo...")
    plt.figure(figsize=(18, 18))

    # Tentar um layout que possa espalhar melhor os nós se k for muito pequeno
    try:
        # pos = nx.spring_layout(G, k=0.55, iterations=50, seed=42) # k maior pode ajudar a espalhar
        # Para grafos muito densos, 'kamada_kawai_layout' pode ser melhor
        pos = nx.kamada_kawai_layout(G)
        if len(G.nodes()) > 100:  # Se muitos nós, spring_layout pode ser lento, usar kamada_kawai ou fruchterman_reingold
            pos = nx.fruchterman_reingold_layout(G, seed=42)
    except Exception as e:
        print(f"Erro ao calcular layout Kamada-Kawai, usando Spring Layout como fallback: {e}")
        pos = nx.spring_layout(G, k=0.35, iterations=30, seed=42)

    node_sizes = [G.nodes[node].get('count', 1) * 100 for node in G.nodes()]
    if not node_sizes:  # Fallback se algo der errado com 'count'
        node_sizes = 100

    edge_widths = [G.edges[u, v]['weight'] * 0.5 for u, v in G.edges()]
    if not edge_widths and G.edges():  # Fallback
        edge_widths = 0.5

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray', alpha=0.5)
    # Ajustar o tamanho da fonte das labels
    font_size = 10
    if len(G.nodes()) > 50:
        font_size = 7
    if len(G.nodes()) > 150:
        font_size = 5  # Muito pequeno, mas pode ser necessário

    # Para evitar sobreposição de labels em grafos densos, pode ser útil não desenhá-las todas
    labels_to_draw = {}
    if len(G.nodes()) < 70:  # Desenha todas as labels para grafos menores
        labels_to_draw = {node: node for node in G.nodes()}
    else:  # Para grafos maiores, desenha apenas labels de nós mais conectados (maior grau)
        # Pega os top N nós por grau
        sorted_nodes = sorted(G.degree, key=lambda item: item[1], reverse=True)
        for i, (node, degree) in enumerate(sorted_nodes):
            if i < 30 or G.nodes[node].get('count', 1) > 2:  # Exibe os 30 mais conectados ou com mais de 2 artigos
                labels_to_draw[node] = node

    nx.draw_networkx_labels(G, pos, labels=labels_to_draw, font_size=font_size, font_weight='bold')

    plt.title(f"Grafo de Coautoria - {SEARCH_QUERY}", fontsize=16)
    plt.axis('off')

    plot_filename = f"{filename_prefix}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot do grafo salvo como: {plot_filename}")
    plt.show()

    graphml_filename = f"{filename_prefix}.graphml"
    try:
        nx.write_graphml(G, graphml_filename)
        print(f"Dados do grafo salvos em formato GraphML como: {graphml_filename}")
    except Exception as e:
        print(f"Erro ao salvar em GraphML: {e}")

    gml_filename = f"{filename_prefix}.gml"
    try:
        nx.write_gml(G, gml_filename)
        print(f"Dados do grafo salvos em formato GML como: {gml_filename}")
    except Exception as e:
        print(f"Erro ao salvar em GML: {e}")


# --- Função Principal ---
def main():
    driver = setup_driver()
    if not driver:
        return

    try:
        if not search_scholar(driver, SEARCH_QUERY):
            print("Não foi possível realizar a pesquisa. Encerrando.")
            return

        all_coauthors_data = scrape_articles_authors(driver, MAX_ARTICLES_TO_FETCH)

        if not all_coauthors_data:
            print("Nenhum dado de autor foi coletado. Encerrando.")
            return

        print(f"\nDados brutos de coautores coletados (primeiros 5 artigos):")
        for i, coauthors in enumerate(all_coauthors_data[:5]):
            print(f"  Artigo {i + 1}: {coauthors}")

        graph = create_coauthorship_graph(all_coauthors_data)
        plot_and_save_graph(graph, filename_prefix=f"grafo_coautoria_{SEARCH_QUERY.replace(' ', '_')}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado no fluxo principal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\nFechando o navegador...")
            driver.quit()


if __name__ == '__main__':
    main()
