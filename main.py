import configparser
import sys
import datetime
import os
import json
import shutil
from settings import settings

from specdata import specdata
import splitter
import hashlib

# Var init with default value
c_profileid = 0
c_profilemaxid = 0
legmin = settings.default_leg_min
legmax = settings.default_leg_max
t19min = settings.default_equip_t19_min
t19max = settings.default_equip_t19_max
t20min = settings.default_equip_t20_min
t20max = settings.default_equip_t20_max
t21min = settings.default_equip_t21_min
t21max = settings.default_equip_t21_max

outputFileName = settings.default_outputFileName
# txt, because standard-user cannot be trusted
inputFileName = settings.default_inputFileName

logFileName = settings.logFileName
errorFileName = settings.errorFileName
# quiet_mode for faster output; console is very slow
b_quiet = settings.b_quiet
i_generatedProfiles = 0

b_simcraft_enabled = settings.default_sim_enabled
s_stage = ""

iterations_firstpart = settings.default_iterations_stage1
iterations_secondpart = settings.default_iterations_stage2
iterations_thirdpart = settings.default_iterations_stage3

target_error_secondpart = settings.default_target_error_stage2
target_error_thirdpart = settings.default_target_error_stage3
gemspermutation = False
s = specdata()

gem_ids = {}
gem_ids["150haste"] = "130220"
gem_ids["200haste"] = "151583"
gem_ids["haste"] = "151583"  # always contains maximum quality
gem_ids["150crit"] = "130219"
gem_ids["200crit"] = "151580"
gem_ids["crit"] = "151580"  # always contains maximum quality
gem_ids["150vers"] = "130221"
gem_ids["200vers"] = "151585"
gem_ids["vers"] = "151585"  # always contains maximum quality
gem_ids["150mast"] = "130222"
gem_ids["200mast"] = "151584"
gem_ids["mast"] = "151584"  # always contains maximum quality
gem_ids["200str"] = "130246"
gem_ids["str"] = "130246"
gem_ids["200agi"] = "130247"
gem_ids["agi"] = "130247"
gem_ids["200int"] = "130248"
gem_ids["int"] = "130248"


#   Error handle
def printLog(stringToPrint):
    if not b_quiet:
        # should this console-output be here at all? outputting to file AND console could be handled separately
        # e.g. via simple debug-toggle (if b_debug: print(...))
        print(stringToPrint)
    today = datetime.date.today()
    logFile.write(str(today) + ":" + stringToPrint + "\n")


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


def handleGems(gems):
    allowed_gems = ["crit", "vers", "haste", "mast", "int", "str", "agi"]
    global splitted_gems
    if gems:
        splitted_gems = gems.split(",")
        for i in range(len(splitted_gems)):
            if splitted_gems[i] not in allowed_gems:
                printLog("Unknown gem to sim, please check your input: " + str(splitted_gems[i]))
                print("Unknown gem to sim, please check your input: " + str(splitted_gems[i]))
                sys.exit(1)


# Check if permutation is valid
def checkUsability():
    # namingdata contains info for the profile-name
    global namingData
    namingData = {}

    temp_t19 = 0
    temp_t20 = 0
    temp_t21 = 0

    for i in range(len(l_gear)):
        if l_gear[i][0:3] == "T19":
            temp_t19 = temp_t19 + 1
        if l_gear[i][0:3] == "T20":
            temp_t20 = temp_t20 + 1
        if l_gear[i][0:3] == "T21":
            temp_t21 = temp_t21 + 1
    if temp_t19 < int(t19min):
        return " " + str(temp_t19) + ": too few T19-items (" + str(t19min) + " asked)"
    if temp_t20 < int(t20min):
        return " " + str(temp_t20) + ": too few T20-items (" + str(t20min) + " asked)"
    if temp_t21 < int(t21min):
        return " " + str(temp_t21) + ": too few T21-items (" + str(t21min) + " asked)"
    if temp_t19 > int(t19max):
        return " " + str(temp_t19) + ": too much T19-items (" + str(t19max) + " asked)"
    if temp_t20 > int(t20max):
        return " " + str(temp_t20) + ": too much T20-items (" + str(t20max) + " asked)"
    if temp_t21 > int(t21max):
        return " " + str(temp_t21) + ": too much T21-items (" + str(t21max) + " asked)"

    if l_gear[10] == l_gear[11]:
        return " Same ring"
    if l_gear[12] == l_gear[13]:
        return " Same trinket"

    nbLeg = 0
    for a in range(len(l_gear)):
        if l_gear[a][0] == "L":
            nbLeg = nbLeg + 1
    if nbLeg < legmin:
        return str(nbLeg) + " leg (" + str(legmin) + " asked)"
    if nbLeg > legmax:
        return str(nbLeg) + " leg (" + str(legmax) + " asked)"

    # check if amanthuls-trinket is the 3rd trinket; otherwise its an invalid profile
    # because 3 other legs have been equipped
    if nbLeg == 3:
        if not getIdFromItem(l_gear[12]) == "154172" and not getIdFromItem(l_gear[13]) == "154172":
            return " 3 legs equipped, but no Amanthul-Trinket found"

    # check gems
    # int, str, agi should be only equipped once:
    nUniqueGems = 0
    for a in range(len(l_gear)):
        gems = getGemsFromItem(l_gear[a])
        if "130246" in gems or "130247" in gems or "130248" in gems:
            nUniqueGems += 1
    if nUniqueGems > 1:
        return str(nUniqueGems) + " too many unique gems (str, agi, int)"

    # if a valid profile was detected, fill namingData; otherwise its pointless
    if nbLeg == 0:
        namingData['Leg0'] = ""
        namingData["Leg1"] = ""
    elif nbLeg == 1:
        for a in range(len(l_gear)):
            if l_gear[a][0] == "L":
                namingData['Leg0'] = getIdFromItem(l_gear[a][0])
    elif nbLeg == 2:
        for a in range(len(l_gear)):
            if l_gear[a][0] == "L":
                if namingData.get('Leg0') != None:
                    namingData['Leg1'] = getIdFromItem(l_gear[a])
                else:
                    namingData['Leg0'] = getIdFromItem(l_gear[a])
    elif nbLeg == 3:
        for a in range(len(l_gear)):
            if l_gear[a][0] == "L":
                if namingData.get('Leg0') == None:
                    namingData['Leg0'] = getIdFromItem(l_gear[a])
                else:
                    if namingData.get('Leg1') != None:
                        namingData['Leg1'] = getIdFromItem(l_gear[a])
                    else:
                        namingData['Leg2'] = getIdFromItem(l_gear[a])

    namingData["T19"] = temp_t19
    namingData["T20"] = temp_t20
    namingData["T21"] = temp_t21

    if getIdFromItem(l_gear[10]) == getIdFromItem(l_gear[11]):
        return F"Ring1: {l_gear[10]} same as Ring2: {l_gear[11]}"
    if getIdFromItem(l_gear[12]) == getIdFromItem(l_gear[13]):
        return F"Trinket1: {l_gear[12]} same as Trinket2: {l_gear[13]}"

    if getIdFromItem(l_gear[12]) in {"154172", "154173", "154174", "154175", "154176", "154177"}:
        if getIdFromItem(l_gear[13]) in {"154172", "154173", "154174", "154175", "154176", "154177"}:
            return " two Pantheon-Trinkets found"
    return ""


