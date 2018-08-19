import sys
import warnings

def getClassSpec(c_class, c_spec):
    b_heal = False
    b_tank = False
    if c_class == "deathknight":
        if c_spec == "frost":
            class_spec = "Frost Death Knight"
        elif c_spec == "unholy":
            class_spec = "Unholy Death Knight"
        elif c_spec == "blood":
            class_spec = "Blood Death Knight"
            b_tank = True
    elif c_class == "demonhunter":
        if c_spec == "havoc":
            class_spec = "Havoc Demon Hunter"
        elif c_spec == "vengeance":
            class_spec = "Vengeance Demon Hunter"
            b_tank = True
    elif c_class == "druid":
        if c_spec == "balance":
            class_spec = "Balance Druid"
        elif c_spec == "feral":
            class_spec = "Feral Druid"
        elif c_spec == "guardian":
            class_spec = "Guardian Druid"
            b_tank = True
        elif c_spec == "restoration":
            class_spec = "Restoration Druid"
            b_heal = True
    elif c_class == "hunter":
        if c_spec == "beast_mastery":
            class_spec = "Beast Mastery Hunter"
        elif c_spec == "survival":
            class_spec = "Survival Hunter"
        elif c_spec == "marksmanship":
            class_spec = "Marksmanship Hunter"
    elif c_class == "mage":
        if c_spec == "frost":
            class_spec = "Frost Mage"
        elif c_spec == "arcane":
            class_spec = "Arcane Mage"
        elif c_spec == "fire":
            class_spec = "Fire Mage"
    elif c_class == "priest":
        if c_spec == "shadow":
            class_spec = "Shadow Priest"
        elif c_spec == "diszipline":
            class_spec = "Diszipline Priest"
            b_heal = True
        elif c_spec == "holy":
            class_spec = "Holy Priest"
            b_heal = True
    elif c_class == "paladin":
        if c_spec == "retribution":
            class_spec = "Retribution Paladin"
        elif c_spec == "holy":
            class_spec = "Holy Paladin"
            b_heal = True
        elif c_spec == "protection":
            class_spec = "Protection Paladin"
            b_tank = True
    elif c_class == "monk":
        if c_spec == "windwalker":
            class_spec = "Windwalker Monk"
        elif c_spec == "brewmaster":
            class_spec = "Brewmaster Monk"
            b_tank = True
        elif c_spec == "mistweaver":
            class_spec = "Mistweaver Monk"
            b_heal = True
    elif c_class == "shaman":
        if c_spec == "enhancement":
            class_spec = "Enhancement Shaman"
        elif c_spec == "elemental":
            class_spec = "Elemental Shaman"
        elif c_spec == "restoration":
            class_spec = "Restoration Shaman"
            b_heal = True
    elif c_class == "rogue":
        if c_spec == "subtlety":
            class_spec = "Subtlety Rogue"
        elif c_spec == "outlaw":
            class_spec = "Outlaw Rogue"
        elif c_spec == "assassination":
            class_spec = "Assassination Rogue"
    elif c_class == "warrior":
        if c_spec == "fury":
            class_spec = "Fury Warrior"
        elif c_spec == "arms":
            class_spec = "Arms Warrior"
        elif c_spec == "protection":
            class_spec = "Protection Warrior"
            b_tank = True
    elif c_class == "warlock":
        if c_spec == "affliction":
            class_spec = "Affliction Warlock"
        elif c_spec == "demonology":
            class_spec = "Demonology Warlock"
        elif c_spec == "destruction":
            class_spec = "Destruction Warlock"
    else:
        raise ValueError("Unsupported class/spec-combination: " + str(c_class) + " - " + str(c_spec) + "\n")
        sys.exit(1)
    if b_tank or b_heal:
        warnings.warn("You are trying to use a tank or heal-spec! Be aware that this may lead to no or incomplete "
                      "results!\n You may need to generate a new Analyzer.json using Analyzer.py which includes a "
                      "profile with your spec.")
    return class_spec


def getRole(c_class, c_spec):
    if c_class == "deathknight":
        return "strattack"
    elif c_class == "demonhunter":
        return "agiattack"
    elif c_class == "druid":
        if c_spec == "balance":
            return "spell"
        elif c_spec == "feral":
            return "agiattack"
        elif c_spec == "guardian":
            return "agiattack"
        elif c_spec == "restoration":
            return "spell"
    elif c_class == "hunter":
        return "agiattack"
    elif c_class == "mage":
        return "spell"
    elif c_class == "priest":
        return "spell"
    elif c_class == "paladin":
        if c_spec == "retribution":
            return "strattack"
        elif c_spec == "holy":
            return "spell"
        elif c_spec == "protection":
            return "strattack"
    elif c_class == "monk":
        if c_spec == "windwalker":
            return "agiattack"
        elif c_spec == "brewmaster":
            return "agiattack"
        elif c_spec == "mistweaver":
            return "spell"
    elif c_class == "shaman":
        if c_spec == "enhancement":
            return "agiattack"
        elif c_spec == "elemental":
            return "spell"
        elif c_spec == "restoration":
            return "spell"
    elif c_class == "rogue":
        return "agiattack"
    elif c_class == "warrior":
        if c_spec == "fury":
            return "strattack"
        elif c_spec == "arms":
            return "strattack"
        elif c_spec == "protection":
            return "strattack"
    elif c_class == "warlock":
        return "spell"
