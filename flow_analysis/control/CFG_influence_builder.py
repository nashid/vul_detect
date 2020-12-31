'''build control dependency map

@author : jumormt
@version : 1.0
'''
__author__ = "jumormt"

import networkx as nx
from networkx.drawing.nx_pydot import read_dot
from utils.svf_parser import getNodeIDNo, getCFGFuncEntryExit, buildCFGNodeToLineDict, locateLineEntry


@DeprecationWarning
def isDoWhileEntry(curNodeID, CFGs, CFGsNodeToLineDict, filePath):
    '''
    judge if cur nodeid is "do-while" 's entry
    :param curNodeID:
    :param CFGs:
    :param CFGsNodeToLineDict:
    :param filePath:
    :return:
    '''
    predNodeIDs = CFGs._pred[curNodeID]
    for predNodeID in predNodeIDs:
        if predNodeID in CFGsNodeToLineDict.keys():
            predLine = CFGsNodeToLineDict[predNodeID]
            with open(filePath, "r", encoding="utf-8", errors='ignore') as f:
                fileContent = f.readlines()
                predLineContent = fileContent[predLine - 1]
                if predLineContent.find("do") != -1:  # do-while
                    return True
    return False


@DeprecationWarning
def isWhileEntry(curNodeID, CFGs, CFGsNodeToLineDict, filePath,
                 hotNodeLineStack):
    '''
    judge if cur nodeid is "while"or "for" 's entry
    note: does not consider do-while {if}
    :param curNodeID:
    :param CFGs:
    :param CFGsNodeToLineDict:
    :param filePath:
    :return:
    '''
    # if isDoWhileEntry(curNodeID, CFGs, CFGsNodeToLineDict, filePath):
    #     return False

    predNodeIDs = CFGs._pred[curNodeID]
    issWhileEntry = False
    for predNodeID in predNodeIDs:
        if predNodeID in CFGsNodeToLineDict:
            predNodeLine = CFGsNodeToLineDict[predNodeID]
            with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
                fileContent = f.readlines()
                lineContent = fileContent[predNodeLine - 1]
                if lineContent.find("break") != -1:
                    return False
                if lineContent.find("while") != -1 or lineContent.find(
                        "for") != -1:
                    issWhileEntry = True
    return issWhileEntry
    # visitedNodeIDs = set()
    # visitedNodeIDs.add(curNodeID)
    #
    # issWhileEntry = dfsIsWhileEntry(curNodeID, CFGs, visitedNodeIDs, CFGsNodeToLineDict, filePath) and (
    #     not ((hotNodeLineStack[-1][1] == "switch" or hotNodeLineStack[-1][1] == "if" or hotNodeLineStack[-1][
    #         1] == "others" or hotNodeLineStack[-1][1] == "loop-if") and hotNodeLineStack[-2][
    #              1] == "do-while"))
    #
    # return issWhileEntry


@DeprecationWarning
def isLoopLikeIfExit(curNodeID, CFGs, CFGsNodeToLineDict, filePath,
                     hotLineStack):
    issLoopLikeIfExit = False

    while (len(hotLineStack) != 0):
        hotline = hotLineStack.pop()
        if hotline[1] == "loop-if":
            break

    if len(hotLineStack) == 0:  # no pred "loop-if"
        return issLoopLikeIfExit

    predNodeIDs = CFGs._pred[curNodeID]
    haveBreak = False
    haveLoop = False
    for predNodeID in predNodeIDs:
        if predNodeID in CFGsNodeToLineDict:
            predNodeLine = CFGsNodeToLineDict[predNodeID]
            with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
                fileContent = f.readlines()
                lineContent = fileContent[predNodeLine - 1]
                if lineContent.find("break") != -1:
                    haveBreak = True
                if lineContent.find("while") != -1 or lineContent.find(
                        "for") != -1:
                    haveLoop = True
    issLoopLikeIfExit = (haveBreak and haveLoop)
    return issLoopLikeIfExit


@DeprecationWarning
def dfsIsWhileEntry(curNodeID, CFGs, visitedNodeIDs, CFGsNodeToLineDict,
                    filePath):
    '''
    isWhileEntry-key，judge if cur nodeid is "while" or "for" 's entry
    :param curNodeID:
    :param CFGs:
    :param visitedNodeIDs:
    :param CFGsNodeToLineDict:
    :param filePath:
    :return:
    '''
    nextNodeIDs = CFGs._succ[curNodeID]

    for nextNodeID in nextNodeIDs:
        if nextNodeID not in visitedNodeIDs:
            visitedNodeIDs.add(nextNodeID)

            if len(CFGs._pred[nextNodeID]
                   ) > 1:  # once meet other branch out - not loop!
                return False
            if len(CFGs._succ[nextNodeID]) > 1:
                # with open("resources/testcase-loop/strcpy-demo.cpp", "r", encoding="utf-8") as f:
                with open(filePath, "r", encoding="utf-8",
                          errors='ignore') as f:
                    fileContent = f.readlines()
                    curLine = CFGsNodeToLineDict[
                        nextNodeID]  # guess exit node must have a line
                    curLineContent = fileContent[curLine - 1]
                    # if (curLineContent.find("if") == -1 and curLineContent.find("switch") == -1 and curLineContent.find(
                    #         "case") == -1):  # not if branch - is while or for!
                    if (curLineContent.find("while") != -1
                            or curLineContent.find("for") !=
                            -1):  # is while or for!
                        return True
                    else:
                        return False

            if (dfsIsWhileEntry(nextNodeID, CFGs, visitedNodeIDs,
                                CFGsNodeToLineDict, filePath)):
                return True
            else:
                return False

    return False  # no more branch - not loop!


