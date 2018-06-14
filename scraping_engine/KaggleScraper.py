from bs4 import BeautifulSoup
import urllib.request

class KaggleScraper:

    # Class for the Kaggle Dataset Repository scraper

    def __init__(self):
        self.base_url = "https://www.kaggle.com/datasets"

        self.repo = 2 # Kaggle

    def get_data(self):
        f = urllib.request.urlopen(self.base_url)
        bs = BeautifulSoup(f,"lxml")
        return bs

    def scrape_data(self):
        return self.get_data()
