import os
from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import glob
import vttToTextGrid
import json

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
CORPUS_FILE_NAMES = "brainrot" # What should the converted .wav or .TextGrid files be called?

CORPUS_PATH = os.path.abspath("download").replace("\\", "/") if inProcessorPath else os.path.abspath("processor/download").replace("\\", "/")
ALIGNER_OUTPUT_PATH = CORPUS_PATH + "/output"
MFA_ALIGN_COMMAND = "mfa align {corpusPath} {dictionaryPath} {modelPath} {outputPath} --clean --final_clean --cleanup_textgrids --uses_speaker_adaptation false --output_format json"
#if erros use --beam 100
# aligner = montreal_forced_aligner.alignment.PretrainedAligner(acoustic_model_path=ACOUSTIC_MODEL_PATH, dictionary_path=DICTIONARY_PATH)

app = Flask(__name__)
CORS(app)

r"""
@param inputPath: Path to video file
@param outputPath: Path to output file. Must be .wav
"""
def ffmpegConvert(inputPath, outputPath):
    if(os.path.exists(inputPath) and os.path.isfile(inputPath)):
        subprocess.call(FFMPEG_DEFAULT_CONVERT.format(inputPath=inputPath, outputPath=outputPath), shell=True)
        os.remove(inputPath)

def align():
    export_path = os.path.join(CORPUS_PATH, "aligned")

    subprocess.run(MFA_ALIGN_COMMAND.format(corpusPath=CORPUS_PATH, 
                                             dictionaryPath=DICTIONARY_PATH,
                                             modelPath=ACOUSTIC_MODEL_PATH,
                                             outputPath=ALIGNER_OUTPUT_PATH
                                             ))
                                                                  
# ffmpegConvert(CORPUS_PATH + "/zoom.mp4", CORPUS_PATH + "/zoom.wav")
# vttToTextGrid.convert(CORPUS_PATH + "/zoom.vtt", CORPUS_PATH + "/zoom.TextGrid")

def getCaptionStream(path):
    tgFile = open(path, encoding="utf8")
    tgJson = json.load(tgFile)
    
    speakers = []
    speakerLineIndicies = {}
    for speaker in tgJson["tiers"]:
        if speaker.endswith("words"): # Only add word tiers to speakers, not phonemes
            speakers.append(speaker) 
            speakerLineIndicies[speaker] = 0
    
    captionStream = []
    print(tgJson["tiers"][speakers[0]]["entries"][speakerLineIndicies[speakers[0]]][0])
    
    searching = True
    while(searching):
        searchingCaption = True
        currentCaption = {"speaker" : "", "msg" : "", "wordTimings" : []}

        while(searchingCaption):
            minTimeWord = [999999999, 999999999, "I should not be seen!"]

            for speaker in speakers:
                if tgJson["tiers"][speaker]["entries"][speakerLineIndicies[speaker]][0] < minTimeWord[0]:
                    minTimeWord = tgJson["tiers"][speaker]["entries"][speakerLineIndicies[speaker]]

            print(minTimeWord)
            break
        break

@app.route("/alive")
def alive():
    return jsonify({"message" : "Hello from Python!"})  
@app.route("/contact")
def contact():
    return jsonify({"status" : "Contact."})

@app.route("/brainrot")
def brainrot():
    mp4Files = glob.glob(f"{CORPUS_PATH}/*.mp4")
    if len(mp4Files) == 0:
        return jsonify({"success" : False})
    
    print(mp4Files)
    
    return jsonify({""})

def testRot():
    mp4Files = glob.glob(f"{CORPUS_PATH}/*.mp4") # Get all mp4, wav, and vtt files in download folder
    wavFiles = glob.glob(f"{CORPUS_PATH}/{CORPUS_FILE_NAMES}.wav")
    vttFiles = glob.glob(f"{CORPUS_PATH}/*.vtt")
    
    if len(mp4Files) < 1: # Only proceed if theres 1 mp4 file or wav file
        if len(wavFiles) == 1: # We can use wav files from previous run
            print("wav file found, not converting mp4")
        else:
            return False
    elif len(mp4Files) > 1:
        return False
    
    if len(vttFiles) < 1:
        return False
    elif len(vttFiles) > 1:
        return False

    if len(mp4Files) == 1: # Convert mp4 to wav if we don't already have a wav file
        mp4File = mp4Files[0]
        ffmpegConvert(mp4File, f"{CORPUS_PATH}/{CORPUS_FILE_NAMES}.wav")
        
    vttFile = vttFiles[0]
    vttToTextGrid.convert(vttFile, f"{CORPUS_PATH}/{CORPUS_FILE_NAMES}.TextGrid")

    align()

    return jsonify({""})
    
getCaptionStream(f"{CORPUS_PATH}/output/brainrot.json")

if __name__ == "__main__":
    app.run(host="localhost", port=6814)