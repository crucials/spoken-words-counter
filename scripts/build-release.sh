cd ./src/ui/web
npm run build
cd ../../../
python -m eel ./src/start_ui.py ./src/ui/web -y --noconsole --log-level=DEBUG --add-data="./bin/ungoogled-chromium_120.0.6099.109-1.1.AppImage:./bin" -n spoken-words-counter