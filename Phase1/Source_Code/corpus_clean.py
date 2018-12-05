from bs4 import BeautifulSoup
import os
from string import punctuation
import io

source="C:/Users/Ravi/Documents/test-collection/cacm/"
clean_corpus_dest="C:/Users/Ravi/Desktop/IR_ProjectRes/Clean_Corpus1/"


def read_filter(source):
    for filename in os.listdir(source):
        folder=source+filename
        open_file=open(folder).read()
        final_content=clean_soup(open_file)
        write_corpus(filename, final_content)

def write_corpus (filename,write_corpus):
    print (filename)
    filename=filename.split('.',1)[0]
    folder=os.path.join(clean_corpus_dest,filename+".txt")
    file_new=io.open(folder,"w",encoding='UTF-8')
    file_new.write(write_corpus)
    file_new.close()


def clean_soup(soup):
    soupContent = BeautifulSoup(soup, 'lxml').get_text()
    soupContent=soupContent.replace('html',' ' )
    soupContent = ''.join(
        map(lambda content: content if ord(content) < 127 else '', soupContent))
    soupContent=case_folding(soupContent)
    soupContent=remove_punc(soupContent)
    return soupContent


def case_folding(soupContent):
    return soupContent.lower()

def remove_punc(soupContent):
    soupContent=''.join(map(lambda x: x if x not in '[]{}()\<>=' else '',soupContent))
    soupContent = ' '.join(map(lambda token: token.strip(punctuation) if token.strip(punctuation) else '', soupContent.split()))
    soupContent = ' '.join(
        map(lambda token: token.replace("'","") if token.replace("'","") else '', soupContent.split()))
    return soupContent



def main():
    read_filter(source)







