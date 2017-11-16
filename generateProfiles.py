# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0301

"""
@author: Kutikuti
"""

import configparser
import sys
import os
import json
import datetime
from settings import settings
from string import digits
import re

# command line settings
outputFileName = ""
classToGenerate = ""
specToGenerate = ""
talentToGenerate = ""
statsFilter = ""


#Local settings
material = ""
potion = ""
flask = ""
food = ""
augmentation = ""
enchantNeck = ""
enchantBack = ""
enchantFinger = ""
gem = ""
allowT19 = False
allowT20 = False
allowT21 = False
trinket1 = ""
trinket2 = ""
main_handSave = ""
off_handSave = ""
fileToUse = ""
itemNB = 0
profileFilter = ["\n","#", "actions", "potion", "flask", "food", "augmentation"]
gearList = ["head","neck","shoulders","back","chest","wrists","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand"]
statsList = ["agi","str","int","stam","crit","haste","vers","mastery","bonus_armor","leech","avoidance"]
profileFilter.extend(gearList)

#Settings.py
tierToGenerate = settings.tier
b_quiet = settings.b_quiet
logFileName = settings.logFileName
errorFileName = settings.errorFileName
apply_stat_filter_to_tier = settings.apply_stat_filter_to_tier
filter_type = settings.filter_type
default_profile_path = settings.default_profile_path
check_previous_tier = settings.check_previous_tier
minimum_tier_to_check = settings.minimum_tier_to_check

#   Error handle
def printLog(stringToPrint):
    if not b_quiet:
        # should this console-output be here at all? outputting to file AND console could be handled separately
        # e.g. via simple debug-toggle (if b_debug: print(...))
        print(stringToPrint)
    today = datetime.date.today()
    logFile.write(str(today) + ":" + stringToPrint + "\n")

def handleCommandLine():
    global outputFileName
    global classToGenerate
    global specToGenerate
    global talentToGenerate
    global b_quiet
    global statsFilter

    # parameter-list, so they are "protected" if user enters wrong commandline
    set_parameters = set()
    set_parameters.add("-o")
    set_parameters.add("-c")
    set_parameters.add("-s")
    set_parameters.add("-t")
    set_parameters.add("-quiet")
    set_parameters.add("-stats")
    for a in range(1, len(sys.argv)):
        if sys.argv[a] == "-o":
            outputFileName = sys.argv[a + 1]
            if outputFileName not in set_parameters:
                printLog("Output file changed to " + outputFileName)
            else:
                print("Error: No or invalid output file declared: " + outputFileName)
                sys.exit(1)
        if sys.argv[a] == "-c":
            classToGenerate = sys.argv[a + 1]
            if classToGenerate not in set_parameters:
                printLog("Class to generate profile changed to " + classToGenerate)
            else:
                print("Error: No or invalid class declared: " + classToGenerate)
                sys.exit(1)
        if sys.argv[a] == "-quiet":
            printLog("Quiet-Mode enabled")
            b_quiet = 1
        if sys.argv[a] == "-s":
            specToGenerate = sys.argv[a + 1]
            if specToGenerate not in set_parameters:
                printLog("Spec to generate profile changed to " + specToGenerate)
            else:
                print("Error: No or invalid spec declared: " + specToGenerate)
                sys.exit(1)
        if sys.argv[a] == "-t":
            talentToGenerate = sys.argv[a + 1]
            if talentToGenerate not in set_parameters:
                printLog("Talent to generate profile changed to " + talentToGenerate)
            else:
                print("Error: No or invalid talent declared: " + talentToGenerate)
                sys.exit(1)
        if sys.argv[a] == "-stats":
            statsFilter = sys.argv[a + 1]
            if statsFilter not in set_parameters:
                printLog("Stat filter profile changed to " + statsFilter)
            else:
                print("Error: No or invalid stat filter declared: " + statsFilter)
                print("Use: stats separated by / ")
                print("Available filter : agi/str/int/stam/crit/haste/vers/mastery/bonus_armor/leech/avoidance")
                sys.exit(1)
        
