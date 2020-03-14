import os
import urllib

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

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

		if "Grid" in str(soup):
			pattern = "Grid...(\r|\n)"
			s = re.sub(pattern, "========\n", str(soup))
			s = s.split("========")[1:]
			# print(s)
			for i, value in enumerate(s):
				if value[0] == "\n":
					value = value[1:]
				with open("./sudokus/Grid_" + url.split("/")[-1].replace(".txt","")+"_" + str(i) + ".txt", mode="w") as f:
					f.write(value)

		if "========" in str(soup):
			s = str(soup).split("========")
			for i,value in enumerate(s):
				if value[0] == "\n":
					value = value[1:]
				with open("./sudokus/Lines_" + "norvig_"+str(i)+".txt", mode="w") as f:
					f.write(value)


def download_sudokus():
	URLs=[
		"http://lipas.uwasa.fi/~timan/sudoku/",
		"http://norvig.com/easy50.txt",
		"https://raw.githubusercontent.com/dimitri/sudoku/master/sudoku.txt",
		"https://projecteuler.net/project/resources/p096_sudoku.txt"
		  ]
	for i in URLs:
		print("downloading some sudokus from", i)
		get_txt(i)


def load_qqwing_sudokus():
	for i in os.listdir("./qqwing_500_gen_sudokus"):
		# i is a txt file representing a sudoku in the correct format
		print("downloading sudokus from QQWing",i)
		with open("./qqwing_500_gen_sudokus/" + i, mode="r") as f:
			s = str(f.read(-1)).split("\n\n\n")
			# print(s)

			for j,value in enumerate(s):
				with open("./sudokus/"+ str(i).replace(".txt","") + "_" + str(j) + ".txt",mode="w") as f:
					f.write(value+"\n")