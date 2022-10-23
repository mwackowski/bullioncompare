from pathlib import Path
import os
DB_PATH = os.path.join(Path(__file__).resolve().parent.parent.parent, 'db.sqlite3')
print(DB_PATH)
