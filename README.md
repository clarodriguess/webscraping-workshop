# 📰 DOU Scraper — Contratos MEC 2025

Scraper desenvolvido durante o workshop **"Web Scraping com Python para análise de dados públicos"**,  no evento **Open Data Day**, organizado pela [PyLadies São Paulo](https://www.linkedin.com/company/pyladiessp/) em parceria com a [Open Knowledge Brasil](https://www.linkedin.com/company/open-knowledge-brasil/), na [FIAP](https://www.linkedin.com/company/fiap/), em São Paulo.

O projeto coleta automaticamente extratos de contratos do **Ministério da Educação (MEC)** relacionados à aquisição de **material didático/escolar** publicados no [Diário Oficial da União](https://in.gov.br) em 2025.

---

## 🎯 Objetivo

Demonstrar na prática como utilizar Python e Selenium para:
- Automatizar a navegação em portais públicos
- Extrair e estruturar dados de documentos oficiais
- Gerar datasets prontos para análise a partir de fontes abertas

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.x | Linguagem principal |
| Selenium | Automação do navegador |
| Pandas | Estruturação e exportação dos dados |
| Regex (`re`) | Extração de campos do texto bruto |
| Chrome + ChromeDriver | Navegador headless via Selenium Grid |

---

## 📁 Estrutura do Projeto

```
.
├── main.py          # Script principal
├── dados/
│   └── contratos_mec_2025.csv   # Dataset gerado (criado na execução)
└── README.md
```

---

## ⚙️ Pré-requisitos

- Python 3.8+
- Docker com Selenium Grid (Chrome) rodando localmente, **ou** ChromeDriver instalado e configurado no PATH

### Instalação das dependências

```bash
pip install selenium pandas
```

### Subindo o Selenium Grid com Docker (recomendado)

```bash
docker run -d -p 4444:4444 --shm-size="2g" selenium/standalone-chrome
```

---

## ▶️ Como executar

```bash
python main.py
```

O script irá:
1. Acessar o portal do Diário Oficial da União
2. Preencher os filtros de busca (termo, período, órgão e tipo de documento)
3. Percorrer todas as páginas de resultados
4. Extrair os dados de cada extrato de contrato
5. Salvar o resultado em `dados/contratos_mec_2025.csv`

---

## 📊 Dados Extraídos

Cada registro no CSV contém os seguintes campos:

| Campo | Descrição |
|---|---|
| `processo` | Número do processo administrativo |
| `contratante` | Órgão contratante |
| `contratado` | Empresa ou entidade contratada |
| `objeto` | Descrição do objeto contratado |
| `vigencia` | Período de vigência do contrato |
| `valor_total` | Valor total do contrato |
| `data_assinatura` | Data de assinatura |

---

## 🔍 Parâmetros de Busca (configuráveis em `main.py`)

| Parâmetro | Valor atual |
|---|---|
| Termo de busca | `"material didático"` |
| Período | `01/01/2025` a `31/12/2025` |
| Tipo de pesquisa | Resultado exato |
| Órgão | Ministério da Educação |
| Tipo de documento | Extrato de Contrato |

---

## ⚠️ Observações

- O site do DOU pode passar por atualizações que alterem seletores e IDs — revise os locators em caso de falha.
- Utilize com responsabilidade, respeitando os termos de uso do portal e as boas práticas de web scraping (intervalos entre requisições, sem sobrecarga ao servidor).
- Os dados coletados são públicos e estão disponíveis no portal oficial do governo federal.

---

## 🌐 Contexto — Open Data Day

O [Open Data Day](https://opendataday.org/) é um evento global anual que promove o uso de dados abertos e incentiva iniciativas que utilizam dados públicos para análise e desenvolvimento de soluções. Este projeto foi desenvolvido como exercício prático durante as celebrações do evento em São Paulo.

---

## 📄 Licença

Este projeto é de uso educacional e livre para estudo e adaptação.