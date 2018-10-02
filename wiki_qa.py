import sys
import re
import itertools
import string
import requests
import rdflib
import lxml.html
import lxml.etree as le
#from unidecode import unidecode

class Question:

    def __init__(self, question):
        self.question = question

    @staticmethod
    def factory(question):
        pat = r"^Who is the (?P<relation>.+) of( the)? (?P<entity>.+)\?$"
        if re.match(pat, question):
            m = re.match(pat, question)
            relation = m.group('relation')
            entity = m.group('entity')
            return WhoQuestion(question, relation, entity)

        pat = r"^What is the (?P<relation>.+) of( the)? (?P<entity>.+)\?"
        if re.match(pat, question):
            m = re.match(pat, question)
            relation = m.group('relation')
            entity = m.group('entity')
            return WhatQuestion(question, relation, entity)
        
        pat = r"^When was (?P<entity>.+) born\?$"
        if re.match(pat, question):
            m = re.match(pat, question)
            entity = m.group('entity')
            return WhenBornQuestion(question, entity)
        


class WhoQuestion(Question):
    def __init__(self, question, relation, entity):
        self.question = question
        self.relation = relation
        self.entity = entity

    def sparql(self):
        s = """SELECT ?p WHERE {{ 
                <{0}>  <{1}> ?p }}""".format(self.entity, self.relation)
        return s
        

class WhatQuestion(Question):
    def __init__(self, question, relation, entity):
        self.question = question
        self.relation = relation
        self.entity = entity

    def sparql(self):
        s = """SELECT ?p WHERE {{ 
                <{0}>  <{1}> ?p }}""".format(self.entity, self.relation)
        return s

class WhenBornQuestion(Question):
    def __init__(self, question,  entity): 
        self.question = question
        self.entity = entity
        self.relation = 'Born'


    def sparql(self):
        s = """SELECT ?p WHERE {{ 
                <{0}>  <Born> ?p }}""".format(self.entity)
        return s


def wiki_page(name):
    wiki_prefix = r'http://en.wikipedia.org/wiki/'
    name = name.replace(' ', '_')
    return wiki_prefix+name

def relation_extract(text):
    pat = '[A-Za-z0-9\%\(\) ]+'
    new_text = []
    for t in text:
        a = ' '.join(re.findall(pat,t)).strip()
        new_text.append(a)
    return ' '.join(new_text).strip()

def remove_white_spaces(text):
    #text = filter(lambda x: x.strip() , text)
    text = map(lambda x: re.sub('\\n', '',x), text)
    return text

def info_extract(text):
    text = remove_white_spaces(text)
    clean = re.sub('\([^()]*\)','', 'SEP'.join(text))
    text = clean.split('SEP')
    text = map(lambda x:' ' if x=='' else x, text)
    text = u''.join(text).encode('utf-8').strip()
    text = re.sub('\s+', ' ',text)
    text = re.sub('\s+,\s+', ', ', text)
    date = r'(\d{1,2}\s)([JFMASOND][a-z]+)(\s\d{4})'
    text = re.sub(date,r'\1\2,\3', text)
    return text.strip()
    
        
def info_list(tr):
    path = "./td//li"
    ul = tr.xpath(path)
    lst = []
    for li in ul:
        path = ".//text()"
        r = li.xpath(path)
        lst.append(''.join(r).strip())
    info = ', SEP'.join(lst)
    info = info_extract(info.split('SEP'))
    return info



def info_box(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    path1 = "//table[contains(@class,'infobox')]"
    path2 = "./tr[./th[contains(@scope,'row')] and ./td]"
    box = doc.xpath(path1)[0]
    table = box.xpath(path2)
    #for element in info_col:
    #    print le.tostring(element)
    relations = []
    entities = []
    for row in table:
        path = "./th//text()"
        relation = row.xpath(path)
        relation = relation_extract(relation)
        #path = "./td//text()[not(./parent::*[contains(@class,'geo')])]"
        path = "./td//text()[not(./ancestor::sup) \
        and not(./parent::a[contains(@href, 'cite_note')]) \
        and not(./ancestor::span[contains(@class, 'geo')])]"

        info = row.xpath(path)
        
        #for element in info:
        #    print le.tostring(element)
        entity = info_extract(info)
        lst = info_list(row)
        if lst:
            entity = lst
        relations.append(relation)
        entities.append(entity)
    return (relations, entities)
        

def hamming(str1, str2):
    size = min(len(str1), len(str2))
    str1 = str1[:size].lower()
    str2 = str2[:size].lower()
    return sum(itertools.imap(str.__ne__, str(str1), str(str2)))
    

def match_best_relation(relations, relation):
    match = min(relations, key=lambda r: hamming(r, relation))
    return match
        
        
def answer(question):
    url = wiki_page(question.entity)
    relations, information = info_box(url)
    ontology(question.entity, relations, information)
    relation = match_best_relation(relations, question.relation)
    index = relations.index(relation)
    info = information[index]
    entity = re.sub(' ', '_', question.entity)
    relation = re.sub(' ', '_', relation)
    question.entity = r'http://example.org/{0}'.format(entity)
    question.relation = r'http://example.org/{0}'.format(relation)
    sparql = question.sparql()
    f = open('query.sparql', 'w')
    f.write(sparql)
    f.close()
    return information[index]
   
def ontology(entity, relations, information):
    g = rdflib.Graph()
    for relation, info in zip(relations, information):
        entity = re.sub(' ', '_', entity)
        relation = re.sub(' ', '_', relation)
        info = re.sub(' ', '_', info)

        sub = rdflib.URIRef('http://example.org/'+entity)
        rel = rdflib.URIRef('http://example.org/'+relation)
        inf = rdflib.URIRef('http://example.org/'+info)


        g.add((sub, rel, inf))

        g.serialize("ontology.nt", format="nt")

        
if __name__ == '__main__':
    #question = "Who is the president of Italy?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "Who is the spouse of Gal Gadot?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "What is the alma mater of Gal Gadot?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "Who is the MVP of the 2011 NBA Finals?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "What is the best picture of the 90th Academy Awards?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "What is the capital of Canada?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "When was Theodor Herzl born?"
    #question = Question.factory(question)
    #print(answer(question))
    #question = "Who is the parent of Barack Obama?"
    #question = Question.factory(question)
    #print(answer(question))

    question = str(sys.argv[1])
    question = Question.factory(question)
    print(answer(question))



