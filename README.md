# Analisador de Sentimentos com IA

Este projeto coleta tweets do X (Twitter), analisa os sentimentos usando modelos de NLP e gera resumos por emoção. Ele combina **web scraping com Selenium** e **modelos de linguagem da Hugging Face** para oferecer uma visão geral das emoções em torno de um tópico específico.

---

## 🚀 Funcionalidades

* 🔍 Busca automática de tweets por palavra-chave e intervalo de datas
* 🔐 Suporte a autenticação via cookies (necessário para evitar bloqueios)
* 🧠 Classificação de emoções com modelo BERT
* 📊 Agrupamento de tweets por sentimento
* ✨ Geração de resumos automáticos por emoção
* 😄 Associação de emojis para cada tipo de sentimento

---

## 📦 Tecnologias utilizadas

* Python 3.x
* Selenium
* WebDriver Manager
* Transformers (Hugging Face)
* ChromeDriver

---

## ⚙️ Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/Claus7777/AnalisadorSentimentos.git
cd analisador-sentimentos
```

### 2. Instale as dependências

```bash
pip install selenium webdriver-manager transformers torch
```

---

## 🔧 Parâmetros principais

No código, você pode ajustar:

```python
SEARCH_QUERY = "Termo since:20XX-XX-XX until:20XX-XX-XX"
MAX_TWEETS = 10
HEADLESS = True
```

* `SEARCH_QUERY`: termo de busca + filtros do Twitter
* `MAX_TWEETS`: quantidade máxima de tweets coletados
* `HEADLESS`: executa o navegador em segundo plano

---

## 🔐 Autenticação (Importante)

O projeto utiliza cookies para acessar o Twitter autenticado.

Edite a variável:

```python
TWITTER_COOKIES = [...]
```

Substitua pelos seus próprios cookies:

* `auth_token`
* `ct0`
* `twid`

⚠️ **Nunca compartilhe seus cookies publicamente.**

---

## ▶️ Como executar

```bash
python main.py
```

---

## 🧠 Como funciona

### 1. Coleta de Tweets

* Acessa a busca do Twitter
* Faz scroll automático
* Extrai textos dos tweets

### 2. Classificação de Sentimentos

Utiliza o modelo:

* `boltuix/bert-emotion`

---

### 3. Agrupamento

Os tweets são organizados por emoção e é calculada a porcentagem de cada grupo.

---

### 4. Sumarização

Para cada emoção:

* Combina múltiplos tweets
* Gera um resumo com:

  * `facebook/bart-large-cnn`

---

## 📊 Exemplo de saída

```bash
Porcentagens por sentimento:
Happiness: 40.00%
Fear: 30.00%
Surprise: 30.00%

📊 Resumo de sentimentos encontrados:

🔸 Happiness: Usuários estão animados com o lançamento... 😄
🔸 Fear: Alguns jogadores demonstram preocupação... 😱
🔸 Surprise: Reações inesperadas sobre o jogo... 😲
```

---

## 📄 Licença

Este projeto é open-source e pode ser usado livremente.

---
