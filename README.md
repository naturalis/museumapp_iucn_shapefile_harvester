# IUCN shapefile downloader


## Required
- Python 3
- Selenium
- Firefox


## .env
- IUCN_USERNAME = credentials for IUCN site
- IUCN_PASSWORD = idem
- DOWNLOAD_REQUEST_NOTICE="Shape files will be used to create maps for use in the mobile app of Naturalis Biodiversity Center (Leiden, The Netherlands)"
- FIREFOX_PROFILE_PATH = path to a firefox profile (such as: /home/maarten/.mozilla/firefox/yau20ogf.IUCN); profile should have automatic savinf og downloaded files, and use DOWNLOAD_FOLDER (see below) as download folder
- DOWNLOAD_FOLDER = folder to downlaod to
IUCN_BASE_URL=https://www.iucnredlist.org/
IUCN_SPECIES_URL=http://apiv3.iucnredlist.org/api/v3/taxonredirect/{}
IUCN_SYNONYM_URL=http://apiv3.iucnredlist.org/api/v3/species/synonym/{}?token={}
IUCN_ACCOUNT_URL=https://www.iucnredlist.org/account
IUCN_SPECIES_BY_NAME_URL=http://apiv3.iucnredlist.org/api/v3/species/{}?token={}
IUCN_TOKEN=2fb242517c37b7693496a6e77a441c2c17b0894a49d829161e601d00203d35f3
PIPELINE_USERNAME=pipeline
PIPELINE_PASSWORD=paradijsvogel
DEBUG=False



## Creating download links

Run:

```
python3 create_download_links.py input.csv
```



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

