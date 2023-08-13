import os
from pathlib import Path

# Path(__file))
BASE_DIR = Path(__file__)
print(BASE_DIR)
print(BASE_DIR.resolve())
print(BASE_DIR.resolve().parent)
print(BASE_DIR.resolve().parent.parent)


print(os.path.join(BASE_DIR, 'my_study_materials', 'static'),)
