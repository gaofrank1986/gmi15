# encoding:utf-8

import requests
import base64


import re

from fuzzywuzzy import fuzz, process
from unidecode import unidecode



reg = re.compile(r'\d+(?:[.,]\d+)?')
bad_reg = re.compile(r'\d+/1000$')
hp_reg = re.compile(r'\d[.,]\d{3}')
lvl_reg = re.compile(r'^\+\d\d?$')
bad_lvl_reg_1 = re.compile(r'^\+?\d\d?$')
bad_lvl_reg_2 = re.compile(r'^\d{4}\d*$')

class cn():
	def __init__(self):
		# super().__init__()

		# self.id = 'cn'
		# self.code = 'chs'
		# self.flags = ['🇨🇳']
		# self.supported = False

		self.hp = '生命值'
		self.heal = '治疗加成'
		self.df = '防御力'
		self.er = '元素充能效率'
		self.em = '元素精通'
		self.atk = '攻击力'
		self.cd = '暴击伤害'
		self.cr = '暴击率'
		self.phys = '物理伤害加成'
		self.elem = '元素伤害加成'
		self.anemo = '风元素伤害加成'
		self.elec = '雷元素伤害加成'
		self.pyro = '火元素伤害加成'
		self.hydro = '水元素伤害加成'
		self.cryo = '冰元素伤害加成'
		self.geo = '岩元素伤害加成'
		self.dend = '草元素伤害加成'

		self.piece_set = '套装'

		self.replace = {'·': '.'}

		self.lvl = '等级'
		self.art_level = '圣遗物等级'

		self.ignore = ['in']

def parse(text):
	stat = None
	results = []
	level = None
	prev = None
	del_prev = True
 
	lang = cn()

	elements = [lang.anemo, lang.elec, lang.pyro, lang.hydro, lang.cryo, lang.geo, lang.dend]
	choices = elements + [lang.hp, lang.heal, lang.df, lang.er, lang.em, lang.atk, lang.cd, lang.cr, lang.phys]
	choices = {unidecode(choice).lower(): choice for choice in choices}

	for line in text.splitlines():
		if not line:
			continue

		if del_prev:
			prev = None
		del_prev = True

		for k,v in lang.replace.items():
			line = line.replace(k,v)
		line = unidecode(line).lower()
		line = line.replace(':','.').replace('-','').replace('0/0','%')
		if line.replace(' ','') in lang.ignore or bad_reg.search(line.replace(' ','')):
			continue
		if  fuzz.partial_ratio(line, unidecode(lang.piece_set).lower()) > 80 and len(line) > 4:
			# print('套装',line)
			break

		value = lvl_reg.search(line.replace(' ',''))
		if value:
			if level == None or (len(results) == 1 and not stat):
				# print('1', line)
				level = int(value[0].replace('+',''))
			continue

		value = hp_reg.search(line.replace(' ',''))
		if value:
			# print('2', line)
			value = int(value[0].replace(',','').replace('.',''))
			results += [[lang.hp, value]]
			stat = None
			continue

		extract = process.extractOne(line, list(choices))
		if extract[1] <= 80:
			extract = process.extractOne(line, list(choices), scorer=fuzz.partial_ratio)

		if ((extract[1] > 80) and len(line.replace(' ','')) > 1) or stat:
			# print('3', line)
			if (extract[1] > 80):
				stat = choices[extract[0]]
			value = reg.findall(line.replace(' ','').replace(',','.'))
			if not value:
				if not prev:
					continue
				# print('4', prev)
				value = prev
			value = max(value, key=len)
			if len(value) < 2:
				continue
			if line.find('%', line.find(value)) != -1 and '.' not in value:
				value = value[:-1] + '.' + value[-1]
			if '.' in value:
				value = float(value)
				stat += '%'
			else:
				value = int(value)
			results += [[stat, value]]
			stat = None
			if len(results) == 5:
				break
			continue

		value = bad_lvl_reg_1.search(line.replace(' ','')) or bad_lvl_reg_2.search(line.replace(' ','').replace('+',''))
		if not value:
			line = line.replace(',','')
			prev = reg.findall(line.replace(' ',''))
			del_prev = False

	# print(level, results)
	return level, results

def ocr(path):

    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(path, 'rb')
    img = base64.b64encode(f.read())

    params = {"image":img}
    access_token = '[24.a759b6f5779a442a934c4121dfa05f2e.2592000.1613054170.282335-23532324]'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        # return (response.json())
        ans = response.json()['words_result']
        ans = [i['words'] for i in ans]
        text = '\n'.join(ans)
        return(text)
    else:
        raise ValueError("cannot get json")
    
    
