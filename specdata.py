import sys
import warnings


def getAcronymForID(item_id):
    # TODO: convert this to a big dict and remove all these elif ;)
    # shared
    if item_id == "154172":
        return "Aman"
    elif item_id == "133976":
        return "Cind"
    elif item_id == "137015":
        return "Eko"
    elif item_id == "146669":
        return "Sentinel"
    elif item_id == "132455":
        return "Norgannon"
    elif item_id == "146666":
        return "Celumbra"
    elif item_id == "132466":
        return "Roots"
    elif item_id == "146668":
        return "Perch"
    elif item_id == "132443":
        return "Aggramar"
    elif item_id == "146667":
        return "Rethus"
    elif item_id == "132444":
        return "Prydaz"
    elif item_id == "152626":
        return "Insignia"
    elif item_id == "132452":
        return "Sephuz"
    elif item_id == "144249":
        return "AHR"
    elif item_id == "144258":
        return "Velen"
    elif item_id == "144259":
        return "KJ"

    # demonhunter
    elif item_id == "137014":
        return "Achor"
    elif item_id == "137022":
        return "Lor"
    elif item_id == "137061":
        return "Raddon"
    elif item_id == "137071":
        return "Rune"
    elif item_id == "137090":
        return "Bio"
    elif item_id == "137091":
        return "Defile"
    elif item_id == "138949":
        return "Kirel"
    elif item_id == "144279":
        return "Grandeur"
    elif item_id == "144292":
        return "Spirit"
    elif item_id == "151799":
        return "Oblivion"
    elif item_id == "137038":
        return "Anger"
    elif item_id == "138854":
        return "Fragment"
    elif item_id == "151639":
        return "Soul"
    elif item_id == "151798":
        return "Chaos"

    # druid
    elif item_id == "137023":
        return "POE"
    elif item_id == "137024":
        return "Fel"
    elif item_id == "137026":
        return "EOI"
    elif item_id == "137025":
        return "Sky"
    elif item_id == "137056":
        return "Luffa"
    elif item_id == "137062":
        return "ED"
    elif item_id == "137067":
        return "Elize"
    elif item_id == "137072":
        return "Aman(Ring)"
    elif item_id == "137078":
        return "Titan"
    elif item_id == "137092":
        return "Oneth"
    elif item_id == "137095":
        return "Edraith"
    elif item_id == "137096":
        return "Petri"
    elif item_id == "137094":
        return "Wild"
    elif item_id == "144242":
        return "Xonis"
    elif item_id == "144295":
        return "LATC"
    elif item_id == "144354":
        return "Fiery"
    elif item_id == "144432":
        return "Oak"
    elif item_id == "151783":
        return "Karma"
    elif item_id == "151801":
        return "Behemoth"
    elif item_id == "137039":
        return "IFE"
    elif item_id == "137040":
        return "Chatoyant"
    elif item_id == "137041":
        return "Dual"
    elif item_id == "137042":
        return "Tearstone"
    elif item_id == "151636":
        return "Soul"

    # monk
    elif item_id == "137016":
        return "Sal"
    elif item_id == "137027":
        return "Fire"
    elif item_id == "137028":
        return "Eithas"
    elif item_id == "137029":
        return "Kat"
    elif item_id == "137057":
        return "Touch"
    elif item_id == "137063":
        return "FO"
    elif item_id == "137068":
        return "Flame"
    elif item_id == "137073":
        return "Unison"
    elif item_id == "137079":
        return "Gai"
    elif item_id == "137097":
        return "Horn"
    elif item_id == "138879":
        return "Ovyds"
    elif item_id == "144239":
        return "Capa"
    elif item_id == "144277":
        return "Anvil"
    elif item_id == "144340":
        return "Rins"
    elif item_id == "151788":
        return "Stout"
    elif item_id == "151811":
        return "Wind"
    elif item_id == "137044":
        return "Jewel"
    elif item_id == "137045":
        return "Eye"
    elif item_id == "137220":
        return "March"
    elif item_id == "151643":
        return "Soul"

    # rogue
    elif item_id == "137030":
        return "Dusk"
    elif item_id == "137031":
        return "Thrax"
    elif item_id == "137032":
        return "Satyr"
    elif item_id == "137069":
        return "Val"
    elif item_id == "137098":
        return "Zoldyck"
    elif item_id == "137099":
        return "Greenskin"
    elif item_id == "137100":
        return "Giants"
    elif item_id == "141321":
        return "Shiv"
    elif item_id == "144236":
        return "Cloak"
    elif item_id == "151815":
        return "Crown"
    elif item_id == "151818":
        return "Dead"
    elif item_id == "137049":
        return "Insignia"
    elif item_id == "150936":
        return "Soul"

    # mage
    elif item_id == "132406":
        return "Sun"
    elif item_id == "132411":
        return "Vashj"
    elif item_id == "132413":
        return "Rhonin"
    elif item_id == "132442":
        return "Cord"
    elif item_id == "132451":
        return "Kilt"
    elif item_id == "132454":
        return "Koralon"
    elif item_id == "132863":
        return "Darcklis"
    elif item_id == "133970":
        return "Zannesu"
    elif item_id == "133977":
        return "Belovir"
    elif item_id == "138140":
        return "Mag"
    elif item_id == "144260":
        return "Ice"
    elif item_id == "144274":
        return "Gravity"
    elif item_id == "144355":
        return "Pyrotex"
    elif item_id == "151808":
        return "Kirin"
    elif item_id == "151809":
        return "Core"
    elif item_id == "151810":
        return "Sindra"
    elif item_id == "132410":
        return "Shard"
    elif item_id == "151642":
        return "Soul"

    # priest
    elif item_id == "132409":
        return "Anunds"
    elif item_id == "132436":
        return "Skjoldr"
    elif item_id == "132437":
        return "Sharaz"
    elif item_id == "132445":
        return "Almaiesh"
    elif item_id == "132447":
        return "Anjuna"
    elif item_id == "132450":
        return "Muzes"
    elif item_id == "132461":
        return "Xalan"
    elif item_id == "132861":
        return "Estel"
    elif item_id == "132864":
        return "Mangazas"
    elif item_id == "133800":
        return "Maiev"
    elif item_id == "133971":
        return "Zenkaram"
    elif item_id == "144244":
        return "Xiraff"
    elif item_id == "144247":
        return "Rammal"
    elif item_id == "151786":
        return "Hallation"
    elif item_id == "151814":
        return "Heart"
    elif item_id == "151787":
        return "Lady"
    elif item_id == "132449":
        return "Phyrix"
    elif item_id == "133973":
        return "Twins"
    elif item_id == "151646":
        return "Soul"
    elif item_id == "137276":
        return "Nero"

    # warlock
    elif item_id == "132357":
        return "Pillar"
    elif item_id == "132374":
        return "Kazzak"
    elif item_id == "132379":
        return "Sindorei"
    elif item_id == "132381":
        return "Stretens"
    elif item_id == "132393":
        return "Ritual"
    elif item_id == "132394":
        return "Hood"
    elif item_id == "132407":
        return "Magi"
    elif item_id == "132456":
        return "FoS"
    elif item_id == "132457":
        return "Cord"
    elif item_id == "144369":
        return "Lost"
    elif item_id == "144385":
        return "Wakener"
    elif item_id == "151821":
        return "Harvest"
    elif item_id == "132369":
        return "Wilfred"
    elif item_id == "132378":
        return "Sacro"
    elif item_id == "132460":
        return "Alythess"
    elif item_id == "151649":
        return "Soul"

    # hunter
    elif item_id == "137033":
        return "Ullr"
    elif item_id == "137034":
        return "Nesing"
    elif item_id == "137064":
        return "Voodoo"
    elif item_id == "137080":
        return "Roar"
    elif item_id == "137081":
        return "Sentinel"
    elif item_id == "137082":
        return "Helbrine"
    elif item_id == "137101":
        return "Call"
    elif item_id == "137227":
        return "Qapla"
    elif item_id == "141353":
        return "Cap"
    elif item_id == "144303":
        return "Gyro"
    elif item_id == "144326":
        return "Mantle"
    elif item_id == "144361":
        return "Butcher"
    elif item_id == "151805":
        return "Parsel"
    elif item_id == "137043":
        return "Frizzo"
    elif item_id == "137055":
        return "Zevrim"
    elif item_id == "137382":
        return "Apex"
    elif item_id == "151641":
        return "Soul"

    # shaman
    elif item_id == "137058":
        return "Tide"
    elif item_id == "137074":
        return "Echoes"
    elif item_id == "137083":
        return "Girdle"
    elif item_id == "137084":
        return "Akainus"
    elif item_id == "137085":
        return "Nazjatar"
    elif item_id == "137102":
        return "AlAkir"
    elif item_id == "137103":
        return "Tempest"
    elif item_id == "137104":
        return "Nobundo"
    elif item_id == "137616":
        return "Emalon"
    elif item_id == "138117":
        return "Journey"
    elif item_id == "143732":
        return "Reminder"
    elif item_id == "151785":
        return "Deep"
    elif item_id == "151819":
        return "Heart"
    elif item_id == "137035":
        return "Deceiver"
    elif item_id == "137036":
        return "Rebalancer"
    elif item_id == "137050":
        return "Eye"
    elif item_id == "137051":
        return "Jonat"
    elif item_id == "151647":
        return "Soul"

    # dk
    elif item_id == "132365":
        return "Bryndaor"
    elif item_id == "132366":
        return "Koltiras"
    elif item_id == "132367":
        return "Gorefiend"
    elif item_id == "132441":
        return "Draugr"
    elif item_id == "132448":
        return "Fourth"
    elif item_id == "132453":
        return "Rattlegore"
    elif item_id == "132458":
        return "Toravon"
    elif item_id == "132459":
        return "Martyr"
    elif item_id == "137075":
        return "Taktheritrix"
    elif item_id == "144280":
        return "March"
    elif item_id == "144281":
        return "Skull"
    elif item_id == "144293":
        return "CCC"
    elif item_id == "151795":
        return "Soulflayer"
    elif item_id == "151796":
        return "Heart"
    elif item_id == "133974":
        return "Lament"
    elif item_id == "137037":
        return "Uvanimor"
    elif item_id == "137223":
        return "Necro"
    elif item_id == "151640":
        return "Deathlord"

    # warrior
    elif item_id == "137060":
        return "Archavon"
    elif item_id == "137077":
        return "Weight"
    elif item_id == "137087":
        return "Najentus"
    elif item_id == "137088":
        return "Ceann"
    elif item_id == "137089":
        return "Vigor"
    elif item_id == "137107":
        return "Mannoroth"
    elif item_id == "137108":
        return "Kakushan"
    elif item_id == "143728":
        return "Strata"
    elif item_id == "151822":
        return "Ararat"
    elif item_id == "151823":
        return "Eye"
    elif item_id == "151824":
        return "Berserker"
    elif item_id == "137052":
        return "Ayala"
    elif item_id == "137054":
        return "Walls"
    elif item_id == "151650":
        return "Soul"

    # paladin
    elif item_id == "137017":
        return "Valkyr"
    elif item_id == "137059":
        return "Tyrs"
    elif item_id == "137065":
        return "Gaze"
    elif item_id == "137070":
        return "Tyelca"
    elif item_id == "137076":
        return "Obsidian"
    elif item_id == "137086":
        return "Thrayns"
    elif item_id == "137105":
        return "Uther"
    elif item_id == "140846":
        return "Aegisjalmur"
    elif item_id == "144275":
        return "Saruan"
    elif item_id == "144358":
        return "Ashes"
    elif item_id == "151782":
        return "Tower"
    elif item_id == "151812":
        return "Pillars"
    elif item_id == "151813":
        return "Inquisitor"
    elif item_id == "137046":
        return "Ilterendi"
    elif item_id == "137047":
        return "Heathcliff"
    elif item_id == "137048":
        return "Liadrin"
    elif item_id == "151644":
        return "Soul"


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
