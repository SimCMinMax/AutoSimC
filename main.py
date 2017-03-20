#from lib_enchant_table import *

# Read settings.ini to init vars
import configparser
import sys
config = configparser.ConfigParser()
config.read(sys.argv[1])
profile = config['Profile']
gear = config['Gear']

# Var init
c_profileid=0
c_profilemaxid=0
legmin=0
legmax=2


# Read settings.ini
#   Profile
c_profilename=profile['profilename']
c_profileid=int(profile['profileid'])
c_class=profile['class']
c_race=profile['race']
c_level=profile['level']
c_spec=profile['spec']
c_role=profile['role']
c_position=profile['position']
c_talents=profile['talents']
c_artifact=profile['artifact']
c_other=profile['other']

#   Gear
c_head=gear['head']
c_neck=gear['neck']
if config.has_option('Gear', 'shoulders'): c_shoulders=gear['shoulders']
else: c_shoulders=gear['shoulder']
c_back=gear['back']
c_chest=gear['chest']
if config.has_option('Gear', 'wrists'): c_wrists=gear['wrists']
else: c_wrists=gear['wrist']
c_hands=gear['hands']
c_waist=gear['waist']
c_legs=gear['legs']
c_feet=gear['feet']
c_finger1=gear['finger1']
c_finger2=gear['finger2']
c_trinket1=gear['trinket1']
c_trinket2=gear['trinket2']
c_main_hand=gear['main_hand']
if config.has_option('Gear', 'off_hand'): c_off_hand=gear['off_hand']
else: c_off_hand=""

# Split vars to lists
l_head=c_head.split('|')
l_neck=c_neck.split('|')
l_shoulders=c_shoulders.split('|')
l_back=c_back.split('|')
l_chest=c_chest.split('|')
l_wrists=c_wrists.split('|')
l_hands=c_hands.split('|')
l_waist=c_waist.split('|')
l_legs=c_legs.split('|')
l_feet=c_feet.split('|')
l_finger1=c_finger1.split('|')
l_finger2=c_finger2.split('|')
l_trinket1=c_trinket1.split('|')
l_trinket2=c_trinket2.split('|')
l_main_hand=c_main_hand.split('|')
l_off_hand=c_off_hand.split('|')

# Add legendary to the right tab
def addToTab(x):
    stringToAdd="L,id="+x[1]+(",bonus_id="+x[2] if x[2]!="" else "")+(",enchant_id="+x[3] if x[3]!="" else "")+(",gem_id="+x[4] if x[4]!="" else "")
    if x[0]=='head': 
        l_head.append(stringToAdd)
    elif x[0]=='neck': 
        l_neck.append(stringToAdd)
    elif x[0]=='shoulders': 
        l_shoulders.append(stringToAdd)
    elif x[0]=='back': 
        l_back.append(stringToAdd)
    elif x[0]=='chest': 
        l_chest.append(stringToAdd)
    elif x[0]=='wrist': 
        l_wrists.append(stringToAdd)
    elif x[0]=='hands': 
        l_hands.append(stringToAdd)
    elif x[0]=='waist': 
        l_waist.append(stringToAdd)
    elif x[0]=='legs': 
        l_legs.append(stringToAdd)
    elif x[0]=='feet': 
        l_feet.append(stringToAdd)
    elif x[0]=='finger1': 
        l_finger1.append(stringToAdd)
    elif x[0]=='finger2': 
        l_finger2.append(stringToAdd)
    elif x[0]=='trinket1': 
        l_trinket1.append(stringToAdd)
    elif x[0]=='trinket2': 
        l_trinket2.append(stringToAdd)

# Manage legendary with command line
def handlePermutation(elements):
    for element in elements:
        pieces = element.split('|')
        addToTab(pieces)

# Check if permutation is valid
def checkUsability():
    if l_gear[10]==l_gear[11]:
        return "same ring"
    if l_gear[12]==l_gear[13]:
        return "same trinket"

    
    nbLeg=0
    for a in range(len(l_gear)):
        if l_gear[a][0]=="L":
            nbLeg=nbLeg+1
    if nbLeg<legmin:
        return str(nbLeg)+" leg (too low)"
    if nbLeg>legmax:
        return str(nbLeg)+" leg (too much)"
    
    return ""

