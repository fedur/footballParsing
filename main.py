import sys
import math as mth
import re

#to-do list, handle quarters

PLAY_NB = 1
def getAbsFieldPos(teamWithBall,side,yd):
    if side == teamWithBall:
        return yd

    else:
        return 55+55-yd

def processHeader(header,play, t1, t2):
    #format of the header: S 1-10 S39
    #res[0] = Team with ball
    #res[1] = Down and distance
    #res[2] = Field position
    rgx = re.compile("\s+")
    res = rgx.split(header)
    teamWithBall = res[0]
    downAndDistance = res[1].split('-')
    fieldPos = res[2]
    if t1[0] == teamWithBall:
        play["off_team"] = t1
        play["def_team"] = t2

    else:
        play["off_team"] = t2
        play["def_team"] = t1


    play["down_nb"] = downAndDistance[0]
    play["distance_to_first"] = downAndDistance[1]
    play["at_yard"]=getAbsFieldPos(
        teamWithBall,
        fieldPos[0],
        (int(fieldPos[1] + fieldPos[2]))
        )

def processPassPlay(text,play):
    #format: QBName pass complete|incomplete to RECEIVER for x yards
    match=re.search("\spass\s(complete|incomplete)\sto\s(.*)",text, re.DOTALL)
    if match != None:
        play["play_type"]="pass"
        playType=match.groups()[0] #complete / incomplete
        play["play_result"]=playType
        #Format: Adam Vance pass complete to Jeremy Murphy for 43 yards to the MTL37,
        # (Tackler Name; Tackler2 name)
        if playType == "complete":
            match2 = \
                re.search("(.*?)\sfor\s(\d+)\syards\sto\sthe\s(\w*)\s.*?\((.*?)\)",
                    match.groups()[1],
                    re.DOTALL)
            if match2 != None:
                #1: Receiver, 2: Gain, 3: FieldPos, 4: Tackler(s)
                play["thrown_to"]=match2.group(1)
                play["gain"]=match2.group(2)
                # Some tackler names overlap on multiple lines...
                play["tackled_by"]=re.sub("\n\s*"," ",match2.group(4))

        #
        elif playType =="incomplete":
            receiver = re.match("(.*?\s.*?)[\s\.,]",
                match.groups()[1])
            if (receiver != None):
                play["thrown_to"]=receiver.groups()[0]
        return True
    else:
        return False

def processRunPlay(text,play):
    match=re.match("(.*?)\srush\sfor\s((?:loss\sof\s)?\d+)",text, re.DOTALL)
    if match != None:
        #1: Name of player, 2: (loss of) x
        play["run_by"]=match.group(1).strip()
        if match.group(2)[0] == 'l':
            yd=re.match(".*(\d+)",match.group(2))
            if yd != None:
                val=int(yd.group(1))
                val=val*-1
                play["gain"]=val
        else:
            play["gain"]=int(match.group(2))

        print(play["run_by"] + ", "+str(play["gain"]))
        
    return True

def processPlay(text,play):
    play["penalty_on_play"] = "true" \
        if re.search("PENALTY",text, re.DOTALL) \
        else "false"

    if not processPassPlay(text,play):
        if not processRunPlay(text,play):
            print("meh")

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

