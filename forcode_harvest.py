import re
import json
from urllib2 import urlopen
from bs4 import BeautifulSoup


def get_link(url):
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    chapitems = soup.findAll('tr', {'id': 'chapitem'})
    chapitem_list = []
    chapitem_link = []
    for chapitem in chapitems:
        chapitem = chapitem.find('a', href=True)
        chapitem_list.append(chapitem.text)
        chapitem_link.append(chapitem.get('href'))
    return chapitem_list, chapitem_link


def get_item(url):
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    printcontent = soup.find('div', {'id': 'printcontent'})
    for result in printcontent.findAll('ul'):
        if len(result.attrs) == 0:
            pattern = re.compile(r'\d{6}.*\n')
            #.*(?=Exclusion)
            match = pattern.findall(result.text)
            return [item.strip() for item in match]


url = 'http://www.abs.gov.au/Ausstats/abs@.nsf/Latestproducts/6BB427AB9696C225CA2574180004463E?opendocument'
group_url = 'http://www.abs.gov.au/Ausstats/abs@.nsf/Latestproducts/'
divisions, division_links = get_link(url)
division_dict = {}

for i in range(len(divisions)):
    group_dict = {}
    division = divisions[i].strip().split(' ', 2)[2]
    _group_url = group_url + division_links[i]
    groups, group_links = get_link(_group_url)
    for j in range(len(groups)):
        group = groups[j].strip().split(' ', 2)[2]
        _field_url = group_url + group_links[j]
        print _field_url
        fields = get_item(_field_url)
        group_dict.setdefault(groups[j], fields)
    division_dict.setdefault(divisions[i], group_dict)

f = json.dumps(division_dict, sort_keys=True, indent=4, separators=(',', ': '))
jsonFile = open('tag_file.json', 'w')
jsonFile.write(f)
jsonFile.close()



