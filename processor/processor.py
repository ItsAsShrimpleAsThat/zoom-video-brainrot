import os
from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import glob
import vttToTextGrid
import json
from time import sleep
from openai import OpenAI

inProcessorPath = os.path.exists("acoustic.path")

acousticPathFilePath = "acoustic.path" if inProcessorPath else "processor/acoustic.path"
dictionaryPathFilePath = "dictionary.path" if inProcessorPath else "processor/dictionary.path"
chatgptKeyFilePath = "chatgpt.key" if inProcessorPath else "processor/chatgpt.key"
promptFilePath = "keywords.prompt" if inProcessorPath else "processor/keywords.prompt"

acousticmodelpathfile = open(acousticPathFilePath, "r")
ACOUSTIC_MODEL_PATH = acousticmodelpathfile.read()
acousticmodelpathfile.close()

dictionarypathfile = open(dictionaryPathFilePath, "r")
DICTIONARY_PATH = dictionarypathfile.read()
dictionarypathfile.close()

gptkeyfile = open(chatgptKeyFilePath, "r")
CHATGPT_KEY = gptkeyfile.read()
gptkeyfile.close()
gptClient = OpenAI(
  api_key = CHATGPT_KEY
)

promptFile = open(promptFilePath, "r")
KEYWORD_PROMPT = promptFile.read()
promptFile.close()

FFMPEG_DEFAULT_CONVERT = "ffmpeg -i {inputPath} -y -vn {outputPath}"
CORPUS_FILE_NAMES = "brainrot" # What should the converted .wav or .TextGrid files be called?

CORPUS_PATH = os.path.abspath("download").replace("\\", "/") if inProcessorPath else os.path.abspath("processor/download").replace("\\", "/")
ALIGNER_OUTPUT_PATH = CORPUS_PATH + "/output"
MFA_ALIGN_COMMAND = "mfa align {corpusPath} {dictionaryPath} {modelPath} {outputPath} --clean --final_clean --cleanup_textgrids --uses_speaker_adaptation false --output_format json"
#if erros use --beam 100
# aligner = montreal_forced_aligner.alignment.PretrainedAligner(acoustic_model_path=ACOUSTIC_MODEL_PATH, dictionary_path=DICTIONARY_PATH)

MAX_CHARACTERS_PER_CAPTION = 25
CAPITALIZE_CAPTIONS = True

LINE_GROUP_SIZE = 2 # How many lines to group together to reduce chatgpt calls
LINE_GROUP_MIN_WORDS = LINE_GROUP_SIZE * 14

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
    print("Starting Alignment")
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
        unmodifiedCaption = True # Caption has not been set
        currentCaption = {"speaker" : "", "text" : "", "wordTimings" : []}
        skippedAll = True # Used to break out while(searching)

        while(searchingCaption):
            minTimeWord = [999999999, 999999999, "I should not be seen!", "speaker"]

            for speaker in speakers:
                if speakerLineIndicies[speaker] >= len(tgJson["tiers"][speaker]["entries"]) - 1:
                    continue
                
                skippedAll = False # Found at least one line, so we shouldnt break out of the loop

                if tgJson["tiers"][speaker]["entries"][speakerLineIndicies[speaker]][0] < minTimeWord[0]:
                    minTimeWord = tgJson["tiers"][speaker]["entries"][speakerLineIndicies[speaker]] + [speaker]

            if skippedAll:
                searching = False
                break
            
            if unmodifiedCaption:  # Initialize caption with speaker
                unmodifiedCaption = False
                currentCaption["speaker"] = minTimeWord[3].removesuffix(" - words")
                currentCaption["minTime"] = minTimeWord[0]

            if currentCaption["speaker"] == minTimeWord[3].removesuffix(" - words"):  # Make sure speaker of this word is the speaker of the current caption
                if len(list(currentCaption["text"])) + len(minTimeWord[2]) > MAX_CHARACTERS_PER_CAPTION: # End caption if it exceeds max characters
                    searchingCaption = False
                    currentCaption["text"] = currentCaption["text"].removesuffix(" ") # Remove trailing space
                    currentCaption["maxTime"] = minTimeWord[1]
                    break
                else:  # Add word and word timings to caption
                    currentCaption["text"] += minTimeWord[2].upper() + " " if CAPITALIZE_CAPTIONS else minTimeWord[2].lower() + " "
                    currentCaption["wordTimings"].append([minTimeWord[0], minTimeWord[1]])
                    speakerLineIndicies[minTimeWord[3]] += 1  #SOMETHING ABOUT ME IS BROKEN, PLEASEFIX
            else:
                searchingCaption = False

        captionStream.append(currentCaption)
        
    return captionStream

@app.route("/alive")
def alive():
    return jsonify({"message" : "Hello from Python!"})  

@app.route("/contact")
def contact():
    return jsonify({"status" : "Contact."})

