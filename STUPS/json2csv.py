#!/usr/bin/env python
# -*- coding: ISO-8859-5 -*-
# author: Quentin Rossy
# date: 16.02.2019
# description: convert data from esc-webintelligence from json to csv
# input: mongoDB export with one collection per line 

import json, sys

DEBUG = False

#To draw progressbar in the shell
def drawProgressBar(percent, barLen = 20):
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
    sys.stdout.flush()
	
#SET INPUT
ENC = 'iso-8859-5' #'iso-8859-5' / 'utf-8'
INPUT = "google.json"
data = open(INPUT, "r", encoding=ENC).readlines()
num_lines = sum(1 for line in data) - 1

#SET OUTPUT
out = open(INPUT+'.csv','w', encoding=ENC)
out.write('id;keywords;date;type;link;rank;title;hostname;snippet\n') #CSV HEADER

#RESHAPE AND WRITE DATA
for i, line in enumerate(data):
	to_json = line[:-1] 					#retire le retour à la ligne, -2 si présence de virgules entre les collections
	json_parsed = json.loads(to_json) 		#input: une collection {} sans rien d'autres avant et après
	
	urls = json_parsed['result']
	for n, url in enumerate(urls):
		outline = ""
		outline += json_parsed['_id']['$oid'] + ";"
		outline += json_parsed['keywords'] + ";"
		outline += json_parsed['date']['$date'] + ";"
		outline += json_parsed['type'] + ";"
	
		outline += url['link'] + ";"
		outline += str(n+1) + ";"
		try:
			outline += url['title'].replace('\n', ' ').replace('\r', '') + ";"
		except:
			outline += ";"
		try:
			outline += url['displayLink'] + ";"
		except:
			outline += ";"
		try:
			outline += "\"" + url['snippet'].replace(';', ' - ').replace('\n', ' ').replace('\r', '') + "\";"
		except:
			outline += ";"
		outline += "\n"
		out.write(outline)	
	
	drawProgressBar(i/num_lines) 			#Drawprogress bar
	if DEBUG and i > 0:
		break
out.close()