import os
from pathlib import Path

os.environ["NLTK_DATA"] = str((Path(__file__).parent / "nltk_data").absolute())
