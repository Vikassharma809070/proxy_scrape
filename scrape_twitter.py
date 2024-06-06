from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pymongo
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_proxy():
    proxy_auth = f"{os.getenv('PROXYMESH_USERNAME')}:{os.getenv('PROXYMESH_PASSWORD')}"
    proxy_url = f'http://{proxy_auth}@proxy.proxyserver.com:port'
    return proxy_url

def get_trending_topics():
    # Set up ProxyMesh
    proxy = get_proxy()
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get('https://twitter.com/login')
        
        # Get Twitter credentials from environment variables
        username = os.getenv('TWITTER_USERNAME')
        password = os.getenv('TWITTER_PASSWORD')
        
        # Logging into Twitter
        driver.find_element(By.NAME, 'session[username_or_email]').send_keys(username)
        driver.find_element(By.NAME, 'session[password]').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'div[data-testid="LoginForm_Login_Button"]').click()
        
        # Wait for the page to load
        time.sleep(5)
        
        # Fetch the trending topics
        trends = driver.find_elements(By.CSS_SELECTOR, 'section[aria-labelledby="accessible-list-2"] div.css-1dbjc4n span')
        trending_topics = [trend.text for trend in trends[:5]]
        
        # Get current IP address
        ip_address = requests.get('https://api.ipify.org').text
        
        return trending_topics, ip_address
    
    finally:
        driver.quit()

def save_to_mongodb(trending_topics, ip_address):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['twitter_trends']
    collection = db['trends']
    
    unique_id = str(datetime.now().timestamp())
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        '_id': unique_id,
        'trend1': trending_topics[0],
        'trend2': trending_topics[1],
        'trend3': trending_topics[2],
        'trend4': trending_topics[3],
        'trend5': trending_topics[4],
        'end_time': end_time,
        'ip_address': ip_address
    }
    
    collection.insert_one(data)
    return data

if __name__ == '__main__':
    trending_topics, ip_address = get_trending_topics()
    data = save_to_mongodb(trending_topics, ip_address)
    print('Data saved to MongoDB:', data)
