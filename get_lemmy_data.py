import sys
import time
import datetime
from fetch_and_save import fetch_and_save
from insert_into_historical import insert_into_historical

wait_time = float(sys.argv[1])
print(f"get_lemmy_data.py called with {sys.argv[1]} seconds between each iteration.")

while True:
    timestamp = datetime.datetime.now()
    print(" get_lemmy_data iteration start time:", timestamp)
    fetch_and_save()
    insert_into_historical()
    print(f"get_lemmy_data iteration runtime: {datetime.datetime.now() - timestamp} \n")
    time.sleep(wait_time)
