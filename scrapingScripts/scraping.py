from bs4 import BeautifulSoup as bs4
from selenium import webdriver
import requests

def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = bs4(response.content, 'html.parser')
        return soup.get_text()
    else:
        raise Exception(f"Failed to retrieve content from {url}, status code: {response.status_code}")
    
def scrape_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    content = driver.page_source
    driver.quit()
    soup = bs4(content, 'html.parser')
    return soup.get_text()
    
if __name__ == "__main__":
    url = "https://onlinebanking.bankmed.com.lb/?module=faq"
    textfile_name = "bankmed_faq.txt"

    try:
        content = scrape_website(url)
        with open(textfile_name, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Content from {url} has been written to {textfile_name}")
    except Exception as e:
        print(str(e))