def getProfileFilePath():
    global default_profile_path
    global fileToUse
    
    fileToUse = default_profile_path + "\\Tier" + str(tierToGenerate) + "\\T" + str(tierToGenerate) + "_" + classToGenerate + "_" + specToGenerate + ("_" + talentToGenerate if not talentToGenerate == "" else "") + ".simc"
    
    if os.path.isfile(fileToUse):   
        return True
    elif not check_previous_tier:
        return False
    else:
        currentTier = tierToGenerate - 1
        while currentTier >= minimum_tier_to_check:
            fileToUse = default_profile_path + "\\Tier" + str(currentTier) + "\\T" + str(currentTier) + "_" + classToGenerate + "_" + specToGenerate + ("_" + talentToGenerate if not talentToGenerate == "" else "") + ".simc"
            if os.path.isfile(fileToUse):   
                return True
            else:
                currentTier = currentTier - 1
        return False
    
    return True
   
def validateSettings():
    global outputFileName
    
    #validate class
    if classToGenerate == "":
        printLog("Error: No class asked")
        sys.exit(0)
    #validate spec
    if specToGenerate == "":
        printLog("Error: No spec asked")
        sys.exit(0)
    #Prepare output filename
    if outputFileName == "":
        outputFileName = "input_"+classToGenerate+"_"+specToGenerate+("_"+talentToGenerate if not talentToGenerate =="" else "")+".simc"
    #validate stat filter
    if not statsFilter == "":
        if "/" in statsFilter: # cut the multiple spec legendaries and handle them separatly
            t = statsFilter.split('/')
            for i in range(len(t)):
                if t[i] not in statsList:
                    printLog("Error: unknown stat filter :" + t[i])
                    sys.exit(0)
        else:
            if statsFilter not in statsList:
                printLog("Error: unknown stat filter :" + statsFilter)
                sys.exit(0)
    if not getProfileFilePath():
        printLog("Error: Couldn't get the initial profile :" + fileToUse)
        sys.exit(0)
        
def getDataSettings():
    global material
    global potion
    global flask
    global food
    global augmentation
    global enchantNeck
    global enchantBack
    global enchantFinger
    global gem
    global allowT19
    global allowT20
    global allowT21

    with open('generatorData.json') as data_file: 
        data = json.load(data_file)

        material = data["classes"][classToGenerate]["material"]
        potion = data["classes"][classToGenerate]["specs"][specToGenerate]["potion"]
        flask = data["classes"][classToGenerate]["specs"][specToGenerate]["flask"]
        food = data["classes"][classToGenerate]["specs"][specToGenerate]["food"]
        augmentation = data["classes"][classToGenerate]["specs"][specToGenerate]["augmentation"]
        enchantNeck = data["classes"][classToGenerate]["specs"][specToGenerate]["enchant"]["neck"]
        enchantBack = data["classes"][classToGenerate]["specs"][specToGenerate]["enchant"]["back"]
        enchantFinger = data["classes"][classToGenerate]["specs"][specToGenerate]["enchant"]["finger"]
        gem = data["classes"][classToGenerate]["specs"][specToGenerate]["gem"]
        allowT19 = data["classes"][classToGenerate]["specs"][specToGenerate]["allowT19"]
        allowT20 = data["classes"][classToGenerate]["specs"][specToGenerate]["allowT20"]
        allowT21 = data["classes"][classToGenerate]["specs"][specToGenerate]["allowT21"]


def sanitizeString(str):
    str.replace("'","")
    str = re.sub(r"\s+", '_', str)
    str.replace(",","_")
    str.replace("-","_")
    str.lower()
    return str
    
def itemElligible(item):
    if "set" in item and not item["set"] == "" and not item["class"] == classToGenerate:
        return False
    if "set" in item and not allowT19 and item["set"] == "T19":
        return False
    if "set" in item and not allowT20 and item["set"] == "T20":
        return False
    if "set" in item and not allowT21 and item["set"] == "T21":
        return False
    if "enable" in item and item["enable"] == False:
        return False
    if not statsFilter == "": #stat filter
        if filter_type == 1:# all filter has to be in the item
            if "set" in item and (( not item["set"] == "" and apply_stat_filter_to_tier) or item["set"] == ""):
                if "/" in statsFilter: # cut the multiple spec legendaries and handle them separatly
                    t = statsFilter.split('/')
                    for i in range(len(t)):
                        if t[i] not in item["stats"]:
                            return False
                else:
                    if statsFilter not in item["stats"]:
                            return False
        elif filter_type == 2:# at least one filter has to be in the item
            if "set" in item and (( not item["set"] == "" and apply_stat_filter_to_tier) or item["set"] == ""):
                if "/" in statsFilter: # cut the multiple spec legendaries and handle them separatly
                    t = statsFilter.split('/')
                    statcount = 0
                    for i in range(len(t)):
                        if t[i] in item["stats"]:
                            statcount = statcount + 1
                    if statcount == 0:
                        return False
                else:
                    if statsFilter not in item["stats"]:
                        return False
    return True

