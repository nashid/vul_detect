'''dataflow using svfg

@author : jumormt
@version : 1.0
'''
__author__ = "jumormt"
from utils.svf_parser import buildSVFGNodeToLineDict, buildSVFGLineToNodeDict


def getCtxBFLines(SVFG, relatedLines, relatedLines_final, isFirst, DFCallPath):
    '''
    get context sensitive backward and forward slices
    for the first round, calc both backward slices and forward slices
    for later rounds(condition lines), only calc backward slices(data dependency)
    :param SVFG:
    :param relatedLines:
    :param relatedLines_final: 已经加入的行，无需再遍历
    :param DFCallPath:
    :return:
    '''
    lineToNodeDict = buildSVFGLineToNodeDict(SVFG)
    nodeToLineDict = buildSVFGNodeToLineDict(SVFG)

    BFLines = set()
    for relatedLine in relatedLines:
        if relatedLine not in lineToNodeDict.keys():
            continue
        relatedNodeIDList = lineToNodeDict[relatedLine]

        # for all rounds, calc backward slices(data dependency)
        backWardQueue = list()
        backWardVisited = set()
        backWardVisited = backWardVisited.union(relatedNodeIDList)
        backWardQueue.extend(relatedNodeIDList)
        while backWardQueue:
            curNodeID = backWardQueue.pop(0)
            predNodeIDs = SVFG._pred[curNodeID]

            isBackWardCall = False
            # isDashedRed = False
            if len(predNodeIDs) > 0:
                predNodeEdges = predNodeIDs[list(predNodeIDs.keys())[0]]
                for predNodeEdge in predNodeEdges:
                    predNodeEdgeAttr = predNodeEdges[predNodeEdge]
                    if "color" in predNodeEdgeAttr.keys(
                    ) and predNodeEdgeAttr["color"] == "red":
                        # if "style" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["style"] == "dashed":
                        #     isDashedRed = True
                        #     break

                        isBackWardCall = True
                        break

            # if isDashedRed:
            #     continue

            for predNodeID in predNodeIDs:

                if (predNodeID not in backWardVisited):
                    if isBackWardCall:  # back call
                        if predNodeID in nodeToLineDict.keys(
                        ) and nodeToLineDict[
                                predNodeID] in DFCallPath:  # in the cur call path

                            backWardVisited.add(predNodeID)
                            backWardQueue.append(predNodeID)
                    else:
                        backWardVisited.add(predNodeID)
                        backWardQueue.append(predNodeID)

                # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                end = predNodeID.find(":s")
                if end != -1:
                    predNodeID = predNodeID[:end]
                    if (predNodeID not in backWardVisited):

                        if isBackWardCall:
                            if predNodeID in nodeToLineDict.keys(
                            ) and nodeToLineDict[
                                    predNodeID] in DFCallPath:  # in the cur call path
                                backWardVisited.add(predNodeID)
                                backWardQueue.append(predNodeID)
                        else:
                            backWardVisited.add(predNodeID)
                            backWardQueue.append(predNodeID)

                if isBackWardCall:
                    if predNodeID not in nodeToLineDict.keys():
                        continue  # not in the cur call path, skip the node
                    else:
                        if nodeToLineDict[predNodeID] not in DFCallPath:
                            continue  # not in the cur call path, skip the node

                predNode = SVFG._node[predNodeID]

                if "label" not in predNode.keys():
                    continue
                label = predNode['label']
                start = label.find("ln:")
                end = label.find("fl:")
                if (start != -1 and end != -1):
                    predLine = int(label[start + 4:end - 1])
                    if (predLine not in relatedLines_final):
                        BFLines.add(predLine)
                        relatedLines_final.add(predLine)
                        predLineNodeIDList = lineToNodeDict[
                            predLine]  # line may map to multiple nodeid
                        for predLineNodeID in predLineNodeIDList:
                            if (predLineNodeID not in backWardVisited):
                                backWardVisited.add(predLineNodeID)
                                backWardQueue.append(predLineNodeID)
                            # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                            end = predLineNodeID.find(":s")
                            if end != -1:
                                predLineNodeID = predLineNodeID[:end]
                                if (predLineNodeID not in backWardVisited):
                                    backWardVisited.add(predLineNodeID)
                                    backWardQueue.append(predLineNodeID)

        if isFirst:
            # for the first round, calc both backward slices and forward slices
            # for the cfg condition, as mentioned aboye, only calc backward slices(its data dependency)
            forWardQueue = list()
            forWardVisited = set()
            forWardVisited = forWardVisited.union(relatedNodeIDList)
            forWardQueue.extend(relatedNodeIDList)
            while forWardQueue:
                curNodeID = forWardQueue.pop(0)

                # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
                # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
                # todo:why? will there be a situation that start from s2 and doesnt have s0 s1?
                curNodeSubIDList = list()
                scount = 0
                if curNodeID + ":s" + str(scount) in SVFG._node.keys():
                    curNodeSubIDList.append(curNodeID + ":s" + str(scount))
                scount = scount + 1
                while (curNodeID + ":s" + str(scount) in SVFG._node.keys()):
                    curNodeSubIDList.append(curNodeID + ":s" + str(scount))
                    scount = scount + 1
                for curNodeSubID in curNodeSubIDList:
                    if (curNodeSubID not in forWardVisited):
                        forWardVisited.add(curNodeSubID)
                        forWardQueue.append(curNodeSubID)

                nextNodeIDs = SVFG._succ[curNodeID]

                isForWardCall = False
                # isDashedBlue = False
                if len(nextNodeIDs) > 0:
                    nextNodeEdges = nextNodeIDs[list(nextNodeIDs.keys())[0]]
                    for nextNodeEdge in nextNodeEdges:
                        nextNodeEdgeAttr = nextNodeEdges[nextNodeEdge]
                        if "color" in nextNodeEdgeAttr.keys(
                        ) and nextNodeEdgeAttr["color"] == "blue":
                            # if "style" in nextNodeEdgeAttr and nextNodeEdgeAttr["style"] == "dashed":
                            #     isDashedBlue = True
                            #     break
                            isForWardCall = True
                            break

                # if isDashedBlue:
                #     continue

                for nextNodeID in nextNodeIDs:

                    nextNode = SVFG._node[nextNodeID]

                    if (nextNodeID not in forWardVisited):
                        if isForWardCall:
                            if nextNodeID in nodeToLineDict.keys(
                            ) and nodeToLineDict[
                                    nextNodeID] in DFCallPath:  # in the cur call path
                                forWardVisited.add(nextNodeID)
                                forWardQueue.append(nextNodeID)
                            else:
                                continue  # not in the cur call path, skip the node
                        else:
                            forWardVisited.add(nextNodeID)
                            forWardQueue.append(nextNodeID)

                    if "label" not in nextNode.keys():
                        continue

                    label = nextNode['label']
                    start = label.find("ln:")
                    end = label.find("fl:")
                    if (start != -1 and end != -1):
                        nextLine = int(label[start + 4:end - 1])
                        if (nextLine not in relatedLines_final):
                            BFLines.add(nextLine)
                            relatedLines_final.add(nextLine)
                            nextLineNodeIDList = lineToNodeDict[
                                nextLine]  # line may map to multiple nodeid
                            for nextLineNodeID in nextLineNodeIDList:
                                if (nextLineNodeID not in forWardVisited):
                                    forWardVisited.add(nextLineNodeID)
                                    forWardQueue.append(nextLineNodeID)

                                # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
                                # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
                                nextLnNodeSubIDList = list()
                                scount = 0
                                if nextLineNodeID + ":s" + str(
                                        scount) in SVFG._node.keys():
                                    nextLnNodeSubIDList.append(nextLineNodeID +
                                                               ":s" +
                                                               str(scount))
                                scount = scount + 1
                                while (nextLineNodeID + ":s" + str(scount)
                                       in SVFG._node.keys()):
                                    nextLnNodeSubIDList.append(nextLineNodeID +
                                                               ":s" +
                                                               str(scount))
                                    scount = scount + 1
                                for nextLnNodeSubID in nextLnNodeSubIDList:
                                    if (nextLnNodeSubID not in forWardVisited):
                                        forWardVisited.add(nextLnNodeSubID)
                                        forWardQueue.append(nextLnNodeSubID)

        # Queue = list()
        # Visited = set()
        # Visited = Visited.union(relatedNodeIDList)
        # Queue.extend(relatedNodeIDList)
        # while Queue:
        #     curNodeID = Queue.pop(0)
        #     predNodeIDs = SVFG._pred[curNodeID]
        #     nextNodeIDs = SVFG._succ[curNodeID]
        #     for predNodeID in predNodeIDs:
        #         forbidCallPass = False
        #         predNodeEdges = predNodeIDs[predNodeID]
        #         for predNodeEdge in predNodeEdges:
        #             predNodeEdgeAttr = predNodeEdges[predNodeEdge]
        #             if("color" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["color"] == "red"):
        #                 forbidCallPass = True
        #                 break
        #         if forbidCallPass:
        #             continue
        #         predNode = SVFG._node[predNodeID]
        #
        #         if (predNodeID not in Visited):
        #             Visited.add(predNodeID)
        #             Queue.append(predNodeID)
        #         if "label" not in predNode.keys():
        #             continue
        #         label = predNode['label']
        #         start = label.find("ln:")
        #         end = label.find("fl:")
        #         if (start != -1 and end != -1):
        #             predLine = int(label[start + 4:end - 1])
        #             if (predLine not in relatedLines_final):
        #                 BFLines.add(predLine)
        #                 relatedLines_final.add(predLine)
        #                 predLineNodeIDList = lineToNodeDict[predLine]
        #                 for predLineNodeID in predLineNodeIDList:
        #                     if (predLineNodeID not in Visited):
        #                         Visited.add(predLineNodeID)
        #                         Queue.append(predLineNodeID)
        #
        #     for nextNodeID in nextNodeIDs:
        #         forbidCallPass = False
        #         nextNodeEdges = predNodeIDs[nextNodeID]
        #         for nextNodeEdge in nextNodeEdges:
        #             nextNodeEdgeAttr = nextNodeEdges[nextNodeEdge]
        #             if ("color" in nextNodeEdgeAttr.keys() and nextNodeEdgeAttr["color"] == "blue"):
        #                 forbidCallPass = True
        #                 break
        #         if forbidCallPass:
        #             continue
        #
        #         nextNode = SVFG._node[nextNodeID]
        #
        #         if (nextNodeID not in Visited):
        #             Visited.add(nextNodeID)
        #             Queue.append(nextNodeID)
        #
        #         if "label" not in nextNode.keys():
        #             continue
        #         label = nextNode['label']
        #         start = label.find("ln:")
        #         end = label.find("fl:")
        #         if (start != -1 and end != -1):
        #             nextLine = int(label[start + 4:end - 1])
        #             if (nextLine not in relatedLines_final):
        #                 BFLines.add(nextLine)
        #                 relatedLines_final.add(nextLine)
        #                 nextLineNodeIDList = lineToNodeDict[nextLine]
        #                 for nextLineNodeID in nextLineNodeIDList:
        #                     if (nextLineNodeID not in Visited):
        #                         Visited.add(nextLineNodeID)
        #                         Queue.append(nextLineNodeID)

    return BFLines


