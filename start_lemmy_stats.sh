pkill gunicorn
./start_dash_app.sh &
interval=3600
while [[ ! -f /home/22/job_stop.txt ]] ; do
    now=$(date +%s) # timestamp in seconds
    sleep $((interval - now % interval))
    bash ./get_lemmy_data.sh >> logs/fetch.log
done