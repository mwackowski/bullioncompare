import os
import sys, time, datetime
import runpy
from pathlib import Path
scriptPath = r'/home/wladzioo/domains/wladzioo.smallhost.pl/public_python/compare_app/scrape_scripts'

for x in os.listdir(scriptPath):
    file_x = os.path.join(scriptPath, x)
    if x not in ('loop.py', 'db_path.py') and os.path.isfile(file_x):
        start = time.time()
        try:
            print(f'{datetime.datetime.now()} Uruchamiam: {x}: {file_x}')
            runpy.run_path(file_x)
#        exec(Path(file_x).read_text())
            print('done')
        except Exception as e:
            print(e)
#        print(f'Czas realizacji: {time.time()-start}')
sys.exit()
