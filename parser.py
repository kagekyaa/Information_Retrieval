'''
Words in bold, in headings (h1, h2, h3), and titles should be treated as more
important than the other words.

Extra credit will be given for ideas that improve the quality of the retrieval, so you
may add more metadata to your index, if you think it will help improve the quality of
the retrieval.

Ranking: you are going to use the scoring formula of Lucene, so that formula is
going to be more or less hidden from you. However, you should study how Lucene
scores the documents wrt the queries, and adjust the several parameters of your
index for better retrieval.

'''
from lxml import html, etree
import string
import os
import json
import re
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

# module for checking file types:
# don't forget dependencies: https://github.com/ahupp/python-magic#dependencies
import magic  # pip install python-magic https://github.com/ahupp/python-magic


def parse_files():
    # elastic search object: build connection:
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}], http_auth=('elastic', '123456'))

    # limit iteration for testing (only process my_limit amount of files):
    count = 0
    my_limit = 10000

    # web pages location :
    my_path = 'C:/Users/Kyaa/Documents/GitHub/121ICS_SearchEngine/WEBPAGES_RAW/'

    # iterating all files:
    for root, dirs, file_names in os.walk(my_path):
        # print root
        # print file_names

        for f in file_names:

            # temporary container for json data:
            data = {}   # refresh every files
            full_path = root + '/' + f
            source_path = root[64:] + '/' + f  # 50 to add webpage_raw, 64 for folder/file only

            # print "source : ", source_path
            data['source_path'] = source_path

            # checking file types if worth to parse or not (1):
            if int(f.find(".json")) != -1 or int(f.find(".tsv")) != -1:  # bookkeeping
                print "irrelevant file : ", f
                continue

            # (2) checking file type with python-magic:
            try:
                file_type = magic.from_file(full_path, mime=True)
                data["file_type"] = file_type
                file_type = file_type.replace("/", "_")  # replace / with _ safety for index path

                # if html file: parse it -else: put it into index by its file type:
                if data["file_type"] == "text/html":
                    print source_path, " : ", data["file_type"]
                    pass
                else:
                    print source_path, " : ", data["file_type"]
                    json_data = json.dumps(data)
                    #print json_data
                    es.index(index='files', doc_type=file_type, id=count, body=json.loads(json_data))
                    continue
            except:
                print "I don't know what kind of file is this!"
                continue

# HTML parsing #
####################################################################################################
            with open(full_path) as input_file:
                soup = BeautifulSoup(input_file, 'html.parser')
                # soup.prettify()   # print html page, in console beautifully

                # title:
                data['title'] = soup.title.text if soup.title else "-"
                # print "Title : ",  soup.title.text if soup.title else "-"

                # meta description:
                if soup.find("meta", attrs={'property': 'og:description'}):
                    meta_description = soup.find("meta", attrs={'property': 'og:description'})
                    print "-------------------------- Social! -----------------------------"
                    # print "meta_description = ", meta_description["content"].strip()
                else:
                    meta_description = soup.find("meta", attrs={'name': 'description'})
                if meta_description:
                    try:
                        data['meta_description'] = meta_description["content"].strip()
                        print "meta_description = ", data['meta_description']
                    except:
                        pass

                # meta author: <meta name="author" content="John Smith">
                meta_author = soup.find("meta", attrs={'name': 'author'})
                if meta_author:
                    try:
                        data['meta_author'] = meta_author["content"].strip()
                        print "meta_author = ", data['meta_author']
                    except:
                        pass

                # meta key:
                meta_key = soup.find("meta", attrs={'name': 'keywords'})
                if meta_key:
                    try:
                        data['meta_key'] = re.sub('[^0-9a-zA-Z.,]+', '', meta_key["content"].encode('utf8')).split(',')
                        print "meta_key = ", data['meta_key']
                    except:
                        pass

                # heading:
                data['heading'] = []
                for i in soup.find_all('h1'):
                    data['heading'].append(i.text.strip())
                    # print "h1 = ", i.text.strip()

                for i in soup.find_all('h2'):
                    data['heading'].append(i.text.strip())
                    # print "h2 = ", i.text.strip()

                for i in soup.find_all('h3'):
                    data['heading'].append(i.text.strip())
                    # print "h3 = ", i.text.strip()

                # bold:
                data['bold'] = []
                for i in soup.find_all('b'):
                    # print "bold = ", i.text.strip()
                    data['bold'].append(i.text.strip())

                # all text in the file:
                # only get alphaNum characters, and erase duplicate spaces
                # print "text = ", " ".join(soup.get_text().encode('utf8').split())  # before alphaNum
                # print "text = ", " ".join(re.sub('[^0-9a-zA-Z.]+', ' ', soup.get_text().encode('utf8')).split())
                data['text'] = " ".join(re.sub('[^0-9a-zA-Z.]+', ' ', soup.get_text().encode('utf8')).split())

####################################################################################################

            # make a json file of parsed data:
            json_data = json.dumps(data)
            # print json_data

            # post it into elastic search Node: #!!
            es.index(index='html_only', doc_type='html_files', id=count, body=json.loads(json_data))

####################################################################################################

            # limit iteration files for code testing :
            count += 1
            if count == my_limit:
                print "Total Files = ", count
                print "Bye!"
                exit()

    print "Total Files = ", count

'''
Evaluation criteria:
- Does your search engine work as expected of search engines?
- How general are the heuristics that you employed to improve the retrieval?
- How complete is the UI? (e.g. links to the actual pages, snippets, etc.)
- Do you demonstrate in-depth knowledge of how your search engine works?
Are you able to answer detailed questions pertaining to any aspect of its implementation?
'''

if __name__ == "__main__":
    parse_files()
