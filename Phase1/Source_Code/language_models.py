import math
from bs4 import BeautifulSoup

dest= "C:/Users/Ravi/Desktop/IR_ProjectRes/Unigram_Indexer/"
baseLines= "C:/Users/Ravi/Desktop/IR_ProjectRes/Baselines1/"
queries_source="C:/Users/Ravi/Documents/test-collection/cacm.query.txt"
unigram_count_file="C:/Users/Ravi/Desktop/IR_ProjectRes/Unigram_Indexer/unigramCount.txt"
term_unigram_file="C:/Users/Ravi/Desktop/IR_ProjectRes/Unigram_Indexer/unigram.txt"

R=0
k1=1.2
b=0.75
k2=100
N=3204
lambdaQueryLikelihood=0.35

def fetch_all_queries(queries_source):
    queries = []
    read_all_queries=open(queries_source).read()
    soupContent = BeautifulSoup(read_all_queries, 'lxml')

    for docTag in soupContent.findAll('doc'):
        query_id=int(docTag.find('docno').text)
        docTag.find('docno').decompose()
        queries.append((query_id,docTag.text.strip().lower()))
    return queries


def averageUnigramDocLen(unigramDocLen):
    totalNum=0
    valueCount=0.0
    for value in unigramDocLen.values():
        valueCount = valueCount + int(value)
        totalNum = totalNum + 1
    avg=valueCount/totalNum
    return avg

def queryProcessing(complete_queries):
    BM25_text = open(baseLines+'BM25.txt', "w+")
    TFIDF_text = open(baseLines + 'TFIDF.txt', "w+")
    QueryLikelikhood_text = open(baseLines + 'QueryLikelikhood.txt', "w+")

    unigram_dict = extract_dict()
    unigramDocLen = unigramCount()
    avrgUnigramDocLen = averageUnigramDocLen(unigramDocLen)

    for query_id,query_text in complete_queries:
        (BM25_List,TFIDF_List,QueryLikelikhood_List)=getRetModels(query_text,unigram_dict,unigramDocLen,avrgUnigramDocLen)
        writeString(BM25_List,query_id,BM25_text,"BM25")
        writeString(TFIDF_List,query_id,TFIDF_text,"TFIDF")
        writeString(QueryLikelikhood_List,query_id,QueryLikelikhood_text,"QueryLikelikhood")

def writeString(listType,query_id,resultFile,type):
    resString=''
    rm_rank=0
    for document_id,finalScore in listType:
        rm_rank=rm_rank+1
        resString=resString + str(query_id)+' '+ "Q0" +' '+document_id+' '+str(rm_rank)+' '+str(finalScore)+' '+type+'\n'
    resultFile.write(resString)



def unigramCount():
    all_content=open(unigram_count_file,'r').read().splitlines()
    unigram_count={}
    for every_entry in all_content:
        unigram_count[every_entry.split()[0]]=int(every_entry.split()[1])
    return unigram_count

def extract_dict():
    all_content=open(term_unigram_file,'r').read().splitlines()
    unigram_res={}
    for each_entry in all_content:
        (document_id,all_entries)=each_entry.split('-->')
        values_entry=all_entries.split()
        doc_tf_tuple=[]
        for val_entry in values_entry:
               length=len(val_entry)
               val_entry=val_entry[1:length-1]
               val_entry=val_entry.split(',')
               doc_tf_tuple.append((val_entry[0],int(val_entry[1])))
        unigram_res[document_id]=doc_tf_tuple
    return unigram_res