def getIdFromItem(item):
    splits = item.split(",")
    for s in splits:
        if s.startswith("id="):
            return s[3:]


# Print a simc profile
def scpout(oh):
    global c_profileid
    global i_generatedProfiles
    result = checkUsability()
    digits = len(str(c_profilemaxid))
    mask = '00000000000000000000000000000000000'
    maskedProfileID = (mask + str(c_profileid))[-digits:]
    # output status every 5000 permutations, user should get at least a minor progress shown; also does not slow down
    # computation very much
    if int(maskedProfileID) % 5000 == 0:
        print("Processed: " + str(maskedProfileID) + "/" + str(c_profilemaxid) + " (" + str(
            round(100 * float(int(maskedProfileID) / int(c_profilemaxid)), 1)) + "%)")
    if int(maskedProfileID) == c_profilemaxid:
        print("Processed: " + str(maskedProfileID) + "/" + str(c_profilemaxid) + " (" + str(
            round(100 * float(int(maskedProfileID) / int(c_profilemaxid)), 1)) + "%)")
    if result != "":
        printLog("Profile:" + str(maskedProfileID) + "/" + str(c_profilemaxid) + ' Warning, not printed:' + result)
    else:
        if not b_quiet:
            print("Profile:" + str(maskedProfileID) + "/" + str(c_profilemaxid))
        outputFile.write(c_class + "=" + getStringForProfile() + maskedProfileID + "\n")
        outputFile.write("specialization=" + c_spec + "\n")
        outputFile.write("race=" + c_race + "\n")
        outputFile.write("level=" + c_level + "\n")
        outputFile.write("role=" + c_role + "\n")
        outputFile.write("position=" + c_position + "\n")
        outputFile.write("talents=" + c_talents + "\n")
        outputFile.write("artifact=" + c_artifact + "\n")
        if c_crucible != "":
            outputFile.write("crucible=" + c_crucible + "\n")
        if c_potion != "":
            outputFile.write("potion=" + c_potion + "\n")
        if c_flask != "":
            outputFile.write("flask=" + c_flask + "\n")
        if c_food != "":
            outputFile.write("food=" + c_food + "\n")
        if c_augmentation != "":
            outputFile.write("augmentation=" + c_augmentation + "\n")
        if c_other != "":
            outputFile.write(c_other + "\n")
        if l_gear[0][0] == "L":
            outputFile.write("head=" + l_gear[0][1:] + "\n")
        elif (l_gear[0][0:3] == "T19" or l_gear[0][0:3] == "T20"):
            outputFile.write("head=" + l_gear[0][3:] + "\n")
        else:
            outputFile.write("head=" + l_gear[0] + "\n")
        outputFile.write("neck=" + (l_gear[1] if l_gear[1][0] != "L" else l_gear[1][1:]) + "\n")

        if l_gear[2][0] == "L":
            outputFile.write("shoulders=" + l_gear[2][1:] + "\n")
        elif (l_gear[2][0:3] == "T19" or l_gear[2][0:3] == "T20"):
            outputFile.write("shoulders=" + l_gear[2][3:] + "\n")
        else:
            outputFile.write("shoulders=" + l_gear[2] + "\n")

        if l_gear[3][0] == "L":
            outputFile.write("back=" + l_gear[3][1:] + "\n")
        elif (l_gear[3][0:3] == "T19" or l_gear[3][0:3] == "T20"):
            outputFile.write("back=" + l_gear[3][3:] + "\n")
        else:
            outputFile.write("back=" + l_gear[3] + "\n")

        if l_gear[4][0] == "L":
            outputFile.write("chest=" + l_gear[4][1:] + "\n")
        elif (l_gear[4][0:3] == "T19" or l_gear[4][0:3] == "T20"):
            outputFile.write("chest=" + l_gear[4][3:] + "\n")
        else:
            outputFile.write("chest=" + l_gear[4] + "\n")

        outputFile.write("wrists=" + (l_gear[5] if l_gear[5][0] != "L" else l_gear[5][1:]) + "\n")

        if l_gear[6][0] == "L":
            outputFile.write("hands=" + l_gear[6][1:] + "\n")
        elif (l_gear[6][0:3] == "T19" or l_gear[6][0:3] == "T20"):
            outputFile.write("hands=" + l_gear[6][3:] + "\n")
        else:
            outputFile.write("hands=" + l_gear[6] + "\n")

        outputFile.write("waist=" + (l_gear[7] if l_gear[7][0] != "L" else l_gear[7][1:]) + "\n")

        if l_gear[8][0] == "L":
            outputFile.write("legs=" + l_gear[8][1:] + "\n")
        elif (l_gear[8][0:3] == "T19" or l_gear[8][0:3] == "T20"):
            outputFile.write("legs=" + l_gear[8][3:] + "\n")
        else:
            outputFile.write("legs=" + l_gear[8] + "\n")

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
        i_generatedProfiles += 1
    c_profileid += 1
    return ()


