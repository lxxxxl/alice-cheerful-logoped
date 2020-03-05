# coding: utf-8
from __future__ import unicode_literals

import json
import logging
import random
import pymorphy2
from flask import Flask, request



class CLFlaskWrapper(Flask):

	# word arrays
	words_noun = None
	words_adjf = None
	words_verb = None
	
	# Stores session states
	# AWAITING_START_CNF		awaiting approval for play
	# AWAITING_SENTENCE_RESP	awaiting for 'next' command or sentence
	sessionStorage = {}

	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_url_rule('/', view_func=self.main, methods=['POST',])

		with open('data/noun.txt') as f:
			self.words_noun = f.readlines()
		with open('data/adjf.txt') as f:
			self.words_adjf = f.readlines()
		with open('data/verb.txt') as f:
			self.words_verb = f.readlines()
    
	def main(self):
		"""Retrieves request body and generates response"""
		#logging.info('Request: %r', request.json)

		response = {
			"version": request.json['version'],
			"session": request.json['session'],
			"response": {
				"end_session": False
			}
		}
	
		self.handle_dialog(request.json, response)

		#logging.info('Response: %r', response)

		return json.dumps(
			response,
			ensure_ascii=False,
			indent=2
		)
		
		
	def get_user_state(self, user_id):
		"""Returns state of session for user"""
		if user_id not in self.sessionStorage:
			return None
		return self.sessionStorage[user_id]
		
	def set_user_state(self, user_id, state):
		"""Sets state of session"""
		self.sessionStorage[user_id] = state

	def handle_dialog(self, request, response):
		"""Process request and generate response"""
		user_id = request['session']['user_id']

		if request['session']['new']:
			# It is new user
			response['response']['text'] = 'Привет! Я - веселый логопед. Я буду говорить предложения, а ты повторяй за мной. Скажи "Привет", и мы начнем.'
			response['response']['buttons'] = self.get_buttons(user_id)
			self.set_user_state(user_id, 'AWAITING_START_CNF')
			return
	
		
		user_str = request['request']['original_utterance'].lower()
		
		if user_str in ['помощь', 'что ты умеешь']:
			response['response']['text'] = 'Я - веселый логопед. Я буду говорить предложения, а ты повторяй за мной.'
			response['response']['buttons'] = self.get_buttons(user_id)
			return
		
		
		if self.get_user_state(user_id) == 'AWAITING_START_CNF':
			if user_str != 'привет':
				response['response']['text'] = 'Скажи "Привет", и мы начнем.'	# Tell ok if it we can start
				response['response']['buttons'] = self.get_buttons(user_id)
			else:
				self.set_user_state(user_id, 'AWAITING_SENTENCE_RESP')
				response['response']['text'] = 'Повторяй: ' + self.generate_random_sentence()
				response['response']['buttons'] = self.get_buttons(user_id)
		
		
		elif self.get_user_state(user_id) == 'AWAITING_SENTENCE_RESP':	
			if user_str == 'Дальше':
				response['response']['text'] = 'Повторяй: ' + self.generate_random_sentence()
				response['response']['buttons'] = self.get_buttons(user_id)
			elif len(user_str)>=20:		# crutch to check validity of sentence
				award = random.choice(['Не плохо.', 'Молодец.', 'Хорошо.', 'Отлично.'])
				response['response']['text'] = award + ' Повторяй: ' + self.generate_random_sentence()
				response['response']['buttons'] = self.get_buttons(user_id)
			else:
				award = random.choice(['Повнимательней. ', 'Постарайся получше.'])
				response['response']['text'] = award + ' Следующее: ' + self.generate_random_sentence()
				response['response']['buttons'] = self.get_buttons(user_id)
	
	def get_buttons(self, user_id):
		"""Creates Button objects for response"""
		state = self.get_user_state(user_id)
		suggests = []
	
		if state == 'AWAITING_START_CNF':
			suggests = [
			{'title': 'Привет', 'hide': True},
			{'title': 'Помощь', 'hide': True}
		]
		elif state == 'AWAITING_SENTENCE_RESP':
			suggests = [
			{'title': 'Дальше', 'hide': True},
			{'title': 'Помощь', 'hide': True}
		]
		return suggests


	def inflect_with_check(self, morph_parsed, tags):
		morph_ret = morph_parsed.inflect(tags)
		if morph_ret == None:
			logging.error('Error',morph_parsed.word,tags)
			return morph_parsed
		return morph_ret
	
	def generate_sentence(self, noun, adjf, verb):
		"""Generates valid sentence with moun, adjective and verb provided"""
	
		morph = pymorphy2.MorphAnalyzer()
	
		p_noun = morph.parse(noun)[0]
		p_adjf = morph.parse(adjf)[0]
		p_verb = morph.parse(verb)[0]
	
		# time and person applies separately because of pymorphy2 limitation
		verb_rules = [['Я', 	{'pres'}, 			{'sing', '1per'}],
						['Я', 	{'past', 'masc'}, 	{'sing', '1per'}],
						['Я', 	{'past', 'femn'}, 	{'sing', '1per'}],
						['Ты', 	{'pres'},			{'sing', '2per'}],
						['Ты', 	{'past', 'masc'}, 	{'sing', '2per'}],
						['Ты', 	{'past', 'femn'}, 	{'sing', '2per'}],
						['Он', 	{'pres'}, 			{'sing', '3per'}],
						['Он', 	{'past', 'masc'}, 	{'sing', '3per'}],
						['Она', {'pres'}, 			{'sing', '3per'}],
						['Она', {'past', 'femn'}, 	{'sing', '3per'}],
						['Они', {'pres'}, 			{'plur', '3per'}],
						['Они', {'past'}, 			{'plur', '3per'}]
					]
		verb_rule = random.choice(verb_rules)
	
		# apply person and count to verb
		p_verb = self.inflect_with_check(p_verb, verb_rule[2])
		# apply time and gender to verb
		p_verb = self.inflect_with_check(p_verb, verb_rule[1])
	
		# choose grammatic case for moun and adjacent
		gram_case = random.choice(['datv', 'accs', 'ablt'])
	
		# choose time for noun and adjacent and apply others
		if bool(random.getrandbits(1)):
			p_noun = self.inflect_with_check(p_noun, {gram_case, 'sing'})
			# set adjacent gender and count equal to noun 
			p_adjf = self.inflect_with_check(p_adjf, {gram_case, p_noun.tag.gender, p_noun.tag.number})
		else:
			p_noun = self.inflect_with_check(p_noun, {gram_case, 'plur'})
			p_adjf = self.inflect_with_check(p_adjf, {gram_case, p_noun.tag.number})
	
		return '{} {} {} {}'.format(verb_rule[0], p_verb.word, p_adjf.word, p_noun.word)

	def generate_random_sentence(self):
		"""Generates valid sentence with random moun, adjective and verb"""
		return self.generate_sentence(
				random.choice(self.words_noun).strip(), 
				random.choice(self.words_adjf).strip(),
				random.choice(self.words_verb).strip()) 



app = CLFlaskWrapper(__name__)
logging.basicConfig(level=logging.DEBUG)


