import unittest
from  wiki_qa import extract

class TestQA(unittest.TestCase):

    def test_extract(self):
        q = 'Who is the president of Italy?'
        answer = ('president','Italy')
        self.assertEqual(extract(q), answer)
        
        q = 'Who is the spouse of Gal Gadot?'
        answer = ('spouse', 'Gal Gadot')
        self.assertEqual(extract(q), answer)

        q = 'What is the alma mater of Gal Gadot?'
        answer = ('alma mater','Gal Gadot')
        self.assertEqual(extract(q), answer)

        q = 'Who is the MVP of the 2011 NBA Finals?'
        answer = ('MVP', '2011 NBA Finals')
        self.assertEqual(extract(q), answer)

        q = 'What is the best picture of the 90th Academy Awards?'
        answer = ('best picture', '90th Academy Awards')
        self.assertEqual(extract(q), answer)

        q = 'What is the capital of Canada?'
        answer = ('capital', 'Canada')
        self.assertEqual(extract(q), answer)

        q = 'When was Theodor Herzl born?'
        answer = 'Theodor Herzl'
        self.assertEqual(extract(q), answer)

        q = 'Who is the parent of Barack Obama?'
        answer = ('parent', 'Barack Obama')
        self.assertEqual(extract(q), answer)

        

    def test_wiki(self):
        pass


if __name__ == '__main__':
    unittest.main()
