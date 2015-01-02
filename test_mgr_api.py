import json
import unittest

from mgr_api.api import (MGRASTException, MGRASTAuthenticationException,
                         mgrast_request, id_check)

 
class Test_api(unittest.TestCase):
 
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
 
 
if __name__ == '__main__':
    unittest.main()