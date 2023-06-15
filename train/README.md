# Train

Usage: *Use the commonVoice recipe*

1. Download the speechbrain repo: https://github.com/speechbrain/speechbrain/
2. Install the requirement dependencies: *pip install -r requirements.txt*, *pip install -e .*
	- Install the transformer library: *pip install transformers*
	- Update the configuration in the train_en_with_wav2vec.yaml file using the settings provided in the hyperparameter.yaml file, Additionally, include the path to your data, as well as the respective CSV files for training, validation, and testing
	- Run the training using: *python train.py hparams/train_en_with_wav2vec.yaml*

