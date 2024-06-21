# cd in the current script folder
cd "$(dirname "$0")"

main() {
  echo "Starting pywol-host..."
  while true; do
    python3 main.py
    echo "Restarting in 300 seconds..."
    sleep 300;
  done
}

main | tee >(logger -t pywol-host)

