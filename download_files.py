from lib import iucn_navigator, database, logclass
import os, sys
import json
from dotenv import load_dotenv

load_dotenv()

IUCN_USERNAME = os.getenv("IUCN_USERNAME")
IUCN_PASSWORD = os.getenv("IUCN_PASSWORD")
FIREFOX_PROFILE_PATH = os.getenv("FIREFOX_PROFILE_PATH")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")
IUCN_BASE_URL = os.getenv("IUCN_BASE_URL")
IUCN_SPECIES_URL = os.getenv("IUCN_SPECIES_URL")
IUCN_ACCOUNT_URL = os.getenv("IUCN_ACCOUNT_URL")
DEBUG = os.getenv("DEBUG")=="True"

logger = logclass.LogClass("iucn downloader","iucn_download.log")

if DEBUG==True:
    logger.info("running in test mode (.env file: DEBUG=True)")

iucn = iucn_navigator.IucnNavigator()

iucn.set_debug(DEBUG)
iucn.set_download_folder(DOWNLOAD_FOLDER)
iucn.set_profile_path(FIREFOX_PROFILE_PATH)
iucn.init_driver()
iucn.set_credentials(IUCN_USERNAME,IUCN_PASSWORD)
iucn.set_logger(logger)

logger.info("downloading to {}".format(DOWNLOAD_FOLDER))

db = database.Database()

previous_downloads = db.get_downloads()
iucn.set_previous_downloads(previous_downloads)

synonyms = db.get_synonyms()
iucn.set_synonyms(synonyms)


logger.info("found {} previous downloads".format(len(previous_downloads)))

iucn.set_url(IUCN_BASE_URL)
iucn.open_url()
iucn.do_login()

logger.info("logged in")

iucn.set_url(IUCN_ACCOUNT_URL)
iucn.open_url()

logger.info("starting download links")

iucn.set_batch_size(200)

iucn.click_download_links()

logger.info("done downloading")
logger.info("logging downloads")

downloads = iucn.get_downloaded_species()

for download in json.loads(downloads):
    db.save_download(download["taxon"],download["download_date"],download["search_date"])

logger.info("done")

