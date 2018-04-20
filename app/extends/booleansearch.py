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


class BooleanSearch():

    @staticmethod
    def constructQueryTree(query):
        elements = query.split(" ")
        # 将要查询的字符串以空格分开
        # for item in elements:
        # 	print(item)
        res = []
        # 最终的结果树

        i = 0
        while i < len(elements):
            tempnode = []
            # 在本次查询中构建的树的结点
            print(elements[i])

            if elements[i] == "AND" or elements[i] == "and":
                tempnode.append("AND")

                # 处理左结点
                # 上一个结点为最终的结果树中的最后一个结点
                # 取出后将其出栈
                prevnode = res[len(res) - 1]
                res.pop()

                tempnode.append(prevnode)

                # 处理右结点
                nextnode = []
                nextnode.append(elements[i + 1])
                tempnode.append(nextnode)

                # 跳过下一个关键字
                i += 1
            else:
                # 如果不是and关键字 则将改关键字作为一个结点直接添加到tempnode中，作为一个单独的结果集。
                tempnode.append(elements[i])
            i += 1

            # 将每一步循环得到的结点集合存入到res中
            res.append(tempnode)

        for item in res:
            print(item)

        firstnode = res[0]

        # 将每个结点之间用or连接起来,表示前后查询结果的合并
        # 每次循环将前后两个结点用or连接起来
        for i in range(1, len(res)):
            currentnode = res[i]
            orNode = []
            orNode.append("OR")
            orNode.append(firstnode)
            orNode.append(currentnode)
            firstnode = orNode

        return firstnode

    @staticmethod
    def searchWithBinaryTree(querytree):
        result = {}
        nodevalue = querytree[0]

        # 如果当前查询树的第一个结点是and或者or的话，则对他们的左子树或者右子树进行递归查询
        if nodevalue == "AND" or nodevalue == "OR":
            leftresult = BooleanSearch.searchWithBinaryTree(querytree[1])
            rightresult = BooleanSearch.searchWithBinaryTree(querytree[2])

        if nodevalue == "AND":
            result = leftresult & rightresult
        elif nodevalue == "OR":
            result = leftresult | rightresult
        else:
            # 如果当前结点为某个单词的话，则对单词进行查询，返回单次查询的结果
            return MiniSearchEngine.SearchSingleKeyword(nodevalue)[0]
        # 返回结果集
        return result


if __name__ == '__main__':
    basedir = r'D:\documents\Python\flask\flaskfitsttime\app\static\documents\BooleanSearch'
    while 1:
        str = input("Please input you str:")
        result = BooleanSearch.searchWithBinaryTree(BooleanSearch.constructQueryTree(str))
        res = MiniSearchEngine.GenerateResultDict(result)
        for item in res:
            print(item)
