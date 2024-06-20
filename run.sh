while true; do
  python3 main.py | logger -t pywol-host
  echo "Restarting in 300 seconds..."
  sleep 300;
done