import json
import unittest

from metaGTools.mgrast.api import (MGRASTException,
                                  MGRASTAuthenticationException,
                                  mgrast_request, id_check)
from metaGTools.mgrast.project_stats import metagenome_project_stats
 
class Test_mgrast_api(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_mgrast_request_invalid_key(self):
        try:
            req = mgrast_request('project', 'mgp6271', {'verbosity':'full'}, 
                                 'invalid_key')
        except MGRASTAuthenticationException as me:
            self.assertIn( 'invalid webkey', me.message)
        
    def test_mgrast_request_insufficient_permissions(self):
        try:
            req = mgrast_request('project', 'mgp6271', {'verbosity':'full'}, '')
        except MGRASTAuthenticationException as me:
            self.assertIn( 'insufficient permissions', me.message)
    
    def test_id_check_missing(self):
        self.assertEqual(id_check('mgp','1234'), 'mgp1234')
        
    def test_id_check_present(self):
        self.assertEqual(id_check('mgp','mgp1234'), 'mgp1234')


class Test_mgrast_project_stats(unittest.TestCase):            
    def test_no_project(self):
        mg_stats = metagenome_project_stats('x', '')
        self.assertEquals( mg_stats, None)
 
 
if __name__ == '__main__':
    unittest.main()