def getBFLines(SVFG, relatedLines, relatedLines_final, isFirst):
    '''

    get context insensitive backward and forward slices
    for the first round, calc both backward slices and forward slices
    for later rounds(condition lines), only calc backward slices(data dependency)

    :param SVFG:
    :param relatedLines:
    :param relatedLines_final: 已经加入的行，无需再遍历
    :param DFCallPath:
    :return:
    '''
    lineToNodeDict = buildSVFGLineToNodeDict(SVFG)
    nodeToLineDict = buildSVFGNodeToLineDict(SVFG)

    BFLines = set()
    for relatedLine in relatedLines:
        if relatedLine not in lineToNodeDict.keys():
            continue
        relatedNodeIDList = lineToNodeDict[relatedLine]

        # for all rounds, calc backward slices(data dependency)
        backWardQueue = list()
        backWardVisited = set()
        backWardVisited = backWardVisited.union(relatedNodeIDList)
        backWardQueue.extend(relatedNodeIDList)
        while backWardQueue:
            curNodeID = backWardQueue.pop(0)
            predNodeIDs = SVFG._pred[curNodeID]

            # isBackWardCall = False
            # isDashedRed = False
            # if len(predNodeIDs) > 0:
            #     predNodeEdges = predNodeIDs[list(predNodeIDs.keys())[0]]
            #     for predNodeEdge in predNodeEdges:
            #         predNodeEdgeAttr = predNodeEdges[predNodeEdge]
            #         if "color" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["color"] == "red":
            #             # if "style" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["style"] == "dashed":
            #             #     isDashedRed = True
            #             #     break
            #
            #             isBackWardCall = True
            #             break

            # if isDashedRed:
            #     continue

            for predNodeID in predNodeIDs:

                if (predNodeID not in backWardVisited):
                    # if isBackWardCall:  # back call
                    #     if predNodeID in nodeToLineDict.keys() and nodeToLineDict[
                    #         predNodeID] in DFCallPath:  # in the cur call path
                    #
                    #         backWardVisited.add(predNodeID)
                    #         backWardQueue.append(predNodeID)
                    # else:
                    #     backWardVisited.add(predNodeID)
                    #     backWardQueue.append(predNodeID)

                    backWardVisited.add(predNodeID)
                    backWardQueue.append(predNodeID)

                # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                end = predNodeID.find(":s")
                if end != -1:
                    predNodeID = predNodeID[:end]
                    if (predNodeID not in backWardVisited):
                        # if isBackWardCall:
                        #     if predNodeID in nodeToLineDict.keys() and nodeToLineDict[
                        #         predNodeID] in DFCallPath:  # in the cur call path
                        #         backWardVisited.add(predNodeID)
                        #         backWardQueue.append(predNodeID)
                        # else:
                        #     backWardVisited.add(predNodeID)
                        #     backWardQueue.append(predNodeID)
                        backWardVisited.add(predNodeID)
                        backWardQueue.append(predNodeID)

                # if isBackWardCall:
                #     if predNodeID not in nodeToLineDict.keys():
                #         continue  # not in the cur call path, skip the node
                #     else:
                #         if nodeToLineDict[predNodeID] not in DFCallPath:
                #             continue  # not in the cur call path, skip the node

                predNode = SVFG._node[predNodeID]

                if "label" not in predNode.keys():
                    continue
                label = predNode['label']
                start = label.find("ln:")
                end = label.find("fl:")
                if (start != -1 and end != -1):
                    predLine = int(label[start + 4:end - 1])
                    if (predLine not in relatedLines_final):
                        BFLines.add(predLine)
                        relatedLines_final.add(predLine)
                        predLineNodeIDList = lineToNodeDict[
                            predLine]  # line may map to multiple nodeid
                        for predLineNodeID in predLineNodeIDList:
                            if (predLineNodeID not in backWardVisited):
                                backWardVisited.add(predLineNodeID)
                                backWardQueue.append(predLineNodeID)
                            # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                            end = predLineNodeID.find(":s")
                            if end != -1:
                                predLineNodeID = predLineNodeID[:end]
                                if (predLineNodeID not in backWardVisited):
                                    backWardVisited.add(predLineNodeID)
                                    backWardQueue.append(predLineNodeID)

        if isFirst:
            # for the first round, calc both backward slices and forward slices
            # for the cfg condition, as mentioned aboye, only calc backward slices(its data dependency)
            forWardQueue = list()
            forWardVisited = set()
            forWardVisited = forWardVisited.union(relatedNodeIDList)
            forWardQueue.extend(relatedNodeIDList)
            while forWardQueue:
                curNodeID = forWardQueue.pop(0)

                # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
                # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
                # todo:why? will there be a situation that start from s2 and doesnt have s0 s1?
                curNodeSubIDList = list()
                scount = 0
                if curNodeID + ":s" + str(scount) in SVFG._node.keys():
                    curNodeSubIDList.append(curNodeID + ":s" + str(scount))
                scount = scount + 1
                while (curNodeID + ":s" + str(scount) in SVFG._node.keys()):
                    curNodeSubIDList.append(curNodeID + ":s" + str(scount))
                    scount = scount + 1
                for curNodeSubID in curNodeSubIDList:
                    if (curNodeSubID not in forWardVisited):
                        forWardVisited.add(curNodeSubID)
                        forWardQueue.append(curNodeSubID)

                nextNodeIDs = SVFG._succ[curNodeID]

                # isForWardCall = False
                # isDashedBlue = False
                # if len(nextNodeIDs) > 0:
                #     nextNodeEdges = nextNodeIDs[list(nextNodeIDs.keys())[0]]
                #     for nextNodeEdge in nextNodeEdges:
                #         nextNodeEdgeAttr = nextNodeEdges[nextNodeEdge]
                #         if "color" in nextNodeEdgeAttr.keys() and nextNodeEdgeAttr["color"] == "blue":
                #             # if "style" in nextNodeEdgeAttr and nextNodeEdgeAttr["style"] == "dashed":
                #             #     isDashedBlue = True
                #             #     break
                #             isForWardCall = True
                #             break

                # if isDashedBlue:
                #     continue

                for nextNodeID in nextNodeIDs:

                    nextNode = SVFG._node[nextNodeID]

                    if (nextNodeID not in forWardVisited):
                        forWardVisited.add(nextNodeID)
                        forWardQueue.append(nextNodeID)
                        # if isForWardCall:
                        #     if nextNodeID in nodeToLineDict.keys() and nodeToLineDict[
                        #         nextNodeID] in DFCallPath:  # in the cur call path
                        #         forWardVisited.add(nextNodeID)
                        #         forWardQueue.append(nextNodeID)
                        #     else:
                        #         continue  # not in the cur call path, skip the node
                        # else:
                        #     forWardVisited.add(nextNodeID)
                        #     forWardQueue.append(nextNodeID)

                    if "label" not in nextNode.keys():
                        continue

                    label = nextNode['label']
                    start = label.find("ln:")
                    end = label.find("fl:")
                    if (start != -1 and end != -1):
                        nextLine = int(label[start + 4:end - 1])
                        if (nextLine not in relatedLines_final):
                            BFLines.add(nextLine)
                            relatedLines_final.add(nextLine)
                            nextLineNodeIDList = lineToNodeDict[
                                nextLine]  # line may map to multiple nodeid
                            for nextLineNodeID in nextLineNodeIDList:
                                if (nextLineNodeID not in forWardVisited):
                                    forWardVisited.add(nextLineNodeID)
                                    forWardQueue.append(nextLineNodeID)

                                # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
                                # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
                                nextLnNodeSubIDList = list()
                                scount = 0
                                if nextLineNodeID + ":s" + str(
                                        scount) in SVFG._node.keys():
                                    nextLnNodeSubIDList.append(nextLineNodeID +
                                                               ":s" +
                                                               str(scount))
                                scount = scount + 1
                                while (nextLineNodeID + ":s" + str(scount)
                                       in SVFG._node.keys()):
                                    nextLnNodeSubIDList.append(nextLineNodeID +
                                                               ":s" +
                                                               str(scount))
                                    scount = scount + 1
                                for nextLnNodeSubID in nextLnNodeSubIDList:
                                    if (nextLnNodeSubID not in forWardVisited):
                                        forWardVisited.add(nextLnNodeSubID)
                                        forWardQueue.append(nextLnNodeSubID)

        # Queue = list()
        # Visited = set()
        # Visited = Visited.union(relatedNodeIDList)
        # Queue.extend(relatedNodeIDList)
        # while Queue:
        #     curNodeID = Queue.pop(0)
        #     predNodeIDs = SVFG._pred[curNodeID]
        #     nextNodeIDs = SVFG._succ[curNodeID]
        #     for predNodeID in predNodeIDs:
        #         forbidCallPass = False
        #         predNodeEdges = predNodeIDs[predNodeID]
        #         for predNodeEdge in predNodeEdges:
        #             predNodeEdgeAttr = predNodeEdges[predNodeEdge]
        #             if("color" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["color"] == "red"):
        #                 forbidCallPass = True
        #                 break
        #         if forbidCallPass:
        #             continue
        #         predNode = SVFG._node[predNodeID]
        #
        #         if (predNodeID not in Visited):
        #             Visited.add(predNodeID)
        #             Queue.append(predNodeID)
        #         if "label" not in predNode.keys():
        #             continue
        #         label = predNode['label']
        #         start = label.find("ln:")
        #         end = label.find("fl:")
        #         if (start != -1 and end != -1):
        #             predLine = int(label[start + 4:end - 1])
        #             if (predLine not in relatedLines_final):
        #                 BFLines.add(predLine)
        #                 relatedLines_final.add(predLine)
        #                 predLineNodeIDList = lineToNodeDict[predLine]
        #                 for predLineNodeID in predLineNodeIDList:
        #                     if (predLineNodeID not in Visited):
        #                         Visited.add(predLineNodeID)
        #                         Queue.append(predLineNodeID)
        #
        #     for nextNodeID in nextNodeIDs:
        #         forbidCallPass = False
        #         nextNodeEdges = predNodeIDs[nextNodeID]
        #         for nextNodeEdge in nextNodeEdges:
        #             nextNodeEdgeAttr = nextNodeEdges[nextNodeEdge]
        #             if ("color" in nextNodeEdgeAttr.keys() and nextNodeEdgeAttr["color"] == "blue"):
        #                 forbidCallPass = True
        #                 break
        #         if forbidCallPass:
        #             continue
        #
        #         nextNode = SVFG._node[nextNodeID]
        #
        #         if (nextNodeID not in Visited):
        #             Visited.add(nextNodeID)
        #             Queue.append(nextNodeID)
        #
        #         if "label" not in nextNode.keys():
        #             continue
        #         label = nextNode['label']
        #         start = label.find("ln:")
        #         end = label.find("fl:")
        #         if (start != -1 and end != -1):
        #             nextLine = int(label[start + 4:end - 1])
        #             if (nextLine not in relatedLines_final):
        #                 BFLines.add(nextLine)
        #                 relatedLines_final.add(nextLine)
        #                 nextLineNodeIDList = lineToNodeDict[nextLine]
        #                 for nextLineNodeID in nextLineNodeIDList:
        #                     if (nextLineNodeID not in Visited):
        #                         Visited.add(nextLineNodeID)
        #                         Queue.append(nextLineNodeID)

    return BFLines


