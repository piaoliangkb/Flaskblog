from flask import render_template, request
from .boolsearch import BoolSearch
from .invert import InvertedFile
from config import Config
from . import extends
import os

@extends.route('/webmining', methods=['POST', 'GET'])
def webmining():
    from ..extends.invert import InvertedFile
    InvertedFile.BuildDocumentIndex()
    InvertedFile.BuildWordIndex()
    # 建立文章索引和单词索引
    basedir = Config.BOOLEANSEARCH_PATH
    allfilename = []
    # 文章路径list
    with open(basedir + "/documentindex.txt") as file:
        for content in file.readlines():
            filepath = content.split('\t')[1].replace('\n', '')
            allfilename.append(filepath)
    content = {}
    # 文章内容list
    for path in allfilename:
        with open(path) as file:
            filename = os.path.split(path)[1]
            # 分割路径和文件名
            content[filename] = file.read()
    data = request.args.get('query', None)
    queryresult = {}
    isfound = True
    occurset, isfound = BoolSearch.SearchSingleKeyword(data, isfound)
    if occurset:
        queryresult = BoolSearch.GenerateResultDict(occurset)
    return render_template('webmining.html', content=content, result=queryresult, isfound=isfound)


@extends.route('/boolsearch', methods=['POST', 'GET'])
def boolsearch():
    InvertedFile.BuildDocumentIndex()
    InvertedFile.BuildWordIndex()
    # 建立文章索引和单词索引
    basedir = Config.BOOLEANSEARCH_PATH
    allfilename = []
    # 文章路径list
    with open(basedir + "/documentindex.txt") as file:
        for content in file.readlines():
            filepath = content.split('\t')[1].replace('\n', '')
            allfilename.append(filepath)
    content = {}
    # 文章内容list
    for path in allfilename:
        with open(path) as file:
            filename = os.path.split(path)[1]
            # 分割路径和文件名
            content[filename] = file.read()
    query = request.args.get('query', None)
    queryresult = {}
    isfound = True
    words = []
    if query:
        words = query.split()
        if len(words) == 1:
            occurset, isfound = BoolSearch.SearchSingleKeyword(words[0], isfound)
            if occurset:
                queryresult = BoolSearch.GenerateResultDict(occurset)
        else:
            resultlist = []
            for i in range(len(words)):
                if i == 0 or i == len(words) - 1:
                    wordindexset, temp = BoolSearch.SearchSingleKeyword(words[i])
                    resultlist.append(wordindexset)
                else:
                    if type(resultlist[i - 1]) == str:
                        # 如果结果集中前一个元素为bool算符，则当前元素应该为集合
                        wordindexset, temp = BoolSearch.SearchSingleKeyword(words[i])
                        resultlist.append(wordindexset)
                    else:
                        if words[i] == "or" or words[i] == "OR":
                            resultlist.append("OR")
                        elif words[i] == "and" or words[i] == "AND":
                            resultlist.append("AND")
                        else:
                            wordindexset, temp = BoolSearch.SearchSingleKeyword(words[i])
                            resultlist.append(wordindexset)
            print(resultlist)
            for i in range(1, len(resultlist)):
                if type(resultlist[i]) == type(resultlist[i - 1]):
                    # 如果两个集合同为set，即两个单词相邻的情况
                    resultlist[i] = resultlist[i - 1] & resultlist[i]
                elif type(resultlist[i - 1]) == str and type(resultlist[i]) == set:
                    if resultlist[i - 1] == "AND":
                        resultlist[i] = resultlist[i] & resultlist[i - 2]
                    elif resultlist[i - 1] == "OR":
                        resultlist[i] = resultlist[i] | resultlist[i - 2]
            queryresult = BoolSearch.GenerateResultDict(resultlist[-1])
            if not queryresult:
                isfound = False
    return render_template('boolsearch.html', content=content, result=queryresult, isfound=isfound, queryword=words)
