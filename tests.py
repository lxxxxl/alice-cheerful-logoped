# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest
import json
 
from api import app
  
class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
 
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
 
 
###############
#### tests ####
###############
 
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 405)

    def test_new_user(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 1}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('Привет!' in json_response, True)

    def test_invalid_request(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"aaa"}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('и мы начнем' in json_response, True)

    def test_help(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"помощь"}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('Я - добрый логопед.' in json_response, True)

    def test_start_dialog(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"привет"}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('Повторяй.' in json_response, True)

    def test_invalid_sentence(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"aaa"}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('Повторяй за мной, или скажи "Дальше".' in json_response, True)

    def test_max_dificulty(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"посложней"}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        response  = self.app.post('/', content_type='application/json', data=request)
        response  = self.app.post('/', content_type='application/json', data=request)
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('Извини, сложней уже некуда.' in json_response, True)

    def test_min_dificulty(self):
        request = '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"попроще"}}'  
        response  = self.app.post('/', content_type='application/json', data=request)
        response  = self.app.post('/', content_type='application/json', data=request)
        response  = self.app.post('/', content_type='application/json', data=request)
        response  = self.app.post('/', content_type='application/json', data=request)
        json_response = json.loads(response.data)
        self.assertNotEqual('Извини, проще уже некуда.' in json_response, True)

        
 
 
if __name__ == "__main__":
    unittest.main()