# Print a simc profile
def scpoutprofileset(oh):
    global c_profileid
    global i_generatedProfiles
    result = checkUsability()
    digits = len(str(c_profilemaxid))
    mask = '00000000000000000000000000000000000'
    maskedProfileID = (mask + str(c_profileid))[-digits:]
    # output status every 5000 permutations, user should get at least a minor progress shown; also does not slow down
    # computation very much
    if int(maskedProfileID) % 5000 == 0:
        print("Processed: " + str(maskedProfileID) + "/" + str(c_profilemaxid) + " (" + str(
            round(100 * float(int(maskedProfileID) / int(c_profilemaxid)), 1)) + "%)")
    if int(maskedProfileID) == c_profilemaxid:
        print("Processed: " + str(maskedProfileID) + "/" + str(c_profilemaxid) + " (" + str(
            round(100 * float(int(maskedProfileID) / int(c_profilemaxid)), 1)) + "%)")
    if result != "":
        printLog("Profile:" + str(maskedProfileID) + "/" + str(c_profilemaxid) + ' Warning, not printed:' + result)
    else:
        if not b_quiet:
            print("Profile:" + str(maskedProfileID) + "/" + str(c_profilemaxid))
        # generate first profile
        if i_generatedProfiles == 0:
            outputFile.write(c_class + "=" + getStringForProfile() + maskedProfileID + "\n")
            outputFile.write("specialization=" + c_spec + "\n")
            outputFile.write("race=" + c_race + "\n")
            outputFile.write("level=" + c_level + "\n")
            outputFile.write("role=" + c_role + "\n")
            outputFile.write("position=" + c_position + "\n")
            outputFile.write("talents=" + c_talents + "\n")
            outputFile.write("artifact=" + c_artifact + "\n")
            if c_crucible != "":
                outputFile.write("crucible=" + c_crucible + "\n")
            if c_potion != "":
                outputFile.write("potion=" + c_potion + "\n")
            if c_flask != "":
                outputFile.write("flask=" + c_flask + "\n")
            if c_food != "":
                outputFile.write("food=" + c_food + "\n")
            if c_augmentation != "":
                outputFile.write("augmentation=" + c_augmentation + "\n")
            if c_other != "":
                outputFile.write(c_other + "\n")
            if l_gear[0][0] == "L":
                outputFile.write("head=" + l_gear[0][1:] + "\n")
            elif (l_gear[0][0:3] == "T19" or l_gear[0][0:3] == "T20" or l_gear[0][0:3] == "T21"):
                outputFile.write("head=" + l_gear[0][3:] + "\n")
            else:
                outputFile.write("head=" + l_gear[0] + "\n")
            outputFile.write("neck=" + (l_gear[1] if l_gear[1][0] != "L" else l_gear[1][1:]) + "\n")

            if l_gear[2][0] == "L":
                outputFile.write("shoulders=" + l_gear[2][1:] + "\n")
            elif (l_gear[2][0:3] == "T19" or l_gear[2][0:3] == "T20" or l_gear[2][0:3] == "T21"):
                outputFile.write("shoulders=" + l_gear[2][3:] + "\n")
            else:
                outputFile.write("shoulders=" + l_gear[2] + "\n")

            if l_gear[3][0] == "L":
                outputFile.write("back=" + l_gear[3][1:] + "\n")
            elif (l_gear[3][0:3] == "T19" or l_gear[3][0:3] == "T20" or l_gear[3][0:3] == "T21"):
                outputFile.write("back=" + l_gear[3][3:] + "\n")
            else:
                outputFile.write("back=" + l_gear[3] + "\n")

            if l_gear[4][0] == "L":
                outputFile.write("chest=" + l_gear[4][1:] + "\n")
            elif (l_gear[4][0:3] == "T19" or l_gear[4][0:3] == "T20" or l_gear[4][0:3] == "T21"):
                outputFile.write("chest=" + l_gear[4][3:] + "\n")
            else:
                outputFile.write("chest=" + l_gear[4] + "\n")

            outputFile.write("wrists=" + (l_gear[5] if l_gear[5][0] != "L" else l_gear[5][1:]) + "\n")

            if l_gear[6][0] == "L":
                outputFile.write("hands=" + l_gear[6][1:] + "\n")
            elif (l_gear[6][0:3] == "T19" or l_gear[6][0:3] == "T20" or l_gear[6][0:3] == "T21"):
                outputFile.write("hands=" + l_gear[6][3:] + "\n")
            else:
                outputFile.write("hands=" + l_gear[6] + "\n")

            outputFile.write("waist=" + (l_gear[7] if l_gear[7][0] != "L" else l_gear[7][1:]) + "\n")

            if l_gear[8][0] == "L":
                outputFile.write("legs=" + l_gear[8][1:] + "\n")
            elif (l_gear[8][0:3] == "T19" or l_gear[8][0:3] == "T20" or l_gear[8][0:3] == "T21"):
                outputFile.write("legs=" + l_gear[8][3:] + "\n")
            else:
                outputFile.write("legs=" + l_gear[8] + "\n")

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
            i_generatedProfiles += 1
        # all other profiles
        else:
            pset_prefix = "profileset.\"" + c_profilename + "_" + maskedProfileID + "\"+="
            outputFile.write("talents=" + c_talents + "\n")
            if c_other != "":
                outputFile.write(pset_prefix + c_other + "\n")
            if l_gear[0][0] == "L":
                outputFile.write(pset_prefix + "head=" + l_gear[0][1:] + "\n")
            elif (l_gear[0][0:3] == "T19" or l_gear[8][0:3] == "T20" or l_gear[8][0:3] == "T21"):
                outputFile.write(pset_prefix + "head=" + l_gear[0][3:] + "\n")
            else:
                outputFile.write(pset_prefix + "head=" + l_gear[0] + "\n")
            outputFile.write(pset_prefix + "neck=" + (l_gear[1] if l_gear[1][0] != "L" else l_gear[1][1:]) + "\n")

            if l_gear[2][0] == "L":
                outputFile.write(pset_prefix + "shoulders=" + l_gear[2][1:] + "\n")
            elif (l_gear[2][0:3] == "T19" or l_gear[2][0:3] == "T20" or l_gear[2][0:3] == "T21"):
                outputFile.write(pset_prefix + "shoulders=" + l_gear[2][3:] + "\n")
            else:
                outputFile.write(pset_prefix + "shoulders=" + l_gear[2] + "\n")

            if l_gear[3][0] == "L":
                outputFile.write(pset_prefix + "back=" + l_gear[3][1:] + "\n")
            elif (l_gear[3][0:3] == "T19" or l_gear[3][0:3] == "T20" or l_gear[3][0:3] == "T21"):
                outputFile.write(pset_prefix + "back=" + l_gear[3][3:] + "\n")
            else:
                outputFile.write(pset_prefix + "back=" + l_gear[3] + "\n")

            if l_gear[4][0] == "L":
                outputFile.write(pset_prefix + "chest=" + l_gear[4][1:] + "\n")
            elif (l_gear[4][0:3] == "T19" or l_gear[4][0:3] == "T20" or l_gear[4][0:3] == "T21"):
                outputFile.write(pset_prefix + "chest=" + l_gear[4][3:] + "\n")
            else:
                outputFile.write(pset_prefix + "chest=" + l_gear[4] + "\n")

            outputFile.write(pset_prefix + "wrists=" + (l_gear[5] if l_gear[5][0] != "L" else l_gear[5][1:]) + "\n")

            if l_gear[6][0] == "L":
                outputFile.write(pset_prefix + "hands=" + l_gear[6][1:] + "\n")
            elif (l_gear[6][0:3] == "T19" or l_gear[6][0:3] == "T20" or l_gear[6][0:3] == "T21"):
                outputFile.write(pset_prefix + "hands=" + l_gear[6][3:] + "\n")
            else:
                outputFile.write(pset_prefix + "hands=" + l_gear[6] + "\n")

            outputFile.write(pset_prefix + "waist=" + (l_gear[7] if l_gear[7][0] != "L" else l_gear[7][1:]) + "\n")

            if l_gear[8][0] == "L":
                outputFile.write(pset_prefix + "legs=" + l_gear[8][1:] + "\n")
            elif (l_gear[8][0:3] == "T19" or l_gear[8][0:3] == "T20" or l_gear[8][0:3] == "T21"):
                outputFile.write(pset_prefix + "legs=" + l_gear[8][3:] + "\n")
            else:
                outputFile.write(pset_prefix + "legs=" + l_gear[8] + "\n")

            outputFile.write(pset_prefix + "feet=" + (l_gear[9] if l_gear[9][0] != "L" else l_gear[9][1:]) + "\n")
            outputFile.write(pset_prefix + "finger1=" + (l_gear[10] if l_gear[10][0] != "L" else l_gear[10][1:]) + "\n")
            outputFile.write(pset_prefix + "finger2=" + (l_gear[11] if l_gear[11][0] != "L" else l_gear[11][1:]) + "\n")
            outputFile.write(
                pset_prefix + "trinket1=" + (l_gear[12] if l_gear[12][0] != "L" else l_gear[12][1:]) + "\n")
            outputFile.write(
                pset_prefix + "trinket2=" + (l_gear[13] if l_gear[13][0] != "L" else l_gear[13][1:]) + "\n")
            outputFile.write(pset_prefix + "main_hand=" + l_gear[14] + "\n")
            if oh == 1:
                outputFile.write(pset_prefix + "off_hand=" + l_gear[15] + "\n\n")
            else:
                outputFile.write("\n")
            i_generatedProfiles += 1

    c_profileid += 1
    return ()