def getBackWardLines(SVFG, backWardRelatedLines, relatedLines_final,
                     edges_final, lineToNodeDict, nodeToLineDict,
                     edges_visited):
    '''get backward data dependent lines

    get backward data dependent lines using SVFG.
    data dependent means the use-def

    :param SVFG:
    :param backWardRelatedLines:
    :param relatedLines_final:
    :param edges_final:
    :param lineToNodeDict:
    :param nodeToLineDict:
    :return:
    '''

    BackWardLines = set()
    for backWardRelatedLine in backWardRelatedLines:
        if backWardRelatedLine not in lineToNodeDict.keys():
            continue
        relatedNodeIDList = lineToNodeDict[backWardRelatedLine]

        # for all rounds, calc backward slices(data dependency)
        backWardQueue = list()
        backWardVisited = set()
        backWardVisited = backWardVisited.union(relatedNodeIDList)
        backWardQueue.extend(relatedNodeIDList)
        while backWardQueue:
            curNodeID = backWardQueue.pop(0)
            cur_end = curNodeID.find(":s")
            if cur_end != -1:
                curNodeID_k = curNodeID[:cur_end]
            else:
                curNodeID_k = curNodeID
            predNodeIDs = SVFG._pred[curNodeID]

            for predNodeID in predNodeIDs:
                if (predNodeID not in backWardVisited):
                    backWardVisited.add(predNodeID)
                    backWardQueue.append(predNodeID)

                # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                end = predNodeID.find(":s")
                if end != -1:
                    predNodeID = predNodeID[:end]
                    if (predNodeID not in backWardVisited):
                        backWardVisited.add(predNodeID)
                        backWardQueue.append(predNodeID)

                if predNodeID not in nodeToLineDict:
                    continue

                predLine = nodeToLineDict[predNodeID]
                if (curNodeID_k in nodeToLineDict):
                    if (predLine != nodeToLineDict[curNodeID_k]):

                        edges_tmp = str(predLine) + "_" + str(
                            nodeToLineDict[curNodeID_k])
                        if edges_tmp not in edges_visited:
                            edges_visited.add(edges_tmp)
                            edges_final.append(
                                [predLine, nodeToLineDict[curNodeID_k]])

                if (predLine not in relatedLines_final):
                    # if predLine.split("_")[1] != "0":
                    BackWardLines.add(predLine)
                    relatedLines_final.add(predLine)

                    predLineNodeIDList = lineToNodeDict[
                        predLine]  # line may map to multiple nodeid
                    for predLineNodeID in predLineNodeIDList:
                        if (predLineNodeID not in backWardVisited):
                            backWardVisited.add(predLineNodeID)
                            backWardQueue.append(predLineNodeID)
                        # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                        end = predLineNodeID.find(":s")
                        if end != -1:
                            predLineNodeID = predLineNodeID[:end]
                            if (predLineNodeID not in backWardVisited):
                                backWardVisited.add(predLineNodeID)
                                backWardQueue.append(predLineNodeID)
    return BackWardLines


