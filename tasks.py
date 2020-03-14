REDIS_HOST = '192.168.1.237'

import copy
from pygraham import *
from redis import Redis
import pickle
pickle.HIGHEST_PROTOCOL = 2

from rq import Queue
import time

RANK = 3


def split(word):
    return [char for char in word]


def to_int(x):
	if x == '0':
		return [1, 2, 3, 4, 5, 6, 7, 8, 9]
	if x == '.':
		return [1,2,3,4,5,6,7,8,9]
	else:
		return int(x)


def show(matrix):
	for i in matrix:
		for j in i:
			for k in j:
				print(k, end='')

			print(" ", end='')
		print()


def squeze_all(matrix):
	for i in range(len(matrix)):
		if (type(matrix[i]) != int) and (len(matrix[i]) == 1):
			matrix[i] = matrix[i][0]
		for j in range(len(matrix[i])):
			if (type(matrix[i][j]) != int) and (len(matrix[i][j]) == 1):
				matrix[i][j] = matrix[i][j][0]
			if type(matrix[i][j]) != int:
				for k in range(len(matrix[i][j])):
					if (type(matrix[i][j][k]) != int) and (len(matrix[i][j][k]) == 1):
						matrix[i][j][k] = matrix[i][j][k][0]

	return matrix


class Sudodata():
	def __init__(self, matrix):
		self.data = matrix

	def cell_rc(self, r, c):
		return self.data[r][c // RANK][c % RANK]

	def assign_cell_rc(self, r, c, v):
		self.data[r][c // RANK][c % RANK] = v

	def cell_rtc(self, r, t, c):
		return self.data[r][t][c]

	def column(self, c):
		return list([self.data[i][c // RANK][c % RANK] for i in range(RANK * RANK)])

	def assign_column(self, c, v):
		for i in range(RANK * RANK):
			self.data[i][c // RANK][c % RANK] = v[i]

	def row(self, r):
		return list([self.data[r][i // RANK][i % RANK] for i in range(RANK * RANK)])

	def assign_row(self, r, v):
		for i in range(RANK * RANK):
			self.data[r][i // RANK][i % RANK] = v[i]

	def triplet(self, r, t):
		return list(self.data[r][t])

	def cell_transform(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				self.assign_cell_rc(i, j, int(self.cell_rc(i, j)))

	def cell_iter(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				yield self.cell_rc(i, j)

	def row_iter(self):
		for i in range(RANK * RANK):
			yield self.row(i)

	def col_iter(self):
		for i in range(RANK * RANK):
			yield self.column(i)

	def box_iter(self):
		for v in range(RANK):
			for i in range(RANK):
				box = []
				for j in range(RANK):
					for k in range(RANK):
						box += [self.cell_rc(v * RANK + j, i * RANK + k)]
				yield box

	def cell_transformer(self, l):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				self.assign_cell_rc(i, j, l(self.cell_rc(i, j)))

	def row_transformer(self, l):
		for i in range(RANK * RANK):
			self.assign_row(i, l(self.row(i)))

	def col_transformer(self, l):
		for i in range(RANK * RANK):
			self.assign_column(i, l(self.column(i)))

	def box_transformer(self, l):
		for v in range(RANK):
			for i in range(RANK):
				box = []
				for j in range(RANK):
					for k in range(RANK):
						box += [(v * RANK + j, i * RANK + k)]

				l(box)

	def __iter__(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				yield self.cell_rc(i, j)

	def __eq__(self, other):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				if self.cell_rc(i, j) != other.cell_rc(i, j):
					return False
		return True

	def is_solved(self):
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				if type(self.cell_rc(i, j)) != int:
					return False

		for i in self.row_iter():
			if len(set([i for i in range(1, 10)]) & set(i)) != 9:
				return False

		for i in self.col_iter():
			if len(set([i for i in range(1, 10)]) & set(i)) != 9:
				return False

		for i in self.box_iter():
			if len(set([i for i in range(1, 10)]) & set(i)) != 9:
				return False

		return True

	def void_elems(self):
		for i in self.row_iter():
			if list(i).filter(lambda x: (type(x) != int) and (len(x) == 0)):
				return True
		return False

	def duplicates(self):
		for i in self.row_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		for i in self.col_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		for i in self.box_iter():
			for j in range(1, 10):
				if len(list(i).filter(lambda x: (type(x) == int) & (x == j))) > 1:
					return True

		return False

	def hash(self):
		hashed = ''
		for i in range(RANK * RANK):
			for j in range(RANK * RANK):
				# hashing is not unique but it's okay
				if type(self.cell_rc(i, j)) == int:
					hashed += str(i) + str(j) + str(self.cell_rc(i, j)) + "-"
				else:
					hashed += str(i) + str(j) + str(sum(self.cell_rc(i, j))) + "-"

		return hashed[:len(hashed) - 1]

	def __repr__(self):
		s = ""
		for i in self.row_iter():
			s += str(i) + "\n"
		return s

	def __str__(self):
		s = ""
		for i in self.row_iter():
			s += str(i) + "\n"
		return s

	def set_matrix(self, matrix):
		self.data = matrix


def propagate_constraints(data):
	exclude = []

	def box_prop(box_indexes):
		for r, c in box_indexes:
			if type(data.cell_rc(r, c)) == int:
				exclude.append(data.cell_rc(r, c))

		for r, c in box_indexes:
			if type(data.cell_rc(r, c)) != int:
				data.assign_cell_rc(r, c, list(set(data.cell_rc(r, c)) - set(exclude)))

		exclude.clear()

	data.box_transformer(box_prop)

	def col_prop(col):
		exclude = []

		for elem in col:
			if type(elem) == int:
				exclude.append(elem)

		for i in range(len(col)):
			if type(col[i]) != int:
				col[i] = list(set(col[i]) - set(exclude))

		return col

	data.col_transformer(col_prop)

	def row_prop(row):
		exclude = []

		for elem in row:
			if type(elem) == int:
				exclude.append(elem)

		for i in range(len(row)):
			if type(row[i]) != int:
				row[i] = list(set(row[i]) - set(exclude))

		return row

	data.row_transformer(row_prop)

	def squeeze(row):
		for i in range(len(row)):
			if (type(row[i]) != int) and (len(row[i]) == 1):
				row[i] = row[i][0]

		return row

	data.row_transformer(squeeze)

	return data


def solve(matrix):
	data = Sudodata(matrix)

	for i in range(4):
		tmp = copy.deepcopy(data)

		for i in range(8):
			data = propagate_constraints(data)

		if data.is_solved():
			return data.data

		if data == tmp:
			possibles = []
			# we have to make a choice, use the smallest array of choices to cut out branches of the tree
			for j in range(RANK * RANK):
				for k in range(RANK * RANK):
					if type(data.cell_rc(j, k)) != int:
						possibles += [(j, k, data.cell_rc(j, k))]

			if len(possibles) == 0:
				return -1

			min_len = 1000
			min_value = (0, 0, [])
			for k, value in enumerate(possibles):
				if len(value[2]) < min_len:
					min_len = len(value[2])
					min_value = value


			###############################
			###############################

			c = Redis(host='192.168.1.237')
			q = Queue(connection=c)

			t0 = time.time()
			jobs = []

			for k in min_value[2]:
				to_pass = copy.deepcopy(data)
				to_pass.assign_cell_rc(min_value[0], min_value[1], k)
				jobs.append(q.enqueue(solve, to_pass.data))

			while any(not job.is_finished for job in jobs):
				time.sleep(0.01)
			t1 = time.time()

			print(t1 - t0)

			for jj in jobs:
				result = jj.return_value
				if result != -1:
					return result

			###############################
			###############################

			# for k in min_value[2]:
			# 	to_pass = copy.deepcopy(data)
			# 	to_pass.assign_cell_rc(min_value[0], min_value[1], k)
			# 	result = solve(to_pass.data)
			# 	if result != -1:
			# 		return result

		# this point is the most difficult of all the program PAY ATTENTION:
		# if you do tmp==data then tmp that is temporary will store the anomalities so you will lose them in a second
		# so the fact that data == tmp, the order of them is not randomic but well thought, dont move them
		if data == tmp:
			return -1

	if data.is_solved():
		return data.data
	return -1