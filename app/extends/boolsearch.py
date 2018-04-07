from config import Config
import os

basedir = Config.BOOLEANSEARCH_PATH


class BoolSearch():
    @staticmethod
    def SearchSingleKeyword(data, isfound=True):
        occurset = set()
        if data is not None:
            with open(basedir + "/wordindex.txt") as file:
                for line in file.readlines():
                    if data == line.split('\t')[0]:
                        occurset = set(line.split('\t')[1].split())
            if occurset:
                isfound = True
            else:
                isfound = False
        return occurset, isfound

    @staticmethod
    def GenerateResultDict(occurset):
        queryresult = {}
        with open(basedir + "/documentindex.txt") as file:
            for line in file.readlines():
                for i in occurset:
                    if i == line.split('\t')[0]:
                        resultpath = line.split('\t')[1].replace('\n', '')
                        with open(resultpath) as file:
                            filename = os.path.split(resultpath)[1]
                            queryresult[filename] = file.read()
                        occurset.remove(i)
                        break
        return queryresult
