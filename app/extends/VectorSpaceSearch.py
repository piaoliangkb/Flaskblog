import os
import math
from config import Config

basedir = Config.BOOLEANSEARCH_PATH

class VectorSpaceSearch():

    pathOfwordindex = basedir + "/wordindex.txt"
    pathOftermfrequency = basedir + "/termfrequency.txt"
    pathOfbasicwords = basedir + "/basicwords.txt"
    pathOfventor = basedir + "/vector.txt"
    pathOfdocindex = basedir + "/documentindex.txt"

    word2DocumentFrequency = {}
    # 每个单词在所有文档中共出现了多少次
    dicTermFrequency = {}
    # 某个单词在某个文档中出现了多少次
    dicDocument2Length = {}
    # 文档的单词总数
    basicWords = []
    # 基础单词
    dicDocid2Vector = {}
    # 文件索引和对应向量的字典
    dicDocid2Filepath = {}
    # 文件索引和对应的路径

    def __init__(self):
        # read the file-termfrequeny into the word2DocumentFrequenct
        # word:all occurtimes in document
        with open(self.pathOftermfrequency) as file:
            lines = file.readlines()
            for line in lines:
                line = line.split()
                self.word2DocumentFrequency[line[0]] = len(line)
        # read the basicwords into basicWords
        with open(self.pathOfbasicwords) as file:
            words = file.read()
            for word in words.split():
                self.basicWords.append(word)
        # read the vector built previously into memory
        with open(self.pathOfventor) as file:
            lines = file.readlines()
            for line in lines:
                thisfilevector = []
                line = line.split()
                for i in range(1, len(line)):
                    thisfilevector.append(line[i])
                self.dicDocid2Vector[line[0]] = thisfilevector
        with open(self.pathOfdocindex) as file:
            lines = file.readlines()
            for line in lines:
                line = line.split()
                self.dicDocid2Filepath[line[0]] = line[1]


    def RepresentQueryAsVector(self, query):
        # split quert into words
        words = query.split()
        # represent the quert as a document
        # count the length of the documeng
        length = len(words)
        # generate the count of each word
        dicWord2Count = {}
        for i in range(length):
            if words[i] in dicWord2Count.keys():
                dicWord2Count[words[i]] += 1
            else:
                dicWord2Count[words[i]] = 1
        # create a query-vector
        qVector = [0 for i in range(len(self.basicWords))]
        for i in range(len(self.basicWords)):
            currentBasicWord = self.basicWords[i]
            if not currentBasicWord in dicWord2Count.keys():
                continue
            dTf = dicWord2Count[currentBasicWord]
            dTf /= length
            # 出现次数除以文档中的单词总数为Tf
            # 该词在文件中的出现次数，而分母则是在文件中所有字词的出现次数之和
            dIdf = math.log10((len(self.dicDocid2Filepath)+1)/(self.word2DocumentFrequency[currentBasicWord]+1))
            # 逆文本频率指数 Inverse Document Frequency
            # 总文件数目除以包含该词语之文件的数目
            qVector[i] = dTf * dIdf
        return qVector

    def GetVectorSimilarity(self, vec1, vec2):
        lengthOfvec1 = 0
        for item in vec1:
            lengthOfvec1 += math.pow(float(item), 2)
        if lengthOfvec1 == 0:
            return 0
        lengthOfvec1 = math.sqrt(lengthOfvec1)

        lengthOfvec2 = 0
        for item in vec2:
            lengthOfvec2 += math.pow(float(item), 2)
        if lengthOfvec2 == 0:
            return 0
        lengthOfvec2 = math.sqrt(lengthOfvec2)

        innerProduct = 0
        for i in range(len(vec1)):
            innerProduct += float(vec1[i]) * float(vec2[i])
        return innerProduct / (lengthOfvec1 * lengthOfvec2)

    def Search(self, query):
        queryVector = self.RepresentQueryAsVector(query)
        docid2Similarities = {}
        for docid in self.dicDocid2Filepath.keys():
            # 遍历所有文章，拿出该文章的Vector
            thisDocVector = self.dicDocid2Vector[str(docid)]
            # 将该文章的vector与查询的vector进行比较，并添加入比较集中
            docid2Similarities[docid] = self.GetVectorSimilarity(thisDocVector, queryVector)
        # 将字典按照value 从大到小排序，即为文章和查询之间的相关性
        # 按照value从大到小排序之后返回的为列表
        aftersortlist = sorted(docid2Similarities.items(), key=lambda item:item[1], reverse=True)
        res = []
        for item in aftersortlist:
            if item[1] > 0:
                res.append(item[0])
        # print(res)
        # res = ['4', '5', '6']
        return res


if __name__ == '__main__':
    a = VectorSpaceSearch()
    a.Search("kept sports")

