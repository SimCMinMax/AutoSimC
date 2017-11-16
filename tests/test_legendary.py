import unittest
import main


class TestLegendary(unittest.TestCase):
    def test_single(self):
        gear_list = {"head": []}
        artifact_string = "head,102,87,99,10"
        main.add_legendary(artifact_string.split(","), gear_list)
        self.assertListEqual(gear_list["head"], ["L,id=102,bonus_id=87,enchant_id=99,gem_id=10"])
