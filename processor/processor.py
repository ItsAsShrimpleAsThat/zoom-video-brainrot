import os
from flask import Flask, jsonify, request, after_this_request
from flask_cors import CORS, cross_origin
import subprocess
import montreal_forced_aligner
from time import sleep

acousticPathFilePath = "acoustic.path" if os.path.exists("acoustic.path") else "processor/acoustic.path"
dictionaryPathFilePath = "dictionary.path" if os.path.exists("dictionary.path") else "processor/dictionary.path"

acousticmodelpathfile = open(acousticPathFilePath, "r")
ACOUSTIC_MODEL_PATH = acousticmodelpathfile.read()
acousticmodelpathfile.close()

dictionarypathfile = open(dictionaryPathFilePath, "r")
DICTIONARY_PATH = dictionarypathfile.read()
dictionarypathfile.close()

FFMPEG_DEFAULT_CONVERT = "ffmpeg -i {inputPath} -y -vn {outputPath}"

# aligner = montreal_forced_aligner.alignment.PretrainedAligner(acoustic_model_path=ACOUSTIC_MODEL_PATH, dictionary_path=DICTIONARY_PATH)

app = Flask(__name__)
CORS(app)

#subprocess.call(FFMPEG_DEFAULT_CONVERT.format(inputPath=, outputPath=), shell=True)

@app.route("/alive")
def alive():
    return jsonify({"message" : "Hello from Python!"})

@app.route("/contact")
def contact():
    return jsonify({"status" : "Contact."})

@app.route("/brainrot")
def brainrot():
    return jsonify({""})

if __name__ == "__main__":
    app.run(host="localhost", port=6814)