#! /usr/bin/env sh
# gets the dataset from kaggle, ensures credentials are set up correctly
# returns a zip file to the output folder
DATASET_NAME=$1
FILE_NAME=$2
KAGGLE_CONFIG=$3
OUTPUT_NAME=$4
echo $DATASET_NAME
echo $FILE_NAME
mkdir -p ~/.kaggle
echo "$KAGGLE_CONFIG" > ~/.kaggle/kaggle.json
sleep 1000000
chmod 600 ~/.kaggle/kaggle.json
echo "Downloading Kaggle Dataset"
kaggle datasets download -d $DATASET_NAME -f $FILE_NAME
echo "Unzipping Dataset"
unzip "$FILE_NAME.zip"
mv $FILE_NAME $OUTPUT_NAME
