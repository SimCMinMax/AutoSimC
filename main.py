import configparser
import sys

# Var init with default value
c_profileid = 0
c_profilemaxid = 0
legmin = 0
legmax = 2
outputFileName = "settings.ini"
inputFileName = "out.simc"


# Add legendary to the right tab
def addToTab(x):
    stringToAdd = "L,id=" + x[1] + (",bonus_id=" + x[2] if x[2] != "" else "") + (
    ",enchant_id=" + x[3] if x[3] != "" else "") + (",gem_id=" + x[4] if x[4] != "" else "")
    if x[0] == 'head':
        l_head.append(stringToAdd)
    elif x[0] == 'neck':
        l_neck.append(stringToAdd)
    elif x[0] == 'shoulders':
        l_shoulders.append(stringToAdd)
    elif x[0] == 'back':
        l_back.append(stringToAdd)
    elif x[0] == 'chest':
        l_chest.append(stringToAdd)
    elif x[0] == 'wrist':
        l_wrists.append(stringToAdd)
    elif x[0] == 'hands':
        l_hands.append(stringToAdd)
    elif x[0] == 'waist':
        l_waist.append(stringToAdd)
    elif x[0] == 'legs':
        l_legs.append(stringToAdd)
    elif x[0] == 'feet':
        l_feet.append(stringToAdd)
    elif x[0] == 'finger1':
        l_finger1.append(stringToAdd)
    elif x[0] == 'finger2':
        l_finger2.append(stringToAdd)
    elif x[0] == 'trinket1':
        l_trinket1.append(stringToAdd)
    elif x[0] == 'trinket2':
        l_trinket2.append(stringToAdd)


# Manage legendary with command line
def handlePermutation(elements):
    for element in elements:
        pieces = element.split('|')
        addToTab(pieces)


# Check if permutation is valid
def checkUsability():
    if l_gear[10] == l_gear[11]:
        return "same ring"
    if l_gear[12] == l_gear[13]:
        return "same trinket"

    nbLeg = 0
    for a in range(len(l_gear)):
        if l_gear[a][0] == "L":
            nbLeg = nbLeg + 1
    if nbLeg < legmin:
        return str(nbLeg) + " leg (too low)"
    if nbLeg > legmax:
        return str(nbLeg) + " leg (too much)"

    return ""


# Print a simc profile
def scpout(oh):
    global c_profileid
    result = checkUsability()
    digits = len(str(c_profilemaxid))
    mask = '00000000000000000000000000000000000'
    maskedProfileID = (mask + str(c_profileid))[-digits:]
    if result != "":
        print("Profile:" + str(c_profileid) + "/" + str(c_profilemaxid) + ' Error:' + result)
    else:
        print("Profile:" + str(c_profileid) + "/" + str(c_profilemaxid))
        outputFile.write(c_class + "=" + c_profilename + "_" + maskedProfileID + "\n")
        outputFile.write("specialization=" + c_spec + "\n")
        outputFile.write("race=" + c_race + "\n")
        outputFile.write("level=" + c_level + "\n")
        outputFile.write("role=" + c_role + "\n")
        outputFile.write("position=" + c_position + "\n")
        outputFile.write("talents=" + c_talents + "\n")
        outputFile.write("artifact=" + c_artifact + "\n")
        if c_other != "": outputFile.write(c_other + "\n")
        outputFile.write("head=" + (l_gear[0] if l_gear[0][0] != "L" else l_gear[0][1:]) + "\n")
        outputFile.write("neck=" + (l_gear[1] if l_gear[1][0] != "L" else l_gear[1][1:]) + "\n")
        outputFile.write("shoulders=" + (l_gear[2] if l_gear[2][0] != "L" else l_gear[2][1:]) + "\n")
        outputFile.write("back=" + (l_gear[3] if l_gear[3][0] != "L" else l_gear[3][1:]) + "\n")
        outputFile.write("chest=" + (l_gear[4] if l_gear[4][0] != "L" else l_gear[4][1:]) + "\n")
        outputFile.write("wrists=" + (l_gear[5] if l_gear[5][0] != "L" else l_gear[5][1:]) + "\n")
        outputFile.write("hands=" + (l_gear[6] if l_gear[6][0] != "L" else l_gear[6][1:]) + "\n")
        outputFile.write("waist=" + (l_gear[7] if l_gear[7][0] != "L" else l_gear[7][1:]) + "\n")
        outputFile.write("legs=" + (l_gear[8] if l_gear[8][0] != "L" else l_gear[8][1:]) + "\n")
        outputFile.write("feet=" + (l_gear[9] if l_gear[9][0] != "L" else l_gear[9][1:]) + "\n")
        outputFile.write("finger1=" + (l_gear[10] if l_gear[10][0] != "L" else l_gear[10][1:]) + "\n")
        outputFile.write("finger2=" + (l_gear[11] if l_gear[11][0] != "L" else l_gear[11][1:]) + "\n")
        outputFile.write("trinket1=" + (l_gear[12] if l_gear[12][0] != "L" else l_gear[12][1:]) + "\n")
        outputFile.write("trinket2=" + (l_gear[13] if l_gear[13][0] != "L" else l_gear[13][1:]) + "\n")
        outputFile.write("main_hand=" + l_gear[14] + "\n")
        if oh == 1:
            outputFile.write("off_hand=" + l_gear[15] + "\n\n")
        else:
            outputFile.write("\n")
    c_profileid += 1
    return ()


