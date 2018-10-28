import json
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Read data and re-format
DATAFILE = 'paper_tag.json'

with open(DATAFILE, 'r') as f:
    data = f.read()
    data = json.loads(data)

# Count all For codes
code2d, code4d, code6d = {}, {}, {}

for paper in data:
    for code in paper['tags']['For 2008 2 Digit Code']:
        code2d.setdefault(code, 0)
    for code in paper['tags']['For 2008 4 Digit Code']:
        code4d.setdefault(code, 0)
    for code in paper['tags']['For 2008 6 Digit Code']:
        code6d.setdefault(code, 0)

counter_code = {}
d = {'code2': code2d, 'code4': code4d, 'code6': code6d}
total_year = {}

for paper in data:
    year = paper['year']
    if year:
        counter_code.setdefault(year, copy.deepcopy(d))
        total_year.setdefault(year, 0)
        for code in paper['tags']['For 2008 2 Digit Code']:
            counter_code[year]['code2'][code] += 1
            total_year[year] += 1
        for code in paper['tags']['For 2008 4 Digit Code']:
            counter_code[year]['code4'][code] += 1
            total_year[year] += 1
        for code in paper['tags']['For 2008 6 Digit Code']:
            counter_code[year]['code6'][code] += 1
            total_year[year] += 1

years = sorted(counter_code.keys())
total_year = [total_year[year] for year in years]


def overview(counter):
    code2_year, code4_year, code6_year = [], [], []
    code2_name, code4_name, code6_name = [], [], []

    for code, _ in counter[years[0]]['code2'].items():
        code2_name.append(code)
    for code, _ in counter[years[0]]['code4'].items():
        code4_name.append(code)
    for code, _ in counter[years[0]]['code6'].items():
        code6_name.append(code)

    for year in years:
        code2_year.append([num for (code, num) in counter[year]['code2'].items()])
        code4_year.append([num for (code, num) in counter[year]['code4'].items()])
        code6_year.append([num for (code, num) in counter[year]['code6'].items()])

    for code4 in code2_name:
        print code4
    # Pattern Recognition and Data Mining 10,
    # Artificial Intelligence and Image Processing not elsewhere classified 52,
    # Database Management 57,
    # Computer-Human Interaction 65,
    # Distributed and Grid Systems 103,
    # Distributed Computing not elsewhere classified 124,
    # Programming Languages 125,
    # Operating Systems 128
    indice = [10, 52, 57, 65, 103, 124, 125, 128]
    code6labels = ['Pattern Recognition and Data Mining',
                   'Artificial Intelligence and Image Processing not elsewhere classified',
                   'Database Management',
                   'Computer-Human Interaction',
                   'Distributed and Grid Systems',
                   'Distributed Computing not elsewhere classified',
                   'Programming Languages',
                   'Operating Systems']


    fig, axs = plt.subplots(len(years), 1, sharex=True, sharey=True)
    for i in range(len(years)):
        axs[i].vlines(code6_name, [0], code6_year[i], lw=2)
        axs[i].grid(True)
        axs[i].set_title(years[i].title(), fontsize=10)
        axs[i].set_xticks(indice)
        axs[i].set_xticklabels(code6labels, fontsize=6, rotation=90)
        axs[i].tick_params(axis='both', which='both', bottom=False, top=False,
                           left=False, right=False, labelleft=True)


    plt.show()

#fig[1,2,3]
#overview(counter_code)


