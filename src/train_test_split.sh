#!/bin/bash

PTP_DATA_DIR="data/split_audio"
TACOTRON_DATA_DIR="src/tacotron2/data"

FILELIST_DIR="src/tacotron2/filelists"
TRAIN_FILE="$FILELIST_DIR/ljs_audio_text_train_filelist.txt"
VAL_FILE="$FILELIST_DIR/ljs_audio_text_val_filelist.txt"

rm -f $TACOTRON_DATA_DIR/*
cp $PTP_DATA_DIR/* $TACOTRON_DATA_DIR

cat data.txt | head -n-10 > $TRAIN_FILE
cat data.txt | tail -n-10 > $VAL_FILE