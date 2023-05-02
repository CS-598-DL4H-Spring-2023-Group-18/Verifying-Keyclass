BASE_PATH="/content/"

cd -- "$BASE_PATH"
git clone https://github.com/CS-598-DL4H-Spring-2023-Group-18/Verifying-Keyclass.git
cd Verifying-Keyclass
mv Multi-Hot KeyClass
pip install snorkel sentence-transformers pyhealth transformers
cd KeyClass/scripts/

mkdir data/
cd data/
FILE_ID="1Sz-EyVyU-wjfKMYsR58Ch8yOI1WXjqop" #Full MIMIC DATASET
#FILE_ID="1DaXCjzs8I4PCpzaldaDNIublK4MedD-_" #10 MIMIC DATASET
URL="https://docs.google.com/uc?export=download&id=$FILE_ID"
echo ${green}===Downloading MIMIC Data...===${reset}
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate $URL -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILE_ID" -O "mimic.zip" && rm -rf /tmp/cookies.txt
echo ${green}===Unzipping MIMIC Data...===${reset}
jar xvf mimic.zip && rm mimic.zip
mv small-mimic mimic

cd -- "$BASE_PATH"
cd Verifying-Keyclass
cd KeyClass/scripts/
CONFIG_LOCATION="${BASE_PATH}Verifying-Keyclass/KeyClass/config_files/config_mimic.yaml"
echo $RUN_ALL_SCRIPT_LOCATION
echo $CONFIG_LOCATION
python run_all.py --config $CONFIG_LOCATION