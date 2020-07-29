#!/usr/bin/env python


import os
import sys

arguments = sys.argv

filein = arguments[1]
delim = arguments[2]
locuslist = []



inputopen = open(filein, "r")
line = inputopen.readline()
while line:
	if line[0] == ">":
		linesplit = line.strip(">").strip().split(delim)
		locus = linesplit[0]
		locuslist.append(locus)
		line = inputopen.readline()
	else:
		line = inputopen.readline()
inputopen.close()
locuslist = set(locuslist)
locuslist = list(locuslist)

identifier_lists = [[] for i in range(0, len(locuslist))]
#count_list = [[] for i in range(0, len(locuslist))]
count_list = [0]*len(locuslist)

inputopen = open(filein, "r")
line = inputopen.readline()
while line:
	if line[0] == ">":
		linesplit = line.strip(">").strip().split(delim)
		locus = linesplit[0]
		if delim + "comp" in line:
			identifier_number = locuslist.index(locus)
			half1, half2 = line.strip().rsplit(delim + delim, 1)
			halflist = half1.split(delim)
			del(halflist[0])
			half1 = delim.join(halflist)
			identifier_lists[identifier_number].append(half1)
			line = inputopen.readline()
		if delim + "R" in line:
			identifier_number = locuslist.index(locus)
			line = line.strip()
			linelist = line.split(delim+delim)
			del(linelist[0])
			linestring = ''.join(linelist)
			identifier_lists[identifier_number].append(linestring)
			line = inputopen.readline()
		else:
			line = inputopen.readline()
	else:
		line = inputopen.readline()
inputopen.close()

tableout = open("tableout.txt", "w")
for locus in locuslist:
	tableout.write("\t"+locus)
tableout.write("\n")

identifier_list_all = sum(identifier_lists, [])

for identifier in set(identifier_list_all):
	tableout.write(identifier)
	count_number = 0
	for list in identifier_lists:
		count = list.count(identifier)
		tableout.write("\t" + str(count))
		current = count_list[count_number] + count
		count_list[count_number] = current
		count_number = count_number + 1
	count2 = identifier_list_all.count(identifier)
	tableout.write("\t" + str(count2))
	tableout.write("\n")

for number in count_list:
	tableout.write("\t" + str(number))	
tableout.close()

