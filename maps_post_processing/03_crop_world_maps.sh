#!/bin/bash

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


CREDITS_IMAGE=_credits.png

if [[ ! -f "$CREDITS_IMAGE" ]]; then
    CREDITS_IMAGE=maps_post_processing/_credits.png
fi

if [[ ! -f "$CREDITS_IMAGE" ]]; then
    echo "can't find $CREDITS_IMAGE"
    exit
fi


OUTDIR_WITH_TEXT=${OUTDIR}/partial_text_in_original
OUTDIR_WITHOUT_TEXT=${OUTDIR}/no_text_in_original

mkdir $OUTDIR
mkdir $OUTDIR_WITH_TEXT
mkdir $OUTDIR_WITHOUT_TEXT

EXTRA_NORTHSOUTH_PIXELS=45

FILES=${INDIR}*.jpg

for f in $FILES
do
    FILE=$(basename $f)
    convert $f -fuzz 5% -trim -crop 3038x1505+0+0 -fuzz 5% -trim ${OUTDIR}${FILE}
    echo "cropped $FILE"
    TEXT=$(tesseract ${OUTDIR}${FILE} stdout)
    if [[ $TEXT == *"Sources:"* || $TEXT == *"GeoBase"* ]]; then
        mv ${OUTDIR}${FILE} $OUTDIR_WITH_TEXT
        echo "moved $FILE to 'partial_text_in_original'"
    else
        convert ${OUTDIR}${FILE} -bordercolor black -border 3x3 -background white -gravity north -splice 0x${EXTRA_NORTHSOUTH_PIXELS} -gravity south -splice 0x${EXTRA_NORTHSOUTH_PIXELS} _tmp.jpg
        rm ${OUTDIR}${FILE}

        DIMENSIONS=$(convert "_tmp.jpg" -format "%wx%h" info:)
        WIDTH=$(echo $DIMENSIONS | sed 's/x[[:digit:]]*//')
        HEIGHT=$(echo $DIMENSIONS | sed 's/[[:digit:]]*x//')

        WIDTH=$(echo "($WIDTH-1535)" | bc)
        HEIGHT=$(echo "($HEIGHT-165)" | bc)

        convert _tmp.jpg -page +${WIDTH}+${HEIGHT} ${CREDITS_IMAGE} -flatten ${OUTDIR_WITHOUT_TEXT}/${FILE}
        echo "added border & credits to $FILE"
    fi
    # rm $f
done



