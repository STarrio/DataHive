from bs4 import BeautifulSoup
import urllib.request
import re
import importlib

utils = importlib.import_module('utils', package="./")


class DataverseScraper:

    """Class for the Dataverse Harvard DataSet Repository scraper"""

    def __init__(self):
        # base_url prepared for string formatting (page parameter)
        self.base_url = "https://dataverse.harvard.edu"
        self.list_url = "/dataverse/harvard?q=&fq0=metadataSource%3A%22Harvard+Dataverse%22&types=datasets&sort=dateSort&order=asc&page={0}"
        self.file_download_url = "https://dataverse.harvard.edu/api/access/datafiles/{0}"

    def get_data(self, page):
        print(self.base_url + self.list_url.format(page))
        f = urllib.request.urlopen(self.base_url + self.list_url.format(page))
        bs = BeautifulSoup(f, 'html.parser')
        return bs.find_all(class_="datasetResult")

    def get_ds(self, path):
        # Retrieves data from a single dataset
        print(self.base_url + path)
        f = urllib.request.urlopen(self.base_url + path)
        bs = BeautifulSoup(f, 'html.parser')
        return bs

    def scrape_data(self, pages=[]):
        # Actually does the scraping
        # Attributes:
        # - Title
        # - Url
        # - Publication date
        # - Authors
        # - Description
        # - Keywords
        # - Number of files
        # - Url download files
        # - Files (for each file):
        #      - Name
        #      - Id

        entries = []

        for page in pages:
            l = self.get_data(page)
            for l_ds in l:
                entry = {}
                path = l_ds.find(class_="card-title-icon-block").a['href']
                detail = self.get_ds(path)
                metadata = detail.find('div', attrs={"id": re.compile("metadataMapTab")}).find(class_="metadata-panel-body")

                # Dataset metadata
                entry['url'] = path
                entry['pub_date'] = metadata.find(
                    attrs={"for": "metadata_publicationDate"}).find_next_sibling().text.strip()
                entry['title'] = metadata.find(attrs={"for": "metadata_title"}).find_next_sibling().text.strip()
                entry['authors'] = utils.str_split_strip('\n', metadata.find(attrs={"for": "metadata_author"}).find_next_sibling().text)
                entry['description'] = metadata.find(attrs={"for": "metadata_dsDescription"}).find_next_sibling().text.strip()
                keywords = metadata.find(attrs={"for": "metadata_keyword"})
                entry['keywords'] = utils.str_split_strip(',|\n', keywords.find_next_sibling().text) if keywords else None

                # Files
                files = detail.find('div', attrs={"id": re.compile("dataFilesTab")}).find_all('a', href=re.compile('fileId=(\d+)&'))

                ids_file = []
                entry['files'] = {}
                for file in files:
                    file_id = re.search('fileId=(\d+)&', file.get('href')).group(1)
                    ids_file.append(file_id)
                    file_name = file.text
                    entry['files'][file_id] = file_name

                entry['files_num'] = len(ids_file)
                entry['files_download_url'] = self.file_download_url.format(",".join(map(str, ids_file)))
                entries.append(entry)

        return entries


if __name__ == "__main__":
    sc = DataverseScraper()
    s = sc.scrape_data(range(1, 2))
    print(s)
