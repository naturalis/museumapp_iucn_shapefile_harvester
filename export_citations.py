import os, csv, sys, re
from dotenv import load_dotenv
from lib import database, logclass

logfile = "log/citation_export.log"
logger = logclass.LogClass("citation exporter",logfile)

logger.info("logging to {}".format(logfile))

load_dotenv()

try:
    infile = sys.argv[1]
except Exception as e:
    print("need a csv file with map file names")
    raise SystemExit

try:
    outfile = sys.argv[2]
except Exception as e:
    print("need a csv outfile")
    raise SystemExit


map_title_dutch = os.getenv("MAP_TITLE_DUTCH")
map_title_english = os.getenv("MAP_TITLE_ENGLISH")
maps_base_url = os.getenv("MAPS_BASE_URL")

infile_lines = 0
exported = 0
no_citation = 0

mapfiles = []
with open(infile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        mapfiles.append([re.sub("_"," ",re.sub("_(\d)[^\.]*(\.jpg)","",row[0])),row[0]])
        infile_lines = infile_lines + 1


db = database.Database()
citations = db.get_citations()
with open(outfile, 'w') as csvfile:
    spamwriter = csv.writer(csvfile)
    for mapfile in mapfiles:
        citation = [i for i in citations if i[0]==mapfile[0]]
        if len(citation)==1:
            spamwriter.writerow([
                mapfile[0],
                maps_base_url + mapfile[1],
                map_title_dutch.format(mapfile[0]),
                map_title_english.format(mapfile[0]),
                citation[0][1],
            ])
            exported = exported + 1
        else:
            logger.warning("'{}' has no citation, skipping map".format(mapfile[0]))
            no_citation = no_citation + 1

logger.info("exported {} citations of {} to {} (skipped {})".format(exported,infile_lines,outfile,no_citation))