def printItem(item):
    global itemNB
    stringToPrint = ""
    if itemElligible(item):
        gemString = ""
        if item["gems"] > 0:
            gemString = ',gem_id='
            for i in range(item["gems"]):
                gemString = gemString + str(gem) + "/"
            gemString = gemString[:-1]
        enchantString = ""
        legString = ""
        setString = ""
        if item["type"]=='neck':
            enchantString = ',enchant=' + enchantNeck
        elif item["type"]=='back':
            enchantString = ',enchant=' + enchantBack
        elif item["type"]=='finger':
            enchantString = ',enchant=' + enchantFinger
        if "set" in item:
            setString = item["set"]
        else:
            legString = "L"
        itemNB = itemNB+1
        printstats = ""
        # printstats = "(" + item["stats"]+ ")"
        stringToPrint = legString + setString + ("--" if not setString == "" or not legString == "" else "") + sanitizeString(item["name"]) + ',id=' + str(item["id"])+ ',bonus_id=' + item["bonus_id"] + gemString + enchantString + printstats +"|"
    return stringToPrint


########################
#### Program Start ######
#########################
sys.stderr = open(errorFileName, 'w')
logFile = open(logFileName, 'w')
handleCommandLine()
validateSettings()
getDataSettings()

#Begin generation, setting is good
with open(outputFileName, 'w', encoding='utf-8') as file:
    #print profile
    file.write('[Profile]\n')
    with open(fileToUse, 'r') as profile:
        lines  = profile.readlines()
        profile.close()

        for line in lines:
            if line.startswith('trinket1'):  
                trinket1Save = line
            if line.startswith('trinket2'):  
                trinket2Save = line
            if line.startswith('main_hand'):
                main_handSave = line
            if line.startswith('off_hand'):  
                off_handSave = line
            if not line.startswith(tuple(profileFilter)):
                file.write(line)
    file.write('\n')

    #print gear
    file.write('[Gear]\n')

    with open('generatorItemData.json') as itemDataFile: 
        with open('generatorLegendaryData.json') as legendaryDataFile: 
            gearDataList  = json.load(itemDataFile)
            legendaryGearDataList  = json.load(legendaryDataFile)
            remove_digits = str.maketrans('', '', digits)#prepare for number removal (finger)
            
            for slot in gearList:
                stringToPrint = ""
                if slot == 'trinket1':
                    file.write(trinket1Save)
                elif slot == 'trinket2':
                    file.write(trinket2Save)
                elif slot == 'main_hand':
                    file.write(main_handSave)
                elif slot == 'off_hand':
                    file.write(off_handSave)
                else:
                    file.write(slot + "=")
                    
                    if slot == "neck" or slot == "back" or slot == "finger1" or slot == "finger2":
                        slotReady = slot.translate(remove_digits)
                        for slotitems in gearDataList[slotReady]:
                            stringToPrint = stringToPrint + printItem(slotitems)
                        #Add legendaries
                        if slotReady in legendaryGearDataList[classToGenerate][specToGenerate]:
                            for slotitemsleg in legendaryGearDataList[classToGenerate][specToGenerate][slotReady]:
                                stringToPrint = stringToPrint + printItem(slotitemsleg)
                    else:
                        for slotitems in gearDataList[slot][material]:
                            stringToPrint = stringToPrint + printItem(slotitems)
                        #Add legendaries
                        if slot in legendaryGearDataList[classToGenerate][specToGenerate]:
                            for slotitemsleg in legendaryGearDataList[classToGenerate][specToGenerate][slot]:
                                stringToPrint = stringToPrint + printItem(slotitemsleg)
                    
                    stringToPrint = stringToPrint[:-1]
                    file.write(stringToPrint)
                    file.write("\n")
            print("items : "+str(itemNB))