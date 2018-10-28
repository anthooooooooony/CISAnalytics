
from urllib2 import urlopen
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import string
import re
import time

from multiprocessing import Pool
import pycouchdb as couchdb

#reload(sys)
#sys.getdefaultencoding()


def getPaper():
    server = couchdb.Server('http://admin:11112222@localhost:5984/')
    db = server.database('paper_cis_replicate')

    l = []
    paper_list = list(db.query("testing/AllPaper"))
    for paper in paper_list:
        l.append(paper['key'])
    return l


'''
def getLinks():

    title_list = getTitles()
    driver = webdriver.Chrome()
    link_list = []
    for title in title_list:
        title = title.replace(' ', '%20')
        url = 'https://search.unimelb.edu.au/?q=' + title + '&page=1'
        print url
        driver.get(url)
        try:
            WebDriverWait(driver, 5, 0.5).until(
                lambda driver: driver.find_element_by_partial_link_text('findanexpert'))
            link_list.append(driver.find_element_by_partial_link_text('findanexpert').get_attribute('href'))
        except TimeoutException:
            link_list.append('')
            print
        except UnicodeError:
            # TODO needs to fix the greek char encoding issue
            link_list.append('')
            print
    driver.close()


def extraction(link):
    page = urlopen(link)
    soup = BeautifulSoup(page, 'html.parser')

'''


experts_url = 'https://findanexpert.unimelb.edu.au/display/org4257'



expert_dict = {}
experts_page = urlopen(experts_url)
soup = BeautifulSoup(experts_page, 'html.parser')
for item in soup.find('ul', {'class': 'property-list'}).findAll('li'):
    a = item.find('a', href=True)
    expert_dict[a.text] = a['href']


def get_author_page(author, expert_dict):
    author = author.split()
    compile_author = author[1] + '\w* ' + author[0]
    for key in expert_dict.keys():
        if re.search(r'' + compile_author, key):
            return key, expert_dict[key]


def extration(url, title):

    def tag_extraction(paper_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        try:
            page = requests.get(paper_url, headers=headers, timeout=5)
        except:
            print 'Error! Skip'
            return {}

        soup = BeautifulSoup(page.text, 'html.parser')
        articles = soup.find('section', {'class': 'property-group'})\
            .findAll('article', {'class': 'property'})
        for article in articles:
            if article.find('h3').text.strip() == 'Has subject area':
                tag_dict = {}
                for subclass in article.findAll('li', {'class': 'subclass'}):
                    l = []
                    for listitem in subclass.findAll('a'):
                        l.append(listitem.text)
                    tag_dict.setdefault(subclass.find('h3').text, l)
                return tag_dict

    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    sections = soup.findAll('section', {'class': 'property-group'})
    for section in sections:
        if section.find('h2').text == 'Publications':
            papers = section.findAll('li', {'role': 'listitem'})
            for paper in papers:
                paper_title = paper.find('a').text.strip().strip('.')
                if re.search(re.escape(title.strip('.')), paper_title, re.I):
                    href = paper.find('a', href=True)['href']
                    href = href.replace('individual', 'display')
                    href = 'https://findanexpert.unimelb.edu.au/' + href
                    tags = tag_extraction(href)
                    return tags

            #return

    #for item in soup.find('ul', {'class': 'property-list'}).findAll('li', {'role': 'listitem'}):
    #    print item


title_tags = {}

paper_list = getPaper()
for paper in paper_list:
    print paper['title']
    author_list = paper['author(s)']
    for author in author_list:
        try:
            a, b = get_author_page(author, expert_dict)
        except TypeError:
            continue
        #
        b = b.replace('individual', 'display')
        author_url = 'https://findanexpert.unimelb.edu.au' + b + '#tab-publications'
        title = paper['title']
        tags = extration(author_url, title)
        paper.setdefault('tags', tags)
        del paper['_rev']
        del paper['_id']
        break


couchserver = couchdb.Server('http://admin:11112222@localhost:5984/')
dbname = 'tag_paper'
if dbname in couchserver:
    db = couchserver.database(dbname)
else:
    db = couchserver.create(dbname)

count_multipro = 1
for item_rslt in paper_list:
    if item_rslt is not None:
        db.save(item_rslt)