# Manage command line parameters
# todo: include logic to split into smaller/larger files (default 50)
def handleCommandLine():
    global inputFileName
    global outputFileName
    global legmin
    global legmax
    global b_quiet
    global b_simcraft_enabled
    global s_stage
    global restart
    global gemspermutation

    # parameter-list, so they are "protected" if user enters wrong commandline
    set_parameters = set()
    set_parameters.add("-i")
    set_parameters.add("-o")
    set_parameters.add("-l")
    set_parameters.add("-quiet")
    set_parameters.add("-sim")
    set_parameters.add("-gems")

    for a in range(1, len(sys.argv)):
        if sys.argv[a] == "-i":
            inputFileName = sys.argv[a + 1]
            if inputFileName not in set_parameters:
                if os.path.isfile(inputFileName):
                    printLog("Input file changed to " + inputFileName)
                else:
                    print("Error: Input file does not exist")
                    sys.exit(1)
            else:
                print("Error: No or invalid input file declared: " + inputFileName)
                sys.exit(1)
        if sys.argv[a] == "-o":
            outputFileName = sys.argv[a + 1]
            if outputFileName not in set_parameters:
                printLog("Output file changed to " + outputFileName)
                # if os.path.isfile(outputFileName):
                #    print("Error: Output file already exists")
                #    sys.exit(1)
            else:
                print("Error: No or invalid output file declared: " + outputFileName)
                sys.exit(1)
        if sys.argv[a] == "-l":
            elements = sys.argv[a + 1].split(',')
            # produces an error if <-l "" 2:2> was entered, what is the correct syntax?
            # i handle this in settings.py
            if elements:
                handlePermutation(elements)
            # number of leg
            if sys.argv[a + 2][0] != "-":
                legNb = sys.argv[a + 2].split(':')
                legmin = int(legNb[0])
                legmax = int(legNb[1])
                printLog("Set legendary to  " + str(legmin) + "/" + str(legmax))
        if sys.argv[a] == "-quiet":
            printLog("Quiet-Mode enabled")
            b_quiet = 1
        # if option -sim exists in commandline incl. stage1,2,3, it overwrites all values of settings.py
        if sys.argv[a] == "-sim":
            # check path of simc.exe
            if not os.path.exists(settings.simc_path):
                printLog("Error: Wrong path to simc.exe: " + str(settings.simc_path))
                print("Error: Wrong path to simc.exe: " + str(settings.simc_path))
                sys.exit(1)
            else:
                printLog("Path to simc.exe valid, proceeding...")
            print("SimCraft-Mode enabled")
            printLog("SimCraft-Mode enabled")
            b_simcraft_enabled = True
            # optional parameter to skip steps and continue at a certain point without deleting intermediate files:
            # usage main.py -i ... -o ... -sim [stage1|stage2|stage3]
            # staging is equivalent to the 3 iteration processes:
            #   - 1: mass processing with few iterations (default)
            #   - 2: picking best n and process these
            #   - 3: picking top n out of these
            # it is essentially used to skip the most time consuming part, stage 1
            # to test alterations and different outputs, e.g. using same gear within different scenarios
            # (standard might be patchwerk, but what happens with this gear- and talentchoice in a helterskelter-szenario?)
            if sys.argv[a + 1] != s_stage:
                restart = True
            else:
                restart = False
            s_stage = sys.argv[a + 1]
            if s_stage in set_parameters:
                printLog("Wrong parameter for -sim: " + str(s_stage))
                print("Wrong parameter for ""-sim"" option: " + str(s_stage))
                sys.exit(1)
            if not s_stage:
                printLog("Missing parameter for -sim: " + s_stage)
                print("Missing parameter for ""-sim"" option: " + str(s_stage))
                sys.exit(1)
            if s_stage != "stage1" and s_stage != "stage2" and s_stage != "stage3":
                printLog("Wrong Parameter for Stage: " + str(s_stage))
                sys.exit(1)
        if sys.argv[a] == "-gems":
            gems = sys.argv[a + 1]
            if gems not in set_parameters:
                gemspermutation = True
                handleGems(gems)


# returns target_error, iterations, elapsed_time_seconds for a given class_spec
def get_data(class_spec):
    result = []
    f = open(os.path.join(os.getcwd(), settings.analyzer_path, settings.analyzer_filename), "r")
    file = json.load(f)
    for variant in file[0]:
        for p in variant["playerdata"]:
            if p["specialization"] == class_spec:
                for s in range(len(p["specdata"])):
                    item = (
                        variant["target_error"], p["specdata"][s]["iterations"],
                        p["specdata"][s]["elapsed_time_seconds"])
                    result.append(item)
    return result


def cleanup():
    printLog("Cleaning up")
    if not os.path.exists(os.path.join(os.getcwd(), settings.result_subfolder)):
        printLog("Result-subfolder does not exist: " + str(settings.result_subfolder) + ", creating it")
        os.makedirs(settings.result_subfolder)

    if os.path.exists(os.path.join(os.getcwd(), settings.subdir3)):
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), settings.subdir3)):
            for file in files:
                if file.endswith(".html"):
                    printLog("Moving file: " + str(file))
                    shutil.move(os.path.join(os.getcwd(), settings.subdir3, file),
                                os.path.join(os.getcwd(), settings.result_subfolder, file))
    if os.path.exists(os.path.join(os.getcwd(), settings.subdir1)):
        if settings.delete_temp_default or input(
                                "Do you want to remove subfolder: " + settings.subdir1 + "? (Press y to confirm): ") == "y":
            printLog("Removing: " + settings.subdir1)
            shutil.rmtree(settings.subdir1)
    if os.path.exists(os.path.join(os.getcwd(), settings.subdir2)):
        if settings.delete_temp_default or input(
                                "Do you want to remove subfolder: " + settings.subdir2 + "? (Press y to confirm): ") == "y":
            shutil.rmtree(settings.subdir2)
            printLog("Removing: " + settings.subdir2)
    if os.path.exists(os.path.join(os.getcwd(), settings.subdir3)):
        if settings.delete_temp_default or input(
                                "Do you want to remove subfolder: " + settings.subdir3 + "? (Press y to confirm): ") == "y":
            shutil.rmtree(settings.subdir3)
            printLog("Removing: " + settings.subdir3)


def validateSettings():
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
    # use a "safe mode", overwriting the values
    if settings.simc_safe_mode:
        printLog("Using Safe Mode")
        settings.simc_threads = 1
    if b_simcraft_enabled:
        if os.name == "nt":
            if not settings.simc_path.endswith("simc.exe"):
                printLog("simc.exe wrong or missing in settings.py path-variable, please edit it")
                sys.exit(0)
        if os.path.exists(os.path.join(os.getcwd(), settings.analyzer_path, settings.analyzer_filename)):
            printLog("Analyzer-file found")
        else:
            printLog("Analyzer-file not found, make sure you have a complete AutoSimc-Package")
            sys.exit(1)
    if settings.default_error_rate_multiplier <= 0:
        printLog("Wrong default_error_rate_multiplier: " + str(settings.default_error_rate_multiplier))