def getBackWardEdgesLines(SVFG, backWardRelatedLines, relatedLines_final,
                          dataFlowEdges, lineToNodeDict, nodeToLineDict):
    '''get backward data dependent lines

    get backward data dependent lines using SVFG.
    data dependent means the use-def

    :param SVFG:
    :param backWardRelatedLines:
    :param relatedLines_final:
    :param dataFlowEdges:
    :param lineToNodeDict:
    :param nodeToLineDict:
    :return:
    '''

    BackWardLines = set()
    for backWardRelatedLine in backWardRelatedLines:
        if backWardRelatedLine not in lineToNodeDict.keys():
            continue
        relatedNodeIDList = lineToNodeDict[backWardRelatedLine]

        # for all rounds, calc backward slices(data dependency)
        backWardQueue = list()
        backWardVisited = set()
        backWardVisited = backWardVisited.union(relatedNodeIDList)
        backWardQueue.extend(relatedNodeIDList)
        while backWardQueue:
            curNodeID = backWardQueue.pop(0)
            predNodeIDs = SVFG._pred[curNodeID]

            # isBackWardCall = False
            # isDashedRed = False
            # if len(predNodeIDs) > 0:
            #     predNodeEdges = predNodeIDs[list(predNodeIDs.keys())[0]]
            #     for predNodeEdge in predNodeEdges:
            #         predNodeEdgeAttr = predNodeEdges[predNodeEdge]
            #         if "color" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["color"] == "red":
            #             # if "style" in predNodeEdgeAttr.keys() and predNodeEdgeAttr["style"] == "dashed":
            #             #     isDashedRed = True
            #             #     break
            #
            #             isBackWardCall = True
            #             break

            # if isDashedRed:
            #     continue

            for predNodeID in predNodeIDs:

                if (predNodeID not in backWardVisited):
                    # if isBackWardCall:  # back call
                    #     if predNodeID in nodeToLineDict.keys() and nodeToLineDict[
                    #         predNodeID] in DFCallPath:  # in the cur call path
                    #
                    #         backWardVisited.add(predNodeID)
                    #         backWardQueue.append(predNodeID)
                    # else:
                    #     backWardVisited.add(predNodeID)
                    #     backWardQueue.append(predNodeID)

                    backWardVisited.add(predNodeID)
                    backWardQueue.append(predNodeID)

                # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                end = predNodeID.find(":s")
                if end != -1:
                    predNodeID = predNodeID[:end]
                    if (predNodeID not in backWardVisited):
                        # if isBackWardCall:
                        #     if predNodeID in nodeToLineDict.keys() and nodeToLineDict[
                        #         predNodeID] in DFCallPath:  # in the cur call path
                        #         backWardVisited.add(predNodeID)
                        #         backWardQueue.append(predNodeID)
                        # else:
                        #     backWardVisited.add(predNodeID)
                        #     backWardQueue.append(predNodeID)
                        backWardVisited.add(predNodeID)
                        backWardQueue.append(predNodeID)

                # if isBackWardCall:
                #     if predNodeID not in nodeToLineDict.keys():
                #         continue  # not in the cur call path, skip the node
                #     else:
                #         if nodeToLineDict[predNodeID] not in DFCallPath:
                #             continue  # not in the cur call path, skip the node

                if predNodeID not in nodeToLineDict:
                    continue

                predLine = nodeToLineDict[predNodeID]

                if (predLine not in relatedLines_final):
                    # if predLine.split("_")[1] != "0":
                    BackWardLines.add(predLine)
                    relatedLines_final.add(predLine)
                    predLineNodeIDList = lineToNodeDict[
                        predLine]  # line may map to multiple nodeid
                    for predLineNodeID in predLineNodeIDList:
                        if (predLineNodeID not in backWardVisited):
                            backWardVisited.add(predLineNodeID)
                            backWardQueue.append(predLineNodeID)
                        # for nodeid:s0 nodeid:s1 etc.. get nodeid instead
                        end = predLineNodeID.find(":s")
                        if end != -1:
                            predLineNodeID = predLineNodeID[:end]
                            if (predLineNodeID not in backWardVisited):
                                backWardVisited.add(predLineNodeID)
                                backWardQueue.append(predLineNodeID)
    return BackWardLines


