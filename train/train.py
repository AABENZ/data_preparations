!git clone https://github.com/speechbrain/speechbrain/
%cd /content/speechbrain/
!pip install -r requirements.txt
!pip install -e .

!pip install transformers

%cd /content/speechbrain/recipes/CommonVoice/ASR/CTC

!python ./train_with_wav2vec.py ./hparams/train_en_with_wav2vec.yaml