@DeprecationWarning
def isIfExit(curNodeID, CFGs, CFGsNodeToLineDict, filePath, hotNodeLineStack):
    '''
    judge if cur nodeid is "if branch" 's like exit
    :param nodeID:
    :param CFGs:
    :return:
    '''
    if hotNodeLineStack[-1][1] == "switch":
        return True
    if hotNodeLineStack[-1][1] == "if" or hotNodeLineStack[-1][1] == "others" or \
            hotNodeLineStack[-1][1] == "if-break":
        predNodeIDs = CFGs._pred[curNodeID]
        with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
            fileContent = f.readlines()
            for predNodeID in predNodeIDs:
                if predNodeID in CFGsNodeToLineDict:
                    predNodeLine = CFGsNodeToLineDict[predNodeID]
                    predNodeLineContent = fileContent[predNodeLine - 1]
                    if predNodeLineContent.find("break") != -1:
                        return False
        return True
    return False


@DeprecationWarning
def dfsIsIfExit(curNodeID, CFGs, visitedNodeIDs, CFGsNodeToLineDict, filePath):
    '''
    isIfExit-key，judge if cur nodeid is "if branch" 's exit
    :param curNodeID:
    :param CFGs:
    :param visitedNodeIDs:
    :param CFGsNodeToLineDict:
    :param testcasesID:
    :param xmlPath:
    :return:
    '''
    nextNodeIDs = CFGs._succ[curNodeID]

    for nextNodeID in nextNodeIDs:
        if nextNodeID not in visitedNodeIDs:
            visitedNodeIDs.add(nextNodeID)

            if len(CFGs._pred[nextNodeID]
                   ) > 1:  # once meet other branch out - not loop!
                return True
            if len(CFGs._succ[nextNodeID]) > 1:
                # with open("resources/testcase-loop/strcpy-demo.cpp", "r", encoding="utf-8") as f:
                with open(filePath, "r", encoding="utf-8",
                          errors='ignore') as f:
                    fileContent = f.readlines()
                    curLine = CFGsNodeToLineDict[
                        nextNodeID]  # guess exit node must have a line
                    curLineContent = fileContent[curLine - 1]
                    if (curLineContent.find("if") != -1
                            or curLineContent.find("switch") != -1
                            or curLineContent.find("case") !=
                            -1):  # once meet if branch - not loop!
                        return True
                    else:
                        return False

            if (dfsIsIfExit(nextNodeID, CFGs, visitedNodeIDs,
                            CFGsNodeToLineDict, filePath)):
                return True
            else:
                return False

    return True  # no more branch - not loop!


@DeprecationWarning
def getDoWhileCondition(curNodeID, CFGs, CFGsNodeToLineDict, filePath):
    '''
    get "do-while" condition line
    :param curNodeID:
    :param CFGs:
    :param CFGsNodeToLineDict:
    :param filePath:
    :return:
    '''
    predNodeIDs = CFGs._pred[curNodeID]
    for predNodeID in predNodeIDs:
        if predNodeID in CFGsNodeToLineDict.keys():
            predLine = CFGsNodeToLineDict[predNodeID]
            with open(filePath, "r", encoding="utf-8", errors='ignore') as f:
                fileContent = f.readlines()
                predLineContent = fileContent[predLine - 1]
                if predLineContent.find(
                        "while") != -1:  # not "do" - condition line
                    return predLine
                if predLineContent.find("}") != -1:
                    visited = set()
                    visited.add(predNodeID)
                    return dfsGetDoWhileCondition(predNodeID, CFGs,
                                                  CFGsNodeToLineDict,
                                                  fileContent, visited)


@DeprecationWarning
def dfsGetDoWhileCondition(curNodeID, CFGs, CFGsNodeToLineDict, fileContent,
                           visited):
    if curNodeID in CFGsNodeToLineDict.keys():
        curLine = CFGsNodeToLineDict[curNodeID]
        curLineContent = fileContent[curLine - 1]
        if curLineContent.find("while") != -1:
            return curLine

    predNodeIDs = CFGs._pred[curNodeID]
    for predNodeID in predNodeIDs:
        if predNodeID not in visited:
            visited.add(predNodeID)
            return dfsGetDoWhileCondition(predNodeID, CFGs, CFGsNodeToLineDict,
                                          fileContent, visited)


@DeprecationWarning
def getWhileCondition(curNodeID, CFGs, filePath, CFGsNodeToLineDict):
    predNodeIDs = CFGs._pred[curNodeID]
    for predNodeID in predNodeIDs:
        if predNodeID in CFGsNodeToLineDict.keys():
            predLine = CFGsNodeToLineDict[predNodeID]
            with open(filePath, "r", encoding="utf-8", errors='ignore') as f:
                predLineContent = f.readlines()[predLine - 1]
                if predLineContent.find("while") != -1 or predLineContent.find(
                        "for") != -1:
                    return predLine


