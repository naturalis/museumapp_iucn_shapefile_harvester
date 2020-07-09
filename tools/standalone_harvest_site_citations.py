import os, csv, sys
from datetime import datetime
from lib import iucn_navigator, database, logclass, env_reader

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

env = env_reader.EnvReader()

IUCN_USERNAME = env.getenv("IUCN_USERNAME")
IUCN_PASSWORD = env.getenv("IUCN_PASSWORD")
IUCN_BASE_URL = env.getenv("IUCN_BASE_URL")
IUCN_SPECIES_URL = env.getenv("IUCN_SPECIES_URL")
IUCN_ACCOUNT_URL = env.getenv("IUCN_ACCOUNT_URL")
IUCN_SYNONYM_URL = env.getenv("IUCN_SYNONYM_URL")
IUCN_SPECIES_BY_NAME_URL = env.getenv("IUCN_SPECIES_BY_NAME_URL")
IUCN_TOKEN = env.getenv("IUCN_TOKEN")
FIREFOX_PROFILE_PATH = env.getenv("FIREFOX_PROFILE_PATH")
DEBUG = env.getenv("DEBUG")=="True"

logger = logclass.LogClass("iucn citation harvester","iucn_download.log")

if DEBUG==True:
    logger.info("running in test mode (.env file: DEBUG=True)")

logger.info("input file: {}".format(infile))


db = database.Database()

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

        if infile_style=="id":
            taxa.append({"name":row[0],"iucn_id":row[1]})
        elif infile_style=="name":
            taxa.append({"name":row[0]})

logger.info("read {} lines".format(len(taxa)))

iucn = iucn_navigator.IucnNavigator()

iucn.set_profile_path(FIREFOX_PROFILE_PATH)
iucn.set_debug(DEBUG)
iucn.init_driver()
iucn.set_credentials(IUCN_USERNAME,IUCN_PASSWORD)

# iucn.set_url(IUCN_BASE_URL)
# iucn.open_url()
# iucn.do_login()

# logger.info("logged in")

# turning a list of just names into names + taxonid
if infile_style=="name":
    logger.info("matching names with taxonid's")
    taxa_with_id = []

    for sp in taxa:
        # if sp["download"]==False:
        #     continue
        iucn.set_url(IUCN_SPECIES_BY_NAME_URL.format(sp["name"],IUCN_TOKEN))
        iucn.open_url()
        iucn_id = iucn.distill_iucn_id()
        if iucn_id:
            taxa_with_id.append({"name":sp["name"],"iucn_id":iucn_id,"harvest_name" : None,"citation" : None})
            logger.info("matched {}: {}".format(sp["name"],iucn_id))
        else:
            logger.debug("couldn't match {} to a taxonid".format(sp["name"]))

    logger.info("turned {} names into {} names with a taxonid".format(len(taxa),len(taxa_with_id)))
    taxa = taxa_with_id

processed = 0
harvested = 0

logger.info("finding citations")
iucn.set_implicit_wait(3)

spamwriter = csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

for i in range(len(taxa)):
    sp = taxa[i]

    try:
        iucn.set_url(IUCN_SPECIES_URL.format(sp["iucn_id"]))
        iucn.open_url()

        is_species_page = iucn.check_species_page()

        if is_species_page:
            citation = iucn.harvest_citation()
            if citation:
                taxa[i]['citation'] = citation
                logger.info("harvested {}: {}".format(sp["name"],taxa[i]['citation']))
                harvested = harvested + 1
            else:
                logger.info("found no citation for {}".format(sp["name"]))
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
                    citation = iucn.harvest_citation()
                    if citation:
                        taxa[i]['citation'] = citation
                        logger.info("harvested {} (by synonym {}): {}".format(syn["name"],sp["name"],taxa[i]['citation']))
                        harvested = harvested + 1
        
        spamwriter.writerow([taxa[i]['name'],taxa[i]['citation']])

    except Exception as e:
        logger.info("failed {} ({})".format(sp["name"],str(e).strip()))
       

    processed = processed + 1

    if (processed % 25) == 0:
        logger.debug("processed {} / {}".format(processed,len(taxa)))
        logger.debug("harvested {}".format(harvested))


logger.info("total processed {} / {}".format(processed,len(taxa)))
logger.info("total harvested {}".format(harvested))

logger.info("done")
