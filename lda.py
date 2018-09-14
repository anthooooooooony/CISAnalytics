import pycouchdb
import pandas as pd
from util import text_processing

server = pycouchdb.Server('http://admin:11112222@localhost:5984/')
db = server.database('paper_cis')

paper_list = list(db.query("testing/names"))

title_list, authors_list, abstract_list, keywords_list, date_list = [], [], [], [], []
for item in paper_list:
    paper = item['key']
    abstract_list.append(text_processing(paper['abstract']))
    title_list.append(paper['title'])
    keywords_list.append(paper['keywords'])

# ======================================================================================================================
# Frequency counting
#

from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.externals import joblib

tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
tf = tf_vectorizer.fit_transform(abstract_list)

# ======================================================================================================================
# Topic modelling
#

from sklearn.decomposition import LatentDirichletAllocation
n_topics = 30


lda = LatentDirichletAllocation(
                                learning_method='online',
                                doc_topic_prior=0.1,
                                n_components=30,
                                perp_tol=0.1,
                                topic_word_prior=0.2
                                )
lda.fit(tf)
print lda.perplexity(tf)


def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print "Topic #{}:".format(topic_idx)
        print " ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]])


def print_doc_topic(model, topic_index):
    for i in range(topic_index):
        print 'Document #{}: Topic #{}:'.format(i, model[i].argmax())


tf_feature_names = tf_vectorizer.get_feature_names()
print_top_words(lda, tf_feature_names, n_top_words=40)
print
print_doc_topic(lda.transform(tf), topic_index=20)

for i in range(10):
    print abstract_list[i]


# ======================================================================================================================
# Parameter Tuning
#
'''
from sklearn.model_selection import GridSearchCV

parameters = {
              'learning_method': ('batch', 'online'),
              'n_components': range(30, 75, 5),
              'perp_tol': (0.001, 0.01, 0.1),
              'doc_topic_prior': (0.001, 0.01, 0.05, 0.1, 0.2),
              'topic_word_prior': (0.001, 0.01, 0.05, 0.1, 0.2)
              }
lda = LatentDirichletAllocation()
model = GridSearchCV(lda, parameters, verbose=2)
model.fit(tf)
df = pd.DataFrame.from_dict(model.cv_results_)
print df.sort_values(by='rank_test_score')
'''