@DeprecationWarning
def isPredBreak(hotlinestack, curNodeID, CFGs, CFGsNodeToLineDict, filePath):
    isPredBreak = False
    haveLoop = False
    while (len(hotlinestack) != 0):
        hotline = hotlinestack.pop()
        if hotline[1] == "do-while" or hotline[1] == "loop":
            break
        if hotline[1] == "switch":
            return isPredBreak
    if len(hotlinestack) == 0:
        return isPredBreak

    for predNodeID in CFGs._pred[curNodeID]:
        if predNodeID in CFGsNodeToLineDict:
            predNodeLine = CFGsNodeToLineDict[predNodeID]
            with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
                fileContent = f.readlines()
                if fileContent[predNodeLine - 1].find("break") != -1:
                    isPredBreak = True
                if fileContent[predNodeLine - 1].find(
                        "for") != -1 or fileContent[predNodeLine -
                                                    1].find("while") != -1:
                    haveLoop = True

    return (isPredBreak and haveLoop)


@DeprecationWarning
def isDoWhileExit(curNodeID, hotNodeLineStack, CFGs, curLineContent,
                  fileContent, CFGNodeTOLineDict):
    # if (hotNodeLineStack[-1][1] == "do-while" and curLineContent.find("while") != -1):
    #     return True

    nextNodeIDs = CFGs._succ[curNodeID]
    nextss = list(nextNodeIDs.keys())
    nextss.sort()
    nextNodeID = nextss[0]
    if len(CFGs._pred[nextNodeID]) > 1:
        predNodeIDs = CFGs._pred[nextNodeID]
        for predNodeID in predNodeIDs:
            if predNodeID != curNodeID:
                if predNodeID in CFGNodeTOLineDict:
                    if fileContent[CFGNodeTOLineDict[predNodeID] -
                                   1].find("do") != -1:
                        return True
    return False


@DeprecationWarning
def isWhileBreak(nextNodeID, CFGs, filePath, CFGsNodeToLineDict):
    pass


@DeprecationWarning
def isLoopCondition(curNodeID, CFGsNodeToLineDict, CFGs):
    nextNodeIDs = CFGs._succ[curNodeID]
    for nextNodeID in nextNodeIDs:
        if nextNodeID in CFGsNodeToLineDict:
            if CFGsNodeToLineDict[nextNodeID] == 0:
                return True
    return False


@DeprecationWarning
def isContainBreakIfEntry(curNodeID, CFGs, fileContent, CFGsNodeToLineDict):
    visited = set()
    nextNodeIDs = CFGs._succ[curNodeID]
    issContainBreakIfEntry = [False, False]
    for nextNodeIDidx in range(len(nextNodeIDs)):
        nextNodeID = list(nextNodeIDs.keys())[nextNodeIDidx]
        visited.add(nextNodeID)
        issContainBreakIfEntry[nextNodeIDidx] = dfsContainBreakIfEntry(
            nextNodeID, CFGs, fileContent, CFGsNodeToLineDict, visited)

    return (issContainBreakIfEntry[0] or issContainBreakIfEntry[1])


@DeprecationWarning
def dfsContainBreakIfEntry(curNodeID, CFGs, fileContent, CFGsNodeToLineDict,
                           visited):
    if curNodeID in CFGsNodeToLineDict:
        curNodeLine = CFGsNodeToLineDict[curNodeID]
        curNodeContent = fileContent[curNodeLine - 1]
        if curNodeContent.find("break") != -1:
            return True

    nextNodeIDs = CFGs._succ[curNodeID]
    for nextNodeID in nextNodeIDs:
        if nextNodeID not in visited:
            visited.add(nextNodeID)

            if len(CFGs._pred[nextNodeID]) > 1 or len(
                    CFGs._succ[nextNodeID]) > 1:
                return False

            return dfsContainBreakIfEntry(nextNodeID, CFGs, fileContent,
                                          CFGsNodeToLineDict, visited)


@DeprecationWarning
def isIfBreakExit(curNodeID, filePath, CFGsNodeToLineDict, CFGs,
                  hotNodeLineStack):
    if hotNodeLineStack[-1][1] == "if" or hotNodeLineStack[-1][1] == "switch" or hotNodeLineStack[-1][1] == "others" or \
            hotNodeLineStack[-1][1] == "if-break":
        predNodeIDs = CFGs._pred[curNodeID]
        with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
            fileContent = f.readlines()
            for predNodeID in predNodeIDs:
                if predNodeID in CFGsNodeToLineDict:
                    predNodeLine = CFGsNodeToLineDict[predNodeID]
                    predNodeLineContent = fileContent[predNodeLine - 1]
                    if predNodeLineContent.find("break") != -1:
                        return True

    return False


