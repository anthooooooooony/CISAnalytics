import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import couchdb


def text_processing(text):
    # Lower casing
    text = text.lower()

    # Remove special punctuation
    for c in string.punctuation:
        text = text.replace(c, ' ')

    # Tokenisation
    word_list = nltk.word_tokenize(text)

    # Remove stopwords
    filtered = [w for w in word_list if w not in stopwords.words('english')]

    # Only NN word reserved
    refiltered = nltk.pos_tag(filtered)
    filtered = [w for w, pos in refiltered if pos.startswith('NN')]

    # Stemming
    #ps = PorterStemmer()
    #filtered = [ps.stem(w) for w in filtered]

    return " ".join(filtered)


def normalization():

    server = couchdb.Server('http://admin:11112222@localhost:5984/')
    db = server['paper_cis_replicate']

    def getPaper():

        l = []
        paper_list = list(db.view("testing/AllPaper"))
        for paper in paper_list:
            l.append(paper['key'])
        return l


    papers = getPaper()
    for paper in papers:
        print paper
        # Remove periods at the end of titles
        paper['title'] = paper['title'].strip('.')

        # Remove commas in names
        paper['author(s)'] = [author.replace(',', ' ') for author in paper['author(s)']]

        # Filter out published year
        regex = '(19|20)\d{2}'
        for item in paper['date']:
            if re.match(regex, item):
                paper['date'] = item
                break

        for paper2 in papers:
            if (paper['_id'] != paper2['_id']) and\
                    (paper['title'].lower() == paper2['title'].lower()):
                db.delete(paper)


    db.update(papers)



normalization()