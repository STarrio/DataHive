from bs4 import BeautifulSoup
import urllib.request
import re
import datetime

from utils import str_split_strip, ex


class DataverseScraper:

    """Class for the Dataverse Harvard DataSet Repository scraper"""

    def __init__(self):
        # base_url prepared for string formatting (page parameter)
        self.base_url = "https://dataverse.harvard.edu"
        self.list_url = "/dataverse/harvard?q=&fq0=metadataSource%3A%22Harvard+Dataverse%22&types=datasets&sort=dateSort&order=asc&page={0}"
        self.file_download_url = "https://dataverse.harvard.edu/api/access/datafiles/{0}"
        self.repo = 1  # DATAVERSE

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
        # - Source repo id (self.repo)
        # - Files (for each file):
        #      - Name
        #      - Id at repo
        #      - Size
        #      - Type

        entries = []
        files = []
        categories = []
        for page in pages:
            l = self.get_data(page)
            for l_ds in l:
                entry = {}
                path = l_ds.find(class_="card-title-icon-block").a['href']
                detail = self.get_ds(path)
                metadata = detail.find('div', attrs={"id": re.compile("metadataMapTab")}).find(class_="metadata-panel-body")

                # Dataset metadata
                entry['url'] = self.base_url + path

                pub_date_data = metadata.find_all(
                    attrs={"for": "metadata_publicationDate"})[1].find_next_sibling().text.strip()
                pub_date = datetime.datetime.strptime(pub_date_data, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
                entry['publication_date'] = pub_date

                entry['title'] = ex(lambda: metadata.find(attrs={"for": "metadata_title"}).find_next_sibling().text.strip())
                entry['authors'] = ex(lambda: str_split_strip('\n', metadata.find(attrs={"for": "metadata_author"}).find_next_sibling().text))
                entry['description'] = ex(lambda: metadata.find(attrs={"for": "metadata_dsDescription"}).find_next_sibling().text.strip())
                categ = ex(lambda: metadata.find(attrs={"for": "metadata_subject"}).find_next_sibling().text.strip())
                categories.append(categ)
                entry['abstract'] = None

                keywords = metadata.find(attrs={"for": "metadata_keyword"})
                entry['keywords'] = str_split_strip(',|\n', keywords.find_next_sibling().text) if keywords and len(keywords.find_next_sibling().text) < 300 else None

                # Files
                files_data = detail.find('div', attrs={"id": re.compile("dataFilesTab")}).find_all('td', class_='col-file-metadata')

                dataset_files = []
                for file in files_data:
                    a_file = file.find('a')

                    file_id = re.search('fileId=(\d+)&', a_file.get('href')).group(1)
                    file_name = a_file.text
                    file_size = file.find('span', attrs={"id": re.compile("fileSize")}).text.strip('-| ')
                    file_type = file.find('span', attrs={"id": re.compile("fileTypeOutputRegular|fileTypeOutputTabular")}).text

                    dataset_files.append({'id_in_source': file_id, 'name': file_name,
                                          'size': file_size, 'file_type': file_type})

                entry['source_id'] = self.repo

                entries.append(entry)
                files.append(dataset_files)

        return entries, files, categories
