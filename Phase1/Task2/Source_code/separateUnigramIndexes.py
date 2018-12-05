import os
import nltk

source = "C:/Users/Ravi/Desktop/IR_ProjectRes/Clean_Corpus1/"
dest= "C:/Users/Ravi/Desktop/IR_ProjectRes/Separated_unigrams/"


def unigram(source):
    for filename in os.listdir(source):
        folder=open(source+filename)
        open_file = folder.read()
        open_file=open_file.split(" ")
        unigrams=nltk.ngrams(open_file,1)
        map=nltk.FreqDist(unigrams)
        write_unigram(map,dest,filename)


def write_unigram(map,dest,filename):
    folder = os.path.join(dest + filename)
    write_unigram_file=open(folder,"a+")
    for key,value in map.items():
        write_unigram_file.write(str(key[0])+" "+filename+" "+str(value)+"\n")


def main():
    queriesRes=unigram(source)