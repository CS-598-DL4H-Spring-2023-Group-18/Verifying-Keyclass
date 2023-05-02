DATA_PATH="/content/Verifying-Keyclass/KeyClass/scripts/data/"
# DATA_PATH = "../datasets/" # Uncomment

DATASETS=('mimic')

MODEL_NAME="all-mpnet-base-v2"

for DATASET in "${DATASETS[@]}"
do
	echo "======================="
	echo "Creating and saving embeddings for the $DATASET dataset..."
	python encode_datasets.py --data_path=$DATA_PATH --dataset=$DATASET --model_name=$MODEL_NAME
done