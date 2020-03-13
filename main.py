import os
from pygraham import *

from scraper import get_txt
from util import solve, show, squeze_all, RANK, Sudodata
from time import time


def split(word):
    return [char for char in word]

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

#download_sudokus()

def load_qqwing_sudokus():
	for i in os.listdir("./qqwing_500_gen_sudokus"):
		# i is a txt file representing a sudoku in the correct format
		with open("./qqwing_500_gen_sudokus/" + i, mode="r") as f:
			s = str(f.read(-1)).split("\n\n\n")
			# print(s)

			for j,value in enumerate(s):
				with open("./sudokus/"+ str(i).replace(".txt","") + "_" + str(j) + ".txt",mode="w") as f:
					f.write(value+"\n")

load_qqwing_sudokus()


def to_int(x):
	if x == '0':
		return [1, 2, 3, 4, 5, 6, 7, 8, 9]
	if x == '.':
		return [1,2,3,4,5,6,7,8,9]
	else:
		return int(x)


def main():
	count = 0
	dataset = list(os.listdir("./sudokus")).filter(lambda x: ".txt" in x)
	alls = len(dataset)

	for i in dataset:
		# i is a txt file representing a sudoku in the correct format
		try:
			with open("./sudokus/" + i,mode="r") as f:
				curr_sudoku = list([])

				for j in f:
					if j == "\n":
						continue
					if j == " \n":
						continue
					if j == " ":
						continue

					# one space between each number
					if j[1] == " ":
						curr_sudoku += [ [list(split(i)).map(to_int) for i in k] for k in [j.replace("\n", "").split(" ")]]
						add = []
						for i in range(RANK):
							add += [curr_sudoku[-1][i*RANK:(i+1)*RANK]]
						curr_sudoku[-1] = add


					# one space every 3
					if (j[1] != " ") and (j[3] == " "):
						curr_sudoku += [ [list(split(i)).map(to_int) for i in k] for k in [j.replace("\n","").split(" ")] ]


					# no space never
					if (j[1] != " ") and (j[3] != " "):
						curr_sudoku += [[list(split(k)).map(to_int) for k in [j.replace("\n", "")]][0]]
						add = []
						for i in range(RANK):
							add += [curr_sudoku[-1][i * RANK:(i + 1) * RANK]]
						curr_sudoku[-1] = add

				curr_sudoku = squeze_all(curr_sudoku)
				result = solve(curr_sudoku)

				if result!= -1:
					result = Sudodata(result)
					count+=1
				#print("--------------------------")
				#print(result)
				print("\r done", count, "out of", alls, end = '')
		except:
			print("An error occured at", i)

	print()
	print("Tot of correct over all:", count,"/", alls)
	print("Accuracy is: %.2f" % ((count/alls)*100), "%")


init = time()
main()
print("Elapsed:", (time() - init)/60, "min")