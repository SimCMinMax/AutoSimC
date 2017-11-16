import unittest
import main


class TestGems(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.gem_list = ["a", "b"]

    def test_gem_combinations1(self):
        gems = main.get_Possible_Gem_Combinations(self.gem_list, 1)
        self.assertListEqual(self.gem_list, gems)

    def test_gem_combinations2(self):
        gems = main.get_Possible_Gem_Combinations(self.gem_list, 2)
        target = ['a/a', 'a/b', 'b/b']
        self.assertListEqual(target, gems)

    def test_gem_combinations3(self):
        gems = main.get_Possible_Gem_Combinations(self.gem_list, 3)
        target = ['a/a/a', 'a/a/b', 'a/b/b', 'b/b/b']
        self.assertListEqual(target, gems)
