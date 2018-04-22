import os
import math
from config import Config

basedir = Config.BOOLEANSEARCH_PATH


class WordVector():
    pathOfwordindex = basedir + "/wordindex.txt"
    pathOftermfrequency = basedir + "/termfrequency.txt"
    pathOfbasicwords = basedir + "/basicwords.txt"
    pathOfventor = basedir + "/vector.txt"

    def generateTermFrenquencyFile(self):
        with open(self.pathOfwordindex) as f:
            lines = f.readlines()
            for line in lines:
                thisWordOccurTimesDict = {}
                line = line.split()
                for i in range(1, len(line)):
                    if not line[i] in thisWordOccurTimesDict.keys():
                        thisWordOccurTimesDict[line[i]] = 1
                    else:
                        thisWordOccurTimesDict[line[i]] += 1
                with open(self.pathOftermfrequency, "a") as file:
                    file.write(line[0] + "\t")
                    for item in thisWordOccurTimesDict.keys():
                        file.write(item + "-" + str(thisWordOccurTimesDict[item]) + "\t")
                    file.write("\n")

    def buildTfIdfVectorFile(self):
        word2DocumentFrequency = {}
        # 每个单词在所有文档中共出现了多少次
        dicTermFrequency = {}
        # 某个单词在某个文档中出现了多少次
        dicDocument2Length = {}
        # 文档的单词总数
        basicWords = []
        # 基础单词
        with open(self.pathOftermfrequency) as file:
            lines = file.readlines()
            for line in lines:
                line = line.split()
                # print(line)
                word2DocumentFrequency[line[0]] = len(line)
                basicWords.append(line[0])
                for i in range(1, len(line)):
                    docindex = line[i].split("-")[0]
                    thiswordoccurtimes = line[i].split("-")[1]
                    thiskey = line[0] + "@" + docindex
                    dicTermFrequency[thiskey] = thiswordoccurtimes
                    if docindex in dicDocument2Length.keys():
                        dicDocument2Length[docindex] += int(thiswordoccurtimes)
                    else:
                        dicDocument2Length[docindex] = int(thiswordoccurtimes)
        # print(word2DocumentFrequency)
        # print(dicTermFrequency)
        # print(dicDocument2Length)
        # print(basicWords)
        with open(self.pathOfbasicwords, "w") as file:
            for words in basicWords:
                file.write(words + "\t")

        # conpute tf-idf for each document and write it in the vector.txt
        if os.path.exists(self.pathOfventor):
            os.remove(self.pathOfventor)
        for docid in dicDocument2Length.keys():
            tfIdf = [0 for i in range(len(basicWords))]
            for i in range(len(basicWords)):
                searchkey = basicWords[i] + "@" + docid
                dTf = 0
                # term frequency 词频
                if searchkey in dicTermFrequency.keys():
                    # 计算当前基础词在当前文档中的出现次数
                    dTf = int(dicTermFrequency[searchkey])
                dTf /= dicDocument2Length[docid]
                # 出现次数除以文档中的单词总数为Tf
                # 该词在文件中的出现次数，而分母则是在文件中所有字词的出现次数之和
                dIdf = math.log10(len(dicDocument2Length) / word2DocumentFrequency[basicWords[i]])
                # 逆文本频率指数 Inverse Document Frequency
                # 总文件数目除以包含该词语之文件的数目
                tfIdf[i] = dTf * dIdf
            with open(self.pathOfventor, "a") as file:
                file.write(docid + "\t")
                for item in tfIdf:
                    file.write(str(item) + "\t")
                file.write("\n")


if __name__ == '__main__':
    a = WordVector()
    a.buildTfIdfVectorFile()
