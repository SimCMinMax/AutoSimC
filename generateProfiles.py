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

legmin = settings.default_leg_min
legmax = settings.default_leg_max
t19min = settings.default_equip_t19_min
t19max = settings.default_equip_t19_max
t20min = settings.default_equip_t20_min
t20max = settings.default_equip_t20_max
t21min = settings.default_equip_t21_min
t21max = settings.default_equip_t21_max
tierToGenerate = settings.tier
b_quiet = settings.b_quiet

outputFileName = settings.default_inputFileName
classToGenerate = ""
specToGenerate = ""
talentToGenerate = ""
profileFilter = ["\n","#", "actions", "potion", "flask", "food", "augmentation"]
gearList = ["head","neck","shoulders","back","chest","wrists","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand"]
profileFilter.extend(gearList)

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

logFileName = settings.logFileName
errorFileName = settings.errorFileName

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

    # parameter-list, so they are "protected" if user enters wrong commandline
    set_parameters = set()
    set_parameters.add("-o")
    set_parameters.add("-c")
    set_parameters.add("-s")
    set_parameters.add("-t")
    set_parameters.add("-quiet")
    # set_parameters.add("-all")
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
                print("Error: No or invalid spec declared: " + talentToGenerate)
                sys.exit(1)
        # if sys.argv[a] == "-all":
            # classToGenerate="all"
            # if classToGenerate not in set_parameters:
                # printLog("Generate all profiles")
            # else:
                # print("Error: No or invalid output file declared: " + classToGenerate)
                # sys.exit(1)

def getProfileFilePath():
    return "..\\simc\\profiles\\Tier" + tierToGenerate + "\\T" + tierToGenerate + "_" + classToGenerate + "_" + specToGenerate + ("_" + talentToGenerate if not talentToGenerate == "" else "") + ".simc"

   
def validateSettings():
    #validate class
    if classToGenerate == "":
        printLog("Error: No class asked")
        sys.exit(0)
    if specToGenerate == "":
        printLog("Error: No spec asked")
        sys.exit(0)
    # validate amount of legendaries
    if legmin > legmax or legmax > 3 or legmin > 3 or legmin < 0 or legmax < 0:
        printLog("Error: Legmin: " + str(legmin) + ", Legmax: " + str(
            legmax) + ". Please check settings.py for these parameters!")
        sys.exit(0)
    # validate tier-set
    if (int(t19min) + int(t20min) + int(
            t21min) > 6) or t19min < 0 or t19min > 6 or t20min < 0 or t20min > 6 or t21min < 0 or t21min > 6 or t19max < 0 or t19max > 6 or t20max < 0 or t20max > 6 or t21max < 0 or t21max > 6 or t19min > t19max or t20min > t20max or t21min > t21max:
        printLog("Error: Wrong Tier-Set-Combination: T19: " + str(t19min) + "/" + str(t19max) + ", T20: " + str(
            t20min) + "/" + str(t20max) + ", T21: " + str(t21min) + "/" + str(
            t21max) + ". Please check settings.py for these parameters!")
        sys.exit(0)
    if tierToGenerate == "":
        printLog("Error: No tier in settings")
        sys.exit(0)
    if not os.path.isfile(getProfileFilePath()):
        printLog("Error: Can't find the profile file : " + getProfileFilePath())
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
    with open(getProfileFilePath(), 'r') as profile:
        lignes  = profile.readlines()
        profile.close()

        for ligne in lignes:
            if not ligne.startswith(tuple(profileFilter)):
                file.write(ligne)
    file.write('\n')

    #print gear
    file.write('[Gear]\n')