def getRetModels(query_text,unigram_dict,unigramDocLen,avrgUnigramDocLen):
    all_content=query_text.split()
    all_docs=[]
    bm25_rank_dict, tfidf_rank_dict, ql_rank_dict, query_freq, document_freq = {}, {}, {}, {}, {}
    for each_entry in all_content:
        if each_entry not in unigram_dict:
            document_freq[each_entry] = 0
        else:
            all_docs = all_docs + unigram_dict[each_entry]
            if each_entry not in document_freq:
                document_freq[each_entry] = len(unigram_dict[each_entry])

        if each_entry not in query_freq:
            query_freq[each_entry]=1
        else:
            query_freq[each_entry]+=1

    print "hi"
    for document_id,term_freq in all_docs:
        if document_id not in bm25_rank_dict:
            (score,scoreTfidf,scoreQL)=calculate_scores(all_content,document_id,unigram_dict,query_freq,document_freq,unigramDocLen,avrgUnigramDocLen)
            bm25_rank_dict.update({document_id:score})
            tfidf_rank_dict.update({document_id:scoreTfidf})
            ql_rank_dict.update({document_id:scoreQL})

    sorted_res_bm25=[]
    res_bm25=sort_docs_of_queries(bm25_rank_dict, sorted_res_bm25)
    sorted_res_tfidf = []
    res_tfidf=sort_docs_of_queries(tfidf_rank_dict, sorted_res_tfidf)
    sorted_res_ql = []
    res_ql=sort_docs_of_queries(ql_rank_dict, sorted_res_ql)


    return (res_bm25,res_tfidf,res_ql)

def calculate_scores(all_content,document_id,unigram_dict,query_freq,document_freq,unigramDocLen,avrgUnigramDocLen):
    numerator = float(unigramDocLen[document_id])
    denominator = avrgUnigramDocLen
    avg_doc_len = numerator / denominator
    const_parameter = 1 - b
    const_parameter2 = b * avg_doc_len
    multiplier = const_parameter + const_parameter2
    K = k1 * multiplier
    bm25_score = 0
    tfidf_score = 0
    ql_score = 0
    count_of_all_words=count_all_words(unigramDocLen)
    for each_entry in all_content:
        if each_entry in unigram_dict:
            termf = get_term_freq(each_entry, document_id, unigram_dict)
        else:
            termf=0
        bm25_score = bm25_score + calc_bm25_score(K, query_freq[each_entry], termf, document_freq[each_entry], 0)
        tfidf_score = tfidf_score + calc_tfidf_score(termf, document_freq[each_entry], unigramDocLen[document_id])
        ql_score = ql_score + calc_queryLikelihood_score(termf, document_freq[each_entry], unigramDocLen[document_id],count_of_all_words )
    return  (bm25_score,tfidf_score,ql_score)

def sort_docs_of_queries(result_dict,sorted_res):
    i=0
    rev_sorted_dict = sorted(result_dict.iteritems(), key=lambda (k, v): (v, k), reverse=True)
    for key, value in rev_sorted_dict:
        i =i+ 1
        sorted_res.append((key, value))
        if i == 100:
            break
    return sorted_res

def count_all_words(unigramDocLen):
    total_word_count=0
    for value in unigramDocLen.values():
        total_word_count=total_word_count+value
    return total_word_count

def get_term_freq(each_entry, document_id, unigram_dict):
    for (document,term_frequency) in unigram_dict[each_entry]:
        if document==document_id:
            return term_frequency
    return 0

def calc_bm25_score(K,query_freq,doc_freq,n,r):
    term1= math.log(((r+0.5)/(R-r+0.5))/((n-r+0.5)/(N-n-R+r+0.5)))
    term2=((k1+1)*doc_freq)/(K+doc_freq)
    term3=((k2+1)*query_freq)/(k2+query_freq)
    return term1*term2*term3



def calc_tfidf_score(term_freq,doc_freq,document_length):
    float_doc_length=float(document_length)
    term_frequency=term_freq/float_doc_length

    inverse_doc_freq=0

    if doc_freq!=0:
        float_doc_freq=float(doc_freq)
        inverse_doc_freq=math.log(N/float_doc_freq)

    return term_frequency*inverse_doc_freq

def calc_queryLikelihood_score(term_freq,doc_freq,document_length,all_words):
    float_doc_len=float(document_length)
    term1=(1-lambdaQueryLikelihood)*(term_freq/float_doc_len)
    float_all_words=float(all_words)
    term2=lambdaQueryLikelihood*(doc_freq/float_all_words)

    finalscore=0
    totalscore=term1+term2
    if totalscore!=0:
        finalscore= math.log(totalscore)

    return finalscore

def main():
    queriesRes=fetch_all_queries(queries_source)
    queryProcessing(queriesRes)













