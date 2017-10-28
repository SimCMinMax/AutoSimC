import sys


class specdata():
    global c_spec, c_class

    def getAcronymForID(self, id):
        # shared
        if id == "154172":
            return "Aman"
        elif id == "133976":
            return "Cind"
        elif id == "137015":
            return "Eko"
        elif id == "146669":
            return "Sentinel"
        elif id == "132455":
            return "Norgannon"
        elif id == "146666":
            return "Celumbra"
        elif id == "132466":
            return "Roots"
        elif id == "146668":
            return "Perch"
        elif id == "132443":
            return "Aggramar"
        elif id == "146667":
            return "Rethus"
        elif id == "132444":
            return "Prydaz"
        elif id == "152626":
            return "Insignia"
        elif id == "132452":
            return "Sephuz"
        elif id == "144249":
            return "AHR"
        elif id == "144258":
            return "Velen"
        elif id == "144259":
            return "KJ"

        # demonhunter
        elif id == "137014":
            return "Achor"
        elif id == "137022":
            return "Lor"
        elif id == "137061":
            return "Raddon"
        elif id == "137071":
            return "Rune"
        elif id == "137090":
            return "Bio"
        elif id == "137091":
            return "Defile"
        elif id == "138949":
            return "Kirel"
        elif id == "144279":
            return "Grandeur"
        elif id == "144292":
            return "Spirit"
        elif id == "151799":
            return "Oblivion"
        elif id == "137038":
            return "Anger"
        elif id == "138854":
            return "Fragment"
        elif id == "151639":
            return "Soul"
        elif id == "151798":
            return "Chaos"

        # druid
        elif id == "137023":
            return "POE"
        elif id == "137024":
            return "Fel"
        elif id == "137026":
            return "EOI"
        elif id == "137025":
            return "Sky"
        elif id == "137056":
            return "Luffa"
        elif id == "137062":
            return "ED"
        elif id == "137067":
            return "Elize"
        elif id == "137072":
            return "Aman(Ring)"
        elif id == "137078":
            return "Titan"
        elif id == "137092":
            return "Oneth"
        elif id == "137095":
            return "Edraith"
        elif id == "137096":
            return "Petri"
        elif id == "137094":
            return "Wild"
        elif id == "144242":
            return "Xonis"
        elif id == "144295":
            return "LATC"
        elif id == "144354":
            return "Fiery"
        elif id == "144432":
            return "Oak"
        elif id == "151783":
            return "Karma"
        elif id == "151801":
            return "Behemoth"
        elif id == "137039":
            return "IFE"
        elif id == "137040":
            return "Chatoyant"
        elif id == "137041":
            return "Dual"
        elif id == "137042":
            return "Tearstone"
        elif id == "151636":
            return "Soul"

        # monk
        elif id == "137016":
            return "Sal"
        elif id == "137027":
            return "Fire"
        elif id == "137028":
            return "Eithas"
        elif id == "137029":
            return "Kat"
        elif id == "137057":
            return "Touch"
        elif id == "137063":
            return "FO"
        elif id == "137068":
            return "Flame"
        elif id == "137073":
            return "Unison"
        elif id == "137079":
            return "Gai"
        elif id == "137097":
            return "Horn"
        elif id == "138879":
            return "Ovyds"
        elif id == "144239":
            return "Capa"
        elif id == "144277":
            return "Anvil"
        elif id == "144340":
            return "Rins"
        elif id == "151788":
            return "Stout"
        elif id == "151811":
            return "Wind"
        elif id == "137044":
            return "Jewel"
        elif id == "137045":
            return "Eye"
        elif id == "137220":
            return "March"
        elif id == "151643":
            return "Soul"

        # rogue
        elif id == "137030":
            return "Dusk"
        elif id == "137031":
            return "Thrax"
        elif id == "137032":
            return "Satyr"
        elif id == "137069":
            return "Val"
        elif id == "137098":
            return "Zoldyck"
        elif id == "137099":
            return "Greenskin"
        elif id == "137100":
            return "Giants"
        elif id == "141321":
            return "Shiv"
        elif id == "144236":
            return "Cloak"
        elif id == "151815":
            return "Crown"
        elif id == "151818":
            return "Dead"
        elif id == "137049":
            return "Insignia"
        elif id == "150936":
            return "Soul"

        # mage
        elif id == "132406":
            return "Sun"
        elif id == "132411":
            return "Vashj"
        elif id == "132413":
            return "Rhonin"
        elif id == "132442":
            return "Cord"
        elif id == "132451":
            return "Kilt"
        elif id == "132454":
            return "Koralon"
        elif id == "132863":
            return "Darcklis"
        elif id == "133970":
            return "Zannesu"
        elif id == "133977":
            return "Belovir"
        elif id == "138140":
            return "Mag"
        elif id == "144260":
            return "Ice"
        elif id == "144274":
            return "Gravity"
        elif id == "144355":
            return "Pyrotex"
        elif id == "151808":
            return "Kirin"
        elif id == "151809":
            return "Core"
        elif id == "151810":
            return "Sindra"
        elif id == "132410":
            return "Shard"
        elif id == "151642":
            return "Soul"

        # priest
        elif id == "132409":
            return "Anunds"
        elif id == "132436":
            return "Skjoldr"
        elif id == "132437":
            return "Sharaz"
        elif id == "132445":
            return "Almaiesh"
        elif id == "132447":
            return "Anjuna"
        elif id == "132450":
            return "Muzes"
        elif id == "132461":
            return "Xalan"
        elif id == "132861":
            return "Estel"
        elif id == "132864":
            return "Mangazas"
        elif id == "133800":
            return "Maiev"
        elif id == "133971":
            return "Zenkaram"
        elif id == "144244":
            return "Xiraff"
        elif id == "144247":
            return "Rammal"
        elif id == "151786":
            return "Hallation"
        elif id == "151814":
            return "Heart"
        elif id == "151787":
            return "Lady"
        elif id == "132449":
            return "Phyrix"
        elif id == "133973":
            return "Twins"
        elif id == "151646":
            return "Soul"
        elif id == "137276":
            return "Nero"

        # warlock
        elif id == "132357":
            return "Pillar"
        elif id == "132374":
            return "Kazzak"
        elif id == "132379":
            return "Sindorei"
        elif id == "132381":
            return "Stretens"
        elif id == "132393":
            return "Ritual"
        elif id == "132394":
            return "Hood"
        elif id == "132407":
            return "Magi"
        elif id == "132456":
            return "FoS"
        elif id == "132457":
            return "Cord"
        elif id == "144369":
            return "Lost"
        elif id == "144385":
            return "Wakener"
        elif id == "151821":
            return "Harvest"
        elif id == "132369":
            return "Wilfred"
        elif id == "132378":
            return "Sacro"
        elif id == "132460":
            return "Alythess"
        elif id == "151649":
            return "Soul"


        # hunter
        elif id == "137033":
            return "Ullr"
        elif id == "137034":
            return "Nesing"
        elif id == "137064":
            return "Voodoo"
        elif id == "137080":
            return "Roar"
        elif id == "137081":
            return "Sentinel"
        elif id == "137082":
            return "Helbrine"
        elif id == "137101":
            return "Call"
        elif id == "137227":
            return "Qapla"
        elif id == "141353":
            return "Cap"
        elif id == "144303":
            return "Gyro"
        elif id == "144326":
            return "Mantle"
        elif id == "144361":
            return "Butcher"
        elif id == "151805":
            return "Parsel"
        elif id == "137043":
            return "Frizzo"
        elif id == "137055":
            return "Zevrim"
        elif id == "137382":
            return "Apex"
        elif id == "151641":
            return "Soul"

        # shaman
        elif id == "137058":
            return "Tide"
        elif id == "137074":
            return "Echoes"
        elif id == "137083":
            return "Girdle"
        elif id == "137084":
            return "Akainus"
        elif id == "137085":
            return "Nazjatar"
        elif id == "137102":
            return "AlAkir"
        elif id == "137103":
            return "Tempest"
        elif id == "137104":
            return "Nobundo"
        elif id == "137616":
            return "Emalon"
        elif id == "138117":
            return "Journey"
        elif id == "143732":
            return "Reminder"
        elif id == "151785":
            return "Deep"
        elif id == "151819":
            return "Heart"
        elif id == "137035":
            return "Deceiver"
        elif id == "137036":
            return "Rebalancer"
        elif id == "137050":
            return "Eye"
        elif id == "137051":
            return "Jonat"
        elif id == "151647":
            return "Soul"


        # dk
        elif id == "132365":
            return "Bryndaor"
        elif id == "132366":
            return "Koltiras"
        elif id == "132367":
            return "Gorefiend"
        elif id == "132441":
            return "Draugr"
        elif id == "132448":
            return "Fourth"
        elif id == "132453":
            return "Rattlegore"
        elif id == "132458":
            return "Toravon"
        elif id == "132459":
            return "Martyr"
        elif id == "137075":
            return "Taktheritrix"
        elif id == "144280":
            return "March"
        elif id == "144281":
            return "Skull"
        elif id == "144293":
            return "CCC"
        elif id == "151795":
            return "Soulflayer"
        elif id == "151796":
            return "Heart"
        elif id == "133974":
            return "Lament"
        elif id == "137037":
            return "Uvanimor"
        elif id == "137223":
            return "Necro"
        elif id == "151640":
            return "Deathlord"

        # warrior
        elif id == "137060":
            return "Archavon"
        elif id == "137077":
            return "Weight"
        elif id == "137087":
            return "Najentus"
        elif id == "137088":
            return "Ceann"
        elif id == "137089":
            return "Vigor"
        elif id == "137107":
            return "Mannoroth"
        elif id == "137108":
            return "Kakushan"
        elif id == "143728":
            return "Strata"
        elif id == "151822":
            return "Ararat"
        elif id == "151823":
            return "Eye"
        elif id == "151824":
            return "Berserker"
        elif id == "137052":
            return "Ayala"
        elif id == "137054":
            return "Walls"
        elif id == "151650":
            return "Soul"

        # paladin
        elif id == "137017":
            return "Valkyr"
        elif id == "137059":
            return "Tyrs"
        elif id == "137065":
            return "Gaze"
        elif id == "137070":
            return "Tyelca"
        elif id == "137076":
            return "Obsidian"
        elif id == "137086":
            return "Thrayns"
        elif id == "137105":
            return "Uther"
        elif id == "140846":
            return "Aegisjalmur"
        elif id == "144275":
            return "Saruan"
        elif id == "144358":
            return "Ashes"
        elif id == "151782":
            return "Tower"
        elif id == "151812":
            return "Pillars"
        elif id == "151813":
            return "Inquisitor"
        elif id == "137046":
            return "Ilterendi"
        elif id == "137047":
            return "Heathcliff"
        elif id == "137048":
            return "Liadrin"
        elif id == "151644":
            return "Soul"

    def getClassSpec(self):
        b_heal = False
        b_tank = False
        if self.c_class == "deathknight":
            if self.c_spec == "frost":
                class_spec = "Frost Death Knight"
            elif self.c_spec == "unholy":
                class_spec = "Unholy Death Knight"
            elif self.c_spec == "blood":
                class_spec = "Blood Death Knight"
                b_tank = True
        elif self.c_class == "demonhunter":
            if self.c_spec == "havoc":
                class_spec = "Havoc Demon Hunter"
            elif self.c_spec == "vengeance":
                class_spec = "Vengeance Demon Hunter"
                b_tank = True
        elif self.c_class == "druid":
            if self.c_spec == "balance":
                class_spec = "Balance Druid"
            elif self.c_spec == "feral":
                class_spec = "Feral Druid"
            elif self.c_spec == "guardian":
                class_spec = "Guardian Druid"
                b_tank = True
            elif self.c_spec == "restoration":
                class_spec = "Restoration Druid"
                b_heal = True
        elif self.c_class == "hunter":
            if self.c_spec == "beast_mastery":
                class_spec = "Beast Mastery Hunter"
            elif self.c_spec == "survival":
                class_spec = "Survival Hunter"
            elif self.c_spec == "marksmanship":
                class_spec = "Marksmanship Hunter"
        elif self.c_class == "mage":
            if self.c_spec == "frost":
                class_spec = "Frost Mage"
            elif self.c_spec == "arcane":
                class_spec = "Arcane Mage"
            elif self.c_spec == "fire":
                class_spec = "Fire Mage"
        elif self.c_class == "priest":
            if self.c_spec == "shadow":
                class_spec = "Shadow Priest"
            elif self.c_spec == "diszipline":
                class_spec = "Diszipline Priest"
                b_heal = True
            elif self.c_spec == "holy":
                class_spec = "Holy Priest"
                b_heal = True
        elif self.c_class == "paladin":
            if self.c_spec == "retribution":
                class_spec = "Retribution Paladin"
            elif self.c_spec == "holy":
                class_spec = "Holy Paladin"
                b_heal = True
            elif self.c_spec == "protection":
                class_spec = "Protection Paladin"
                b_tank = True
        elif self.c_class == "monk":
            if self.c_spec == "windwalker":
                class_spec = "Windwalker Monk"
            elif self.c_spec == "brewmaster":
                class_spec = "Brewmaster Monk"
                b_tank = True
            elif self.c_spec == "mistweaver":
                class_spec = "Mistweaver Monk"
                b_heal = True
        elif self.c_class == "shaman":
            if self.c_spec == "enhancement":
                class_spec = "Enhancement Shaman"
            elif self.c_spec == "elemental":
                class_spec = "Elemental Shaman"
            elif self.c_spec == "restoration":
                class_spec = "Restoration Shaman"
                b_heal = True
        elif self.c_class == "rogue":
            if self.c_spec == "subtlety":
                class_spec = "Subtlety Rogue"
            elif self.c_spec == "outlaw":
                class_spec = "Outlaw Rogue"
            elif self.c_spec == "assassination":
                class_spec = "Assassination Rogue"
        elif self.c_class == "warrior":
            if self.c_spec == "fury":
                class_spec = "Fury Warrior"
            elif self.c_spec == "arms":
                class_spec = "Arms Warrior"
            elif self.c_spec == "protection":
                class_spec = "Protection Warrior"
                b_tank = True
        elif self.c_class == "warlock":
            if self.c_spec == "affliction":
                class_spec = "Affliction Warlock"
            elif self.c_spec == "demonology":
                class_spec = "Demonology Warlock"
            elif self.c_spec == "destruction":
                class_spec = "Destruction Warlock"
        else:
            print("Unsupported class/spec-combination: " + str(self.c_class) + " - " + str(self.c_spec) + "\n")
            sys.exit(1)
        if b_tank or b_heal:
            if input(
                    "You are trying to use a tank or heal-spec! Be aware that this may lead to no or incomplete results!\n You may need to generate a new Analyzer.json using Analyzer.py which includes a profile with your spec (Enter to continue") == "q":
                sys.exit(0)
        return class_spec

    def getRole(self):
        if self.c_class == "deathknight":
            return "strattack"
        elif self.c_class == "demonhunter":
            return "agiattack"
        elif self.c_class == "druid":
            if self.c_spec == "balance":
                return "spell"
            elif self.c_spec == "feral":
                return "agiattack"
            elif self.c_spec == "guardian":
                return "agiattack"
            elif self.c_spec == "restoration":
                return "spell"
        elif self.c_class == "hunter":
            return "agiattack"
        elif self.c_class == "mage":
            return "spell"
        elif self.c_class == "priest":
            return "spell"
        elif self.c_class == "paladin":
            if self.c_spec == "retribution":
                return "strattack"
            elif self.c_spec == "holy":
                return "spell"
            elif self.c_spec == "protection":
                return "strattack"
        elif self.c_class == "monk":
            if self.c_spec == "windwalker":
                return "agiattack"
            elif self.c_spec == "brewmaster":
                return "agiattack"
            elif self.c_spec == "mistweaver":
                return "spell"
        elif self.c_class == "shaman":
            if self.c_spec == "enhancement":
                return "agiattack"
            elif self.c_spec == "elemental":
                return "spell"
            elif self.c_spec == "restoration":
                return "spell"
        elif self.c_class == "rogue":
            return "agiattack"
        elif self.c_class == "warrior":
            if self.c_spec == "fury":
                return "strattack"
            elif self.c_spec == "arms":
                return "strattack"
            elif self.c_spec == "protection":
                return "strattack"
        elif self.c_class == "warlock":
            return "spell"