@DeprecationWarning
def dfsBuildCFGDepdcy(curNodeID, hotNodeLineStack, CFGs, visitedNodeIDs,
                      CFGDepdcy, CFGsNodeToLineDict, filePath):
    '''
    buildCFGDepdcy - key，build control-flow dependency map
    :param curNodeID:
    :param hotNodeLineStack: control-flow dependent line(scope) stack
    :param CFGs:
    :param visitedNodeIDs:
    :param CFGDepdcy:
    :param CFGsNodeToLineDict:
    :return:
    '''

    nextNodeIDs = CFGs._succ[curNodeID]
    isLoop = False
    outLpNodeID = None
    if (len(nextNodeIDs) > 1):

        if (hotNodeLineStack[-1][1] == "loop"
            ):  # loop - for loop, only two branches
            if not isLoopCondition(curNodeID, CFGsNodeToLineDict, CFGs):
                isLoop = True

                # bigger node id - outside loop scope
                if getNodeIDNo(list(nextNodeIDs.keys())[0],
                               CFGs) > getNodeIDNo(
                                   list(nextNodeIDs.keys())[1], CFGs):
                    outLpNodeID = list(nextNodeIDs.keys())[0]
                else:
                    outLpNodeID = list(nextNodeIDs.keys())[1]

    nextss = list(nextNodeIDs.keys())
    nextss.sort(key=lambda x: getNodeIDNo(x, CFGs))
    for nextNodeID in nextss:  # smaller nodeidNo first
        # for nextNodeID in nextNodeIDs:
        # nextNodeIDidx = len(list(nextNodeIDs.keys())) - nextNodeIDidx - 1
        # nextNodeID = list(nextNodeIDs.keys())[nextNodeIDidx]
        if nextNodeID not in visitedNodeIDs:
            visitedNodeIDs.add(nextNodeID)
            outLoopHotLine = None
            if (isLoop and outLpNodeID == nextNodeID):
                outLoopHotLine = hotNodeLineStack.pop(
                )  # for outside loop scope

            nextNode = CFGs._node[nextNodeID]

            if ("color" in nextNode.keys() and nextNode["color"] == "black"):

                if (
                        len(CFGs._succ[nextNodeID]) > 1
                ):  # entering if scope , loop(while or for) branch or do-while exit

                    if nextNodeID in CFGsNodeToLineDict.keys():
                        curLine = CFGsNodeToLineDict[nextNodeID]
                        if (curLine != hotNodeLineStack[-1][0]):
                            if curLine not in CFGDepdcy:
                                CFGDepdcy[curLine] = hotNodeLineStack[-1][0]

                    # with open("resources/testcase-loop/strcpy-demo.cpp", "r", encoding="utf-8") as f:
                    with open(filePath, "r", encoding="utf-8",
                              errors='ignore') as f:

                        fileContent = f.readlines()
                        # update control-flow dependent line(scope)
                        curLine = CFGsNodeToLineDict[
                            nextNodeID]  # guess branch entering must have a line
                        curLineContent = fileContent[curLine - 1]
                        # hotNodeLineStack.append([curLine, "if"]) if curLineContent.find("if")!=-1 else hotNodeLineStack.append([curLine, "loop"])

                        # if (curLineContent.find("if") != -1 and isContainBreakIfEntry(nextNodeID, CFGs, fileContent,
                        #                                                               CFGsNodeToLineDict)):
                        #     hotNodeLineStack.append([curLine, "if-break"])

                        if (
                                curLineContent.find("if") != -1
                        ):  # if scope todo:switch(pass)?do-while? delete?(bug)
                            hotNodeLineStack.append([curLine, "if"])
                        elif (curLineContent.find("switch") != -1
                              or curLineContent.find("case") != -1):
                            hotNodeLineStack.append([curLine, "switch"])
                        elif (isLoopCondition(
                                nextNodeID, CFGsNodeToLineDict,
                                CFGs)):  # loop may have multiple condition
                            dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack,
                                              CFGs, visitedNodeIDs, CFGDepdcy,
                                              CFGsNodeToLineDict, filePath)
                            if (isLoop and outLpNodeID == nextNodeID):
                                hotNodeLineStack.append(outLoopHotLine)
                            continue
                        # elif (hotNodeLineStack[-1][1] == "do-while" and curLineContent.find("while") != -1):  # do-while exit
                        elif (isDoWhileExit(
                                nextNodeID, hotNodeLineStack, CFGs,
                                curLineContent, fileContent,
                                CFGsNodeToLineDict)):  # do-while exit

                            predHotLines = list()
                            predHotLineName = hotNodeLineStack[-1][1]
                            while predHotLineName != "do-while":
                                predHotLine = hotNodeLineStack.pop()
                                predHotLines.append(predHotLine)
                                predHotLineName = hotNodeLineStack[-1][1]
                            predHotLine = hotNodeLineStack.pop()
                            predHotLines.append(predHotLine)

                            if nextNodeID in CFGsNodeToLineDict.keys():
                                curLine = CFGsNodeToLineDict[nextNodeID]
                                if (curLine != predHotLine[0]):
                                    # if (curLine not in CFGDepdcy):
                                    #     CFGDepdcy[curLine] = hotNodeLineStack[-1][0]
                                    CFGDepdcy[curLine] = predHotLine[0]

                            if (predHotLine[0] != hotNodeLineStack[-1][0]
                                ):  # the exit must be condition
                                CFGDepdcy[
                                    predHotLine[0]] = hotNodeLineStack[-1][0]

                            dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack,
                                              CFGs, visitedNodeIDs, CFGDepdcy,
                                              CFGsNodeToLineDict, filePath)
                            while (len(predHotLines) != 0):
                                hotNodeLineStack.append(predHotLines.pop())

                            if (isLoop and outLpNodeID == nextNodeID):
                                hotNodeLineStack.append(outLoopHotLine)
                            continue

                        elif (hotNodeLineStack[-1][1] == "loop"
                              and (curLineContent.find("while") != -1
                                   or curLineContent.find("for") != -1
                                   or curLineContent.find("if") != -1)
                              ):  # loop(while or for)
                            # if (hotNodeLineStack[-1][1] == "do-while_while"):
                            #     hotNodeLineStack[-1][1] = "do-while"
                            hotNodeLineStack[-1][0] = curLine
                            dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack,
                                              CFGs, visitedNodeIDs, CFGDepdcy,
                                              CFGsNodeToLineDict, filePath)
                            if (isLoop and outLpNodeID == nextNodeID):
                                hotNodeLineStack.append(outLoopHotLine)
                            continue
                        elif (curLineContent.find("while") != -1
                              or curLineContent.find("for") != -1):
                            hotNodeLineStack.append([curLine, "loop-if"])
                        else:
                            curHotLine = hotNodeLineStack[-1][0]
                            hotNodeLineStack.append([curHotLine, "others"])

                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        hotNodeLineStack.pop()  # reverse-leaving cur-scope
                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue

                if (
                        len(CFGs._pred[nextNodeID]) > 1
                ):  # if exit , entering do-while or loop(while or for) branch or

                    if (nextNodeID in CFGsNodeToLineDict
                            and CFGsNodeToLineDict[nextNodeID] == 0):
                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue
                    elif (isPredBreak(hotNodeLineStack.copy(), nextNodeID,
                                      CFGs, CFGsNodeToLineDict, filePath)):
                        # meeting break, noting not break in switch
                        predHotLines = list()
                        predHotLineName = hotNodeLineStack[-1][1]
                        while predHotLineName != "loop" and predHotLineName != "do-while":
                            predHotLine = hotNodeLineStack.pop()
                            predHotLines.append(predHotLine)
                            predHotLineName = hotNodeLineStack[-1][1]
                        predHotLine = hotNodeLineStack.pop()
                        predHotLines.append(predHotLine)
                        if nextNodeID in CFGsNodeToLineDict.keys():
                            curLine = CFGsNodeToLineDict[nextNodeID]
                            if (curLine != hotNodeLineStack[-1][0]):
                                if curLine not in CFGDepdcy:
                                    CFGDepdcy[curLine] = hotNodeLineStack[-1][
                                        0]
                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        while len(predHotLines) != 0:
                            hotNodeLineStack.append(predHotLines.pop())
                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue

                    elif (isDoWhileEntry(nextNodeID, CFGs, CFGsNodeToLineDict,
                                         filePath)):  # do-while entry

                        doWhileCdLine = getDoWhileCondition(
                            nextNodeID, CFGs, CFGsNodeToLineDict, filePath)
                        hotNodeLineStack.append([doWhileCdLine, "do-while"])

                        if nextNodeID in CFGsNodeToLineDict.keys():
                            curLine = CFGsNodeToLineDict[nextNodeID]
                            if (curLine != hotNodeLineStack[-1][0]):
                                if curLine not in CFGDepdcy:
                                    CFGDepdcy[curLine] = hotNodeLineStack[-1][
                                        0]

                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        hotNodeLineStack.pop()
                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue

                    elif (isWhileEntry(
                            nextNodeID, CFGs, CFGsNodeToLineDict, filePath,
                            hotNodeLineStack)):  # while entry - may have bug
                        # if (hotNodeLineStack[-1][1] == "do-while"):
                        #     hotNodeLineStack[-1][1] = "do-while_while"
                        # pass
                        whileCdLine = getWhileCondition(
                            nextNodeID, CFGs, filePath, CFGsNodeToLineDict)
                        hotNodeLineStack.append([whileCdLine, "loop"])
                        if nextNodeID in CFGsNodeToLineDict.keys():
                            curLine = CFGsNodeToLineDict[nextNodeID]
                            if (curLine != hotNodeLineStack[-1][0]):
                                # if curLine not in CFGDepdcy:
                                #     CFGDepdcy[curLine] = hotNodeLineStack[-1][0]
                                CFGDepdcy[curLine] = hotNodeLineStack[-1][0]

                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        hotNodeLineStack.pop()
                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue
                    elif (isLoopLikeIfExit(nextNodeID, CFGs,
                                           CFGsNodeToLineDict, filePath,
                                           hotNodeLineStack.copy())):

                        predHotLines = list()
                        predHotLineName = hotNodeLineStack[-1][1]
                        while predHotLineName != "loop-if":
                            predHotLine = hotNodeLineStack.pop()
                            predHotLines.append(predHotLine)
                            predHotLineName = hotNodeLineStack[-1][1]
                        predHotLine = hotNodeLineStack.pop()
                        predHotLines.append(predHotLine)

                        if nextNodeID in CFGsNodeToLineDict.keys():
                            curLine = CFGsNodeToLineDict[nextNodeID]
                            if (curLine != hotNodeLineStack[-1][0]):
                                # if (curLine not in CFGDepdcy):
                                #     CFGDepdcy[curLine] = hotNodeLineStack[-1][0]
                                CFGDepdcy[curLine] = hotNodeLineStack[-1][0]

                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        while (len(predHotLines) != 0):
                            hotNodeLineStack.append(predHotLines.pop())

                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue

                    elif isIfExit(nextNodeID, CFGs, CFGsNodeToLineDict,
                                  filePath, hotNodeLineStack
                                  ):  # leaving if branch or implicit if
                        predHotLine = hotNodeLineStack.pop()

                        if nextNodeID in CFGsNodeToLineDict.keys():
                            curLine = CFGsNodeToLineDict[nextNodeID]
                            if (curLine != hotNodeLineStack[-1][0]):
                                if curLine not in CFGDepdcy:
                                    CFGDepdcy[curLine] = hotNodeLineStack[-1][
                                        0]

                        dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                                          visitedNodeIDs, CFGDepdcy,
                                          CFGsNodeToLineDict, filePath)
                        hotNodeLineStack.append(
                            predHotLine)  # reverse-entering pre-scope
                        if (isLoop and outLpNodeID == nextNodeID):
                            hotNodeLineStack.append(outLoopHotLine)
                        continue
                    elif isIfBreakExit(nextNodeID, filePath,
                                       CFGsNodeToLineDict, CFGs,
                                       hotNodeLineStack):
                        # todo:如何pop
                        pass
                    else:  # other
                        pass
                    # else: # loop

            if nextNodeID in CFGsNodeToLineDict.keys():
                curLine = CFGsNodeToLineDict[nextNodeID]
                if (curLine != hotNodeLineStack[-1][0]):
                    if curLine not in CFGDepdcy:
                        CFGDepdcy[curLine] = hotNodeLineStack[-1][0]

            dfsBuildCFGDepdcy(nextNodeID, hotNodeLineStack, CFGs,
                              visitedNodeIDs, CFGDepdcy, CFGsNodeToLineDict,
                              filePath)
            if (isLoop and outLpNodeID == nextNodeID):
                hotNodeLineStack.append(outLoopHotLine)


