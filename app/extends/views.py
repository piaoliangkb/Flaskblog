from flask import render_template, request
from .minisearchengine import MiniSearchEngine
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
    occurset, isfound = MiniSearchEngine.SearchSingleKeyword(data, isfound)
    if occurset:
        queryresult = MiniSearchEngine.GenerateResultDict(occurset)
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
    # 文章内容list，进入界面时展示文章内容
    for path in allfilename:
        with open(path) as file:
            filename = os.path.split(path)[1]
            # 分割路径和文件名
            content[filename] = file.read()

    query = request.args.get('query', None)
    # 查询参数的获取
    queryresult = {}
    # 查询结果字典
    isfound = True
    # 标记是否查询到结果
    words = []
    if query:
        words = query.split()
        if len(words) == 1:
            occurset, isfound = MiniSearchEngine.SearchSingleKeyword(words[0], isfound)
            if occurset:
                queryresult = MiniSearchEngine.GenerateResultDict(occurset)
        else:
            resultlist = []
            # 建立一个列表暂存“单词对应的索引集合信息”和“bool关键词”
            for i in range(len(words)):
                if i == 0 or i == len(words) - 1:
                    wordindexset, temp = MiniSearchEngine.SearchSingleKeyword(words[i])
                    resultlist.append(wordindexset)
                else:
                    """
                    对于以下四种情况分别处理：
                    "AND" "AND"
                    "AND" set
                    set "AND"
                    set set
                    如果前一个元素为bool算符，那么当前元素必定当作单词
                    如果前一个元素为集合，当前元素若为AND OR则为bool算符，否则当作单词
                    """
                    if type(resultlist[i - 1]) == str:
                        # 如果结果集中前一个元素为bool算符，则当前元素应该为集合
                        wordindexset, temp = MiniSearchEngine.SearchSingleKeyword(words[i])
                        resultlist.append(wordindexset)
                    else:
                        if words[i] == "or" or words[i] == "OR":
                            resultlist.append("OR")
                        elif words[i] == "and" or words[i] == "AND":
                            resultlist.append("AND")
                        else:
                            wordindexset, temp = MiniSearchEngine.SearchSingleKeyword(words[i])
                            resultlist.append(wordindexset)
            # print(resultlist)
            for i in range(1, len(resultlist)):
                # 只有遇到当前元素为indexset才进行处理，若遇到bool运算符则检测下一个元素
                if type(resultlist[i]) == type(resultlist[i - 1]):
                    # 如果两个集合同为set，即两个单词相邻的情况
                    # [set set]
                    resultlist[i] = resultlist[i - 1] & resultlist[i]
                elif type(resultlist[i - 1]) == str and type(resultlist[i]) == set:
                    # [AND set]
                    if resultlist[i - 1] == "AND":
                        resultlist[i] = resultlist[i] & resultlist[i - 2]
                    elif resultlist[i - 1] == "OR":
                        resultlist[i] = resultlist[i] | resultlist[i - 2]
            queryresult = MiniSearchEngine.GenerateResultDict(resultlist[-1])
            if not queryresult:
                isfound = False
    return render_template('boolsearch.html', content=content, result=queryresult, isfound=isfound, queryword=words)