def topk_year(k, counter):
    years = sorted(counter.keys())
    code4_topk_year = {}

    for i in range(len(years)):
        year = years[i]
        s = sorted(counter[year]['code4'].items(), key=lambda item: item[1], reverse=True)
        for j in range(k):
            code4_topk_year.setdefault(s[j][0], [np.nan for _ in range(len(years))])
            code4_topk_year[s[j][0]][i] = j + 1

    print code4_topk_year

    years = [int(year) for year in sorted(counter.keys())]

    def rankline(data, marker_width=.5, color='red', label=None):
        y_data = np.repeat(data, 2)
        x_data = np.zeros(len(y_data))
        x_data[0::2] = np.arange(years[0], years[-1] + 1) - (marker_width / 2)
        x_data[1::2] = np.arange(years[0], years[-1] + 1) + (marker_width / 2)
        lines = []
        lines.append(plt.Line2D(x_data, y_data, lw=1, linestyle='--', color=color, label=label))
        for x in range(0, len(data) * 2, 2):
            lines.append(plt.Line2D(x_data[x: x + 2], y_data[x: x + 2],
                                    lw=4, linestyle='solid', color=color, label=label))
        return lines

    colors = plt.cm.get_cmap("hsv", k + 1)

    artists = []
    for code, rankings in code4_topk_year.items():
        color = colors(code4_topk_year.items().index((code, rankings)))
        artists.extend(rankline(rankings, label=code, color=color))

    fig, ax = plt.subplots()

    for artist in artists:
        ax.add_artist(artist)

    plt.ylim(.75, k + .25)
    ytick = np.arange(1, k + 1, 1)
    ax.spines['top'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.tick_params(axis='both', which='both', bottom=False, top=False,
                    labelbottom=True, left=False, right=False, labelleft=True)
    plt.yticks(ytick)
    plt.gca().invert_yaxis()
    ax.set_xbound([years[0] - .5, years[-1] + .5])
    #plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.show()


# fig 4
#topk_year(4, counter_code)


year_lookup = {}
for index, year in enumerate(years):
    year_lookup.setdefault(year, index)


def discipline_boxplot(counter, k):
    sum_code2 = {}
    for year in counter.keys():
        for code, num in counter[year]['code6'].items():
            sum_code2[code] = sum_code2.setdefault(code, 0) + num
    sorted_sum_code2 = sorted(sum_code2.items(), key=lambda item: item[1], reverse=True)[: k + 1]

    print sorted_sum_code2


    counter_code2 = {}
    for code, _ in sorted_sum_code2:
        counter_code2.setdefault(code, np.zeros(len(years)))


    for year in years:
        index = year_lookup[year]
        for code, num in counter[year]['code6'].items():
            if code in counter_code2:
                counter_code2[code][index] += num

    x_data = [i[0] for i in sorted_sum_code2]
    y_data = []
    for code in x_data:
        y_data.append(counter_code2[code])

    fig, ax = plt.subplots()
    ax.boxplot(y_data, showmeans=True, meanline=True, showfliers=False, vert=False)
    ax.set_yticks(range(1, k + 2))
    ax.set_yticklabels(x_data, fontsize='small')
    plt.grid(True, 'major', 'x', ls='--', lw=.5, c='k', alpha=.3)

    plt.show()


# fig 5
discipline_boxplot(counter_code, 8)


def subdiscipline_linegraph(counter, k):
    sum_code4 = {}
    for year in counter.keys():
        for code, num in counter[year]['code6'].items():
            sum_code4[code] = sum_code4.setdefault(code, 0) + num

    sorted_sum_code4 = sorted(sum_code4.items(), key=lambda item: item[1])[-k - 1:]


    counter_code4 = {}
    for code, _ in sorted_sum_code4:
        counter_code4.setdefault(code, np.zeros(len(years)))

    for year in years:
        index = year_lookup[year]
        for code, num in counter[year]['code6'].items():
            if code in counter_code4:
                counter_code4[code][index] += num



    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #fig.subplots_adjust(left=.06, right=.75, bottom=.02, top=.94)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    #fig.subplots_adjust(left=.06, right=.75, bottom=.02, top=.94)

    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.tick_params(axis='both', which='both', bottom=False, top=False,
                    labelbottom=True, left=False, right=False, labelleft=True)

    colors = plt.cm.get_cmap("hsv", k + 1)

    subdisciplines = ['Artificial Intelligence And Image Processing',
                      'Information Systems',
                      'Distributed Computing',
                      'Data Format',
                      'Library And Information Studies',
                      'Electrical And Electronic Engineering',
                      'Cognitive Sciences',
                      'Biochemistry And Cell Biology',
                      'Public Health And Health Services',
                      'Ophthalmology And Optometry',
                      'Clinical Sciences',
                      'Communications Technologies']

    for code, index in sorted_sum_code4:
        #if code in subdisciplines:
        color = colors(sorted_sum_code4.index((code, index)))
        #else:
        #    color = 'grey'
        print code
        ratio = list(map(lambda x: x[0]/x[1], zip(counter_code4[code], total_year)))
        plt.plot(years, ratio, color=color, lw=.5)
        y_pos = counter_code4[code][-1]
        plt.text(int(years[-1]) + .5, y_pos, code, color=color)
        plt.ylabel('ratio of total number')


    plt.show()


# fig 6
#subdiscipline_linegraph(counter_code, 6)


author_d = {}
for paper in data:
    for author in paper['author(s)']:
        author_d.setdefault(author, 0)

counter_author = {}

for paper in data:
    year = paper['year']
    if year:
        counter_author.setdefault(year, copy.deepcopy(author_d))
        for author in paper['author(s)']:
            counter_author[year][author] += 1


def author_boxplot(counter, k):

    sum_author = {}
    for year in counter.keys():
        for author, num in counter[year].items():
            sum_author[author] = sum_author.setdefault(author, 0) + num

    sorted_sum_author = sorted(sum_author.items(), key=lambda item: item[1], reverse=True)[: k + 1]

    counter_author_year = {}
    for author, _ in sorted_sum_author:
        counter_author_year.setdefault(author, np.zeros(len(years)))

    for year in years:
        index = year_lookup[year]
        for author, num in counter[year].items():
            if author in counter_author_year:
                counter_author_year[author][index] += num

    x_data = [i[0] for i in sorted_sum_author]

    y_data = []
    for author in x_data:
        y_data.append(counter_author_year[author])

    x_data = ['author' + str(i) for i in range(1, k + 2)]

    fig, ax = plt.subplots()
    ax.boxplot(y_data, showmeans=True, meanline=True, showfliers=False)
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    ax.set_xticks(range(1, k + 2))
    ax.set_xticklabels(x_data, fontsize='small', rotation=90)

    plt.show()


author_boxplot(counter_author, 19)


def author_hist(counter):

    counter_paper_year = {}
    for year in years:
        counter_paper_year.setdefault(year, {})

    for year in years:
        for author, num in counter[year].items():
            counter_paper_year[year][num] = counter_paper_year[year].setdefault(num, 0) + 1

    fig, axs = plt.subplots(len(years), 1, sharex=True)

    for i in range(len(years)):
        year = years[i]
        data = counter_paper_year[year]
        x_data = [j[0] for j in data.items()[1:]]
        y_data = [j[1] for j in data.items()[1:]]
        axs[i].plot(x_data, y_data)
        axs[i].grid(True)
        axs[i].set_title(years[i])



    plt.show()


#author_hist(counter_author)