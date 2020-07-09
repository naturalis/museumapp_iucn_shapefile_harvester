#!/bin/bash

source ./.env

RAW_DATA=$(curl -s -XGET https://$PIPELINE_USERNAME:$PIPELINE_PASSWORD@pipeline-museumapp.naturalis.nl/iucn.php)

echo $RAW_DATA | jq -r '.[] | "@" + .scientific_name + "@," + .taxonid' | sed -e 's/@/\"/g'

