from config import Config
import os

basedir = Config.BOOLEANSEARCH_PATH


class MiniSearchEngine():
    @staticmethod
    def SearchSingleKeyword(data, isfound=True):
        occurset = set()
        # 初始化结果集合为空
        if data is not None:
            with open(basedir + "/wordindex.txt") as file:
                for line in file.readlines():
                    if data == line.split('\t')[0]:
                        # 如果在wordindex文件中有对应的单词
                        occurset = set(line.split('\t')[1].split())
                        # 将对应单词出现的文章索引号添加到occurset中
            if occurset:
                isfound = True
            else:
                isfound = False
                # 若未查找到结果，isfound返回False
        return occurset, isfound

    @staticmethod
    def GenerateResultDict(occurset):
        queryresult = {}
        with open(basedir + "/documentindex.txt") as file:
            for line in file.readlines():
                for i in occurset:
                    if i == line.split('\t')[0]:
                        # 如果occurset集合中的元素对应文件索引中的索引值，则取出当前索引值对应的文件地址
                        resultpath = line.split('\t')[1].replace('\n', '')
                        # 索引对应的文件地址
                        with open(resultpath) as file:
                            filename = os.path.split(resultpath)[1]
                            # 文件名
                            queryresult[filename] = file.read()
                            # 文件名->文件内容对应字典
                        occurset.remove(i)
                        # 移除occurset中对应的值
                        break
        return queryresult