@DeprecationWarning
def buildCFGDepdcy(CFGs, CFGsNodeToLineDict, entryDict, filePath):
    '''
    build control-flow dependency map de - deprecated informal!

    :param CFGs:
    :param CFGsNodeToLineDict: {node:line}
    :param entryDict: cfg-entry {line:nodeid}
    :return: {line:its cfg-dependency-line} - funcLine:0 , func's first line:funcLine
    '''
    CFGDepdcy = dict()

    for key in entryDict:
        entryNodeID = entryDict[key]
        # entryNode = CFGs._node[entryNodeID]
        visitedNodeIDs = set()
        visitedNodeIDs.add(entryNodeID)
        hotLineStack = list()
        hotLineStack.append([key, "method"])
        CFGDepdcy[key] = 0
        dfsBuildCFGDepdcy(entryNodeID, hotLineStack, CFGs, visitedNodeIDs,
                          CFGDepdcy, CFGsNodeToLineDict, filePath)

    return CFGDepdcy


def connectExitZeroToExit(CFGs, funcDict, filePathList, lineToEntry,
                          CFGNodeToLineDict):
    '''connect exit(0) to exit node

    :param CFGs:
    :param funcDict:
    :param filePathList:
    :param lineToEntry: {entryLine:funcname}
    :param CFGNodeToLineDict: {nodeid:line}
    :return:
    '''
    for nodeid in CFGs._node:
        node = CFGs._node[nodeid]
        if len(CFGs._succ[nodeid]) == 0:
            if "color" in node and node["color"] == "black":
                if nodeid in CFGNodeToLineDict:
                    line = CFGNodeToLineDict[nodeid]
                    # with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
                    #     fileContent = f.readlines()
                    #     lineContent = fileContent[line-1]
                    # if lineContent.find("exit")!=-1 and lineContent.find("0") != -1:
                    methodLine = locateLineEntry(line,
                                                 list(lineToEntry.keys()))
                    entryName = lineToEntry[methodLine]
                    exitNodeID = funcDict[entryName]["exit"]
                    CFGs.add_edge(nodeid, exitNodeID)
    return CFGs


