import unittest

from project_stats import metagenome_project_stats

class Test_mgrast_project_stats(unittest.TestCase):            
    def test_no_project(self):
        mg_stats = metagenome_project_stats('1000', '')
        self.assertEquals(mg_stats, None)
 
 
if __name__ == '__main__':
    unittest.main()