def getForWardLines(SVFG, forWardRelatedLines, forwardRelatedLines_final,
                    edges_final, lineToNodeDict, nodeToLineDict,
                    edges_visited):
    '''get forward data influent lines

    get forward data influent lines using SVFG.
    data influent means the def-use

    :param SVFG:
    :param forWardRelatedLines:
    :param forwardRelatedLines_final:
    :param lineToNodeDict:
    :param nodeToLineDict:
    :return:
    '''

    ForWardLines = set()
    for forWardRelatedLine in forWardRelatedLines:
        if forWardRelatedLine not in lineToNodeDict.keys():
            continue
        relatedNodeIDList = lineToNodeDict[forWardRelatedLine]

        # for the first round, calc both backward slices and forward slices
        # for the cfg condition, as mentioned aboye, only calc backward slices(its data dependency)
        forWardQueue = list()
        forWardVisited = set()
        forWardVisited = forWardVisited.union(relatedNodeIDList)
        forWardQueue.extend(relatedNodeIDList)
        while forWardQueue:
            curNodeID = forWardQueue.pop(0)
            cur_end = curNodeID.find(":s")
            if cur_end != -1:
                curNodeID_k = curNodeID[:cur_end]
            else:
                curNodeID_k = curNodeID

            # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
            # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
            # todo:why? will there be a situation that start from s2 and doesnt have s0 s1?
            curNodeSubIDList = list()
            scount = 0
            if curNodeID + ":s" + str(scount) in SVFG._node.keys():
                curNodeSubIDList.append(curNodeID + ":s" + str(scount))
            scount = scount + 1
            while (curNodeID + ":s" + str(scount) in SVFG._node.keys()):
                curNodeSubIDList.append(curNodeID + ":s" + str(scount))
                scount = scount + 1
            for curNodeSubID in curNodeSubIDList:
                if (curNodeSubID not in forWardVisited):
                    forWardVisited.add(curNodeSubID)
                    forWardQueue.append(curNodeSubID)

            nextNodeIDs = SVFG._succ[curNodeID]

            for nextNodeID in nextNodeIDs:

                if (nextNodeID not in forWardVisited):
                    forWardVisited.add(nextNodeID)
                    forWardQueue.append(nextNodeID)

                if nextNodeID not in nodeToLineDict:
                    continue

                nextLine = nodeToLineDict[nextNodeID]
                if (curNodeID_k in nodeToLineDict):
                    if (nodeToLineDict[curNodeID_k] != nextLine):
                        edges_tmp = str(
                            nodeToLineDict[curNodeID_k]) + "_" + str(nextLine)
                        if edges_tmp not in edges_visited:
                            edges_visited.add(edges_tmp)
                            edges_final.append(
                                [nodeToLineDict[curNodeID_k], nextLine])

                if (nextLine not in forwardRelatedLines_final):
                    # if nextLine.split("_")[1] != "0":
                    ForWardLines.add(nextLine)
                    forwardRelatedLines_final.add(nextLine)
                    nextLineNodeIDList = lineToNodeDict[
                        nextLine]  # line may map to multiple nodeid
                    for nextLineNodeID in nextLineNodeIDList:
                        if (nextLineNodeID not in forWardVisited):
                            forWardVisited.add(nextLineNodeID)
                            forWardQueue.append(nextLineNodeID)

                        # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
                        # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
                        nextLnNodeSubIDList = list()
                        scount = 0
                        if nextLineNodeID + ":s" + str(
                                scount) in SVFG._node.keys():
                            nextLnNodeSubIDList.append(nextLineNodeID + ":s" +
                                                       str(scount))
                        scount = scount + 1
                        while (nextLineNodeID + ":s" + str(scount)
                               in SVFG._node.keys()):
                            nextLnNodeSubIDList.append(nextLineNodeID + ":s" +
                                                       str(scount))
                            scount = scount + 1
                        for nextLnNodeSubID in nextLnNodeSubIDList:
                            if (nextLnNodeSubID not in forWardVisited):
                                forWardVisited.add(nextLnNodeSubID)
                                forWardQueue.append(nextLnNodeSubID)

    return ForWardLines


