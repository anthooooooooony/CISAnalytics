import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


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