def generate_checksum_of_permutations():
    hash_md5 = hashlib.sha3_256()
    with open(settings.default_outputFileName, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    print(str(hash_md5.hexdigest()))


def get_Possible_Gem_Combinations(numberOfGems):
    printLog("Creating Gem Combinations")
    printLog("Number of Gems: " + str(numberOfGems))
    l_gems = []
    # 1 gem
    if numberOfGems == 1:
        for r in splitted_gems:
            l_gems.append(gem_ids.get(r))
    # 2 gems
    if numberOfGems == 2:
        for r in splitted_gems:
            for s in splitted_gems:
                if r < s:
                    l_gems.append(gem_ids.get(r) + "/" + gem_ids.get(s))
                else:
                    l_gems.append(gem_ids.get(s) + "/" + gem_ids.get(r))
    if numberOfGems == 3:
        for r in splitted_gems:
            for s in splitted_gems:
                for t in splitted_gems:
                    p = [r, s, t]
                    p.sort()
                    l_gems.append(gem_ids.get(p[0]) + "/" + gem_ids.get(p[1]) + "/" + gem_ids.get(p[2]))
    return l_gems


def getGemsFromItem(item):
    a = item.split(",")
    gems = []
    for i in range(len(a)):
        # look for gem_id-string in items
        if a[i].startswith("gem_id"):
            b, c = a[i].split("=")
            gems = c.split("/")
            # up to 3 possible gems
    return gems


# gearlist contains a list of items, as in l_head
def permutateGemsInSlotGearList(slot_gearlist, slot):
    printLog("Permutating slot_gearlist: " + str(slot_gearlist))
    for item in slot_gearlist:
        printLog(str(item))
        a = item.split(",")
        gems = []
        for i in range(len(a)):
            # look for gem_id-string in items
            if a[i].startswith("gem_id"):
                b, c = a[i].split("=")
                gems = c.split("/")
                # up to 3 possible gems
        new_gems = get_Possible_Gem_Combinations(len(gems))
        printLog("New Gems: " + str(new_gems))
        new_item = ""
        for n in range(len(a)):
            if not str(a[n]).startswith("gem") and not a[n] == "":
                new_item += "," + str(a[n])
        while new_gems:
            ins = new_item + ",gem_id=" + new_gems.pop()
            if slot == 1:
                if ins not in l_head:
                    l_head.insert(0, ins)
            if slot == 2:
                if ins not in l_neck:
                    l_neck.insert(0, ins)
            if slot == 3:
                if ins not in l_shoulders:
                    l_shoulders.insert(0, ins)
            if slot == 4:
                if ins not in l_chest:
                    l_chest.insert(0, ins)
            if slot == 5:
                if ins not in l_wrists:
                    l_wrists.insert(0, ins)
            if slot == 6:
                if ins not in l_hands:
                    l_hands.insert(0, ins)
            if slot == 7:
                if ins not in l_waist:
                    l_waist.insert(0, ins)
            if slot == 8:
                if ins not in l_legs:
                    l_legs.insert(0, ins)
            if slot == 9:
                if ins not in l_feet:
                    l_feet.insert(0, ins)
            if slot == 10:
                if ins not in l_finger1:
                    l_finger1.insert(0, ins)
            if slot == 11:
                if ins not in l_finger2:
                    l_finger2.insert(0, ins)
            if slot == 12:
                if ins not in l_trinket1:
                    l_trinket1.insert(0, ins)
            if slot == 13:
                if ins not in l_trinket2:
                    l_trinket2.insert(0, ins)
            # look for gems-string in items
            # todo implement
            if a[i].startswith("gems"):
                print(str(a[i]))


# add gems to the lists
# current template
## gems=150crit_150crit_150crit (not implemented yet)
## shoulder=,id=146666,bonus_id=3459/3530,gem_id=130220/130220/130220
def permutateGems():
    printLog("Permutating Gems")
    permutateGemsInSlotGearList(l_head, 1)
    permutateGemsInSlotGearList(l_neck, 2)
    permutateGemsInSlotGearList(l_shoulders, 3)
    permutateGemsInSlotGearList(l_chest, 4)
    permutateGemsInSlotGearList(l_wrists, 5)
    permutateGemsInSlotGearList(l_hands, 6)
    permutateGemsInSlotGearList(l_waist, 7)
    permutateGemsInSlotGearList(l_legs, 8)
    permutateGemsInSlotGearList(l_feet, 9)
    permutateGemsInSlotGearList(l_finger1, 10)
    permutateGemsInSlotGearList(l_finger2, 11)
    permutateGemsInSlotGearList(l_trinket1, 12)
    permutateGemsInSlotGearList(l_trinket2, 13)


# todo: add checks for missing headers, prio low
def permutate():
    # Read input.txt to init vars
    config = configparser.ConfigParser()
    config.read(inputFileName, encoding='utf-8-sig')
    profile = config['Profile']
    gear = config['Gear']

    # Read input.txt
    #   Profile
    global c_profilename
    c_profilename = profile['profilename']
    global c_profileid
    c_profileid = int(profile['profileid'])
    global c_class
    c_class = profile['class']
    global c_race
    c_race = profile['race']
    global c_level
    c_level = profile['level']
    global c_spec
    c_spec = profile['spec']
    global c_role
    c_role = profile['role']
    global c_position
    c_position = profile['position']
    global c_talents
    c_talents = profile['talents']
    global c_artifact
    c_artifact = profile['artifact']
    global c_crucible
    if config.has_option('Profile', 'crucible'):
        c_crucible = profile['crucible']
    else:
        c_crucible = ""
    global c_potion
    if config.has_option('Profile', 'potion'):
        c_potion = profile['potion']
    else:
        c_potion = ""
    global c_flask
    if config.has_option('Profile', 'flask'):
        c_flask = profile['flask']
    else:
        c_flask = ""
    global c_food
    if config.has_option('Profile', 'food'):
        c_food = profile['food']
    else:
        c_food = ""
    global c_augmentation
    if config.has_option('Profile', 'augmentation'):
        c_augmentation = profile['augmentation']
    else:
        c_augmentation = ""
    global c_other
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
    global l_head
    l_head = c_head.split('|')
    global l_neck
    l_neck = c_neck.split('|')
    global l_shoulders
    l_shoulders = c_shoulders.split('|')
    global l_back
    l_back = c_back.split('|')
    global l_chest
    l_chest = c_chest.split('|')
    global l_wrists
    l_wrists = c_wrists.split('|')
    global l_hands
    l_hands = c_hands.split('|')
    global l_waist
    l_waist = c_waist.split('|')
    global l_legs
    l_legs = c_legs.split('|')
    global l_feet
    l_feet = c_feet.split('|')
    global l_finger1
    l_finger1 = c_finger1.split('|')
    global l_finger2
    l_finger2 = c_finger2.split('|')
    global l_trinket1
    l_trinket1 = c_trinket1.split('|')
    global l_trinket2
    l_trinket2 = c_trinket2.split('|')
    global l_main_hand
    l_main_hand = c_main_hand.split('|')
    global l_off_hand
    l_off_hand = c_off_hand.split('|')
    global l_talents
    l_talents = c_talents.split('|')

    # permutate talents
    temp_talents = []
    if settings.enable_talent_permutation:
        for t in l_talents:
            for a in range(1, 4):
                for b in range(1, 4):
                    for c in range(1, 4):
                        for d in range(1, 4):
                            for e in range(1, 4):
                                for f in range(1, 4):
                                    for g in range(1, 4):
                                        temp_talent = ""
                                        if settings.permutate_row1:
                                            temp_talent = str(a)
                                        else:
                                            temp_talent = str(t[0])
                                        if settings.permutate_row2:
                                            temp_talent += str(b)
                                        else:
                                            temp_talent += str(t[1])
                                        if settings.permutate_row3:
                                            temp_talent += str(c)
                                        else:
                                            temp_talent += str(t[2])
                                        if settings.permutate_row4:
                                            temp_talent += str(d)
                                        else:
                                            temp_talent += str(t[3])
                                        if settings.permutate_row5:
                                            temp_talent += str(e)
                                        else:
                                            temp_talent += str(t[4])
                                        if settings.permutate_row6:
                                            temp_talent += str(f)
                                        else:
                                            temp_talent += str(t[5])
                                        if settings.permutate_row7:
                                            temp_talent += str(g)
                                        else:
                                            temp_talent += str(t[6])
                                        if temp_talent not in temp_talents:
                                            temp_talents.append(temp_talent)
        for t in temp_talents:
            if t not in l_talents:
                l_talents.append(t)

    # add gem-permutations
    if gemspermutation:
        permutateGems()

    # better handle rings and trinket-combinations
    # should now be deterministic, previous versions generated a random order and numbering

    for a in l_finger2:
        if l_finger1.count(a) == 0:
            l_finger1.append(a)

    for b in l_trinket2:
        if l_trinket1.count(b) == 0:
            l_trinket1.append(b)

    l_fingers = []
    l_trinkets = []

    for ring in l_finger1:
        for ring2 in l_finger1:
            if ring == ring2:
                continue
            else:
                if ring < ring2:
                    ring_combo = ring + "|" + ring2
                    if ring_combo not in l_fingers:
                        l_fingers.append(ring_combo)
                else:
                    ring_combo = ring2 + "|" + ring
                    if ring_combo not in l_fingers:
                        l_fingers.append(ring_combo)

    for trinket in l_trinket1:
        for trinket2 in l_trinket1:
            if trinket == trinket2:
                continue
            else:
                if trinket < trinket2:
                    trinket_combo = trinket + "|" + trinket2
                    if trinket_combo not in l_trinkets:
                        l_trinkets.append(trinket_combo)
                else:
                    trinket_combo = trinket2 + "|" + trinket
                    if trinket_combo not in l_trinkets:
                        l_trinkets.append(trinket_combo)

    # Make permutations
    global outputFile
    outputFile = open(outputFileName, 'w')
    global l_gear
    l_gear = ["head", "neck", "shoulders", "back", "chest", "wrists", "hands", "waist", "legs", "feet", "finger1",
              "finger2", "trinket1", "trinket2", "main_hand", "off_hand"]

    # changed according to merged fields
    global c_profilemaxid
    c_profilemaxid = len(l_head) * len(l_neck) * len(l_shoulders) * len(l_back) * len(l_chest) * len(l_wrists) * len(
        l_hands) * len(l_waist) * len(l_legs) * len(l_feet) * len(l_fingers) * len(l_trinkets) * len(l_main_hand) * len(
        l_off_hand) * len(l_talents)

    if not input("About " + str(c_profilemaxid) + " permutations will be generated. They will take approx. " + str(
            round(c_profilemaxid * 1.05, 2)) + " kB. Press y to continue, Enter to exit: ") == "y":
        printLog("User exit")
        sys.exit(0)

    printLog("Starting permutations : " + str(c_profilemaxid))
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
                                                    trinkets = l_trinkets[l].split('|')
                                                    l_gear[12] = trinkets[0]
                                                    l_gear[13] = trinkets[1]
                                                    for m in range(len(l_talents)):
                                                        c_talents = l_talents[m]
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

    printLog("Ending permutations. Valid: " + str(i_generatedProfiles))
    print("Generated permutations. Valid: " + str(i_generatedProfiles))
    outputFile.close()


def checkResultFiles(subdir, count=2):
    printLog("Checking Files in subdirectory: " + str(subdir))
    print("Checking Files in subdirectory: " + str(subdir))
    if os.path.exists(os.path.join(os.getcwd(), subdir)):
        empty = 0
        checkedFiles = 0
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), subdir)):
            for file in files:
                checkedFiles += 1
                if file.endswith(".sim"):
                    name = file[0:file.find(".")]
                    if not os.path.exists(os.path.join(os.getcwd(), subdir, name + ".result")):
                        printLog("Result file not found for .sim: " + str(subdir) + "/" + str(file))
                        empty += 1
                    elif os.stat(os.path.join(os.getcwd(), subdir, name + ".result")).st_size <= 0:
                        printLog("File is empty: " + str(subdir) + "/" + str(name))
                        empty += 1
    else:
        printLog("Error: Subdir does not exist: " + str(subdir))
        return False

    if checkedFiles == 0:
        printLog("No files in: " + str(subdir))
        print("No files in: " + str(subdir) + ", exiting")
        return False

    if empty > 0:
        printLog("Empty files in: " + str(subdir) + " -> " + str(empty))
        print("Warning: Empty files in: " + str(subdir) + " -> " + str(empty))

        if not settings.skip_questions:
            q = input("Do you want to resim the empty files? Warning: May not succeed! (Press q to quit): ")
            if q == "q":
                printLog("User exit")
                sys.exit(0)

        printLog(F"Resimming files: Count: {count}")
        if count > 0:
            count -= 1
            if splitter.resim(subdir):
                return checkResultFiles(subdir)
        else:
            printLog("Maximum number of retries reached, sth. is wrong; exiting")
            sys.exit(0)
    else:
        printLog("Checked all files in " + str(subdir) + " : Everything seems to be alright.")
        print("Checked all files in " + str(subdir) + " : Everything seems to be alright.")
        return True


