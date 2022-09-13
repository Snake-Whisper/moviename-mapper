import os
import sys
import re

CSV_FILE = "lib/enterpriseArcher.csv"
VIDEO_DIR = "/mnt/tele5/enterpriseArcherOK"
SIMULATE = True
BORDER = 0.5

filelist = []
content = []
model = {}

hit_model = {}
#Schema: {fileID: {titleRef1:score, titleRef2:score}]}

mapping = {}
#Schema: {titleRef: [hitPercentage, fileId]}


def main():
    global content, filelist
    # Read and clean CSV File
    try:
        with open(CSV_FILE) as file:
            content = [cleanCSVRow(row.split(";")) for row in file.readlines()]
    except FileNotFoundError:
        print("CSV File not found")
    finally:
        file.close()
    buildModel(content)
    
    #generate datastructure showing how many title splits are equal between fs name and csv file data in percentage
    filelist = os.listdir(VIDEO_DIR)
    generateHitModel([os.path.splitext(file)[0] for file in filelist])
    generateMapping()
    printMapping()
    addEppisodeToFileNames()


def splitTitle(title: str):
    return re.split('[_\s-]', title.upper())


def cleanCSVRow(row: list):
    """Exspects an already splitted CSV row as parameter. Returns cleaned Tuple in Form of (<sesion>,<episode>,<title>)"""
    assert len(row) >= 3, "Exspected: <Session>;<Episode>;<Title>"
    return (int(row[0].strip('.')), int(row[1].strip('.')), "".join(row[2:]).strip())


def buildModel(data: list):
    """Build Model with words as key an reference to titles as value if they ocour. Example: {'The': {1, 4, 5}}"""
    for index, item in enumerate(data):
        for word in splitTitle(item[-1]):
            if word not in model:
                model[word] = set()
            model[word].add(index)


def generateHitModel(data: list):
    """Build a datastructure showing in percentage how often title fragment from fs are founf in titles from the model genertaed from datafile (eg. csv)"""
    for fileId, item in enumerate(data):
        hits = {}
        titles = splitTitle(item)
        count_titles = len(titles)
        for word in titles:
            if word in model:
                for titleRef in model[word]:
                    if titleRef not in hits:
                        hits[titleRef] = 0
                    hits[titleRef] += 1
        for titleRef in hits:
            hits[titleRef] /= count_titles
        hit_model[fileId] = hits

def generateMapping():
    for titleRef in range(len(content)):
        mapping[titleRef] = [0, -1]
    for fileId in hit_model:
        for titleRef in hit_model[fileId]:
            if hit_model[fileId][titleRef] > mapping[titleRef][0]:
                #update highscore
                mapping[titleRef][0] = hit_model[fileId][titleRef]

                #update fileId
                mapping[titleRef][1] = fileId

def printMapping():
    for titleRef in [i for i in mapping if mapping[i][0]>=BORDER]:
        print(f"[{int(mapping[titleRef][0] * 100)} %] {content[titleRef]}\t=> {filelist[mapping[titleRef][1]]}")
    print()
    print ("="*10)
    print ("Problems")
    print("="*10)
    print()
    for titleRef in [i for i in mapping if mapping[i][0]<BORDER]:
        print(f"[{int(mapping[titleRef][0] * 100)} %] {content[titleRef]}\t=> {filelist[mapping[titleRef][1]]}")

def addEppisodeToFileNames():
    for titleRef in [i for i in mapping if mapping[i][0]>=BORDER]:
        filename = f"S{content[titleRef][0]}E{content[titleRef][1]}_{content[titleRef][2]}.mp4"
        print(f"{filelist[mapping[titleRef][1]]} => {filename}")
if __name__ == '__main__':
    main()
