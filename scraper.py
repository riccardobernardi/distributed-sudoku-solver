import os
import urllib

from bs4 import BeautifulSoup
from urllib.request import urlopen

def make_soup(url):
	html = urlopen(url).read()
	return BeautifulSoup(html, features="html.parser", from_encoding="iso-8859-1")


def get_txt(url):
	if ".txt" not in url:
		soup = make_soup(url)
		txt_links = [link.get('href') for link in soup.findAll('a')]
		for i,each in enumerate(txt_links):
			if ("txt" in each) and ("_s" not in each):
				filename = "lipas_" + each
				urllib.request.urlretrieve(url+"/"+each, "./sudokus/" + filename)
		return
	else:
		soup = make_soup(url)
		#print(soup)
		s = str(soup).split("========")
		for i,value in enumerate(s):
			if value[0] == "\n":
				value = value[1:]
			with open("./sudokus/" + "norvig_"+str(i)+".txt", mode="w") as f:
				f.write(value)
