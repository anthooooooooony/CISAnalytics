import json
import re

with open('paper_tag.json') as f:
	data = json.load(f)

#build topic index
with open('tag_file.json') as ftag:
	tag_data = json.load(ftag)

color_ind = {}
reverse_ind = {}
for tag2 in tag_data:
	code = re.findall(r'(\d+)\s.+$', tag2)[0]
	title = re.findall(r'\d+\s(.+$)', tag2)[0]
	color_ind[title] = int(code)
	reverse_ind[code] = title
print(reverse_ind)

code_ind = {}
for tag2 in tag_data:
	for tag4 in tag_data[tag2]:
		code = re.findall(r'(\d\d)\d+\s.+$', tag4)[0];
		title = re.findall(r'\d+\s(.+$)', tag4)[0];
		code_ind[title] = code;


def name_unify(name):
	modify = re.findall(r'(.+\s\w)\w+$', name)
	if modify:
		return modify[0]
	else:
		return name

#put unified names in cowork
co_author = []
for paper in data:
	co_author.append(paper['author(s)'])
for paper in co_author:
	for i, author in enumerate(paper):
		unified = name_unify(author)
		paper[i] = unified

distr = {}

for paper in data:
	tags = paper["tags"]["For 2008 4 Digit Code"]
	for author in paper['author(s)']:
		if author not in distr.keys():
			distr[author] = {}
		for tag in tags:
			if tag not in distr[author].keys():
				distr[author][tag] = 0
			distr[author][tag] += 1

#all academics into dict
author_dict = dict()
for paper in co_author:
	for author in paper:
		author_dict[author] = author_dict.get(author, 0) + 1

rank = {}

for people in distr:
	temp_sort = sorted(distr[people], key=distr[people].get, reverse = True)
	temp_rank = []
	for i in range(len(temp_sort)):
		rank_title = temp_sort[i].upper();
		# print(rank_title);
		temp_tuple = (rank_title, distr[people][temp_sort[i]], int(code_ind[rank_title]), reverse_ind[code_ind[rank_title]])
		temp_rank.append(temp_tuple)
	rank[people] = temp_rank
	

#all nodes with id, name and no. of papers
nodes = []
index = 0
for author in sorted(author_dict):
	try:
		color = code_ind[rank[author][0][0]]
	except IndexError:
		color = -1
	academic = {"name": author, "id": index, "papers": author_dict[author], "rank": rank[author], "code": int(color)}
	index += 1
	nodes.append(academic)



#create id index
id_index = dict()
for academic in nodes:
	id_index[academic["name"]] = academic["id"]

#all pairs of coworkers
pairs = []
for paper in co_author:
	for p1 in range(len(paper)):
		for p2 in range(p1+1,len(paper)):
			pairs.append(sorted([paper[p1],paper[p2]]))

#count each pair
pair_dict = dict()
for pair in sorted(pairs):
	pair = tuple(pair)
	pair_dict[pair] = pair_dict.get(pair, 0) + 1

# all links
links = []
for pair in pair_dict.keys():
	link = {"source": id_index[pair[0]], "target": id_index[pair[1]], "weight": pair_dict[pair]}
	links.append(link)

relation_data = {}
relation_data.update({"nodes": nodes})
relation_data.update({"links": links})
print(relation_data)

# write to file
with open('fdg_cis5.json', 'w') as outfile:
	json.dump(relation_data, outfile)
