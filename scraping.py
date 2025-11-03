from bs4 import BeautifulSoup as bs4
import requests

def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = bs4(response.content, 'html.parser')
        return soup.get_text()
    else:
        raise Exception(f"Failed to retrieve content from {url}, status code: {response.status_code}")
    
if __name__ == "__main__":
    url = "https://www.bankofbeirut.com/en/FAQ"
    textfile_name = "bank_of_beirut_faq.txt"

    try:
        content = scrape_website(url)
        with open(textfile_name, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Content from {url} has been written to {textfile_name}")
    except Exception as e:
        print(str(e))