def static_stage1():
    printLog("Entering static mode, stage1")
    # split into chunks of 50
    splitter.split(outputFileName, settings.splitting_size)
    # sim these with few iterations, can still take hours with huge permutation-sets; fewer than 100 is not advised
    splitter.sim(settings.subdir1, "iterations=" + str(iterations_firstpart), s, 1)
    static_stage2()


def static_stage2():
    printLog("Entering static mode, stage2")
    if checkResultFiles(settings.subdir1):
        # now grab the top 100 of these and put the profiles into the 2nd temp_dir
        splitter.grabBest(settings.default_top_n_stage2, settings.subdir1, settings.subdir2, outputFileName)
        # where they are simmed again, now with 1000 iterations
        splitter.sim(settings.subdir2, "iterations=" + str(iterations_secondpart), s, 1)
    else:
        printLog("Error, some result-files are empty in " + str(settings.subdir1))
        print("Error, some result-files are empty in " + str(settings.subdir1))
        sys.exit(1)
    static_stage3()


def static_stage3():
    printLog("Entering static mode, stage3")
    if checkResultFiles(settings.subdir2):
        # again, for a third time, get top 3 profiles and put them into subdir3
        splitter.grabBest(settings.default_top_n_stage3, settings.subdir2, settings.subdir3, outputFileName)
        # sim them finally with all options enabled; html-output remains in this folder
        splitter.sim(settings.subdir3, "iterations=" + str(iterations_thirdpart), s, 2)
    else:
        printLog("Error, some result-files are empty in " + str(settings.subdir1))
        print("Error, some result-files are empty in " + str(settings.subdir1))
        sys.exit(1)
    print("Simulation succeed!")


