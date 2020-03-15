import os
import pickle

pickle.HIGHEST_PROTOCOL = 2

import rq
from pygraham import *
from redis import Redis
import pickle

pickle.HIGHEST_PROTOCOL = 2
from rq import Queue
import time
from scraper import download_sudokus, load_qqwing_sudokus
from util import solve, squeze_all, RANK, split, to_int, Sudodata, parse_sudoku
from time import sleep
from antiplagiarism import antiplagiarism

try:
	download_sudokus()
	load_qqwing_sudokus()
except:
	print("Some downloads went wrong...")

plagiarism = antiplagiarism("./sudokus", type=".txt", grams=2, threshold=0.9)
print("number of sudokus that are very similar:", len(plagiarism), "(over 90% of similarity)")

DISTRIBUTE = True
VIEW_RESULTS = False


def main():
	count = 0
	solved = 0
	dataset = list(os.listdir("./sudokus")).filter(lambda x: ".txt" in x)
	num_sudoku_avail = len(dataset)
	c = Redis(host='192.168.1.237')
	q = Queue(connection=c)
	jobs = []

	for i in dataset:
		# i is a txt file representing a sudoku in the correct format
		try:
			with open("./sudokus/" + i, mode="r") as f:
				curr_sudoku = parse_sudoku(f)

				if DISTRIBUTE:
					jobs.append(q.enqueue(solve, curr_sudoku))
					print("\r [DISTRIBUTED] Distributed sudokus: ", count, "out of", num_sudoku_avail, end='')
				else:
					result = solve(curr_sudoku)

					if result != -1:
						if VIEW_RESULTS:
							result = Sudodata(result)
							print("--------------------------")
							print(result)
						solved += 1
					print("\r [SEQUENTIAL] Solved sudokus:", count, "out of", num_sudoku_avail, end='')

				count += 1
		except:
			print("A sudoku was wrongly formatted, in particular:", i)

	if DISTRIBUTE:
		print()
		distributed_finished = 0
		excluded = set()
		while any(not job.is_finished for job in jobs):
			for i in jobs:
				if i.is_finished and (i.get_id() not in excluded):
					excluded.add(i.get_id())
					distributed_finished += 1
				print("\r [DISTRIBUTED] Solved sudokus: ", distributed_finished, "out of", num_sudoku_avail, end='')
			sleep(0.01)

		for jj in jobs:
			result = jj.return_value
			if (result != -1) and (result is not None) and (result != "None"):
				# return result
				solved += 1

	print()
	print("Tot of correct over all:", solved, "/", num_sudoku_avail)
	print("Accuracy is: %.2f" % ((solved / num_sudoku_avail) * 100), "%")


init = time.time()
main()
print("Elapsed:", (time.time() - init) / 60, "min")
