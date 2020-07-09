from lib import iucn_navigator, database, logclass
import os, sys
import json
from dotenv import load_dotenv

load_dotenv()

IUCN_USERNAME = os.getenv("IUCN_USERNAME")
IUCN_PASSWORD = os.getenv("IUCN_PASSWORD")
FIREFOX_PROFILE_PATH = os.getenv("FIREFOX_PROFILE_PATH")
IUCN_BASE_URL = os.getenv("IUCN_BASE_URL")
IUCN_ACCOUNT_URL = os.getenv("IUCN_ACCOUNT_URL")
DEBUG = os.getenv("DEBUG")=="True"

logfile = "log/iucn_request_remover.log"

logger = logclass.LogClass("iucn request remover",logfile)

if DEBUG==True:
    logger.info("running in test mode (.env file: DEBUG=True)")

always_delete = False

if len(sys.argv)>1:
    always_delete = (sys.argv[1]=="always_delete")
    logger.info("always_delete set to {}".format(always_delete))

iucn = iucn_navigator.IucnNavigator()

iucn.set_debug(DEBUG)
iucn.set_profile_path(FIREFOX_PROFILE_PATH)
iucn.init_driver()
iucn.set_credentials(IUCN_USERNAME,IUCN_PASSWORD)
iucn.set_logger(logger)

db = database.Database()

previous_downloads = db.get_downloads()
iucn.set_previous_downloads(previous_downloads)

logger.info("found {} downloads".format(len(previous_downloads)))

iucn.set_url(IUCN_BASE_URL)
iucn.open_url()
iucn.do_login()

logger.info("logged in")

iucn.set_url(IUCN_ACCOUNT_URL)
iucn.open_url()

logger.info("removing download links")

iucn.remove_download_links(always_delete)

logger.info("done")

