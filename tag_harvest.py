
from urllib2 import Request, urlopen

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


def getTitles():
    server = couchdb.Server('http://admin:11112222@localhost:5984/')
    db = server.database('paper_cis')

    l = []
    paper_list = list(db.query("testing/Titles"))
    for paper in paper_list:
        l.append(paper['key'])

    return l


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


getLinks()