def getForWardEdgesLines(SVFG, forWardRelatedLines, forwardRelatedLines_final,
                         dataflowEdges, lineToNodeDict, nodeToLineDict):
    '''get forward data influent lines

    get forward data influent lines using SVFG.
    data influent means the def-use

    :param SVFG:
    :param forWardRelatedLines:
    :param forwardRelatedLines_final:
    :param dataflowEdges:
    :param lineToNodeDict:
    :param nodeToLineDict:
    :return:
    '''

    ForWardLines = set()
    for forWardRelatedLine in forWardRelatedLines:
        if forWardRelatedLine not in lineToNodeDict.keys():
            continue
        relatedNodeIDList = lineToNodeDict[forWardRelatedLine]

        # for the first round, calc both backward slices and forward slices
        # for the cfg condition, as mentioned aboye, only calc backward slices(its data dependency)
        forWardQueue = list()
        forWardVisited = set()
        forWardVisited = forWardVisited.union(relatedNodeIDList)
        forWardQueue.extend(relatedNodeIDList)
        while forWardQueue:
            curNodeID = forWardQueue.pop(0)

            # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
            # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
            # todo:why? will there be a situation that start from s2 and doesnt have s0 s1?
            curNodeSubIDList = list()
            scount = 0
            if curNodeID + ":s" + str(scount) in SVFG._node.keys():
                curNodeSubIDList.append(curNodeID + ":s" + str(scount))
            scount = scount + 1
            while (curNodeID + ":s" + str(scount) in SVFG._node.keys()):
                curNodeSubIDList.append(curNodeID + ":s" + str(scount))
                scount = scount + 1
            for curNodeSubID in curNodeSubIDList:
                if (curNodeSubID not in forWardVisited):
                    forWardVisited.add(curNodeSubID)
                    forWardQueue.append(curNodeSubID)

            nextNodeIDs = SVFG._succ[curNodeID]

            # isForWardCall = False
            # isDashedBlue = False
            # if len(nextNodeIDs) > 0:
            #     nextNodeEdges = nextNodeIDs[list(nextNodeIDs.keys())[0]]
            #     for nextNodeEdge in nextNodeEdges:
            #         nextNodeEdgeAttr = nextNodeEdges[nextNodeEdge]
            #         if "color" in nextNodeEdgeAttr.keys() and nextNodeEdgeAttr["color"] == "blue":
            #             # if "style" in nextNodeEdgeAttr and nextNodeEdgeAttr["style"] == "dashed":
            #             #     isDashedBlue = True
            #             #     break
            #             isForWardCall = True
            #             break

            # if isDashedBlue:
            #     continue

            for nextNodeID in nextNodeIDs:

                if (nextNodeID not in forWardVisited):
                    forWardVisited.add(nextNodeID)
                    forWardQueue.append(nextNodeID)
                    # if isForWardCall:
                    #     if nextNodeID in nodeToLineDict.keys() and nodeToLineDict[
                    #         nextNodeID] in DFCallPath:  # in the cur call path
                    #         forWardVisited.add(nextNodeID)
                    #         forWardQueue.append(nextNodeID)
                    #     else:
                    #         continue  # not in the cur call path, skip the node
                    # else:
                    #     forWardVisited.add(nextNodeID)
                    #     forWardQueue.append(nextNodeID)

                if nextNodeID not in nodeToLineDict:
                    continue

                nextLine = nodeToLineDict[nextNodeID]
                if (nextLine not in forwardRelatedLines_final):
                    # if nextLine.split("_")[1] != "0":
                    ForWardLines.add(nextLine)
                    forwardRelatedLines_final.add(nextLine)
                    nextLineNodeIDList = lineToNodeDict[
                        nextLine]  # line may map to multiple nodeid
                    for nextLineNodeID in nextLineNodeIDList:
                        if (nextLineNodeID not in forWardVisited):
                            forWardVisited.add(nextLineNodeID)
                            forWardQueue.append(nextLineNodeID)

                        # for nodeid:s0  nodeid:s1 etc.. we need their forward information, just append them into queue
                        # mention that sometimes G only has nodeid:s1 but does not have nodeid:s0
                        nextLnNodeSubIDList = list()
                        scount = 0
                        if nextLineNodeID + ":s" + str(
                                scount) in SVFG._node.keys():
                            nextLnNodeSubIDList.append(nextLineNodeID + ":s" +
                                                       str(scount))
                        scount = scount + 1
                        while (nextLineNodeID + ":s" + str(scount)
                               in SVFG._node.keys()):
                            nextLnNodeSubIDList.append(nextLineNodeID + ":s" +
                                                       str(scount))
                            scount = scount + 1
                        for nextLnNodeSubID in nextLnNodeSubIDList:
                            if (nextLnNodeSubID not in forWardVisited):
                                forWardVisited.add(nextLnNodeSubID)
                                forWardQueue.append(nextLnNodeSubID)

    return ForWardLines


