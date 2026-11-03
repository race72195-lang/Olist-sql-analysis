"""Downloads the Olist Brazilian E-Commerce dataset from Kaggle into the data/ folder."""

import shutil
from pathlib import Path

import kagglehub

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

path = Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))
for csv_file in sorted(path.glob("*.csv")):
    shutil.copy(csv_file, DATA_DIR / csv_file.name)
    print("copied", csv_file.name)

print("Done. Files are in:", DATA_DIR)
