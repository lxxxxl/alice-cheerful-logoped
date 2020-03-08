# coding: utf-8
from __future__ import unicode_literals

import json
import logging
import random
import pymorphy2
from difflib import SequenceMatcher
from flask import Flask, request



class CLFlaskWrapper(Flask):

	# word arrays
	words_noun = None
	words_adjf = None
	words_verb = None
	
	"""
	 Stores session information
	session{'state', 'dificulty', 'last_sentence'}

	Possible states:
	AWAITING_START_CNF		awaiting approval for play
	AWAITING_SENTENCE_RESP	awaiting for 'next' command or sentence

	dificulty:
	1			only one word
	2			noun with verb or adjective
	3			full sentence
	"""
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
		
		
	def create_session(self, user_id):
			"""Creates session with default params"""
			self.sessionStorage[user_id] = {}
			self.sessionStorage[user_id]['last_sentence'] = ''
			self.sessionStorage[user_id]['dificulty'] = 2		# default dificulty is "noun with verb or adjective"
			self.sessionStorage[user_id]['state'] = 'AWAITING_START_CNF'

	def get_session(self, user_id):
		"""Get session context for user_if provided"""
		if user_id not in self.sessionStorage:					# setup default params for new user
			self.create_session(user_id)
		return self.sessionStorage[user_id]


	def handle_dialog(self, request, response):
		"""Process request and generate response"""
		user_id = request['session']['user_id']

		if request['session']['new']:
			# It is new user
			self.get_session(user_id)['state'] = 'AWAITING_START_CNF'
			response['response']['text'] = 'Привет! Я - добрый логопед. Я буду говорить предложения, а ты повторяй за мной. Скажи "Привет", и мы начнем.'
			response['response']['buttons'] = self.get_buttons(user_id)
			return
	
		
		user_str = request['request']['original_utterance'].lower()
		
		if user_str in ['помощь', 'что ты умеешь']:
			response['response']['text'] = 'Я - добрый логопед. Я буду говорить предложения, а ты повторяй за мной. Если хочешь поменять сложность, то скажи "Попроще", или "Посложней".'
			response['response']['buttons'] = self.get_buttons(user_id)
			return				
		
		if self.get_session(user_id)['state'] == 'AWAITING_START_CNF':
			if user_str != 'привет':
				response['response']['text'] = 'Скажи "Привет", и мы начнем.'
				response['response']['buttons'] = self.get_buttons(user_id)
				return
			else:
				self.get_session(user_id)['state'] = 'AWAITING_SENTENCE_RESP'
				response['response']['text'] = 'Повторяй. '
				response['response']['buttons'] = self.get_buttons(user_id)

		if user_str == 'попроще':
			if self.get_session(user_id)['dificulty'] <= 1:
				response['response']['text'] = 'Извини, проще уже некуда. Повторяй за мной, или скажи "Дальше". ' + "\n" + self.get_session(user_id)['last_sentence']
				return
			else:
				self.get_session(user_id)['dificulty'] -= 1
				response['response']['text'] = 'Хорошо, давай попроще. Повторяй. '

		elif user_str == 'посложней':
			if self.get_session(user_id)['dificulty'] >= 3:
				response['response']['text'] = 'Извини, сложней уже некуда. Повторяй за мной, или скажи "Дальше". ' + "\n" + self.get_session(user_id)['last_sentence']
				return
			else:
				self.get_session(user_id)['dificulty'] += 1
				response['response']['text'] = 'Хорошо, давай посложней. Повторяй. '
		
		
		elif self.get_session(user_id)['state'] == 'AWAITING_SENTENCE_RESP':	
			if user_str == 'Дальше':
				response['response']['text'] = 'Повторяй. '
				response['response']['buttons'] = self.get_buttons(user_id)
			elif self.similiar(user_str, self.get_session(user_id)['last_sentence']) >= 0.7:
				award = random.choice(['Не плохо.', 'Молодец.', 'Хорошо.', 'Отлично.'])
				response['response']['text'] = award + ' Повторяй. '
				response['response']['buttons'] = self.get_buttons(user_id)
			else:
				award = random.choice(['Повнимательней. ', 'Постарайся получше. '])
				response['response']['text'] = award + ' Повторяй за мной, или скажи "Дальше". ' + "\n" + self.get_session(user_id)['last_sentence']
				response['response']['buttons'] = self.get_buttons(user_id)
				return

		random_sentence = self.generate_random_sentence(self.get_session(user_id)['dificulty'])
		self.get_session(user_id)['last_sentence'] = random_sentence
		response['response']['text'] += "\n" + random_sentence
	
	def get_buttons(self, user_id):
		"""Creates Button objects for response"""
		state = self.get_session(user_id)['state']
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
		else:
			suggests = [
			{'title': 'Помощь', 'hide': True}
		]
		return suggests


	def inflect_with_check(self, morph_parsed, tags):
		morph_ret = morph_parsed.inflect(tags)
		if morph_ret == None:
			logging.error('Error',morph_parsed.word,tags)
			return morph_parsed
		return morph_ret
	
	def generate_sentence_3(self, noun, adjf, verb, reduce_dificulty=False):
		"""Generates valid sentence with  with dificulty level 3, moun, adjective and verb"""
	
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
	
		if not reduce_dificulty:
			return '{} {} {} {}'.format(verb_rule[0], p_verb.word, p_adjf.word, p_noun.word)
		else:
			if bool(random.getrandbits(1)):
				return '{} {}'.format(p_verb.word, p_noun.word)
			else:
				return '{} {}'.format(p_adjf.word, p_noun.word)

	def generate_sentence_2(self, noun, adjf, verb):
		"""Generates valid sentence with dificulty level 2, noun with verb or adjective"""
		return self.generate_sentence_3(noun, adjf, verb, reduce_dificulty=True)

	def generate_sentence_1(self, noun_arr, adjf_arr, verb_arr):
		"""Generates valid sentence with dificulty level 1, one word"""
		return random.choice(noun_arr + adjf_arr + verb_arr).strip()

	def generate_random_sentence(self, dificulty):
		"""Generates valid sentence with random moun, adjective and verb"""

		sentence = ''
		if dificulty <= 1:
			sentence = self.generate_sentence_1(
				self.words_noun, 
				self.words_adjf,
				self.words_verb)
		elif dificulty >= 3:
			sentence = self.generate_sentence_3(
				random.choice(self.words_noun).strip(), 
				random.choice(self.words_adjf).strip(),
				random.choice(self.words_verb).strip())
		else:
			sentence = self.generate_sentence_2(
				random.choice(self.words_noun).strip(), 
				random.choice(self.words_adjf).strip(),
				random.choice(self.words_verb).strip()) 

		return sentence
	
	def similiar(self, str1, str2):
		""" Returns similiarity ratio of two strings"""
		return SequenceMatcher(None, str1, str2).ratio()



app = CLFlaskWrapper(__name__)
logging.basicConfig(level=logging.DEBUG)


