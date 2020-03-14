import os

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

# download_sudokus()
# load_qqwing_sudokus()

# plagiarism = antiplagiarism("./sudokus",type=".txt", grams=2,threshold=0.9)
# print("number of sudokus that are very similar:",len(plagiarism))

DISTRIBUTE = True


def main():
	count = 0
	solved = 0
	dataset = list(os.listdir("./sudokus")).filter(lambda x: ".txt" in x)
	alls = len(dataset)


	#######################################################
	c = Redis(host='192.168.1.237')
	q = Queue(connection=c)

	t0 = time.time()
	jobs = []
	for i in range(10):
		jobs.append(q.enqueue(split, "cane"))

	while any(not job.is_finished for job in jobs):
		time.sleep(0.01)
	t1 = time.time()

	print(t1 - t0)

	for i in jobs:
		print(i.return_value)
	#######################################################


	c = Redis(host='192.168.1.237')
	q = Queue(connection=c)
	jobs = []

	for i in dataset:
		# i is a txt file representing a sudoku in the correct format
		with open("./sudokus/" + i, mode="r") as f:
			curr_sudoku = parse_sudoku(f)

			if DISTRIBUTE:
				jobs.append(q.enqueue(solve, curr_sudoku))
			else:
				result = solve(curr_sudoku)

				if result != -1:
					# result = Sudodata(result)
					# print("--------------------------")
					# print(result)
					solved += 1
			count += 1

			print("\r done", count, "out of", alls, end='')

	print()
	if DISTRIBUTE:
		count = 0
		while any(not job.is_finished for job in jobs):
			count += 1
			sleep(0.01)
			if count == 1000:
				break

		for jj in jobs:
			result = jj.return_value
			if (result != -1) and (result is not None) and (result != "None"):
				return result
	print("Tot of correct over all:", solved, "/", alls)
	print("Accuracy is: %.2f" % ((solved / alls) * 100), "%")


init = time.time()
main()
print("Elapsed:", (time.time() - init) / 60, "min")
