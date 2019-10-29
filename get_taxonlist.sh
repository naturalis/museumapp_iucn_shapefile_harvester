#!/bin/bash

source ./.env

RAW_DATA=$(curl -s -XGET https://$PIPELINE_USERNAME:$PIPELINE_PASSWORD@pipeline-museumapp.naturalis.nl/taxon_list.php)

echo $RAW_DATA | jq -r '.[]' | sed -e 's/@/\"/g'

