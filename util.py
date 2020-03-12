import copy

from pygraham import *

RANK = 3
DEBUG = 0

def show(matrix):
	for i in matrix:
		for j in i:
			for k in j:
				print(k, end = '')

			print(" ",end='')
		print()

def dprint(*args):
	if DEBUG==1:
		print(*args)

def squeze_all(matrix):
	for i in range(len(matrix)):
		if (type(matrix[i])!=int) and (len(matrix[i])==1):
			matrix[i] = matrix[i][0]
		for j in range(len(matrix[i])):
			if (type(matrix[i][j]) != int) and (len(matrix[i][j]) == 1):
				matrix[i][j] = matrix[i][j][0]
			if type(matrix[i][j]) != int:
				for k in range(len(matrix[i][j])):
					if (type(matrix[i][j][k]) != int) and(len(matrix[i][j][k]) == 1):
						matrix[i][j][k] = matrix[i][j][k][0]

	return matrix

class Sudodata():
	def __init__(self, matrix):
		self.data = list(matrix)
		self.cycles = {}

	def cell_rc(self,r,c):
		return self.data[r][c//RANK][c%RANK]

	def assign_cell_rc(self,r,c,v):
		self.data[r][c//RANK][c%RANK] = v

	def cell_rtc(self,r,t,c):
		return self.data[r][t][c]

	def column(self,c):
		return list([self.data[i][c//RANK][c%RANK] for i in range(RANK*RANK)])

	def assign_column(self,c,v):
		for i in range(RANK * RANK):
			self.data[i][c//RANK][c%RANK] = v[i]

	def row(self,r):
		return list([self.data[r][i//RANK][i%RANK] for i in range(RANK*RANK)])

	def assign_row(self,r,v):
		for i in range(RANK * RANK):
			self.data[r][i//RANK][i%RANK] = v[i]

	def triplet(self,r,t):
		return list(self.data[r][t])

	def cell_transform(self):
		for i in range(RANK*RANK):
			for j in range(RANK * RANK):
				self.assign_cell_rc(i,j,int(self.cell_rc(i,j)))

	def cell_iter(self):
		for i in range(RANK*RANK):
			for j in range(RANK * RANK):
				yield self.cell_rc(i,j)

	def row_iter(self):
		for i in range(RANK*RANK):
			yield self.row(i)

	def col_iter(self):
		for i in range(RANK*RANK):
			yield self.column(i)

	def box_iter(self):
		for v in range(RANK):
			for i in range(RANK):
				box = []
				for j in range(RANK):
					for k in range(RANK):
						box += [self.cell_rc(v*RANK + j,i*RANK+k)]
				yield box

	def cell_transformer(self, l):
		for i in range(RANK*RANK):
			for j in range(RANK * RANK):
				self.assign_cell_rc(i,j, l(self.cell_rc(i,j)))

	def row_transformer(self, l):
		for i in range(RANK*RANK):
			self.assign_row(i, l(self.row(i)))

	def col_transformer(self, l):
		for i in range(RANK*RANK):
			self.assign_column(i, l(self.column(i)))

	def box_transformer(self, l):
		for v in range(RANK):
			for i in range(RANK):
				box = []
				for j in range(RANK):
					for k in range(RANK):
						box += [(v*RANK + j, i*RANK+k)]

				l(box)

	def __iter__(self):
		for i in range(RANK*RANK):
			for j in range(RANK*RANK):
				yield self.cell_rc(i,j)

	def __eq__(self, other):
		for i in range(RANK*RANK):
			for j in range(RANK*RANK):
				if self.cell_rc(i, j) != other.cell_rc(i, j):
					return False
		return True

	def check_cycles(self, other):
		for i in range(RANK*RANK):
			for j in range(RANK*RANK):
				# ambiguity manifests when the cells are different but they are cyclic and at the end you cannot solve the cycle
				# ambiguity/cycles are typical of difficult sudokus where there are too few known values
				if self.cell_rc(i, j) != other.cell_rc(i, j):
					mm = str(self.cell_rc(i, j)).replace(" ", "").replace(",", "").replace("[", "").replace("]", "")
					if mm not in self.cycles:
						self.cycles[mm] = 1
					else:
						self.cycles[mm] += 1
						if self.cycles[mm] > 15:
							print("hai cicli non risolvibili, opera una scelta")
							return True
		return False

	def is_solved(self):
		for i in range(RANK*RANK):
			for j in range(RANK*RANK):
				if type(self.cell_rc(i,j)) != int:
					return False
		return True

	def hash(self):
		hashed = ''
		for i in range(RANK*RANK):
			for j in range(RANK*RANK):
				# hashing is not unique but it's okay
				if type(self.cell_rc(i,j)) == int:
					hashed += str(i)+str(j)+str(self.cell_rc(i,j))+"-"
				else:
					hashed += str(i) + str(j) + str(sum(self.cell_rc(i, j))) + "-"

		return hashed[:len(hashed)-1]

	def save(self):
		pass

	def choose(self):
		pass


def solve(matrix):
	print("-----------------------------")
	dprint("setup")

	data = Sudodata(matrix)
	exclude = []
	moves = -1

	for i in range(1000):
		tmp = copy.deepcopy(data)
		dprint("-----------------------------")
		dprint("box prop")

		def box_prop(box_indexes):
			for r, c in box_indexes:
				if type(data.cell_rc(r,c)) == int:
					exclude.append(data.cell_rc(r,c))

			for r, c in box_indexes:
				if type(data.cell_rc(r,c)) != int:
					data.assign_cell_rc(r,c,list(set(data.cell_rc(r,c)) - set(exclude)))

			exclude.clear()

		data.box_transformer(box_prop)

		dprint("-----------------------------")
		dprint("col prop")

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

		dprint("-----------------------------")
		dprint("row prop")

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

		dprint("-----------------------------")
		dprint("squeezing")

		def squeeze(row):
			for i in range(len(row)):
				if (type(row[i]) != int) and (len(row[i])==1):
					row[i] = row[i][0]

			return row

		data.row_transformer(squeeze)

		if (data == tmp) and (not data.is_solved()):
			# then you should take a decision to change this fact
			data.save() # this should save the matrix
			data.choose() # this should take a decision
			# all matrices saved are encoded so there is history of them
			# every hoistory-matrix is associated hashed so the comparation with a new one is very fast
			# if no choice is new then you have to backtrack to the first one available going in the very past


		# this point is the most difficult of all the program PAY ATTENTION:
		# if you do tmp==data then tmp that is temporary will store the anomalities so you will lose them in a second
		# so the fact that data == tmp, the order of them is not randomic but well thought, dont move them
		if data == tmp:
			dprint("stopped at iteration:", i)
			moves = i
			break

		if data.check_cycles(tmp):
			print("stopped at iteration: ", i,"for cycles")
			moves = i
			break

		if i == 100:
			dprint("ci sta mettendo troppo, siamo a 100 mosse")
			pass

	dprint("result is:")

	for row in data.row_iter():
		dprint(row)

	if data.is_solved():
		print("SOLVED in ", moves, "moves")
		print(data.hash())
	else:
		print("NOT solved in ", moves, "moves")