def getDFCallPathList(SVFG, apiLine):
    '''
    only for context sensitive analysis
    for each api, calc call(line)-set list
    :param SVFG:
    :param apiLine:
    :return:
    '''
    lineToNodeDict = buildSVFGLineToNodeDict(SVFG)
    DFCallPathList = list()  # [set(), set()] set - call line path
    DFForWardCallPathList = list()  # [set(), set()] set - call line path
    nodeToLineDict = buildSVFGNodeToLineDict(SVFG)

    apiNodeIDList = lineToNodeDict[apiLine]
    visitedDFBackCallPathList = set()
    visitedDFForCallPathList = set()

    for apiNodeID in apiNodeIDList:
        DFBackCallPathList = list()  # [set(), set()] set - call line path
        DFBackCallPathIDList = list()  # [set(), set()] set - call line path
        visited = set()
        visited.add(apiNodeID)
        callPath = list()
        callPathID = list()

        callPathStr = str(nodeToLineDict[apiNodeID])
        dfsgetDFBackCallPathList(visited, apiNodeID, SVFG, callPath,
                                 callPathStr, callPathID, DFBackCallPathList,
                                 DFBackCallPathIDList,
                                 visitedDFBackCallPathList, nodeToLineDict,
                                 lineToNodeDict)

        # merge DFBackCallPathList
        for DFBackCallPath in range(len(DFBackCallPathList)):
            for DFBackCallPath2 in range(len(DFBackCallPathList)):
                if (DFBackCallPathList[DFBackCallPath] != None
                        and DFBackCallPathList[DFBackCallPath2] != None
                        and DFBackCallPathList[DFBackCallPath] !=
                        DFBackCallPathList[DFBackCallPath2]
                        and DFBackCallPathList[DFBackCallPath].issubset(
                            DFBackCallPathList[DFBackCallPath2])):
                    DFBackCallPathList[DFBackCallPath] = None

        DFBackCallPathListNew = list()
        DFBackCallPathIDListNew = list()
        for i in range(len(DFBackCallPathList)):
            if DFBackCallPathList[i] != None:
                DFBackCallPathListNew.append(DFBackCallPathList[i])
                DFBackCallPathIDListNew.append(DFBackCallPathIDList[i])
        DFBackCallPathList = DFBackCallPathListNew
        DFBackCallPathIDList = DFBackCallPathIDListNew

        for DFBackCallPathidx in range(len(DFBackCallPathList)):
            visited = set()
            visited.add(apiNodeID)
            callPath = list()
            callPathStr = str(nodeToLineDict[apiNodeID])
            DFBackCallPath = DFBackCallPathList[DFBackCallPathidx]
            DFBackCallPathID = DFBackCallPathIDList[DFBackCallPathidx]

            dfsgetDFForWardCallPathList(visited, apiNodeID, SVFG, callPath,
                                        callPathStr, DFBackCallPathID,
                                        DFForWardCallPathList,
                                        visitedDFForCallPathList,
                                        nodeToLineDict)
            # merge DFForWardCallPathList
            for DFForWardCallPath in range(len(DFForWardCallPathList)):
                for DFForWardCallPath2 in range(len(DFForWardCallPathList)):
                    if (DFForWardCallPathList[DFForWardCallPath] != None and
                            DFForWardCallPathList[DFForWardCallPath2] != None
                            and DFForWardCallPathList[DFForWardCallPath] !=
                            DFForWardCallPathList[DFForWardCallPath2] and
                            DFForWardCallPathList[DFForWardCallPath].issubset(
                                DFForWardCallPathList[DFForWardCallPath2])):
                        DFForWardCallPathList[DFForWardCallPath] = None

            DFForWardCallPathListNew = list()

            for i in range(len(DFForWardCallPathList)):
                if DFForWardCallPathList[i] != None:
                    DFForWardCallPathListNew.append(DFForWardCallPathList[i])

            DFForWardCallPathList = DFForWardCallPathListNew

            if DFForWardCallPathList == []:
                DFCallPathList.append(DFBackCallPath)
            else:
                for DFForWardCallPath in DFForWardCallPathList:
                    DFCallPathList.append(
                        DFBackCallPath.union(DFForWardCallPath))

    return DFCallPathList


