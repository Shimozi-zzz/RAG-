import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import constants
print("ENDPOINT:", constants.ENDPOINT)
print("_HF_DEFAULT_ENDPOINT:", constants._HF_DEFAULT_ENDPOINT)
print()
print("Will it use mirror?", constants.ENDPOINT == "https://hf-mirror.com")