# Print a simc profile
def scpout(oh):
    global c_profileid
    result = checkUsability()
    digits = len(str(c_profilemaxid))
    mask = '00000000000000000000000000000000000'
    maskedProfileID=(mask+str(c_profileid))[-digits:]
    if result!="":
        print("Profile:"+str(c_profileid)+"/"+str(c_profilemaxid)+' Error:'+result)
    else:
        print("Profile:"+str(c_profileid)+"/"+str(c_profilemaxid))
        outputFile.write(c_class+"="+c_profilename+"_"+maskedProfileID+"\n")
        outputFile.write("specialization="+c_spec+"\n")
        outputFile.write("race="+c_race+"\n")
        outputFile.write("level="+c_level+"\n")
        outputFile.write("role="+c_role+"\n")
        outputFile.write("position="+c_position+"\n")
        outputFile.write("talents="+c_talents+"\n")
        outputFile.write("artifact="+c_artifact+"\n")
        if c_other!="": outputFile.write(c_other+"\n")
        outputFile.write("head="+ (l_gear[0] if l_gear[0][0]!="L" else l_gear[0][1:]) +"\n")
        outputFile.write("neck="+ (l_gear[1] if l_gear[1][0]!="L" else l_gear[1][1:]) +"\n")
        outputFile.write("shoulders="+ (l_gear[2] if l_gear[2][0]!="L" else l_gear[2][1:]) +"\n")
        outputFile.write("back="+ (l_gear[3] if l_gear[3][0]!="L" else l_gear[3][1:]) +"\n")
        outputFile.write("chest="+ (l_gear[4] if l_gear[4][0]!="L" else l_gear[4][1:]) +"\n")
        outputFile.write("wrists="+ (l_gear[5] if l_gear[5][0]!="L" else l_gear[5][1:]) +"\n")
        outputFile.write("hands="+ (l_gear[6] if l_gear[6][0]!="L" else l_gear[6][1:]) +"\n")
        outputFile.write("waist="+ (l_gear[7] if l_gear[7][0]!="L" else l_gear[7][1:]) +"\n")
        outputFile.write("legs="+ (l_gear[8] if l_gear[8][0]!="L" else l_gear[8][1:]) +"\n")
        outputFile.write("feet="+ (l_gear[9] if l_gear[9][0]!="L" else l_gear[9][1:]) +"\n")
        outputFile.write("finger1="+ (l_gear[10] if l_gear[10][0]!="L" else l_gear[10][1:]) +"\n")
        outputFile.write("finger2="+ (l_gear[11] if l_gear[11][0]!="L" else l_gear[11][1:]) +"\n")
        outputFile.write("trinket1="+ (l_gear[12] if l_gear[12][0]!="L" else l_gear[12][1:]) +"\n")
        outputFile.write("trinket2="+ (l_gear[13] if l_gear[13][0]!="L" else l_gear[13][1:]) +"\n")
        outputFile.write("main_hand="+l_gear[14]+"\n")
        if oh==1:
            outputFile.write("off_hand="+l_gear[15]+"\n\n")
        else:
            outputFile.write("\n")
    c_profileid+=1
    return()

# Manage command line parameters
def handleCommandLine():
    global outputFileName
    global legmin
    global legmax
    legmin=int(sys.argv[4][0] if len(sys.argv)==5 else "0")
    legmax=int(sys.argv[4][2] if (len(sys.argv)==5 and len(sys.argv[4])==3) else "2")
    if len(sys.argv)>3:
        elements=sys.argv[3].split(',')
        handlePermutation(elements)
    outputFileName=sys.argv[2]
    
# Program start
handleCommandLine()

outputFile=open(outputFileName,'w')
l_gear=["head","neck","shoulders","back","chest","wrists","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand"]
c_profilemaxid = len(l_head)*len(l_neck)*len(l_shoulders)*len(l_back)*len(l_chest)*len(l_wrists)*len(l_hands)*len(l_waist)*len(l_legs)*len(l_feet)*len(l_finger1)*len(l_finger2)*len(l_trinket1)*len(l_trinket2)*len(l_main_hand)*len(l_off_hand)
for a in range(len(l_head)):
    l_gear[0]=l_head[a]
    for b in range (len(l_neck)):
        l_gear[1]=l_neck[b]
        for c in range (len(l_shoulders)):
            l_gear[2]=l_shoulders[c]
            for d in range (len(l_back)):
                l_gear[3]=l_back[d]
                for e in range (len(l_chest)):
                    l_gear[4]=l_chest[e]
                    for f in range (len(l_wrists)):
                        l_gear[5]=l_wrists[f]
                        for g in range (len(l_hands)):
                            l_gear[6]=l_hands[g]
                            for h in range (len(l_waist)):
                                l_gear[7]=l_waist[h]
                                for i in range (len(l_legs)):
                                    l_gear[8]=l_legs[i]
                                    for j in range (len(l_feet)):
                                        l_gear[9]=l_feet[j]
                                        for k in range (len(l_finger1)):
                                            l_gear[10]=l_finger1[k]
                                            for l in range (len(l_finger2)):
                                                l_gear[11]=l_finger2[l]
                                                for m in range (len(l_trinket1)):
                                                    l_gear[12]=l_trinket1[m]
                                                    for n in range (len(l_trinket2)):
                                                        l_gear[13]=l_trinket2[n]
                                                        if c_off_hand!="":
                                                            for o in range (len(l_main_hand)):
                                                                l_gear[14]=l_main_hand[o]
                                                                for p in range (len(l_off_hand)):
                                                                    l_gear[15]=l_off_hand[p]
                                                                    scpout(1)
                                                        else:
                                                            for o in range (len(l_main_hand)):
                                                                l_gear[14]=l_main_hand[o]
                                                                scpout(0)
outputFile.close