@app.route("/brainrot")
def brainrot():
    mp4Files = glob.glob(f"{CORPUS_PATH}/*.mp4") # Get all mp4, wav, and vtt files in download folder
    wavFiles = glob.glob(f"{CORPUS_PATH}/{CORPUS_FILE_NAMES}.wav")
    vttFiles = glob.glob(f"{CORPUS_PATH}/*.vtt")
    
    if len(mp4Files) < 1: # Only proceed if theres 1 mp4 file or wav file
        if len(wavFiles) == 1: # We can use wav files from previous run
            print("wav file found, not converting mp4")
        else:
            print("ERROR: mp4 file or wav file not found in corpus folder")
            return jsonify({"status" : "ERROR: mp4 file or wav file not found in corpus folder"})
    elif len(mp4Files) > 1:
        print("ERROR: more than 1 mp4 file found. please only place 1 mp4 file in corpus folder")
        return jsonify({"status" : "ERROR: more than 1 mp4 file found. please only place 1 mp4 file in corpus folder"})
    
    if len(vttFiles) < 1:
        return jsonify({"status" : "ERROR: no vtt file found in corpus folder"})
    elif len(vttFiles) > 1:
        return jsonify({"status" : "ERROR: more than 1 vtt file found. please only place 1 vtt file in corpus folder"})

    if len(mp4Files) == 1: # Convert mp4 to wav if we don't already have a wav file
        print("Converting MP4")
        mp4File = mp4Files[0]
        ffmpegConvert(mp4File, f"{CORPUS_PATH}/{CORPUS_FILE_NAMES}.wav")
        
    vttFile = vttFiles[0]
    vttToTextGrid.convert(vttFile, f"{CORPUS_PATH}/{CORPUS_FILE_NAMES}.TextGrid")

    align()

    return jsonify({"status" : "success", "captionStream" : getCaptionStream(f"{ALIGNER_OUTPUT_PATH}/{CORPUS_FILE_NAMES}.json"), "keywords": getKeywords(glob.glob(f"{CORPUS_PATH}/*.vtt")[0])})
    #return jsonify({"status" : "success", "captionStream" : getCaptionStream(f"{ALIGNER_OUTPUT_PATH}/{CORPUS_FILE_NAMES}.json")})

@app.route("/getStoredCaptionStream")
def getStoredCaptionStream():
    return jsonify({"status" : "success", "captionStream" : getCaptionStream(f"{ALIGNER_OUTPUT_PATH}/{CORPUS_FILE_NAMES}.json")})

def getKeywords(vttFilePath):
    keywords = []

    lines = vttToTextGrid.getVTTLines(vttFilePath)

    currentGroupSize = 0
    line = {"text": "", "minTime": 0.0, "maxTime": 0.0, "instruction": True, "keywords": []}
    #for i in range(len(lines) - 1):
    for i in range(30):
        if currentGroupSize == 0:
            line["text"] += lines[i]["text"] + " "
            line["minTime"] = min(line["minTime"], lines[i]["minTime"])
            line["maxTime"] = min(line["maxTime"], lines[i]["maxTime"])
            currentGroupSize += 1
            i += 1

        if currentGroupSize < LINE_GROUP_SIZE:
            line["text"] += lines[i]["text"] + " "
            line["minTime"] = min(line["minTime"], lines[i]["minTime"])
            line["maxTime"] = min(line["maxTime"], lines[i]["maxTime"])
            currentGroupSize += 1

            if len(lines) - i >= LINE_GROUP_SIZE:
                continue

        line["text"].removesuffix(" ")

        response = "INSTRUCTION"
        sleepTime = 0.31
        if len(line["text"].split(" ")) > LINE_GROUP_MIN_WORDS:
            # Get chatgpt response
            completion = gptClient.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                        {
                            "role": "system",
                            "content": KEYWORD_PROMPT
                        },
                        {
                            "role": "user",
                            "content": line["text"]
                        }
                ]
            )

            response = completion.choices[0].message.content
        else:
            sleepTime = 0

        print(response)

        if(response == "INSTRUCTION"):
            line["instruction"] = True
            line["keywords"] = None
            keywords.append(line)
        else:
            line["instruction"] = False
            test = ""
            keywordsList = response.replace(" ", "").split(",")
            line["keywords"] = keywordsList
            keywords.append(line)

        currentGroupSize = 0
        line = {"text": "", "minTime": 0.0, "maxTime": 0.0, "instruction": True, "keywords": []}

        sleep(sleepTime) # Avoid rate limits lmao
    
    keywordsJSONContainer = { "keywords" : keywords }
    keywordOutputFile = open(f"{ALIGNER_OUTPUT_PATH}/key.words", "w")
    keywordOutputFile.write(json.dumps(keywordsJSONContainer))
    keywordOutputFile.close()

    return keywords

if __name__ == "__main__":
    app.run(host="localhost", port=6814)