# Manage command line parameters
def handleCommandLine():
    global inputFileName
    global outputFileName
    global legmin
    global legmax

    for a in range(1, len(sys.argv)):
        if sys.argv[a] == "-i": inputFileName = sys.argv[a + 1]
        if sys.argv[a] == "-o": outputFileName = sys.argv[a + 1]
        if sys.argv[a] == "-l":
            elements = sys.argv[a + 1].split(',')
            handlePermutation(elements)
            # number of leg
            if sys.argv[a + 2][0] != "-":
                legNb = sys.argv[a + 2].split(':')
                legmin = int(legNb[0])
                legmax = int(legNb[1])


#########################   
#### Program Start ###### 
#########################   

handleCommandLine()

# Read settings.ini to init vars
config = configparser.ConfigParser()
config.read(inputFileName)
profile = config['Profile']
gear = config['Gear']

# Read settings.ini
#   Profile
c_profilename = profile['profilename']
c_profileid = int(profile['profileid'])
c_class = profile['class']
c_race = profile['race']
c_level = profile['level']
c_spec = profile['spec']
c_role = profile['role']
c_position = profile['position']
c_talents = profile['talents']
c_artifact = profile['artifact']
c_other = profile['other']

#   Gear
c_head = gear['head']
c_neck = gear['neck']
if config.has_option('Gear', 'shoulders'):
    c_shoulders = gear['shoulders']
else:
    c_shoulders = gear['shoulder']
c_back = gear['back']
c_chest = gear['chest']
if config.has_option('Gear', 'wrists'):
    c_wrists = gear['wrists']
else:
    c_wrists = gear['wrist']
c_hands = gear['hands']
c_waist = gear['waist']
c_legs = gear['legs']
c_feet = gear['feet']
c_finger1 = gear['finger1']
c_finger2 = gear['finger2']
c_trinket1 = gear['trinket1']
c_trinket2 = gear['trinket2']
c_main_hand = gear['main_hand']
if config.has_option('Gear', 'off_hand'):
    c_off_hand = gear['off_hand']
else:
    c_off_hand = ""

# Split vars to lists
l_head = c_head.split('|')
l_neck = c_neck.split('|')
l_shoulders = c_shoulders.split('|')
l_back = c_back.split('|')
l_chest = c_chest.split('|')
l_wrists = c_wrists.split('|')
l_hands = c_hands.split('|')
l_waist = c_waist.split('|')
l_legs = c_legs.split('|')
l_feet = c_feet.split('|')
l_finger1 = c_finger1.split('|')
l_finger2 = c_finger2.split('|')
l_trinket1 = c_trinket1.split('|')
l_trinket2 = c_trinket2.split('|')
l_main_hand = c_main_hand.split('|')
l_off_hand = c_off_hand.split('|')