def dynamic_stage1():
    printLog("Entering dynamic mode, stage1")
    result_data = get_data(class_spec)
    print("Listing options:")
    print("Estimated calculation times based on your data:")
    print("Class/Spec: " + str(class_spec))
    print("Number of permutations to simulate: " + str(i_generatedProfiles))
    for current in range(len(result_data)):
        te = result_data[current][0]
        tp = round(float(result_data[current][2]), 2)
        est = round(float(result_data[current][2]) * i_generatedProfiles, 0)
        h = round(est / 3600, 1)

        print("(" + str(current) + "): Target Error: " + str(te) + "%: " + " Time/Profile: " + str(
            tp) + " sec => Est. calc. time: " + str(est) + " sec (~" + str(h) + " hours)")

    if settings.skip_questions:
        calc_choice = settings.auto_dynamic_stage1_target_error_table
    else:
        calc_choice = input("Please enter the type of calculation to perform (q to quit): ")
    if calc_choice == "q":
        printLog("Quitting application")
        sys.exit(0)
    if int(calc_choice) < len(result_data) and int(calc_choice) >= 0:
        printLog("Sim: Chosen Class/Spec: " + str(class_spec))
        printLog("Sim: Number of permutations: " + str(i_generatedProfiles))
        printLog("Sim: Chosen calculation:" + str(int(calc_choice)))

        te = result_data[int(calc_choice)][0]
        tp = round(float(result_data[int(calc_choice)][2]), 2)
        est = round(float(result_data[int(calc_choice)][2]) * i_generatedProfiles, 0)

        printLog(
            "Sim: (" + str(calc_choice) + "): Target Error: " + str(te) + "%:" + " Time/Profile: " + str(
                tp) + " => Est. calc. time: " + str(est) + " sec")
        time_all = round(est, 0)
        printLog("Estimated calculation time: " + str(time_all) + "")
        if not settings.skip_questions:
            if time_all > 43200:
                if input("Warning: This might take a *VERY* long time (>12h) (q to quit, Enter to continue: )") == "q":
                    print("Quitting application")
                    sys.exit(0)

        # split into chunks of n (max 100) to not destroy the hdd
        # todo: calculate dynamic amount of n
        splitter.split(outputFileName, settings.splitting_size)
        splitter.sim(settings.subdir1, "target_error=" + str(te), s, 1)

        # if the user chose a target_error which is lower than the default_one for the next step
        # he is given an option to either skip stage 2 or adjust the target_error
        if float(te) <= float(settings.default_target_error_stage2):
            printLog("Target_Error chosen in stage 1: " + str(te) + " <= Default_Target_Error for stage 2: " + str(
                settings.default_target_error_stage2) + "\n")
            print("Warning!\n")
            print("Target_Error chosen in stage 1: " + str(te) + " <= Default_Target_Error for stage 2: " + str(
                settings.default_target_error_stage2) + "\n")
            new_value = input(
                "Do you want to continue anyway (y), quit (q), skip to stage3 (s) or enter a new target_error for stage2 (n)?: ")
            printLog("User chose: " + str(new_value))
            if new_value == "q":
                sys.exit(0)
            if new_value == "n":
                target_error_secondpart = input("Enter new target_error (Format: 0.3): ")
                printLog("User entered target_error_secondpart: " + str(target_error_secondpart))
                dynamic_stage2(target_error_secondpart, str(te))
            if new_value == "s":
                dynamic_stage3(True, settings.default_target_error_stage3, str(te))
            if new_value == "y":
                dynamic_stage2(settings.default_target_error_stage2, str(te))
        else:
            pass
            dynamic_stage2(settings.default_target_error_stage2, str(te))


def dynamic_stage2(targeterror, targeterrorstage1):
    printLog("Entering dynamic mode, stage2")
    checkResultFiles(settings.subdir1)
    if settings.default_use_alternate_grabbing_method:
        splitter.grabBestAlternate(targeterrorstage1, settings.subdir1, settings.subdir2, outputFileName)
    else:
        # grabbing top 100 files
        splitter.grabBest(settings.default_top_n_stage2, settings.subdir1, settings.subdir2, outputFileName)
    # where they are simmed again, now with higher quality
    splitter.sim(settings.subdir2, "target_error=" + str(targeterror), s, 1)
    # if the user chose a target_error which is lower than the default_one for the next step
    # he is given an option to either skip stage 2 or adjust the target_error
    if float(target_error_secondpart) <= float(settings.default_target_error_stage3):
        printLog("Target_Error chosen in stage 2: " + str(
            targeterror) + " <= Default_Target_Error stage 3: " + str(
            settings.default_target_error_stage3))
        print("Warning!\n")
        printLog("Target_Error chosen in stage 2: " + str(
            targeterror) + " <= Default_Target_Error stage 3: " + str(
            settings.default_target_error_stage3))
        new_value = input(
            "Do you want to continue (y), quit (q) or enter a new target_error for stage3 (n)?: ")
        printLog("User chose: " + str(new_value))
        if new_value == "q":
            sys.exit(0)
        if new_value == "n":
            target_error_thirdpart = input("Enter new target_error (Format: 0.3): ")
            printLog("User entered target_error_thirdpart: " + str(target_error_thirdpart))
            dynamic_stage3(False, target_error_thirdpart, targeterror)
        if new_value == "y":
            dynamic_stage3(False, settings.default_target_error_stage3, targeterror)
    else:
        dynamic_stage3(False, settings.default_target_error_stage3, targeterror)


def dynamic_stage3(skipped, targeterror, targeterrorstage2):
    printLog("Entering dynamic mode, stage3")
    ok = False
    if skipped:
        ok = checkResultFiles(settings.subdir1)
    else:
        ok = checkResultFiles(settings.subdir2)
    if ok:
        printLog(".result-files ok, proceeding")
        # again, for a third time, get top 3 profiles and put them into subdir3
        if skipped:
            if settings.default_use_alternate_grabbing_method:
                splitter.grabBestAlternate(targeterrorstage2, settings.subdir1, settings.subdir3, outputFileName)
            else:
                splitter.grabBest(settings.default_top_n_stage3, settings.subdir1, settings.subdir3, outputFileName)
        else:
            if settings.default_use_alternate_grabbing_method:
                splitter.grabBestAlternate(targeterrorstage2, settings.subdir2, settings.subdir3, outputFileName)
            else:
                splitter.grabBest(settings.default_top_n_stage3, settings.subdir2, settings.subdir3, outputFileName)
        # sim them finally with all options enabled; html-output remains in subdir3, check cleanup for moving to results
        splitter.sim(settings.subdir3, "target_error=" + str(targeterror), s, 2)
    else:
        printLog("No valid .result-files found for stage3!")