def preProcessCFG(CFGs, funcDict, filePath, lineToEntry, nodeToLineDict):
    '''preProcess CFG

    todo: preprocess CFG. e.g. exit(0) should be lined to exit node?

    :param CFGs:
    :param funcDict:
    :param filePath:
    :param lineToEntry: {entryLine:funcname}
    :param nodeToLineDict: {nodeid:line}
    :return:
    '''

    CFGs = connectExitZeroToExit(CFGs, funcDict, filePath, lineToEntry,
                                 nodeToLineDict)

    return CFGs


def buildPdomTree(entryID, exitID, funName, CFGsR):
    '''build post domains tree

     Construct the postdominator tree for AugCFG

    :param entryID:
    :param exitID:
    :param funName:
    :param CFGsR:
    :return:
    '''

    #  Augment the CFG by adding a node Start with edge (Start, entry)
    #  labeled “T” and edge (Start, exit) labeled “F”;call this AugCFG
    CFGsR.add_edges_from([(entryID, funName), (exitID, funName)])
    nxPdomDict = nx.immediate_dominators(CFGsR, exitID)
    # PdomEdgeDict = dict()

    PdomEdges = list()
    for i in nxPdomDict:
        # if getNodeIDNo(nxPdomDict[i],CFGsR) not in PdomEdgeDict:
        #     PdomEdgeDict[getNodeIDNo(nxPdomDict[i],CFGsR)] = list()
        if (nxPdomDict[i] != i):
            # PdomEdgeDict[getNodeIDNo(nxPdomDict[i],CFGsR)].append(getNodeIDNo(i,CFGsR))
            PdomEdges.append((nxPdomDict[i], i))
    # print(PdomEdgeDict)
    PdomTree = nx.DiGraph()
    PdomTree.add_edges_from(PdomEdges)
    return PdomTree