# better handle rings and trinket-combinations

for a in l_finger2:
    if l_finger1.count(a) == 0:
        l_finger1.append(a)

for b in l_trinket2:
    if l_trinket1.count(b) == 0:
        l_trinket1.append(b)

set_fingers = set()
set_trinkets = set()

# compare items using simple string.compare-function, so "lowest" item (bitwise) will always be in front
# if combination is not in our result-set, concatenate and insert "|"-splitter
for ring in l_finger1:
    for ring2 in l_finger1:
        if ring == ring2:
            continue
        else:
            if ring < ring2:
                ring_combo = ring + "|" + ring2
                if ring_combo not in set_fingers:
                    set_fingers.add(ring_combo)
            else:
                ring_combo = ring2 + "|" + ring
                if ring_combo not in set_fingers:
                    set_fingers.add(ring_combo)

for trinket in l_trinket1:
    for trinket2 in l_trinket1:
        if trinket == trinket2:
            continue
        else:
            if trinket < trinket2:
                trinket_combo = trinket + "|" + trinket2
                set_trinkets.add(trinket_combo)
            else:
                trinket_combo = trinket2 + "|" + trinket
                set_trinkets.add(trinket_combo)

# convert set into list, i did not want to change the "theme" of the original data-structure
l_fingers = []
l_trinkets = []
while set_fingers:
    l_fingers.append(set_fingers.pop())
while set_trinkets:
    l_trinkets.append(set_trinkets.pop())

# free some memory
del set_fingers
del set_trinkets

# Make permutations
outputFile = open(outputFileName, 'w')
l_gear = ["head", "neck", "shoulders", "back", "chest", "wrists", "hands", "waist", "legs", "feet", "finger1",
          "finger2", "trinket1", "trinket2", "main_hand", "off_hand"]

#changed according to merged fields
c_profilemaxid = len(l_head) * len(l_neck) * len(l_shoulders) * len(l_back) * len(l_chest) * len(l_wrists) * len(
    l_hands) * len(l_waist) * len(l_legs) * len(l_feet) * len(l_fingers) * len(l_trinkets) * len(l_main_hand) * len(
    l_off_hand)
for a in range(len(l_head)):
    l_gear[0] = l_head[a]
    for b in range(len(l_neck)):
        l_gear[1] = l_neck[b]
        for c in range(len(l_shoulders)):
            l_gear[2] = l_shoulders[c]
            for d in range(len(l_back)):
                l_gear[3] = l_back[d]
                for e in range(len(l_chest)):
                    l_gear[4] = l_chest[e]
                    for f in range(len(l_wrists)):
                        l_gear[5] = l_wrists[f]
                        for g in range(len(l_hands)):
                            l_gear[6] = l_hands[g]
                            for h in range(len(l_waist)):
                                l_gear[7] = l_waist[h]
                                for i in range(len(l_legs)):
                                    l_gear[8] = l_legs[i]
                                    for j in range(len(l_feet)):
                                        l_gear[9] = l_feet[j]
                                        # changed according to new concatenated fields
                                        for k in range(len(l_fingers)):
                                            fingers = l_fingers[k].split('|')
                                            l_gear[10] = fingers[0]
                                            l_gear[11] = fingers[1]
                                            for l in range(len(l_trinkets)):
                                                trinkets = l_trinkets[k].split('|')
                                                l_gear[12] = trinkets[0]
                                                l_gear[13] = trinkets[1]
                                                if c_off_hand != "":
                                                    for o in range(len(l_main_hand)):
                                                        l_gear[14] = l_main_hand[o]
                                                        for p in range(len(l_off_hand)):
                                                            l_gear[15] = l_off_hand[p]
                                                            scpout(1)
                                                else:
                                                    for o in range(len(l_main_hand)):
                                                        l_gear[14] = l_main_hand[o]
                                                        scpout(0)
outputFile.close
