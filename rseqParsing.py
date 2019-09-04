import sys
import math as mth
import re

#to-do list, handle quarters

PLAY_NB = 1
def processHeader(header,play, t1, t2):
    #format of the header: S 1-10 S39
    #res[0] = Team with ball
    #res[1] = Down and distance
    #res[2] = Field position
    rgx = re.compile("\s+")
    res = rgx.split(header)
    teamWithBall = res[0]
    if t1[0] == teamWithBall:
        play["off_team"] = t1
        play["def_team"] = t2

    else:
        play["off_team"] = t2
        play["def_team"] = t1

    downAndDistance = res[1].split('-')
    play["down_nb"] = downAndDistance[0]
    play["distance_to_first"] = downAndDistance[1]

    fieldPos=res[2]
    side=fieldPos[0]
    yd=(int(fieldPos[1] + fieldPos[2]))
    if side == teamWithBall:
        play["at_yard"] = yd

    else:
        play["at_yard"] = 55+55-yd

def processPlay(text,play):
    if re.search("\spass\s",text,re.DOTALL) != None:
        #format: QBName pass complete|incomplete to RECEIVER for x yards 
        reg=re.compile("\spass\s(complete|incomplete)\sto\s(.*)", re.DOTALL)
        match=reg.search(text)
        print(match.groups())

    elif re.search("\srush\s",text, re.DOTALL) != None:
        play["play_type"]="run"

def processDrive(text, t1,t2):
    global PLAY_NB
    text=text.strip()
    teams = "(?:" + t1[0] + "|" + t2[0] + ")"
    header="("+teams+"\s+[1-3]-\d+\s+"+teams+"\d+)"
    reg=re.compile(header, re.DOTALL)
    res = reg.split(text)
    #we only care about plays 
    # so we remove the first thing before the first header split
    del res[0]
    play={}
    for i in range(len(res)-1):
        if i % 2 == 0:
            play.clear()
            play["play_nb"]= PLAY_NB
            PLAY_NB = PLAY_NB + 1
            processHeader(res[i],play,t1,t2)
        else:
            processPlay(res[i],play)

def main(file):
    f = open(file, 'r')
    # grab team names
    # Example: Concordia vs Sherbrooke (2018-10-27)
    title = f.readline().strip()
    teams = title.split('vs')
    T1=teams[0].strip()
    team2Res = teams[1].strip().split(" ")
    T2=team2Res[0]
    DATE=team2Res[1]
    f = open(file, 'r')

    # Get Play-By-Play infos
    startSection='Play-by-Play Summary \(1st quarter\)'
    endSection='=FINAL SCORE='
    regex = re.compile(startSection+".*"+endSection, re.DOTALL)
    m = regex.search(f.read())
    allPlays = m.group()

    # Regex used for splitting drives
    # Group makes it so delimiter forms a group on its own
    regex = re.compile('(---------------.*?---------------)')
    res = regex.split(allPlays)

    # Getting my drives without delimiters
    drives= []
    summaries = []
    for i in range(len(res)):
        if i % 2 == 0:
            drives.append(res[i])
        else:
            summaries.append(res[i])

    plays=[]
    for drive in drives:
        processDrive(drive,T1,T2)

if __name__ == "__main__":
    main(sys.argv[1])

