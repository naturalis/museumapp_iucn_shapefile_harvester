import os, shutil, json, time
import urllib.request as request
from datetime import datetime
from os import listdir
from os.path import isfile, join
from threading import Thread
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class IucnNavigator:

    download_folder = None
    debug = False
    logger = None
    previous_downloads = []
    synonyms = []
    have_skipped = []
    batch_size = 100
    downloaded = 0
    implicit_wait = None
    taxon = None

    def __init__(self):
        pass


    def __del__(self):
        if not self.debug:
            self.driver.quit()


    def set_debug(self,state):
        self.debug = state


    def set_credentials(self,username,password):
        self.username = username
        self.password = password


    def set_profile_path(self,firefox_profile_path):
        self.firefox_profile_path = firefox_profile_path


    def set_download_notice(self,download_notice):
        self.download_notice = download_notice


    def set_download_folder(self,download_folder):
        self.download_folder = download_folder


    def set_previous_downloads(self,previous_downloads):
        self.previous_downloads = previous_downloads


    def set_synonyms(self,synonyms):
        self.synonyms = synonyms


    def set_logger(self,logger):
        self.logger = logger


    def set_batch_size(self,batch_size):
        self.batch_size = batch_size


    def set_url(self,url):
        self.url = url


    def set_implicit_wait(self,implicit_wait):
        self.implicit_wait = implicit_wait


    def set_taxon(self,taxon):
        self.taxon = taxon


    def open_url(self):
        if self.implicit_wait:
            self.driver.implicitly_wait(self.implicit_wait) # seconds
        self.driver.get(self.url)


    def init_driver(self):
        profile = webdriver.FirefoxProfile(self.firefox_profile_path)
        if not self.download_folder == None:
            profile.set_preference("browser.download.dir", self.download_folder)
        self.driver = webdriver.Firefox(profile,log_path="./log/geckodriver.log")


    def do_login(self):
        element = self.driver.find_element_by_id("login-button")
        element.click()

        element = self.driver.find_element_by_id("login-modal-email")
        element.send_keys(self.username)

        element = self.driver.find_element_by_id("login-modal-password")
        element.send_keys(self.password)

        element = self.driver.find_element_by_name("button")
        element.click()


    def parse_synonym_page(self):
        element = self.driver.find_element_by_id("json")
        d = element.get_attribute("innerHTML")
        e = json.loads(d)
        if e["count"]>0:
            return { "name" : e["result"][0]["accepted_name"], "accepted_id" : e["result"][0]["accepted_id"] }
        else:
            return False


    def check_species_page(self):
        try:
            element = self.driver.find_element_by_id("json")
            d = element.get_attribute("innerHTML")
            e = json.loads(d)
        except Exception:
            return True

        if e["message"] == "Species id not found!":
            return False
        else:
            raise ValueError(e["message"])


    def distill_iucn_id(self):
        try:
            element = self.driver.find_element_by_id("json")
            d = element.get_attribute("innerHTML")
            e = json.loads(d)
            return e["result"][0]["taxonid"]
        except Exception:
            return False


    def click_element(self,tag_name,text):
        element = self.driver.find_elements_by_tag_name(tag_name)
        for ele in element:
            if ele.text==text:
                ele.click()
                break


    def do_shapefile_download_click(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "download_search_results"))
        )

        element = self.driver.find_element_by_name("download_search_results")
        element.click()

        element = self.driver.find_element_by_link_text("Range data - Polygons (SHP)")
        element.click()

        element = self.driver.find_element_by_id("description")
        element.send_keys(self.download_notice)

        self.click_element("button","Next")

        element = self.driver.find_element_by_id("one_off_reproduction_yes")
        element.click()

        self.click_element("button","Next")

        element = self.driver.find_elements_by_tag_name("label")
        for ele in element:
            if ele.get_attribute("for")=="terms_of_use":
                ele.click()
                break

        if not self.debug:
            self.click_element("button","Finish")
        else:
            raise ValueError("didn't finalize download request (debug True)")


    def click_download_links(self):
        self.logger.info("download batch size {}".format(self.batch_size))

        self.downloads = []
        element = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/main/div/div[2]/div/div/article[2]/header/ol")
        lis = element.find_elements_by_tag_name("li")
        for li in lis:

            if self.downloaded >= self.batch_size:
                self.logger.info("reached download batch size {}; exiting".format(self.batch_size))
                break

            files_before = self.get_downloaded_files_list()

            subdivs = li.find_elements_by_tag_name("div")

            tmp = subdivs[0].text.split("\n")
            date = tmp[0].replace("Search on","").replace(" at "," ").strip()
            taxon = tmp[1].replace("Description:","").strip()

            if self.was_downloaded_previously(taxon):
                self.logger.info("skipping {} (previously downloaded)".format(taxon))
                continue

            synonym = self.resolve_synonym(taxon)

            if not synonym:
                label = taxon
            else:
                label = "{}_[{}]".format(synonym,taxon)

            link = subdivs[2].find_element_by_tag_name("a")

            if not self.debug:
                try:
                    link.click()

                    files_after = self.get_downloaded_files_list()
                    files_diff = list(set(files_after) - set(files_before))

                    new_name = "redlist-species-data--{}--({}).zip".format(label.lower().replace(" ","_"),date)
                    new_file = self.rename_downloaded_file(files_diff[0],new_name)

                    self.logger.info("downloaded {} to {}".format(taxon,new_file))

                    self.downloads.append({
                        "taxon" : taxon,
                        "file" : new_file,
                        "search_date" : date,
                        "download_date" : str(datetime.fromtimestamp(datetime.timestamp(datetime.now())))
                        })

                    self.downloaded += 1

                except Exception as err:
                    self.logger.info("error occurred while downloading {}: {}".format(taxon,err))
                    
            else:
                self.logger.info("skipped actual download of {} (debug mode)".format(taxon))


    def get_downloaded_species(self):
        return json.dumps(self.downloads)


    def get_downloaded_files_list(self):
        onlyfiles = [f for f in listdir(self.download_folder) if isfile(join(self.download_folder, f))]
        return onlyfiles


    def rename_downloaded_file(self,old_name,new_name):
        new = os.path.join(self.download_folder,new_name)
        shutil.move(os.path.join(self.download_folder,old_name),new)
        return new


    def was_downloaded_previously(self,name):
        name_match = [item for item in self.previous_downloads if item[0] == name ]
        if name_match:
            return True
        else:
            return False


    def resolve_synonym(self,name):
        name_match = [item for item in self.synonyms if item[0] == name ]
        if name_match:
            return name_match[0][1]
        else:
            return False


    def harvest_citation(self):
        try:
            citation = ""
            tags = self.driver.find_elements_by_xpath("//*[contains(text(), 'The IUCN Red List of Threatened Species.')]")
            for tag in tags:
                if tag.tag_name=="small":
                    citation = tag.text

            return citation
        except Exception as e:
            logger.info("failed citation for {} ({})".format(self.taxon,str(e).strip()))
            return False


    def remove_download_links(self,always_delete=False):
        running = True

        while running:

            try:
                element = self.driver.find_element_by_xpath("//*[contains(text(), 'Saved downloads')]/../ol")
                li = element.find_element_by_tag_name("li")
                subdivs = li.find_elements_by_tag_name("div")
                tmp = subdivs[0].text.split("\n")
                taxon = tmp[1].replace("Description:","").strip()

                if not always_delete and not self.was_downloaded_previously(taxon) and not taxon in self.have_skipped:
                    self.logger.info("skipping {} (not yet downloaded)".format(taxon))
                    self.have_skipped.push(taxon)
                    continue

                button = subdivs[3].find_element_by_class_name("button--secondary")
                button.click()
                alert = self.driver.switch_to_alert()

                if not self.debug:
                    alert.accept()
                    time.sleep(1)
                    self.logger.info("removed request for {}".format(taxon))
                else:
                    alert.dismiss()
                    self.logger.info("skipped actual removal of {} (debug mode)".format(taxon))
                    running = False

            except Exception as e:
                # print(str(e))
                running = False

