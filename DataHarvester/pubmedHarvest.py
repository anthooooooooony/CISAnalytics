from urllib2 import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import string
import re
import time
from multiprocessing import Pool
import pycouchdb as couchdb

start_time = time.time()

home_page = 'https://www.ncbi.nlm.nih.gov/pubmed/'
url = "https://www.ncbi.nlm.nih.gov/pubmed/?" \
      "term=computing+and+information+systems+university+of+melbourne"
first_page = urlopen(url)
soup_first = BeautifulSoup(first_page, 'html.parser')
last_page = int(soup_first.find('input', {'id': 'pageno'}).get('last'))

all_links = []
count = 1
link_no = 1


def extraction(http):
    #print 'url: {}'.format(http)
    page = urlopen(http)
    soup = BeautifulSoup(page, 'html.parser')
    pub = {}

# get Author step 1
# get author id
    all_auths = {}
    target_index = []
    try:
        for item in soup.find('div', {'class': 'afflist'}).findAll('dt'):
            try:
                all_auths[int(item.text)] = item.next_sibling.text
            except ValueError:
                pass
    except AttributeError:
        return
    #print 'afflist: {}'.format(all_auths)

    for key in all_auths:
        if re.search(r'computing (&|and) information systems', all_auths[key], re.I) \
                and re.search(r'university of melbourne', all_auths[key], re.I):

            target_index.append(key)
    if not target_index:
        return
    #print 'target index: {}'.format(target_index)

# get Author step 2
# get List index
    author_list = {}
    for item in soup.find('div', {'class': 'auths'}).findAll('a'):
        author = item.text
        try:
            if item.next_sibling.text in string.punctuation:
                item = item.next_sibling
            next_item = int(re.sub(r',', '', item.next_sibling.text))
        except AttributeError:
            next_item = 'not int'

        indices = []
        while isinstance(next_item, int):
            item = item.next_sibling
            try:
                next_item = int(re.sub(r',', '', item.text))
                indices.append(next_item)
            except(ValueError, AttributeError):
                next_item = 'not int'
        author_list[author] = indices

# get Author step3
# get target author(could be a list)
    target_auth = []
    for index in target_index:
        for author in author_list:
            if index in author_list[author]:
                target_auth.append(author)
    if not target_auth:
        return
    print 'target authors: {}'.format(target_auth)
    pub.update({'author(s)': target_auth})

# get Title
    div = soup.find('div', {'class': 'rprt abstract'}).h1
    pub.update({'title': div.text})

# get abstract
    abstr = ''
    try:
        raw_abstr = soup.find('div', {'class': 'abstr'}).div
    except AttributeError:
        raw_abstr = ''
    try:
        unwanted = raw_abstr.find('p', {'class': 'copyright'})
        unwanted.extract()
    except(AttributeError, TypeError):
        pass
    for item in raw_abstr:
        abstr += item.text
    # find all with tag div and class 'abstr'
    pub.update({'abstract': abstr.strip()})


# get keywords
    try:
        keywords = soup.find('div', {'class': 'keywords'}).find('p').text.lower().split('; ')
    except AttributeError:
        keywords = []
    pub.update({'keywords': keywords})

# get date and year
    metadata = soup.find('meta', {'name': 'description'})
    raw_date = metadata.attrs['content']
    yymmdd = re.split('[,.;]', raw_date)[1].strip().split(' ')
    pub.update({'date': yymmdd})

    return pub


def get_link():
    link_list = []
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    for rslt in soup.findAll('div', {'class': 'rslt'}):
        link = home_page + rslt.find('dd').text
        link_list.append(link)
    try:
        browser.find_element_by_xpath('//a[@title="Next page of results"]').click()
    except NoSuchElementException:
        pass
    return link_list


browser = webdriver.Chrome()
browser.get(url)

while count <= last_page:
    all_links += get_link()
    count += 1
browser.close()

p = Pool(24)
records = p.map(extraction, all_links)
p.terminate()
p.join()


couchserver = couchdb.Server('http://admin:11112222@localhost:5984/')
dbname = 'paper_cis'
if dbname in couchserver:
    db = couchserver.database(dbname)
else:
    db = couchserver.create(dbname)

count_multipro = 1
for item_rslt in records:
    final_rslt = item_rslt
    if final_rslt is not None:
        db.save(final_rslt)


print((time.time()-start_time)/60)
