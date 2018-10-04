import pycouchdb as couchdb
from tag_class import ForCode


def getPaper():
    server = couchdb.Server('http://admin:11112222@localhost:5984/')
    db = server.database('tag_paper')
    l = []
    paper_list = list(db.query("testing/AllPaper"))
    for paper in paper_list:
        l.append(paper['key'])
    return l


def getTags(tags, for_code_class):
    tag_dict = {
        'For 2008 6 Digit Code': [],
        'For 2008 4 Digit Code': [],
        'For 2008 2 Digit Code': []
    }

    if tags is None:
        return tag_dict
    group_flag = 'For 2008 4 Digit Code' in tags.keys()
    division_flag = 'For 2008 2 Digit Code' in tags.keys()
    group_list = tags['For 2008 4 Digit Code'] if group_flag else []
    group_list = [group.title() for group in group_list]
    division_list = tags['For 2008 2 Digit Code'] if division_flag else []

    if 'For 2008 6 Digit Code' in tags:
        tag_dict['For 2008 6 Digit Code'] = \
            tag_dict.get('For 2008 6 Digit Code') + tags['For 2008 6 Digit Code']
        for tag in tags['For 2008 6 Digit Code']:
            tag_ins = for_code_class.search(tag, 'field')

            if tag_ins is None:
                continue

            group, _ = tag_ins.getGroup()
            group = group.title()
            division, _ = tag_ins.getDivision()
            division = division.upper()

            if group not in group_list:
                group_list.append(group)
            if division not in division_list:
                division_list.append(division)

            tag_dict['For 2008 4 Digit Code'] = group_list
            tag_dict['For 2008 2 Digit Code'] = division_list

    if group_flag:
        for tag in tags['For 2008 4 Digit Code']:
            tag_ins = for_code_class.search(tag, 'group')
            if tag_ins is None:
                continue

            division, _ = tag_ins.getDivision()

            if division not in division_list:
                division_list.append(division)

            tag_dict['For 2008 2 Digit Code'] = division_list

    return tag_dict

forcode = ForCode()
# PubMed count 139

'''
tags = {u'Seo 2008 6 Digit Code':
            [u'Hearing, Vision, Speech and Their Disorders', u'Human Diagnostics'],
        u'For 2008 6 Digit Code': [u'Computer Software not elsewhere classified ',
                                   u'Optometry and Ophthalmology not elsewhere classified']}

print getTags(tags, forcode)


'''

paper_list = getPaper()
for i in range(len(paper_list)):
    if 'tags' in paper_list[i]:
        tags = paper_list[i]['tags']
        paper_list[i]['tags'] = getTags(tags, forcode)


couchserver = couchdb.Server('http://admin:11112222@localhost:5984/')
dbname = 'updated_tag_paper'
if dbname in couchserver:
    db = couchserver.database(dbname)
else:
    db = couchserver.create(dbname)

for paper in paper_list:
    if paper is not None:
        del paper['_rev']
        del paper['_id']
        db.save(paper)