def dfsgetDFBackCallPathList(visited, curNodeID, SVFG, callPath, callPathStr,
                             callPathID, DFBackCallPathList,
                             DFBackCallPathIDList, visitedDFBackCallPathList,
                             nodeToLineDict, lineToNodeDict):
    '''
    only for context sensitive analysis
    get backward call chain
    :param visited:
    :param curNodeID:
    :param SVFG:
    :param callPath:
    :param DFBackCallPathList:
    :param nodeToLineDict:
    :return:
    '''
    end = curNodeID.find(":s")
    if end != -1:
        curNodeID = curNodeID[:end]
        # if curNodeID not in visited:
        #     visited.add(curNodeID)
    predNodeIDs = SVFG._pred[curNodeID]
    if len(predNodeIDs) == 0:
        if len(callPath) != 0:
            if callPathStr not in visitedDFBackCallPathList:
                DFBackCallPathList.append(set(callPath))
                visitedDFBackCallPathList.add(callPathStr)
                DFBackCallPathIDList.append(set(callPathID))
                # DFCallPathList.append(callPath)
        return

    isBackWardCall = False
    isDashedRed = False
    if len(predNodeIDs) > 0:
        predNodeEdges = predNodeIDs[list(predNodeIDs.keys())[0]]
        for predNodeEdge in predNodeEdges:
            predNodeEdgeAttr = predNodeEdges[predNodeEdge]
            if "color" in predNodeEdgeAttr.keys(
            ) and predNodeEdgeAttr["color"] == "red":
                if "style" in predNodeEdgeAttr.keys(
                ) and predNodeEdgeAttr["style"] == "dashed":
                    isDashedRed = True
                    break

                isBackWardCall = True
                break

    if isDashedRed:
        return

    for predNodeID in predNodeIDs:
        if predNodeID not in visited:
            visited.add(predNodeID)

            if isBackWardCall:

                end = predNodeID.find(":s")
                if end != -1:
                    line = nodeToLineDict[predNodeID[:end]]
                    predNodeID2 = predNodeID[:end]
                    label = SVFG._node[predNodeID2]["label"]
                    start = label.find(">")
                    callPathID.append(int(label[start + 1:-3]))
                else:  # theoritically, will not execute this path
                    line = nodeToLineDict[predNodeID]
                    predNodeID2 = predNodeID

                # if SVFG._node[predNodeID2]["color"] == "green":
                #
                #     nodes = lineToNodeDict[line]
                #     for node in nodes:
                #         if SVFG._node[node]["color"] == "blue":
                #             predNodeID2 = node
                #             break
                callPath.append(line)
                visited.add(predNodeID2)
                callPathStrr = str(line) + "_" + callPathStr
                dfsgetDFBackCallPathList(visited, predNodeID2, SVFG, callPath,
                                         callPathStrr, callPathID,
                                         DFBackCallPathList,
                                         DFBackCallPathIDList,
                                         visitedDFBackCallPathList,
                                         nodeToLineDict, lineToNodeDict)
                callPath.pop()
                callPathID.pop()
                visited.remove(predNodeID2)
                if predNodeID in visited:
                    visited.remove(predNodeID)
                continue

            # end = predNodeID.find(":s")
            # if end != -1:
            #     if predNodeID[:end] in nodeToLineDict:
            #         line = nodeToLineDict[predNodeID[:end]]
            #         predNodeID2 = predNodeID[:end]
            #         if "color" in SVFG._node[predNodeID2]:
            #             if SVFG._node[predNodeID2]["color"] == "green":
            #
            #                 nodes = lineToNodeDict[line]
            #                 for node in nodes:
            #                     if "label" in SVFG._node[node]:
            #                         label = SVFG._node[node]["label"]
            #                         if label.find("th arg") != -1:
            #                             predNodeID2 = node
            #                             break
            #                 visited.add(predNodeID2)
            #                 dfsgetDFBackCallPathList(visited, predNodeID2, SVFG, callPath, callPathStr,
            #                                          DFBackCallPathList,
            #                                          visitedDFBackCallPathList, nodeToLineDict, lineToNodeDict)
            #                 visited.remove(predNodeID2)
            #                 if predNodeID in visited:
            #                     visited.remove(predNodeID)
            #                 continue
            # else:
            #     if predNodeID in nodeToLineDict:
            #         line = nodeToLineDict[predNodeID]
            #         predNodeID2 = predNodeID
            #         if "color" in SVFG._node[predNodeID2]:
            #             if SVFG._node[predNodeID2]["color"] == "green":
            #
            #                 nodes = lineToNodeDict[line]
            #                 for node in nodes:
            #                     if "label" in SVFG._node[node]:
            #                         label = SVFG._node[node]["label"]
            #                         if label.find("th arg") != -1:
            #                             predNodeID2 = node
            #                             break
            #                 visited.add(predNodeID2)
            #                 dfsgetDFBackCallPathList(visited, predNodeID2, SVFG, callPath, callPathStr,
            #                                          DFBackCallPathList,
            #                                          visitedDFBackCallPathList, nodeToLineDict, lineToNodeDict)
            #                 visited.remove(predNodeID2)
            #                 if predNodeID in visited:
            #                     visited.remove(predNodeID)
            #                 continue

            dfsgetDFBackCallPathList(visited, predNodeID, SVFG, callPath,
                                     callPathStr, callPathID,
                                     DFBackCallPathList, DFBackCallPathIDList,
                                     visitedDFBackCallPathList, nodeToLineDict,
                                     lineToNodeDict)
            visited.remove(predNodeID)


def dfsgetDFForWardCallPathList(visited, curNodeID, SVFG, callPath,
                                callPathStr, DFBackCallPathID,
                                DFForWardCallPathList,
                                visitedDFForCallPathList, nodeToLineDict):
    '''
    only for context sensitive analysis
    get forward call chain
    :param visited:
    :param curNodeID:
    :param SVFG:
    :param callPath:
    :param DFBackCallPath:
    :param DFForWardCallPathList:
    :param nodeToLineDict:
    :return:
    '''
    curNodeAndSubIDList = list()
    curNodeAndSubIDList.append(curNodeID)
    scount = 0
    if curNodeID + ":s" + str(scount) in SVFG._node.keys():
        curNodeAndSubIDList.append(curNodeID + ":s" + str(scount))
    scount = scount + 1
    while (curNodeID + ":s" + str(scount) in SVFG._node.keys()):
        curNodeAndSubIDList.append(curNodeID + ":s" + str(scount))
        scount = scount + 1

    for curNodeID in curNodeAndSubIDList:

        nextNodeIDs = SVFG._succ[curNodeID]
        if len(nextNodeIDs) == 0:
            if len(callPath) != 0:
                if callPathStr not in visitedDFForCallPathList:
                    DFForWardCallPathList.append(set(callPath))
                    visitedDFForCallPathList.add(callPathStr)
                    # DFCallPathList.append(callPath)
            continue

        isForWardCall = False
        isDashedBlue = False
        if len(nextNodeIDs) > 0:
            nextNodeEdges = nextNodeIDs[list(nextNodeIDs.keys())[0]]
            for nextNodeEdge in nextNodeEdges:
                nextNodeEdgeAttr = nextNodeEdges[nextNodeEdge]
                if "color" in nextNodeEdgeAttr.keys(
                ) and nextNodeEdgeAttr["color"] == "blue":
                    if "style" in nextNodeEdgeAttr and nextNodeEdgeAttr[
                            "style"] == "dashed":
                        isDashedBlue = True
                        break
                    isForWardCall = True
                    break
        if isDashedBlue:
            continue

        meetBackWard = False
        if isForWardCall:  # blue solid edge
            end = curNodeID.find(":s")
            if end != -1:  # theoritically, no need the condition
                label = SVFG._node[curNodeID[:end]]["label"]
                s = curNodeID[end + 1:]
                snum = int(curNodeID[end + 2:])
                start = label.find(s)
                end = label.find("s" + str(snum + 1))  # next node
                if (end != -1):  # not the final subnode
                    num = int(label[start + 3:end - 2])
                else:  # the final node
                    num = int(label[start + 3:-3])
                if num in DFBackCallPathID:  # make sure forward the related-backward
                    meetBackWard = True

        for nextNodeID in nextNodeIDs:
            if nextNodeID not in visited:

                if isForWardCall:

                    if not meetBackWard:  # cut off the not-backward-related-forward call
                        continue
                    visited.add(nextNodeID)
                    callPath.append(nodeToLineDict[nextNodeID])
                    callPathStrr = callPathStr + "_" + nodeToLineDict[
                        nextNodeID]
                    dfsgetDFForWardCallPathList(visited, nextNodeID, SVFG,
                                                callPath, callPathStrr,
                                                DFBackCallPathID,
                                                DFForWardCallPathList,
                                                visitedDFForCallPathList,
                                                nodeToLineDict)
                    callPath.pop()
                    visited.remove(nextNodeID)
                    continue

                visited.add(nextNodeID)

                dfsgetDFForWardCallPathList(visited, nextNodeID, SVFG,
                                            callPath, callPathStr,
                                            DFBackCallPathID,
                                            DFForWardCallPathList,
                                            visitedDFForCallPathList,
                                            nodeToLineDict)
                visited.remove(nextNodeID)
