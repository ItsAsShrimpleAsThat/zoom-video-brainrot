# I've never fucking heard of this format but Montreal Forced Aligner uses it, so I must learn it
# Heres a link kinda clears it up a tiny bit? https://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html
# And a tool that converts other subtitle formats to TextGrid https://github.com/patrickschu/textgrid-convert

import os

if __name__ == "__main__":
    print("Why are you trying to run this lmao")
    #exit(0)

"""
Exapands to:
---------------------
File type = "ooTextFile"
Object class = "TextGrid"

xmin = {minTime}
xmax = {maxTime}
tiers? <exists>
size = {numTiers}
item []:
"""
TEXTGRID_HEADER = "File type = \"ooTextFile\"\nObject class = \"TextGrid\"\n\nxmin = {minTime}\nxmax = {maxTime}\ntiers? <exists>\nsize = {numTiers}\nitem []:\n"

# returns tuple of min and max timestamps
def parseTimestamps(timestamps):
    minTimeString, __, maxTimeString = timestamps.split(" ")

    minTimeSplit = minTimeString.split(":")
    maxTimeSplit = maxTimeString.split(":")

    minTime = int(minTimeSplit[0]) * 3600 + int(minTimeSplit[1]) * 60 + float(minTimeSplit[2])
    maxTime = int(maxTimeSplit[0]) * 3600 + int(maxTimeSplit[1]) * 60 + float(maxTimeSplit[2])

    return (minTime, maxTime)

#print(parseTimestamps("01:30:36.290 --> 01:30:37.140"))
def convert(vttPath, outputPath):
    if not os.path.exists(vttPath):
        print("Path " + vttPath + " was not found.")

    vttFile = open(vttPath, "r") # Input file
    
    vttFileList = vttFile.readlines()

    open(outputPath, "w").close() # Empty textgrid file if it exists
    textGridFile = open(outputPath, "a") # Output file

    # Go to end and get max time and number of tiers
    maxTime, numTiers = None, None
    searchLine = len(vttFileList) - 1
    for safetyCounter in range(10):  # Run loop max 10 times in case something gets fucked up
        line = vttFileList[searchLine]
        
        if "-->" in line:  # "-->" is found in vtt timestamps
            prevLine = vttFileList[searchLine - 1].strip("\n") # JUST TO BE SURE, we make sure the previous line is a number. if it is, we know we're looking at a timestamp
            if prevLine.isdigit():  # Who knows, maybe someone's zoom name is "-->"
                numTiers = int(prevLine)
                maxTime = parseTimestamps(line)[1]
                break
        searchLine -= 1
    
    # Get first timestamp starting time
    minTime = parseTimestamps(vttFileList[3])[0]

    textGridFile.write(TEXTGRID_HEADER.format(minTime = minTime,
                                              maxTime = maxTime,    # Write header with the xmax and size we just calculated
                                              numTiers = numTiers))

    for i in range(2, len(vttFileList)):
        line = vttFileList[i].strip("\n")

        if line.isdigit():
            pass

        if(i < 10): 
            print(line)

    vttFile.close()

convert("download/test.vtt", "download/output.TextGrid")