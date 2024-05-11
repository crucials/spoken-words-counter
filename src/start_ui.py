import subprocess
import os
import signal
from threading import Thread

from dotenv import load_dotenv
import waitress
from flask import Flask, jsonify
import waitress.server
from werkzeug.exceptions import HTTPException

from utils.create_path_from_executable import create_path_from_executable


load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

@app.errorhandler(HTTPException)
def send_json_error_response(error: HTTPException):
    return jsonify(error=error.code, explanation=error.description), error.code

def exit_after_electron_stopped(electron_subprocess: subprocess.Popen):
    electron_subprocess.wait()
    os.kill(os.getpid(), signal.SIGINT)

if os.environ.get('MODE') == 'DEVELOPMENT':
    print('launching electron in development mode, dont forget to install npm packages',
          'in \'./src/ui/electron\' folder and build the vue frontend',
          'with \'npm run build\'', '\n')
    electron_subprocess = subprocess.Popen('cd ./src/ui/electron; npx electron .',
                                           shell=True)
    
    Thread(target=exit_after_electron_stopped, args=[electron_subprocess]).start()

    print('launching flask server', '\n')
    app.run()
else:
    print('launching electron in production mode, with bundled executable')
    electron_executable_path = create_path_from_executable(
        'ui', 'electron', 'dist', 'spoken-words-counter.AppImage'
    )
    electron_subprocess = subprocess.Popen([], executable=electron_executable_path,
                                           shell=True)

    Thread(target=exit_after_electron_stopped, args=[electron_subprocess]).start()

    print('launching flask server', '\n')
    waitress.serve(app)