def buildPdomPtoChildDict(pdomTree, CFGsR):
    '''build postdominator tree parent to child dict

    mention the child is call the child including indirect as long as there exists a path from the node
    to the child node.

    :param pdomTree:
    :param CFGsR:
    :return: {nodeid:its all childs}
    '''

    pdomPtoChild = dict()
    # pdomPtoChildID = dict()
    for pnode in pdomTree._node:
        if pnode not in pdomPtoChild:
            pdomPtoChild[pnode] = set()
            # pdomPtoChildID[getNodeIDNo(pnode, CFGsR)] = set()

        queue = list()
        queue.append(pnode)
        while queue:
            fro = queue.pop(0)
            pdomPtoChild[pnode].add(fro)
            # pdomPtoChildID[getNodeIDNo(pnode, CFGsR)].add(getNodeIDNo(fro, CFGsR))
            for nxt in pdomTree._succ[fro]:
                queue.append(nxt)

        pdomPtoChild[pnode].remove(pnode)
        # pdomPtoChildID[getNodeIDNo(pnode, CFGsR)].remove(getNodeIDNo(pnode, CFGsR))
    return pdomPtoChild


def appendCFGDepdcyDict(CFGDepdcyDict, CFGInfluenceDict, CFGs,
                        PdomPtoChildDict, pdomTree):
    '''update control flow dependency dict

    :param CFGDepdcyDict:
    :param CFGs:
    :param PdomPtoChildDict:
    :param pdomTree:
    :return:{nodeid:set(its control dependent nodeids)}
    '''
    CDEdge = list()

    # Step4 : For AugCFG S consists of (Start, En),
    # (1,2), (1,4), (2,3),
    # (2,5) (i.e., those edges (A,B) in the AugCFG for which B is not an ancestor of A in Pdom
    # tree)
    for edge in CFGs.edges:
        if edge[1] in PdomPtoChildDict and edge[0] in PdomPtoChildDict:
            if not (edge[1] in PdomPtoChildDict
                    and edge[0] in PdomPtoChildDict[edge[1]]):
                CDEdge.append(edge)

    for edge in CDEdge:
        curNode = edge[0]
        L = None
        # Step5: find least common ancestor L
        if curNode in PdomPtoChildDict:
            if edge[1] in PdomPtoChildDict[curNode]:
                L = curNode
            else:
                while (len(pdomTree._pred[curNode]) != 0):
                    curNode = list(pdomTree._pred[curNode].keys())[0]
                    if edge[1] in PdomPtoChildDict[curNode]:
                        L = curNode
                        break
            # find nodes following pdomtree; edge[0] is the control dependent node
            Nodes = list()
            curNode = edge[1]
            while (curNode != L):
                Nodes.append(curNode)
                curNode = list(pdomTree._pred[curNode].keys())[0]

            if edge[0] not in CFGInfluenceDict:
                CFGInfluenceDict[edge[0]] = set()
            CFGInfluenceDict[edge[0]] = CFGInfluenceDict[edge[0]].union(
                set(Nodes))

            for node in Nodes:
                if node not in CFGDepdcyDict:
                    CFGDepdcyDict[node] = set()
                CFGDepdcyDict[node].add(edge[0])
    return CFGDepdcyDict, CFGInfluenceDict


