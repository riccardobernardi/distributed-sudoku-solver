# Distributed Sudoku Solver

Author: Riccardo Bernardi

E-mail: 864018@stud.unive.it

The code and the report were entirely developed only by Riccardo Bernardi.

## Table of Contents

- 1 Background
- 2 Web Scraping
- 3 Data Model
- 4 Constraint Propagation
- 5 BackTracking
- 6 Distributed Computation
- 7 Results
- 8 Conclusions
- 9 Bibliography

## 1 Background

The sudoku is a challenging game about finding the proper numbers that can stay in a certain cell of a 9x9 square. A number is correct when it respects the constraints of:

- 1 only one number with same value on the same row, column and 3x3 box
- 2 on the same row, column and 3x3 box have to be every number from 1 to 9 in only one copy

Some numbers at the start of the game are already provided on the sudoku and cannot be modified, you can only insert new numbers.

Another important notice about sudokus is that a sudoku that is correct should have exactly one solution, this is very important because asserting this fact will allow us to search for a solution with the certainty of converging.

Constraint Propagation is about taking the rule as written before and building a method that checks that fact but my implementation works in a different way, it prunes wrong solutions from possible ones. In particular at the very start every 0 cell(void cells to be calculated) are substituted by an array [1...9] and the **propagate_constraints** function will prune wrong ones.

The easiest puzzles will be solved by just doing the steps before but for the hardest ones you will need to apply **backtracking** that is about searching for all possible solutions in the puzzle until the only one solution is found. If a wrong one is found it is ignored.

The author is a passionate sudoku solver and a passionate python programmer so you will find additions with respect to the basic assignment's requests.

Some libraries that were used in the assignment are previous projects of the author published on PYPI, in these cases will be put references.



## 2 Web Scraping



- checking the repetitions - antilagiarism
- some functional constructs - pygraham



## 3 Data Model



## 4 Constraint Propagation



## 5 BackTracking



## 6 Distributed Computation



## 7 Results



## 8 Conclusions



## 9 Bibliography







## Features

- webscraping from many sources
- constraint propagation
- distributed computation on a cluster
- check of similarity between sudokus
- ~2000 sudokus to evaluate performances