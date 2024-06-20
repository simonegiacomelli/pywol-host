while true; do
  python3 main.py | logger -t pywol-host
  sleep 300;
done