def buildCFGDepedcyInflueceDict(cfgPath, filePathList):
    '''build cfgdependency and cfg inlunce for cur code

        :param cfgPath: path to icfg.dot
        :param filePathList: the source code path
        :return:
            :first: {nodeid:set(its control dependent nodeids)}
            :second: {line:set{its control dependent lines}}
            :third: {nodeid:set(its control influent nodeids)}
            :forth: {line:set(its control influent lines)}
        '''
    CFGs = read_dot(cfgPath)
    funcDict, lineToEntry = getCFGFuncEntryExit(CFGs, filePathList)
    nodeToLineDict = buildCFGNodeToLineDict(CFGs, filePathList)
    CFGs = preProcessCFG(CFGs, funcDict, filePathList, lineToEntry,
                         nodeToLineDict)

    CFGsR = CFGs.reverse(True)
    CFGDepdcyDict = dict()
    CFGInfluenceDict = dict()
    for funName in funcDict:
        exitID = funcDict[funName]["exit"]
        entryID = funcDict[funName]["entry"]
        pdomTree = buildPdomTree(entryID, exitID, funName, CFGsR)
        PdomPtoChildDict = buildPdomPtoChildDict(pdomTree, CFGsR)
        CFGs.add_edges_from([(funName, entryID), (funName, exitID)])

        CFGDepdcyDict, CFGInfluenceDict = appendCFGDepdcyDict(
            CFGDepdcyDict, CFGInfluenceDict, CFGs, PdomPtoChildDict, pdomTree)

    CFGLineDepdcyDict = dict()
    CFGLineInflueceDict = dict()

    for key in CFGInfluenceDict:
        if key in nodeToLineDict:
            lineKey = nodeToLineDict[key]
            if lineKey not in CFGLineInflueceDict:
                CFGLineInflueceDict[lineKey] = set()
            for cfif in list(CFGInfluenceDict[key]):
                if cfif in nodeToLineDict:
                    CFGLineInflueceDict[lineKey].add(nodeToLineDict[cfif])
                if cfif in funcDict:
                    CFGLineInflueceDict[lineKey].add(
                        funcDict[cfif]["entryLine"])
        elif key in funcDict:
            lineKey = funcDict[key]["entryLine"]
            if lineKey not in CFGLineInflueceDict:
                CFGLineInflueceDict[lineKey] = set()
            for cfif in list(CFGInfluenceDict[key]):
                if cfif in nodeToLineDict:
                    CFGLineInflueceDict[lineKey].add(nodeToLineDict[cfif])
                if cfif in funcDict:
                    CFGLineInflueceDict[lineKey].add(
                        funcDict[cfif]["entryLine"])

    for key in CFGDepdcyDict:
        if key in nodeToLineDict:
            lineKey = nodeToLineDict[key]
            if lineKey not in CFGLineDepdcyDict:
                CFGLineDepdcyDict[lineKey] = set()
            for cfdp in list(CFGDepdcyDict[key]):
                if cfdp in nodeToLineDict:
                    CFGLineDepdcyDict[lineKey].add(nodeToLineDict[cfdp])
                if cfdp in funcDict:
                    CFGLineDepdcyDict[lineKey].add(funcDict[cfdp]["entryLine"])
        elif key in funcDict:
            lineKey = funcDict[key]["entryLine"]
            if lineKey not in CFGLineDepdcyDict:
                CFGLineDepdcyDict[lineKey] = set()
            for cfdp in list(CFGDepdcyDict[key]):
                if cfdp in nodeToLineDict:
                    CFGLineDepdcyDict[lineKey].add(nodeToLineDict[cfdp])
                if cfdp in funcDict:
                    CFGLineDepdcyDict[lineKey].add(funcDict[cfdp]["entryLine"])

    return CFGDepdcyDict, CFGLineDepdcyDict, CFGInfluenceDict, CFGLineInflueceDict

    # Gr = nx.DiGraph(
    #     [("1", "En"), ("2", "1"), ("4", "1"), ("3", "2"), ("5", "2"), ("5", "4"), ("6", "5"), ("Ex", "3"), ("Ex", "6")])
    # Gr.add_edges_from([("Ex", "St"), ("En", "St")])
    # G = Gr.reverse(True)
    # d = dict()
    # r = nx.immediate_dominators(Gr, "Ex")
    # edges = list()
    # for key in r:
    #     if r[key] not in d:
    #         d[r[key]] = list()
    #     if r[key] != key:
    #         d[r[key]].append(key)
    #         edges.append((r[key], key))
    # print(d)
    # pdomTree = nx.DiGraph()
    # pdomTree.add_edges_from(edges)
    # CDEdge = list()
    #
    # pdomPtoChild = dict()
    # for pnode in pdomTree._node:
    #     if pnode not in pdomPtoChild:
    #         pdomPtoChild[pnode] = set()
    #
    #     queue = list()
    #     queue.append(pnode)
    #     while queue:
    #         fro = queue.pop()
    #         pdomPtoChild[pnode].add(fro)
    #         for nxt in pdomTree._succ[fro]:
    #             queue.append(nxt)
    #
    #     pdomPtoChild[pnode].remove(pnode)
    #
    # for edge in G.edges:
    #     if not (edge[1] in pdomPtoChild and edge[0] in pdomPtoChild[edge[1]]):
    #         CDEdge.append(edge)
    #
    # CDDict = dict()
    # for edge in CDEdge:
    #     curNode = edge[0]
    #     L = None
    #     if edge[1] in pdomPtoChild[curNode]:
    #         L = curNode
    #     else:
    #         while (len(pdomTree._pred[curNode]) != 0):
    #             curNode = list(pdomTree._pred[curNode].keys())[0]
    #             if edge[1] in pdomPtoChild[curNode]:
    #                 L = curNode
    #                 break
    #
    #     Nodes = list()
    #     curNode = edge[1]
    #     while (curNode != L):
    #         Nodes.append(curNode)
    #         curNode = list(pdomTree._pred[curNode].keys())[0]
    #
    #     for node in Nodes:
    #         if node not in CDDict:
    #             CDDict[node] = set()
    #         CDDict[node].add(edge[0])
    #     print()
    #
    # print()

    # print()


if __name__ == '__main__':
    root = "resources/testcase-buildcfg/"
    cfgPath = root + "icfg_initial.dot"
    filePath = "resources/testcase-buildcfg/strcpy-demo.cpp"

    CFGDepdcyDict, CFGLineDepdcyDict, CFGInflueceDict, CFGLineInflueceDict = buildCFGDepedcyInflueceDict(
        cfgPath, filePath)

    print("end")