def stage1():
    printLog("Entering Stage1")
    print("You have to choose one of the following modes for calculation:")
    print("1) Static mode uses a fixed amount, but less accurate calculations per profile (" + str(
        iterations_firstpart) + "," + str(iterations_secondpart) + "," + str(iterations_thirdpart) + ")")
    print("   It is however faster if simulating huge amounts of profiles")
    print(
        "2) Dynamic mode (preferred) lets you choose a specific 'correctness' of the calculation, but takes more time.")
    print(
        "   It uses the chosen target_error for the first part; in stage2 error lowers to " + str(
            target_error_secondpart) + " and " + str(
            target_error_thirdpart) + " for the final top " + str(settings.default_top_n_stage3))
    if settings.skip_questions:
        sim_mode = str(settings.auto_choose_static_or_dynamic)
    else:
        sim_mode = input("Please choose your mode (Enter to exit): ")
    if sim_mode == "1":
        static_stage1()
    elif sim_mode == "2":
        dynamic_stage1()
    else:
        print("Error, wrong mode: Stage1")
        printLog("Error, wrong mode: Stage1")
        sys.exit(0)


def stage2_restart():
    printLog("Restarting at Stage2")
    print("Restarting at Stage2")
    if not checkResultFiles(settings.subdir1):
        printLog("Error restarting at subdir: " + str(settings.subdir1))
        print("Error restarting at subdir: " + str(settings.subdir1))
    if settings.skip_questions:
        mode_choice = str(settings.auto_choose_static_or_dynamic)
    else:
        mode_choice = input("What mode did you use: Static (1) or dynamic (2): ")
    if mode_choice == "1":
        static_stage2()
    elif mode_choice == "2":
        if settings.skip_questions:
            new_te = settings.default_target_error_stage2
        else:
            new_te = input("Which target_error do you want to use for stage2: (Press enter for default: " + str(
                target_error_secondpart) + "):")
        if str(new_te) != str(target_error_secondpart) and splitter.user_targeterror != "0.0":
            dynamic_stage2(new_te, splitter.user_targeterror)
        else:
            dynamic_stage2(target_error_secondpart, splitter.user_targeterror)
    else:
        printLog("Error, wrong mode: Stage2_restart")
        print("Error, wrong mode: Stage2_restart")
        sys.exit(0)


def stage3_restart():
    printLog("Restarting at Stage3")
    print("Restarting at Stage3")
    if not checkResultFiles(settings.subdir2):
        printLog("Error restarting, some .result-files are empty in " + str(settings.subdir2))
        print("Error restarting at subdir: " + str(settings.subdir1))
    if settings.skip_questions:
        mode_choice = str(settings.auto_choose_static_or_dynamic)
    else:
        mode_choice = input("What mode did you use: Static (1) or dynamic (2): ")
    if mode_choice == "1":
        static_stage3()
    elif mode_choice == "2":
        if input("Did you skip stage 2? (y,n)") == "y":
            skip = True
        else:
            skip = False
        if settings.skip_questions:
            new_te = settings.default_target_error_stage3
        else:
            new_te = input("Which target_error do you want to use for stage3: (Press enter for default: " + str(
                target_error_thirdpart) + "):")
        if str(new_te) != str(target_error_thirdpart) and splitter.user_targeterror != "0.0":
            dynamic_stage3(skip, new_te, splitter.user_targeterror)
        else:
            dynamic_stage3(skip, target_error_thirdpart, splitter.user_targeterror)
    else:
        printLog("Error, wrong mode: Stage3_restart")
        print("Error, wrong mode: Stage3_restart")
        sys.exit(0)


def getStringForProfile():
    # example: "Uther_Soul_T19-2p_T20-2p_T21-2p"
    # scpout later adds a increment for multiple versions of this
    template = "%A%B%C%D%E%F"
    if namingData.get('Leg0') != "None":
        template = template.replace("%A", str(s.getAcronymForID(namingData.get('Leg0'))) + "_")
    else:
        template = template.replace("%A", "")

    if namingData.get('Leg1') != "None":
        template = template.replace("%B", str(s.getAcronymForID(namingData.get('Leg1'))) + "_")
    else:
        template = template.replace("%B", "")

    if namingData.get('Leg2') != "None":
        template = template.replace("%C", str(s.getAcronymForID(namingData.get('Leg2'))) + "_")
    else:
        template = template.replace("%C", "")

    if namingData.get("T19") != "None" and namingData.get("T19") != 0 and namingData.get(
            "T19") != 1 and namingData.get("T19") != 3 and namingData.get("T19") != 5:
        template = template.replace("%D", "T19-" + str(namingData.get('T19')) + "p_")
    else:
        template = template.replace("%D", "")

    if namingData.get("T20") != "None" and namingData.get("T20") != 0 and namingData.get(
            "T20") != 1 and namingData.get("T20") != 3 and namingData.get("T20") != 5:
        template = template.replace("%E", "T20-" + str(namingData.get('T20')) + "p_")
    else:
        template = template.replace("%E", "")

    if namingData.get("T21") != "None" and namingData.get("T21") != 0 and namingData.get(
            "T21") != 1 and namingData.get("T21") != 3 and namingData.get("T21") != 5:
        template = template.replace("%F", "T21-" + str(namingData.get('T21')) + "p_")
    else:
        template = template.replace("%F", "")

    return template


def checkinterpreter():
    maj, min, mic, rel, ser = sys.version_info
    if maj != 3:
        return False
    if min < 6:
        return False
    return True


# just a workaround for skipping generation of out.simc
def getClassFromInput():
    config = configparser.ConfigParser()
    config.read(inputFileName, encoding='utf-8-sig')
    profile = config['Profile']
    return profile['class']


# just set things in the data-file, has to be accessed later in splitter.py
def setClassSpecData():
    s.c_class = c_class
    s.c_spec = c_spec


########################
#### Program Start ######
#########################
sys.stderr = open(errorFileName, 'w')
logFile = open(logFileName, 'w')

# check version of python-interpreter running the script
if not checkinterpreter():
    printLog("Python-Version too old: You are running Python " + str(sys.version))
    print("Python-Version too old: You are running Python " + str(sys.version))
    printLog("Please install at least Python-Version 3.6.x")
    print("Please install at least Python-Version 3.6.x")
    sys.exit(0)

handleCommandLine()
validateSettings()

# can always be rerun since it is now deterministic
if s_stage == "stage1" or s_stage == "":
    permutate()
    outputGenerated = True
else:
    if input(F"Do you want to generate {outputFileName} again? Press y to regenerate: ") == "y":
        permutate()
        outputGenerated = True
    else:
        outputGenerated = False

setClassSpecData()

if not settings.skip_questions:
    if i_generatedProfiles > 50000:
        if input(
                "-----> Beware: Computation with Simcraft might take a VERY long time with this amount of profiles! <----- (Press Enter to continue, q to quit)") == "q":
            printLog("Program exit by user")
            sys.exit(0)

if outputGenerated:
    if i_generatedProfiles == 0:
        print("No valid combinations found. Please check settings.py and your simpermut-export.")
        sys.exit(1)

if b_simcraft_enabled:
    if outputGenerated:
        class_spec = s.getClassSpec()
    else:
        class_spec = getClassFromInput()

    if s_stage == "":
        s_stage = settings.default_sim_start_stage

    if s_stage == "stage1":
        stage1()
    if s_stage == "stage2":
        if restart:
            if input("Do you want to restart stage 2?: (Enter to proceed, q to quit): ") == "q":
                printLog("Restart aborted by user")
            else:
                stage2_restart()
    if s_stage == "stage3":
        if input("Do you want to restart stage 3?: (Enter to proceed, q to quit): ") == "q":
            printLog("Restart aborted by user")
        else:
            stage3_restart()

if settings.clean_up_after_step3:
    cleanup()
logFile.close()
