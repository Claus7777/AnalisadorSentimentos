from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from transformers import pipeline
from collections import defaultdict

import random;
import time

SEARCH_QUERY = ""
MAX_TWEETS = 10
HEADLESS = True  # Mude para False se quiser ver o navegador


sentiment_analysis = pipeline("text-classification", model="boltuix/bert-emotion")

label_to_emoji = {
    "Sadness": "😢",
    "Anger": "😠",
    "Love": "❤️",
    "Surprise": "😲",
    "Fear": "😱",
    "Happiness": "😄",
    "Neutral": "😐",
    "Disgust": "🤢",
    "Shame": "🙈",
    "Guilt": "😔",
    "Confusion": "😕",
    "Desire": "🔥",
    "Sarcasm": "😏"
}

# === FUNÇÃO PARA CONFIGURAR O NAVEGADOR ===
def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--lang=pt-BR")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

TWITTER_COOKIES = [
    {
        'name': 'auth_token',
        'value': '',  
        'domain': '.x.com'
    },
    {
        'name': 'ct0',
        'value': '',
        'domain': '.x.com'
    },
    {
        'name': 'twid',
        'value': '', 
        'domain':  '.x.com'
    }
]


def setup_driver_with_cookies(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=pt-BR")
    
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def add_cookies_to_driver(driver):
    """Add authentication cookies to the driver"""
    try:
        driver.get("https://twitter.com")
        time.sleep(2)
        
        for cookie in TWITTER_COOKIES:
            try:
                driver.add_cookie(cookie)
                print(f"Added cookie: {cookie['name']}")
            except Exception as e:
                print(f"Failed to add cookie {cookie['name']}: {e}")
        
        driver.refresh()
        time.sleep(3)
        
        # Verify login by checking for specific elements
        if driver.find_elements(By.XPATH, '//a[@data-testid="AppTabBar_Profile_Link"]'):
            print("Successfully authenticated with cookies!")
            return True
        else:
            print("Authentication may have failed")
            return False
            
    except Exception as e:
        print(f"Error adding cookies: {e}")
        return False

def scrape_tweets_with_auth(query, max_tweets):
    driver = setup_driver_with_cookies(HEADLESS)
    
    if not add_cookies_to_driver(driver):
        print("Failed to authenticate. Check your cookies.")
        driver.quit()
        return []
    
    search_url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
    print(f"Searching: {search_url}")
    driver.get(search_url)
    time.sleep(5)
    
    tweets = set()
    scroll_attempts = 0
    max_scroll_attempts = 15
    
    while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
        try:
            elements = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
            print(f"Found {len(elements)} tweet elements on page")
            
            new_tweets_count = 0
            for el in elements:
                tweet_text = el.text.strip()
                if tweet_text and tweet_text not in tweets:
                    tweets.add(tweet_text)
                    print(f"Tweet {len(tweets)}: {tweet_text[:80]}...")
                    new_tweets_count += 1
                    if len(tweets) >= max_tweets:
                        break
            
            print(f"Total tweets: {len(tweets)} | New this scroll: {new_tweets_count}")
            
            if len(tweets) >= max_tweets:
                break
            
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            scroll_attempts += 1
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            break
    
    print(f"Finished scraping. Collected {len(tweets)} tweets.")
    driver.quit()
    return list(tweets)[:max_tweets]

def scrape_tweets(query, max_tweets):
    driver = setup_driver(HEADLESS)
    search_url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
    driver.get(search_url)
    time.sleep(5)

    tweets = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(tweets) < max_tweets:
        elements = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
        for el in elements:
            tweets.add(el.text)
            print("Found tweet!")
            print(el.text)
            if len(tweets) >= max_tweets:
                break

        # Scroll para baixo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    return list(tweets)[:max_tweets]



def classify_and_group(tweets):
    grouped = defaultdict(list)
    sentiment_counts = defaultdict(int)

    for tweet in tweets:
        result = sentiment_analysis(tweet)[0]
        label = result["label"].capitalize()
        grouped[label].append(tweet)
        sentiment_counts[label] += 1

    total = sum(sentiment_counts.values())

    print("\nPorcentagens por sentimento:")
    for label, count in sentiment_counts.items():
        percentage = (count / total) * 100
        print(f"{label}: {percentage:.2f}%")

    return grouped


def summarize_emotions(grouped_tweets):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summaries = {}

    for emotion, texts in grouped_tweets.items():
        # Randomly select up to 10 texts from this emotion group
        if len(texts) > 10:
            selected_texts = random.sample(texts, 10)
        else:
            selected_texts = texts
        
        combined = " ".join(selected_texts)

        if len(combined.split()) < 30:
            summaries[emotion] = "(Muito pouco conteúdo para sumário.)"
            continue

        summary = summarizer(combined, max_length=300, min_length=30, do_sample=False)
        emoji = label_to_emoji.get(emotion, "❓")
        summaries[emotion] = f"{summary} {emoji}"
    return summaries

if __name__ == "__main__":
    tweets = scrape_tweets_with_auth(SEARCH_QUERY, 100)
    if not tweets:
        print("Nenhum tweet encontrado.")
        exit()

    grouped = classify_and_group(tweets)
    print(tweets)
    summaries = summarize_emotions(grouped)

    print(f"\n Resumo de sentimentos encontrados para '{SEARCH_QUERY}':\n")
    for emotion, summary in summaries.items():
        print(f" {emotion}: {summary}\n")
