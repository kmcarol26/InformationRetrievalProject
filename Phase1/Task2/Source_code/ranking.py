from bs4 import BeautifulSoup
import re


queries_source="C:/Users/Ravi/Documents/test-collection/cacm.query.txt"
final_query_text="C:/Users/Ravi/Desktop/IR_ProjectRes/query_res.txt"


def queries_extract(queries_source):
    all_queries = open(queries_source).read()
    soupContent = BeautifulSoup(all_queries, 'lxml')
    query_file = open(final_query_text, "w+")

    for docTag in soupContent.findAll('doc'):
        queryInfo= docTag.find('docno')
        queryInfo.decompose()
        docText=docTag.text.strip()
        docText = str(docText)
        docText=re.sub('[^a-zA-Z0-9 ]','',docText)
        docText=docText.lower()
        query_file.write(docText+"\n")



def main():
    queriesRes=queries_extract(queries_source)













