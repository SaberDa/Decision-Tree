# -*- coding: utf-8 -*-

from math import log
import operator

def createDataSet():
    dataSet = [[1,1,'yes'], [1,1,'yes'], [1,0,'no'], [0,1,'no'],[0,1,'no']]
    labels = ['no surfacing', 'flippers']
    return dataSet,labels


# 计算给定数据集的shannon熵
def caluShannonEnt(dataSet):
    numEntries = len(dataSet)
    # 为所有可能分类创建字典
    labelCounts = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob * log(prob,2)    # 以2为底求对数
    return shannonEnt

# 按照给定特征划分数据集
# 当我们按照某个特征划分数据集时，就需要将所有符合要求的元素抽取出来

"""参数：
dataSet：待划分的数据集
axis：划分数据集的特征
value：需要返回的特征的值
"""

def splitDataSet(dataSet, axis, value):

    # 创建新的list的对象
    # 因为在python中函数传递的是列表的引用，若该列表在函数中被修改则会影响该列表对象的整个生存周期。
    # 为了消除这个不良影响，我们创建一个新的列表对象，以不修改原始数据

    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]  # chop out axis used for splitting
            reducedFeatVec.extend(featVec[axis + 1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

# 选择最好的数据划分方式
# 遍历整个数据集，循环计算Shannon熵和spiltDataSet()函数，找到最好的特征划分方式

'''数据需要满足的要求
一：数据必须是一种由列表元素组成的列表，而且所有的列表元素都要具备相同的数据长度
二：数据的最后一列或者每个实例的最后一个元素是当前实例的类型标签
'''

def chooseBestFeatureToSpilt(dataSet):
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = caluShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numFeatures):
        # 创建唯一的分类标签列表
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        # 从列表中创建集合是python中得到列表中唯一元素值最快的方法
        newEntropy = 0.0
        for value in uniqueVals:
            # 计算每种划分方式的信息熵
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * caluShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy
        if (infoGain > bestInfoGain):
            # 计算最好的信息增益
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature


# 使用分类名称的列表，然后创建键值为classList中唯一值的数据字典，字典对象存储了classCount中每个类标签出现的频率
# 然后使用operator操作键值排序字典，并返回出现最多的分类名称
def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(), key = operator.itemgetter(1),
                              reversed = True)
    return sortedClassCount

# 创建树的函数代码

'''参数：
dataSet：数据集
                数据集的要求同上
labels：标签列表，
                标签列表包含了数据集中所有特征的标签，算法本身并不需要这个变量，但是为了给出数据明确的含义
                我们将它作为一个参数输入
'''

def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    # 类别完全相同则停止划分
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    # 停止条件：使用完了所有特征，但仍然不能讲数据集划分成仅包含唯一类别的分组
    if len(dataSet[0]) == 1:
        # 遍历完所有特征是返回出现次数最多的类别
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSpilt(dataSet)
    bestFeatLabel = labels[bestFeat]
    # 得到列表包含的所有属性值
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]   # 复制类标签，为保护原始数据
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value),
                                                  subLabels)
    return myTree

# 使用决策树的分类函数
def classify(inputTree, featLabels, testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    # 将标签类型转换为引索
    # 以解决程序无法确定特征在数据集中的位置。特征标签列表将帮助程序处理这个问题
    featIndex = featLabels.index(firstStr)
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLabels, testVec)
            else:
                classLabel = secondDict[key]
    return classLabel

# 使用pickle模块储存决策树
# 为节省时间，能够在每次执行分类时调用已经构造好的决策树
def storeTree(inputTree, fileName):
    import pickle
    fw = open(fileName,'w')
    pickle.dump(inputTree, fw)
    fw.close()

def grabTree(fileName):
    import pickle
    fr = open(fileName)
    return pickle.load(fr)





