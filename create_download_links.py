import os, csv, sys
from datetime import datetime
from dotenv import load_dotenv
from lib import iucn_navigator, database, logclass

# python create_download_links.py input/taxon_list.csv
# input file either "name","id" or just "name"

try:
    infile = sys.argv[1]
except Exception as e:
    print("need a csv file")
    raise SystemExit

try:
    limit = int(sys.argv[2])
except Exception as e:
    limit = 0


load_dotenv()

IUCN_USERNAME = os.getenv("IUCN_USERNAME")
IUCN_PASSWORD = os.getenv("IUCN_PASSWORD")
DOWNLOAD_REQUEST_NOTICE = os.getenv("DOWNLOAD_REQUEST_NOTICE")
FIREFOX_PROFILE_PATH = os.getenv("FIREFOX_PROFILE_PATH")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")
IUCN_BASE_URL = os.getenv("IUCN_BASE_URL")
IUCN_SPECIES_URL = os.getenv("IUCN_SPECIES_URL")
IUCN_ACCOUNT_URL = os.getenv("IUCN_ACCOUNT_URL")
IUCN_SYNONYM_URL = os.getenv("IUCN_SYNONYM_URL")
IUCN_SPECIES_BY_NAME_URL = os.getenv("IUCN_SPECIES_BY_NAME_URL")
IUCN_TOKEN = os.getenv("IUCN_TOKEN")
DEBUG = os.getenv("DEBUG")=="True"

logger = logclass.LogClass("iucn download requester","iucn_download.log")

if DEBUG==True:
    logger.info("running in test mode (.env file: DEBUG=True)")

logger.info("input file: {}".format(infile))
logger.info("taxon limit: {}".format(limit))


logger.info("firefox profile path: {}".format(FIREFOX_PROFILE_PATH))
logger.info("download folder: {}".format(DOWNLOAD_FOLDER))
logger.info("download request notice: {}".format(DOWNLOAD_REQUEST_NOTICE))


db = database.Database()
past_requests = db.get_download_requests()

taxa = []
requested_previous = 0
infile_style = None

logger.info("reading {}".format(infile))

with open(infile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        if infile_style == None:
            try:
                row[1]
                infile_style="id"
            except Exception as e:
                infile_style="name"

            logger.info("infile style: {}".format(infile_style))

        prev = None
        name_match = [item for item in past_requests if item[0] == row[0] ]

        if name_match:
            prev = "name"
            requested_previous = requested_previous + 1
        else:
            synonym_match = [item for item in past_requests if item[1] == row[0] ]
            if name_match:
                prev = "synonym"
                requested_previous = requested_previous + 1

        if infile_style=="id":
            taxa.append({"name":row[0],"iucn_id":row[1],"download":prev==None,"previous_match":prev})
        elif infile_style=="name":
            taxa.append({"name":row[0],"download":prev==None,"previous_match":prev})


logger.info("read {} lines, of which {} were previously requested".format(len(taxa),requested_previous))


iucn = iucn_navigator.IucnNavigator()

iucn.set_debug(DEBUG)
iucn.set_download_folder(DOWNLOAD_FOLDER)
iucn.set_profile_path(FIREFOX_PROFILE_PATH)
iucn.init_driver()
iucn.set_credentials(IUCN_USERNAME,IUCN_PASSWORD)
iucn.set_download_notice(DOWNLOAD_REQUEST_NOTICE)

iucn.set_url(IUCN_BASE_URL)
iucn.open_url()
iucn.do_login()

logger.info("logged in")

# turning a list of just names into names + taxonid
if infile_style=="name":
    logger.info("matching names with taxonid's")
    taxa_with_id = []

    for sp in taxa:
        if sp["download"]==False:
            continue
        iucn.set_url(IUCN_SPECIES_BY_NAME_URL.format(sp["name"],IUCN_TOKEN))
        iucn.open_url()
        iucn_id = iucn.distill_iucn_id()
        if iucn_id:
            taxa_with_id.append({"name":sp["name"],"iucn_id":iucn_id,"download":sp["download"],"previous_match":sp["previous_match"]})
            logger.info("matched {}: {}".format(sp["name"],iucn_id))
        else:
            logger.debug("couldn't match {} to a taxonid".format(sp["name"]))

    logger.info("turned {} names into {} names with a taxonid".format(len(taxa),len(taxa_with_id)))
    taxa = taxa_with_id

processed = 0
scheduled = 0

logger.info("finding download links")

for sp in taxa:
    try:
        if sp["download"]==False:
            logger.debug("skipping {} (download previously requested)".format(sp["name"]))
            continue

        iucn.set_url(IUCN_SPECIES_URL.format(sp["iucn_id"]))
        iucn.open_url()

        is_species_page = iucn.check_species_page()

        if is_species_page:
            iucn.do_shapefile_download_click()
            logger.info("scheduled for download: {}".format(sp["name"]))
            db.save_download_request(sp["name"],str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))))
            scheduled = scheduled + 1
        else:
            iucn.set_url(IUCN_SYNONYM_URL.format(sp["name"],IUCN_TOKEN))
            iucn.open_url()
            syn = iucn.parse_synonym_page()
            if syn==False:
                raise Exception("couldn't find species by name or synonym")
            else:
                iucn.set_url(IUCN_SPECIES_URL.format(syn["accepted_id"]))
                iucn.open_url()
                if not iucn.check_species_page():
                    raise Exception("resolved synonym, but resolved ID led nowhere (!?)")
                else:
                    iucn.do_shapefile_download_click()
                    logger.info("scheduled for download: {} (by synonym {})".format(syn["name"],sp["name"]))
                    db.save_download_request(syn["name"],str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))),sp["name"])
                    scheduled = scheduled + 1

    except Exception as e:
        logger.info("failed {} ({})".format(sp["name"],str(e).strip()))

    processed = processed + 1

    if limit > 0 and scheduled >= limit:
        logger.info("reached limit {}".format(limit))
        break

    if (processed % 25) == 0:
        logger.debug("processed {} / {}".format(processed,len(taxa)))
        logger.debug("scheduled {}".format(scheduled))


logger.info("total processed {} / {}".format(processed,len(taxa)))
logger.info("total scheduled {}".format(scheduled))

logger.info("done")
