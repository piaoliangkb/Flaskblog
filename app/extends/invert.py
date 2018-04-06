import os
from config import Config
basepath = Config.BOOLEANSEARCH_PATH


class InvertedFile():
    @staticmethod
    def BuildDocumentIndex():
        if os.path.exists(basepath + "\documentindex.txt"):
            return
        #如果已经存在文件索引文件，则跳过该函数

        index = 1
        with open(basepath + "\documentindex.txt", "w") as f:
            for filename in os.listdir(basepath):
                if filename != "documentindex.txt":
                    f.write(str(index) + "\t" + os.path.join(basepath, filename) + "\n")
                    index = index + 1

    @staticmethod
    def BuildWordIndex():
        if os.path.exists(basepath + "\wordindex.txt"):
            return
        #如果已经存在单词索引文件，则跳过该函数

        WordDir = {} # 建立字典保存单词和文章编号列表的对应关系
        with open(basepath + "\documentindex.txt") as f:
            for line in f:
                fileindex = line.split('\t')[0]
                filepath = line.split('\t')[1].replace('\n', '')
                with open(filepath) as file:
                    filecontent = file.read() # 读出文件中所有内容，返回string
                    filecontent = filecontent.replace('[', '').replace(']', '').replace('.', '').replace(',', '').replace('"', '')
                    for i in range(10):
                        filecontent = filecontent.replace(str(i), '')
                    filecontent = filecontent.split() # 不带参数的split会处理所有空格，返回一个list
                    for item in filecontent:
                        if item in WordDir.keys():
                            WordDir[item].append(fileindex)
                        else:
                            WordDir[item] = [fileindex]
        with open(basepath + "\wordindex.txt", "w") as f:
            for item in WordDir.keys():
                f.write(item + '\t')
                for i in WordDir[item]:
                    f.write(i + ' ')
                f.write('\n')




