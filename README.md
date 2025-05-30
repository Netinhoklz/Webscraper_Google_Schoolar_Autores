# 📈 Google Scholar Co-authorship Network Analyzer

Este projeto é um **Web Scraper** e **Analisador de Redes de Coautoria** desenvolvido em Python. Ele utiliza Selenium para extrair dados de artigos do Google Scholar, foca nos autores de cada publicação e, em seguida, constrói e visualiza uma rede de colaboração entre eles usando `networkx` e `matplotlib`. O objetivo principal é mapear as relações de coautoria em uma área de pesquisa específica, identificando pesquisadores proeminentes e suas conexões.

---

## ✨ Funcionalidades

* **Web Scraping Robusto:**
    * Coleta informações de autores de artigos do Google Scholar usando **Selenium e Beautiful Soup**.
    * Configurado para usar o navegador **Microsoft Edge (Chromium)** com `webdriver_manager` para gerenciamento automático do driver.
    * Implementa estratégias **anti-bloqueio** como User-Agents rotativos e atrasos aleatórios para evitar detecção e CAPTCHAs.
    * Navega por múltiplas páginas de resultados de pesquisa.
* **Análise de Coautoria:**
    * Extrai e limpa os nomes dos autores de cada artigo.
    * Cria um **grafo de coautoria** onde os nós são os autores e as arestas representam colaborações.
    * Pondera as arestas com base no número de artigos em que os autores colaboraram.
* **Visualização de Rede:**
    * Gera um **plot visual do grafo de coautoria** utilizando `matplotlib`, mostrando a estrutura das colaborações.
    * O tamanho dos nós reflete a quantidade de artigos encontrados para cada autor (pode ser ajustado para grau ou outras métricas).
    * As labels dos autores são exibidas de forma inteligente para grafos maiores, focando nos nós mais conectados.
    * Salva o grafo em formatos populares como **PNG (imagem), GraphML e GML** para análise posterior em ferramentas como Gephi.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Selenium:** Para automação do navegador e scraping dinâmico.
* **BeautifulSoup4 (`bs4`):** Para parsing eficiente do HTML.
* **webdriver-manager:** Para gerenciar e baixar automaticamente o driver do Microsoft Edge.
* **networkx:** Para criação, manipulação e análise de grafos.
* **matplotlib:** Para visualização e plotagem dos grafos.
* **collections (defaultdict, Counter):** Para estruturas de dados auxiliares.
* **itertools (combinations):** Para gerar combinações de autores.

---

## 🚀 Como Rodar

### Pré-requisitos

Certifique-se de ter o **Microsoft Edge (Chromium)** instalado em seu sistema.

### Instalação

1.  Clone este repositório:
    ```bash
    git clone [https://github.com/seu-usuario/nome-do-repositorio.git](https://github.com/seu-usuario/nome-do-repositorio.git)
    cd nome-do-repositorio
    ```
2.  Crie um ambiente virtual (opcional, mas recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate   # No Windows
    ```
3.  Instale as dependências:
    ```bash
    pip install selenium beautifulsoup4 networkx matplotlib webdriver-manager
    ```

### Execução

1.  Abra o arquivo `seu_script.py` (ou o nome que você deu ao seu arquivo) e, se desejar, ajuste as variáveis de configuração na seção `--- Configurações ---`:
    * `SEARCH_QUERY`: A consulta de pesquisa para o Google Scholar (ex: `'ppgia unifor'`).
    * `MAX_ARTICLES_TO_FETCH`: O número máximo de artigos a serem processados.
    * `NEXT_PAGE_BUTTON_XPATH`: O XPath do botão "Próxima Página" do Google Scholar (já configurado, mas pode precisar de ajuste se o site mudar).

2.  Execute o script:
    ```bash
    python seu_script.py
    ```

O script abrirá uma janela do navegador Edge, realizará a pesquisa, coletará os dados e, ao final, exibirá o grafo de coautoria e o salvará como imagem (`.png`) e arquivos de grafo (`.graphml`, `.gml`) na mesma pasta do script.

---

## ⚠️ Observações e Limitações

* **CAPTCHA:** O Google Scholar pode ocasionalmente apresentar CAPTCHAs, especialmente após muitas requisições. O script inclui detecção básica e interromperá a execução se um CAPTCHA for identificado. Nesses casos, uma pausa ou intervenção manual pode ser necessária.
* **Mudanças no Google Scholar:** A estrutura HTML do Google Scholar pode mudar com o tempo, o que pode quebrar o scraping. O `NEXT_PAGE_BUTTON_XPATH` é um ponto comum de falha. Se o script não estiver funcionando, verifique os seletores CSS/XPath.
* **Número de Artigos:** Definir `MAX_ARTICLES_TO_FETCH` muito alto pode aumentar a chance de ser bloqueado ou levar muito tempo para ser executado. Comece com um número menor para testes.
* **Visualização:** Para grafos muito grandes, a visualização no `matplotlib` pode ficar densa. Recomenda-se exportar para GraphML/GML e usar ferramentas dedicadas como [Gephi](https://gephi.org/) para análises e visualizações mais aprofundadas.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues, enviar pull requests ou sugerir melhorias.

---
