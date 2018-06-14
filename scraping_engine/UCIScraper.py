from bs4 import BeautifulSoup
import urllib.request
import extension_dict

IGNORED_DATASETS = ["UJI Pen Characters (Version 2)",
                                           "Prodigy",
                                           "Reuters Transcribed Subset",
                                           "UJIIndoorLoc-Mag",
                                           "Dishonest Internet users Dataset",
                                           "APS Failure at Scania Trucks",
                                           "IDA2016Challenge",
                                           "chestnut – LARVIC",
                                           "Early biomarkers of Parkinson's disease based on natural connected speech",
                                           "Improved Spiral Test Using Digitized Graphics Tablet for Monitoring Parkinson’s Disease",
                                           "Mesothelioma’s disease data set"]

class UCIScraper:

    # Class for the UCI Machine Learning Repository scraper

    def __init__(self):
        self.base_url = "http://archive.ics.uci.edu/ml/"
        self.table_url = "datasets/?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=table"
        self.repo = 2 # UCI
        self.extension_dict = extension_dict.ext_dict

    def get_data(self):
        # Retrieves data from /datasets.html
        f = urllib.request.urlopen(self.base_url+self.table_url)
        bs = BeautifulSoup(f,"html.parser")
        return bs.find_all("table")

    def get_ds(self,path):
        # Retrieves data from a single dataset
        f = urllib.request.urlopen(self.base_url+path)
        bs = BeautifulSoup(f,'lxml')
        return bs.find_all("table")[1]

    def get_files(self,path):
        # Retrieves data from dataset's files
        f = urllib.request.urlopen(self.base_url+path)
        bs = BeautifulSoup(f,'lxml')
        return bs.table.contents[7:-3]

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
        files = []
        for i in range(len(l_ds)//2):
            entry = {}
            ds_soup = l_ds[2*i]
            path = ds_soup.a['href']
            name = ds_soup.contents[1].table.tr.contents[1].p.string

            # Ignore troublesome dataset with unscrapeable description
            if(name in IGNORED_DATASETS):
                continue

            entry["url"] = self.base_url + path
            entry["name"] = name
            entry["no_instances"] = ds_soup.contents[11].p.string.replace('\xa0','') if len(ds_soup.contents)>11 else ""
            entry["no_attr"] = ds_soup.contents[13].p.string.replace('\xa0','') if len(ds_soup.contents)>13 else ""

            # scraping over url with get_ds(url)
            detail = self.get_ds(path)
            try:
                download_url = detail.table.span.find_next_siblings()[1].contents[2]['href'][3:]
            except:
                print("IGNORE THIS ONE")
                continue
            abstract = detail.p.find_next_sibling().contents[1][2:]
            area = detail.table.find_next_sibling().find_all("tr")[0].find_all("td")[-1].p.string
            description = "".join([s if type(s)==str else s.string for s in detail.find_all("p",class_="small-heading")[1].find_next_sibling().contents if len(s)>6])

            entry["files_download_url"] = self.base_url + download_url
            entry["abstract"] = abstract
            entry["category"] = area
            entry["description"] = description

            files = self.get_files(download_url)

            files_data = [(f.td.find_next_siblings()[0].a['href'],f.td.find_next_siblings()[2].string) for f in files if f!='\n']

            dataset_files = []

            for f in files_data:
                file_id = f[0]
                file_name = f[0]
                file_size = f[1]

                file_name_separated = file_id.split(".")
                file_type = self.extension_dict[file_name_separated[-1]] if len(file_name_separated)>1 else "Plain text"

                dataset_files.append({'id_in_source':file_id, 'name':file_name, 'size':file_size, 'file_type':file_type})

            entry['source_id'] = self.repo
            entries.append(entry)
            files.append(dataset_files)

        return entries, files


# if __name__ == "__main__":
#     sc = DataverseScraper()
#     datasets, files = sc.scrape_data(range(1, 2))
#     print(datasets)
#     pass
