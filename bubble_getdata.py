import json
import re

#build tag index
with open('paper_tag.json') as t:
	tag_data = json.load(t)

with open("tag_file.json") as f:
	data = json.load(f)

code2 = dict()
code4 = dict()
code6 = dict()

index6 = dict()
index4 = dict()
index2 = dict()

# create code/name index for each level
for level2 in data.keys():
	for level4 in data[level2]:
		for level6 in data[level2][level4]:
			level6_index = re.findall(r'\d+', level6)[0]
			level6_name = re.findall(r'\d+\s(.+$)', level6)[0]
			index6[level6_name.lower()] = level6_index

		level4_index = re.findall(r'\d+', level4)[0]
		level4_name = re.findall(r'\d+\s(.+$)', level4)[0]
		index4[level4_name.lower()] = level4_index

	level2_index = re.findall(r'\d+', level2)[0]
	level2_name = re.findall(r'\d+\s(.+$)', level2)[0]
	index2[level2_name.lower()] = level2_index

# collect labels and counts
for paper in tag_data:
	year = paper["date"]
	for tag_group in paper["tags"]:
		for tag in paper["tags"][tag_group]:
			temp_tag = tag.lower().rstrip()
			if "2 " in tag_group:
				try:
					index = index2[temp_tag]
					if index not in code2.keys():
						code2[index] = {}
					if year not in code2[index].keys():
						code2[index][year] = 0
					code2[index][year] += 1
					
				except (KeyError, TypeError):
					pass
			elif "4" in tag_group:
				try:
					index = index4[temp_tag]
					if index not in code4.keys():
						code4[index] = {}
					if year not in code4[index].keys():
						code4[index][year] = 0
					code4[index][year] += 1
				except (KeyError, TypeError):
					pass
			elif "6" in tag_group:
				try:
					index = index6[temp_tag]
					if index not in code6.keys():
						code6[index] = {}
					if year not in code6[index].keys():
						code6[index][year] = 0
					code6[index][year] += 1
				except (KeyError, TypeError):
					pass

# create profiles for each academic
group2 = []
for level2 in data.keys():
	group4 = []
	for level4 in data[level2]:
		group6 = []
		for level6 in data[level2][level4]:
			level6_index = re.findall(r'\d+', level6)[0]
			level6_name = re.findall(r'\d+\s(.+$)', level6)[0]
			try:
				size = sum(code6[level6_index].values())
				color = re.findall(r'^\d\d', level6_index)[0]
				item6 = {"id": level6_index, "name": level6_name, "size": size, "color": int(color), "year": code6[level6_index]}
				group6.append(item6)
			except KeyError:
				size = 0	
			
		level4_index = re.findall(r'\d+', level4)[0]
		level4_name = re.findall(r'\d+\s(.+$)', level4)[0]
		if group6:
			try:
				size = sum(code4[level4_index].values())
			except KeyError:
				size = 0
			color = re.findall(r'^\d\d', level4_index)[0]
			item4 = {"id": level4_index, "name": level4_name, "size": size, "children": group6, "color": color, "year": code4[level4_index]}
			group4.append(item4)
		
		
	level2_index = re.findall(r'\d+', level2)[0]
	level2_name = re.findall(r'\d+\s(.+$)', level2)[0]
	try:
		size = sum(code2[level2_index].values())
	except KeyError:
		size = 0
	color = re.findall(r'^\d\d', level2_index)[0]
	item2 = {"id": level2_index, "name": level2_name, "size": size, "children": group4, "color": color, "year": code2[level2_index]}
	group2.append(item2)

total_paper = 0
for paper in group2:
	sub = paper["size"]
	total_paper += sub

cis = {"id": 0, "name": "CIS", "children": group2, "color": 20, "size": total_paper}

# write to file
with open("new_bubble_data.json", 'w') as outfile:
 	json.dump(cis, outfile)




