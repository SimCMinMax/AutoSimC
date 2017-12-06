import os
import json
import subprocess
import sys
import hashlib

from marshmallow import Schema, fields

from settings import settings

path = settings.analyzer_path
combined_path = os.path.join(os.getcwd(), path)
simc_path = settings.simc_path

raw_data = []
analyzed_data = []
analysis_filename = "Analysis.json"
num_profiles_per_sim = 1


class Variant():
    def __init__(self, version, git_revision, target_error, fight_style):
        self.version = version
        self.git_revision = git_revision
        self.target_error = target_error
        self.fight_style = fight_style
        self.hash = self.hash_me()
        self.playerdata = []

    def hash_me(self):
        h = hashlib.sha256()
        h.update(self.version.encode("utf-8"))
        h.update(self.git_revision.encode("utf-8"))
        h.update(str(self.target_error).encode("utf-8"))
        # change this later to include manual options (added enemies etc.)
        h.update(self.fight_style.encode("utf-8"))
        # todo: include apl etc. here later
        # hash.update(data["apl"].encode("utf-8"))
        return h.hexdigest()


class PlayerData():
    def __init__(self, specialization, reference_hash):
        self.specialization = specialization
        self.reference_hash = reference_hash
        self.hash = self.hash_me()
        self.specdata = []

    def hash_me(self):
        h = hashlib.sha256()
        h.update(self.specialization.encode("utf-8"))
        return h.hexdigest()

    def __eq__(self, other):
        return self.specialization == other.specialization


class SpecData():
    def __init__(self, race, elapsed_time_seconds, iterations, playerhash):
        self.race = race
        self.elapsed_time_seconds = elapsed_time_seconds
        self.iterations = iterations
        self.reference_hash = playerhash

    def __eq__(self, other):
        return self.race == other.race


class SpecDataSchema(Schema):
    race = fields.Str()
    elapsed_time_seconds = fields.Str()
    iterations = fields.Str()


class PlayerDataSchema(Schema):
    specialization = fields.Str()
    specdata = fields.Nested(SpecDataSchema(), many="True")


class VariantSchema(Schema):
    version = fields.Str()
    git_revision = fields.Str()
    target_error = fields.Float()
    fight_style = fields.Str()
    hash = fields.Str()
    playerdata = fields.Nested(PlayerDataSchema(), many="True")


# generates profiles
# target_error must be >=0.0
def sim_profiles(target_error):
    if target_error < 0.0:
        print("Target_Error < 0")
        sys.exit(1)
    for roots, dirs, files in os.walk(combined_path):
        for file in files:
            if file.endswith(".simc"):
                name = file[0:file.find(".")]
                if not os.path.exists(os.path.join(combined_path, name + '-mode' + str(target_error) + '.result')):
                    profiles_to_sim = [os.path.join(combined_path, file) for _ in range(num_profiles_per_sim)]
                    cmd = [simc_path, *profiles_to_sim,
                           'json2=' + os.path.join(combined_path, '_' + str(name)) + '-mode' + str(
                               target_error) + '.result',
                           'target_error=' + str(target_error),
                           'process_priority=low', 'output=nul', 'single_actor_batch=1',
                           'analyze_error_interval=10']
                    subprocess.call(cmd)


def extract_data(file):
    data = json.load(file)
    dataset = {}
    dataset["version"] = data["version"]
    dataset["git_revision"] = data["git_revision"]
    dataset["target_error"] = data["sim"]["options"]["target_error"]
    dataset["fight_style"] = data["sim"]["options"]["fight_style"]

    l_players = []

    players = data["sim"]["players"]
    for p in players:
        playerdata = {}
        playerdata["name"] = p["name"]
        playerdata["race"] = p["race"]
        playerdata["specialization"] = p["specialization"]
        playerdata["dps"] = p["collected_data"]["dps"]["mean"]
        playerdata["elapsed_time_seconds"] = data["sim"]["statistics"]["elapsed_time_seconds"]
        playerdata["iterations"] = data["sim"]["options"]["iterations"]
        l_players.append(playerdata)

    dataset["playerdata"] = l_players
    raw_data.append(dataset)


# parses the results of simulated profiles
def parse_json_output():
    for roots, dirs, files in os.walk(combined_path):
        for file in files:
            if file.endswith(".result"):
                currentfile = open(os.path.join(combined_path, file), "r")
                extract_data(currentfile)
                currentfile.close()


# parses
def generate_json_analysis():
    global raw_data
    raw_data = sorted(raw_data, key=lambda d: d["target_error"])
    for data in raw_data:
        v = Variant(data["version"], data["git_revision"], data["target_error"], data["fight_style"])

        exist_variant = False
        for o in range(len(analyzed_data)):
            if v.hash == analyzed_data[o].hash:
                exist_variant = True
        if not exist_variant:
            analyzed_data.append(v)

        for i in range(len(data["playerdata"])):
            p = PlayerData(data["playerdata"][i]["specialization"], v.hash_me())

            for variant in analyzed_data:
                if p.reference_hash == variant.hash:
                    if p not in variant.playerdata:
                        variant.playerdata.append(p)

            s = SpecData(data["playerdata"][i]["race"], data["playerdata"][i]["elapsed_time_seconds"]/num_profiles_per_sim,
                         data["playerdata"][i]["iterations"], p.hash_me())

            for variant in analyzed_data:
                for pdata in variant.playerdata:
                    if s.reference_hash == pdata.hash:
                        if s not in pdata.specdata:
                            pdata.specdata.append(s)

def main():
    if input("Removing existing result-files (Press enter)"):
        for roots, dirs, files in os.walk(combined_path):
            for file in files:
                if file.endswith(".result"):
                    os.remove(os.path.join(combined_path, file))

    sim_profiles(2)
    sim_profiles(1)
    sim_profiles(0.7)
    sim_profiles(0.5)
    sim_profiles(0.4)
    sim_profiles(0.3)
    sim_profiles(0.2)
    sim_profiles(0.15)
    sim_profiles(0.1)
    sim_profiles(0.075)
    sim_profiles(0.05)
    parse_json_output()

    # now all files are parsed and relevant content stored in raw_data[]
    # we can now calculate things and put them into our analyzed_data{}
    generate_json_analysis()

    # output it
    with open(os.path.join(combined_path, analysis_filename), "w") as write:
        schema = VariantSchema(many="True")
        json.dump(schema.dump(analyzed_data), write, indent=4)

        # we have now generated our analysis-intermediate which contains aggregated details
        # schema: fightvariant n -> spec s -> race r
        # explanation: you can e.g. extract the average amount of iterations for calculation of a certain amount of
        # profiles of a spec and race in a given fight (different fight_style, different target_error) etc.
        # todo: implement additional fight- and spec-parameters, e.g. talents(!!), apl (both are currently not in the json2-output (17.5.2017))


if __name__ == "__main__":
    main()
