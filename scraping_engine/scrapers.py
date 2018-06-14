from bs4 import BeautifulSoup
import urllib.request

class UCIScraper:
    # Class for the UCI Machine Learning Repository scraper
    def __init__(self):
        self.base_url = "http://archive.ics.uci.edu/ml/"
        self.table_url = "datasets/?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=table"

    def get_data(self):
        # Retrieves data from /datasets.html
        f = urllib.request.urlopen(self.base_url+self.table_url)
        bs = BeautifulSoup(f,"lxml")
        l = bs.find_all("table")
        return l

    def get_ds(self,path):
        # Retrieves data from a single dataset
        pass

    def scrape_data(self):
        print(self.base_url+self.table_url)
        # Actually does the scraping
        # Attributes:
        # - Name
        # - no instances
        # - no attrs
        l = self.get_data()
        l_ds=l[1].find_all("table")[3].find_all("tr")[1:]
        entries = []
        for i in range(len(l_ds)//2):
            entry = {}
            ds_soup = l_ds[2*i]
            entry["url"] = ds_soup.a['href']
            entry["name"] = ds_soup.contents[1].table.tr.contents[1].p.string
            entry["no_instances"] = ds_soup.contents[11].p.string.replace('\xa0','') if len(ds_soup.contents)>11 else ""
            entry["no_attr"] = ds_soup.contents[13].p.string.replace('\xa0','') if len(ds_soup.contents)>13 else ""
            # scraping over url with get_ds(url)
            entries.append(entry)
        return entries


# if __name__ == "__main__":
#     sc = DataverseScraper()
#     datasets, files = sc.scrape_data(range(1, 2))
#     print(datasets)
#     pass
