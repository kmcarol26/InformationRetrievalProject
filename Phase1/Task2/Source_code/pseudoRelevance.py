import math
import operator


final_query_text="C:/Users/Ravi/Desktop/IR_ProjectRes/query_res.txt"
unigram_file="C:/Users/Ravi/Desktop/IR_ProjectRes/Unigram_Indexer/unigram.txt"
pseudo_rel_file="C:/Users/Ravi/Desktop/IR_ProjectRes/pseudo_relevance.txt"
top_bm25_files="C:/Users/Ravi/Desktop/IR_ProjectRes/bm25_top_res.txt"
separate_unigram= "C:/Users/Ravi/Desktop/IR_ProjectRes/Separated_unigrams/"
common_words_doc="C:/Users/Ravi/Documents/test-collection/common_words.txt"
baselineBM25="C:/Users/Ravi/Desktop/IR_ProjectRes/Baselines1/BM25.txt"

R=0.0
k1=1.2
k2=100
r=0
b=0.75
total_num_docs=100

topmost_documents={}
pseudo_rel_top_documents={}
topmost_terms={}

def get_all_common_words():
    words=[]
    all_content = open(common_words_doc, 'r').read().splitlines()
    for each_entry in all_content:
        words.append(each_entry.replace("\n",""))
    return words

def extract_queries(filename):
    filename=open(filename)
    lines=''.join(filename.readlines()).split("\n")
    all_content = []
    for line in lines:
        all_content.append(line.split())
    return all_content



def pseudoRelevance_feedback():
    extract_results = extract_queries(final_query_text)
    common_words_all=get_all_common_words()
    all_content = open(baselineBM25, 'r').read().splitlines()
    for each_entry in all_content:
        queryString=int(each_entry.split()[0])
        rank=each_entry.split()[2]
        if queryString not in topmost_documents:
            topmost_documents[queryString] = []
        topmost_documents[queryString].append(rank)

    for key,value in topmost_documents.items():
        keyNum=int(key)
        pseudo_rel_top_documents[keyNum]=[]
        count=0
        while count<10:
            pseudo_rel_top_documents[keyNum].append(value[count])
            count+=1

    for value in pseudo_rel_top_documents.values():
        for each_value in value:
            topmost_terms[each_value]=[]

    for key in topmost_terms.keys():
        result_topmost={}
        all_content = open(separate_unigram+key+".txt",'r').read().splitlines()
        for each_entry in all_content:
            each_entry=each_entry.split()
            limit = 3
            length=len(each_entry)
            if(length==limit):
                queryText=each_entry[0]
                if queryText not in common_words_all:
                    term_freq=int(each_entry[2])
                    result_topmost[queryText]=term_freq
        reverse_sorted_result=sorted(result_topmost.iteritems(), key=operator.itemgetter(1), reverse=True)
        i=0
        for term,value in reverse_sorted_result:
            if i==1:
                break
            topmost_terms[key].append(term)
            i += 1

    for key,value in pseudo_rel_top_documents.items():
        i = 0
        while i < len(value):
            all_terms=topmost_terms[value[i]]
            j = 0
            while j < len(all_terms):
                results=extract_results[key-1]
                if all_terms[j] not in results:
                    results.append(all_terms[j])
                j = j + 1
            i = i + 1

    write_pseudo_rel=open(pseudo_rel_file,"w+")

    for each_entry in extract_results:
        count=0
        while count< len(each_entry):
            write_pseudo_rel.write(each_entry[count])
            write_pseudo_rel.write(" ")
            count=count+1
        write_pseudo_rel.write("\n")


def get_top_bm25(unigram_file,bm25_files):
    bm25_file = open(bm25_files, "w+")
    all_queries = extract_queries(pseudo_rel_file)
    all_content = open(unigram_file, 'r').read().splitlines()
    unigram_res = {}

    for each_entry in all_content:
        document_id = each_entry.split('-->')[0]
        all_entries = each_entry.split('-->')[1]
        unigram_res[document_id] = {}
        for every_query in all_entries.split():
            length = len(every_query)
            every_query = every_query[1:length - 1]
            every_query = every_query.split(',')
            unigram_res[document_id][every_query[0]] = int(every_query[1])

    (length_doc,tot_length)=calc_doc_len(unigram_res)

    bm25_result_list = []
    i = 0
    while i < len(all_queries):
        query_frequency = {}
        final_query = {}
        for each_entry in all_queries[i]:
            query_frequency[each_entry] = all_queries[i].count(each_entry)
            if each_entry in unigram_res:
                bm25_score_prep(unigram_res[each_entry], length_doc, final_query, query_frequency, each_entry,
                                tot_length, len(length_doc))
        i += 1
        bm25_result_list.append(final_query)

    query_number = 1
    for each_entry in bm25_result_list:
        rev_sorted_score = sorted(each_entry.iteritems(), key=operator.itemgetter(1), reverse=True)
        top_res_num = 1
        for each_entry in rev_sorted_score[:total_num_docs]:
            document_id = each_entry[0]
            score = each_entry[1]
            bm25_file.write(str(query_number) + "Q0" + " " + str(document_id) + " " + str(top_res_num) + " " + str(
                score) + " " + "BM25" + "\n")
            top_res_num += 1
        query_number = query_number + 1


def bm25_score_prep(unigram_res, length_doc, final_query, query_frequency, each_entry, tot_length, N):
    for document_id, document_freq in unigram_res.items():
        bm25_total_score = BM25_score_calc(len(unigram_res), document_freq, query_frequency[each_entry], 0, N,
                                           length_doc[document_id], tot_length / N)
        if document_id not in final_query:
            final_query[document_id] = bm25_total_score
        else:
            final_query[document_id] = final_query[document_id] + bm25_total_score


def calc_doc_len(res_dict):
    document_len = {}
    document_length = 0
    for unigram_values in res_dict.values():
        for key, value in unigram_values.items():
            if key not in document_len:
                document_len[key] = value
            else:
                document_len[key] = document_len[key] + value

    for each_value in document_len.values():
        document_length = document_length + each_value

    return document_len, document_length


def BM25_score_calc(n, doc_freq, query_freq, r, N, doc_len, avg_doc_len):
    numerator = float(doc_len)
    denominator = float(avg_doc_len)
    division_const = numerator / denominator
    K = k1 * ((1 - b) + b * division_const)
    term1 = math.log(((r + 0.5) / (R - r + 0.5)) / ((n - r + 0.5) / (N - n - R + r + 0.5)))
    term2 = ((k1 + 1) * doc_freq) / (K + doc_freq)
    term3 = ((k2 + 1) * query_freq) / (k2 + query_freq)
    return term1 * term2 * term3


def main():
    pseudoRelevance_feedback()
    get_top_bm25(unigram_file, top_bm25_files)