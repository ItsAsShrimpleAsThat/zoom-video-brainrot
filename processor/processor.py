import os
from flask import Flask, jsonify, request, after_this_request
from flask_cors import CORS, cross_origin
import subprocess
import montreal_forced_aligner
from time import sleep

acousticmodelpathfile = open("acoustic.path")
ACOUSTIC_MODEL_PATH = acousticmodelpathfile.read()
acousticmodelpathfile.close()

dictionarypathfile = open("dictionary.path", "r")
DICTIONARY_PATH = dictionarypathfile.read()
dictionarypathfile.close()

FFMPEG_DEFAULT_CONVERT = "ffmpeg -i {inputPath} -y -vn {outputPath}"

# aligner = montreal_forced_aligner.alignment.PretrainedAligner(acoustic_model_path=ACOUSTIC_MODEL_PATH, dictionary_path=DICTIONARY_PATH)

app = Flask(__name__)
CORS(app)

#subprocess.call(FFMPEG_DEFAULT_CONVERT.format(inputPath=, outputPath=), shell=True)

@app.route("/alive")
def alive():
  
  print("I HAVE BEEN RUN")
  return jsonify({"message" : "Hello from Python!"})

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=6814)