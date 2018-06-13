from bs4 import BeautifulSoup
import urllib.request

class UCIScraper:
    # Class for the UCI Machine Learning Repository scraper
    def __init__(self):
        self.base_url = "http://archive.ics.uci.edu/ml/"
        self.table_url = "datasets/?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=table"
        self.repo = 0 # UCI

    def get_data(self):
        # Retrieves data from /datasets.html
        f = urllib.request.urlopen(self.base_url+self.table_url)
        bs = BeautifulSoup(f,"lxml")
        return bs.find_all("table")

    def get_ds(self,path):
        # Retrieves data from a single dataset
        f = urllib.request.urlopen(self.base_url+path)
        bs = BeautifulSoup(f,'lxml')
        return bs.find_all("table")[1]

    def scrape_data(self):

        # Actually does the scraping
        # Attributes:
        # - Name
        # - no instances
        # - no attrs
        # - download link (data folder)
        # - area
        # - abstract
        # - data set information

        l = self.get_data()
        l_ds=l[1].find_all("table")[3].find_all("tr")[1:]
        entries = []
        for i in range(len(l_ds)//2):
            entry = {}
            ds_soup = l_ds[2*i]
            path = ds_soup.a['href']
            entry["url"] = self.base_url + path
            entry["name"] = ds_soup.contents[1].table.tr.contents[1].p.string
            entry["no_instances"] = ds_soup.contents[11].p.string.replace('\xa0','') if len(ds_soup.contents)>11 else ""
            entry["no_attr"] = ds_soup.contents[13].p.string.replace('\xa0','') if len(ds_soup.contents)>13 else ""

            # scraping over url with get_ds(url)
            detail = self.get_ds(path)
            download_url = detail.table.span.find_next_siblings()[1].contents[2]['href'][2:]
            abstract = detail.p.find_next_sibling().contents[1][2:]
            area = detail.table.find_next_sibling().find_all("tr")[0].find_all("td")[-1].p.string
            info = "".join([s for s in detail.find_all("p",class_="small-heading")[1].find_next_sibling().contents if len(s)>6])

            entry["files_download_url"] = self.base_url + download_url
            entry["abstract"] = abstract
            entry["category"] = area
            entry["info"] = info

            entries.append(entry)
        return entries


# if __name__ == "__main__":
#     sc = DataverseScraper()
#     datasets, files = sc.scrape_data(range(1, 2))
#     print(datasets)
#     pass
