#!/bin/bash

# source ./.env
MAPS_BASE_URL=""

INDIR=$1
OUTDIR=$2

if [ -z "$INDIR" ]; then
    echo "need an input directory"
    exit
fi

if [ -z "$OUTDIR" ]; then
    echo "need an output directory"
    exit
fi

FILES=${INDIR}*.jpg
DATE=$(date "+%F--%T")
ADD_ON="--trimmed--(${DATE})"

EXTRA_NORTHSOUTH_PIXELS=45

for f in $FILES
do
    FILE=$(basename $f)
    NEW_NAME=$(echo $FILE | sed s/\.jpg/$ADD_ON\.jpg/g)
    NEW_NAME=$(echo $NEW_NAME | sed s/[.][/]//)
    NEW_PATH=${OUTDIR}${NEW_NAME}

    ## just trim all the white
    # convert $f -fuzz 5% -trim $NEW_PATH

    ## trim all the white and buffer north & south, because Q42 creates rounded buffers
    convert $f -fuzz 5% -trim -background white -gravity north -splice 0x${EXTRA_NORTHSOUTH_PIXELS} -gravity south -splice 0x${EXTRA_NORTHSOUTH_PIXELS} ${NEW_PATH}

    ## create rounded corners! woohoo!
    # convert $f -fuzz 5% -trim \( +clone -alpha extract \
    #     \( -size 25x25 xc:black -draw 'fill white circle 25,25 25,0' -write mpr:arc +delete \) \
    #     \( mpr:arc \) -gravity northwest -composite \
    #     \( mpr:arc -flip \) -gravity southwest -composite \
    #     \( mpr:arc -flop \) -gravity northeast -composite \
    #     \( mpr:arc -rotate 180 \) -gravity southeast -composite \) \
    #     -alpha off -compose CopyOpacity -composite -compose over \
    #     \( -clone 0 -fill black -colorize 100 \) \
    #     \( -clone 0 -alpha extract -virtual-pixel black -morphology edgein octagon:3  \) \
    #     -compose over -composite \
    #     \( +clone -background white -shadow 0x0 \) \
    #     +swap -background none -layers merge +repage $NEW_PATH

    # echo "converted $f to ${NEW_PATH}"
    TAXON=$(echo ${FILE} | sed -e 's/_print.*$//g' | sed -e 's/_/ /g')
    TAXON=$(echo ${FILE} | sed -e 's/_print.*$//g' | sed -e 's/[0-9\-]*//g' | sed -e 's/_/ /g' | sed -e 's/[[:space:]]*$//') 
    echo "\"${TAXON}\",\"${MAPS_BASE_URL}${NEW_NAME}\""
done

