import os
from flask import Flask, jsonify, request, after_this_request
from flask_cors import CORS, cross_origin
import subprocess
import montreal_forced_aligner
from time import sleep

import montreal_forced_aligner.config
import vttToTextGrid

inProcessorPath = os.path.exists("acoustic.path")

acousticPathFilePath = "acoustic.path" if inProcessorPath else "processor/acoustic.path"
dictionaryPathFilePath = "dictionary.path" if inProcessorPath else "processor/dictionary.path"

acousticmodelpathfile = open(acousticPathFilePath, "r")
ACOUSTIC_MODEL_PATH = acousticmodelpathfile.read()
acousticmodelpathfile.close()

dictionarypathfile = open(dictionaryPathFilePath, "r")
DICTIONARY_PATH = dictionarypathfile.read()
dictionarypathfile.close()

FFMPEG_DEFAULT_CONVERT = "ffmpeg -i {inputPath} -y -vn {outputPath}"

CORPUS_PATH = os.path.abspath("download").replace("\\", "/") if inProcessorPath else os.path.abspath("processor/download").replace("\\", "/")
ALIGNER_OUTPUT_PATH = CORPUS_PATH + "/output"
MFA_ALIGN_COMMAND = "mfa align {corpusPath} {dictionaryPath} {modelPath} {outputPath} --clean --final_clean --cleanup_textgrids --uses_speaker_adaptation false"
#if erros use --beam 100

# aligner = montreal_forced_aligner.alignment.PretrainedAligner(acoustic_model_path=ACOUSTIC_MODEL_PATH, dictionary_path=DICTIONARY_PATH)

app = Flask(__name__)
CORS(app)

r"""
@param inputPath: Path to video file
@param outputPath: Path to output file. Must be .wav
"""
def ffmpegConvert(inputPath, outputPath):
    subprocess.call(FFMPEG_DEFAULT_CONVERT.format(inputPath=inputPath, outputPath=outputPath), shell=True)

def align():
    export_path = os.path.join(CORPUS_PATH, "aligned")

    subprocess.run(MFA_ALIGN_COMMAND.format(corpusPath=CORPUS_PATH, 
                                             dictionaryPath=DICTIONARY_PATH,
                                             modelPath=ACOUSTIC_MODEL_PATH,
                                             outputPath=ALIGNER_OUTPUT_PATH
                                             )
                                             )
                                                                  
# ffmpegConvert(CORPUS_PATH + "/zoom.mp4", CORPUS_PATH + "/zoom.wav")
# vttToTextGrid.convert(CORPUS_PATH + "/zoom.vtt", CORPUS_PATH + "/zoom.TextGrid")

print("hello")
align()

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