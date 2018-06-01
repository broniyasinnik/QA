import sys
import re
import requests
import rdflib
import lxml.html

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
            return WhenQuestion(question, relation, entity)
        


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

class WhenQuestion(Question):
    def __init__(self, question,  entity): 
        self.question = question
        self.entity = entity

    def sparql(self):
        s = """SELECT ?p WHERE {{ 
        <{0}>  <Born> ?p }}""".format(self.entity)
        return s

#def extract(question):
#    pat1 = r"^(Who|What) is the (?P<relation>.+) of( the)? (?P<entity>.+)\?$"
#    pat2 = r"^When was (?P<entity>.+) born\?$"
#    q1 = re.compile(pat1)
#    q2 = re.compile(pat2)
#    if re.match(q1, question):
#        m = re.match(q1, question)
#        return (m.group('relation'), m.group('entity'))
#    if re.match(q2, question):
#        m = re.match(q2, question)
#        return m.group('entity')

def wiki_page(name):
    wiki_prefix = r'http://en.wikipedia.org/wiki/'
    name = name.replace(' ', '_')
    return wiki_prefix+name

def info_box(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    path1 = "//table[contains(@class,'infobox')]"
    path2 = "./tr/td"
    path3 = "./../th"
    box = doc.xpath(path1)[0]
    info_col = box.xpath(path2)
    rel_col = []
    indexes = []
    for i, element in enumerate(info_col):
        relation = element.xpath(path3)
        if relation:
            rel_col.append(relation[0])
            indexes.append(i)
    info_col = [element for i, element in enumerate(info_col) if i in indexes]
    path4 = ".//text()"
    for rel, info in zip(rel_col, info_col):
        text1 = rel.xpath(path4)
        text2 = info.xpath(path4)
        text1 = ' '.join(text1).strip()
        print text1+"----->"+str(text2)


if __name__ == '__main__':
    info_box(wiki_page('2011 NBA Finals'))
    #question = str(sys.argv[1])
    #print question
