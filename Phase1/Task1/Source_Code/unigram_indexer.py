import os
import nltk

source = "C:/Users/Ravi/Desktop/IR_ProjectRes/Clean_Corpus1/"
dest= "C:/Users/Ravi/Desktop/IR_ProjectRes/Unigram_Indexer1/"


def unigram(invertedList):
    for filename in os.listdir(source):
        folder=open(source+filename)
        open_file = folder.read()
        open_file=open_file.split(" ")
        length=len(open_file)
        for i in range(length):
            token = open_file[i]
            invertedList = calculate_index(token, filename, invertedList)
    unigram_folder = os.path.join(dest, "unigram.txt")
    write_unigram_file=open(unigram_folder,"w")
    for key,value in invertedList.items():
        kv_pair=''
        for k,v in value.items():

            key_value_pair="("+k+","+str(v)+") "
            key_value_pair=str(key_value_pair)
            kv_pair+=key_value_pair
        k=str(key)
        write_unigram_file.write(
            str(k)+"-->"+str(kv_pair)+"\n")
    return invertedList


def calculate_index(token,filename,invertedList):
    if token not in invertedList:
        freq = {filename:1}
        invertedList.update({token:freq})
    elif filename in invertedList[token]:
        invertedList[token][filename] = invertedList[token][filename] + 1
    else:
        invertedList[token].update({filename:1})
    return invertedList

def generate(source):
    for file in os.listdir(source):
        filename=open(source+file)
        content= filename.read()
        tokens=content.split(' ')
        file_name=file.split("_raw")[0]
        write_content(len(tokens), file_name,"unigramCount.txt",dest)

def write_content(collection, file_name, type, destination):
        folder = os.path.join(destination, type)
        write_unigramCount_file = open(folder, "a+")
        filename = str(file_name)
        write_unigramCount_file.write(filename + " " + str(collection) + '\n')

def main():
    invertedList1={}
    unigram(invertedList1)
    generate(source)




