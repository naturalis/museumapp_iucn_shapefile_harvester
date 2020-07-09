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

THRESHOLD=0.065

if [[ ! -z $3 ]]; then
    THRESHOLD=$3
fi

DIR_WHITES=${OUTDIR}non_world_white_dominant
DIR_WORLD=${OUTDIR}world_maps
DIR_NORMALS=${OUTDIR}original_ok

if [[ "$THRESHOLD" = "reset" ]]; then
    echo "resetting world & white dominant"
    mv $DIR_WHITES/*  $INDIR
    mv $DIR_WORLD/*   $INDIR
    exit
fi

if [[ "$THRESHOLD" = "reset-all" ]]; then
    echo "resetting all"
    mv $DIR_WHITES/*  $INDIR
    mv $DIR_WORLD/*   $INDIR
    mv $DIR_NORMALS/* $INDIR
    exit
fi

mkdir $OUTDIR
mkdir $DIR_WHITES
mkdir $DIR_WORLD
mkdir $DIR_NORMALS

WHITE=#FFFFFF

echo "ratio threshold: $THRESHOLD"
echo "white: $WHITE"

for FILE in $INDIR*.jpg; do

    # convert "$FILE" -colors 256 -depth 8 -format %c histogram:info: | sort -nr | head -n 10
    # exit 0

    # OUT=$(convert "$FILE" -depth 8 -format %c histogram:info: | sort -nr | head -n 10)
    OUT=$(convert "$FILE" -depth 8 -format %c histogram:info: | sort -nr | head -n 100)

    SAVEIFS=$IFS
    IFS=$'\n'
    # COUNT=0
    WHITE_COUNT=0

    for LINE in $OUT; do

        if [[ $LINE == *"$WHITE"* ]]; then
            WHITE_COUNT=$(echo "$LINE" | awk '{print $1}' | sed 's/://')
        fi

        # if [[ $COUNT < 2 ]]; then
        #     if [[ $LINE != *"#FFFFFF"* ]]; then
        #         BIGGEST_NON_WHITE_COUNT=$(echo "$LINE" | awk '{print $1}' | sed 's/://')
        #     fi
        # fi

        # (( COUNT++ ))

    done

    IFS=$SAVEIFS

    if [[ $WHITE_COUNT == 0 ]]; then
        echo "skipping $FILE (found no white)"
        continue
    fi

    W_TIMES_H=$(convert "$FILE" -format "%wx%h" info:)
    W_TIMES_H=$(echo $W_TIMES_H | sed 's/x/*/')
    FULL_IMAGE=$(echo "($W_TIMES_H)" | bc)
    RATIO=$(echo "scale=2; ($WHITE_COUNT/$FULL_IMAGE)" | bc)
    PREDOMINANTLY_WHITE=$(echo "scale=2; ($WHITE_COUNT/$FULL_IMAGE)>=$THRESHOLD" | bc)

    if [[ $PREDOMINANTLY_WHITE == 1 ]]; then

        convert $FILE -fuzz 5% -trim _tmp.jpg
        BORDER_PIXEL=$(convert _tmp.jpg[1x1+3+3] -format "%[fx:int(255*r)],%[fx:int(255*g)],%[fx:int(255*b)]" info:)
        rm _tmp.jpg

        if [[ $BORDER_PIXEL == "0,0,0" ]]; then
            echo "copying $FILE to $DIR_WHITES ($RATIO / $BORDER_PIXEL)"
            cp $FILE $DIR_WHITES
        else
            echo "copying $FILE to $DIR_WORLD ($RATIO / $BORDER_PIXEL)"
            cp $FILE $DIR_WORLD
        fi

    else
        echo "copying $FILE to $DIR_NORMALS ($RATIO)"
        cp $FILE $DIR_NORMALS
    fi

done
