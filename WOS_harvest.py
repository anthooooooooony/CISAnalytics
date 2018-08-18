from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import pycouchdb as couchdb

usn = # username
psw = # password
wos = 'http://apps.webofknowledge.com.ezp.lib.unimelb.edu.au/'


def item_extract():
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    data = {}

    # get author step 1
    # get address index
    addr_index = {}
    try:
        for item in soup.findAll('a', id=re.compile("addressWOS")):
            address = item.text
            index = int(re.findall(r'\d+', address)[0])
            name = re.findall(r']\s(.+)', address)[0]
            addr_index[index] = name
    except AttributeError:
        return
    target_index = []
    search_words = ['Comp', 'Informat Syst']
    for key in addr_index:
        addr = addr_index[key]
        if all(key in addr for key in search_words) or 'CIS' in addr and 'Univ Melbourne' in addr:
            target_index.append(key)
    if not target_index:
        return

    # get author step 2
    # get author index
    author_index = {}
    try:
        for item in soup.find('span', text="By:").parent.findAll('a', {'title': "Find more records by this author"}):
            author = item.text
            indices = []
            for digit in item.next_sibling.next_sibling.findAll('a'):
                indices.append(int(digit.text))
            author_index[author] = indices
    except AttributeError:
        return

    # get author step 3
    # get target author
    target_author = []
    for index in target_index:
        for author in author_index:
            if index in author_index[author]:
                target_author.append(author)
    data.update({'author(s)': target_author})

    # get title
    title = soup.find('div', {'class': "title"}).value.text
    data.update({'title': title})

    # get abstract
    abstr = ''
    try:
        abstr = soup.find('div', text="Abstract").next_sibling.next_sibling.text
    except AttributeError:
        pass
    data.update({'abstract': abstr})

    # get keywords
    keywords_list = set()
    try:
        keywords = soup.find('div', text="Keywords").parent
        for item in keywords.findAll('p'):
            for word in item.findAll('a'):
                keywords_list.add(word.text.lower())
    except AttributeError:
        pass
    data.update({'keywords': list(keywords_list)})

    # get date
    date = soup.find('span', text="Published:").next_sibling.lower()
    date = date.split(' ')
    data.update({'date': date})

    return data

chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chromeOptions.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(chrome_options=chromeOptions, executable_path='/Users/lanzzzzl/chromedriver')
browser.get(wos)

# find username and password element
username = browser.find_element_by_name('username')
password = browser.find_element_by_name('password')
# send username and password
username.send_keys(usn)
password.send_keys(psw)

# click login button
signin = browser.find_element_by_xpath('//button[@class="button cta"]')
browser.execute_script('arguments[0].click()', signin)

# select adv search
browser.find_element_by_xpath('//a[@title="Use Advanced Search to Narrow Your Search to Specific Criteria"]').click()


# input searchbox
browser.find_element_by_tag_name("textarea").clear()
search_box = browser.find_element_by_tag_name('textarea')
# search_keyword = 'AD=(Univ Melbourne AND ((Comp AND Informat Syst) OR CIS))'
search_keyword = 'AD=(Univ of Melbourne)'
search_box.send_keys(search_keyword)

# click search button
browser.find_element_by_id("search-button").click()

# get result from history
browser.find_element_by_xpath('//div[@id="set_1_div"]//a[@title="Click to view the results"]').click()

# iterate each article
element = WebDriverWait(browser, 10).until(EC.element_to_be_clickable(
    (By.XPATH, '//div[contains(@id, "RECORD_1")]/div[@class="search-results-content"]/div/div/a')))
element.click()

couchserver = couchdb.Server('http://127.0.0.1:5984')
dbname = 'data'
if dbname in couchserver:
    db = couchserver.database(dbname)
else:
    db = couchserver.create(dbname)

no = 1
while True:
    extracted = item_extract()
    if extracted is not None:
        db.save(extracted)
    no += 1
    try:
        browser.find_element_by_xpath('//a[@title="Next Page"]').click()
    except NoSuchElementException:
        browser.close()
        break
