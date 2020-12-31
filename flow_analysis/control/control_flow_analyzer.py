'''control flow based on CFGDepdcyInfluenceBuilder

@author : jumormt
@version : 1.0
'''
__author__ = "jumormt"


@DeprecationWarning
def getConditionLines(relatedLines, CFGDepdcy, relatedLines_final):
    '''
    calc relatedLines-control-dependency-lines
    :param relatedLines:
    :param CFGDepdcy: {line:its cfg-dependency-line}
    :param relatedLines_final:
    :return: relatedLines-control-dependency-lines
    '''
    conditionLines = set()
    for relatedLine in relatedLines:
        if relatedLine not in CFGDepdcy:  # global
            conditionLine = 0
        else:
            conditionLine = CFGDepdcy[relatedLine]

        while (conditionLine != 0):
            if (conditionLine not in relatedLines_final):
                relatedLines_final.add(conditionLine)
                conditionLines.add(conditionLine)

            if relatedLine not in CFGDepdcy:  # global
                conditionLine = 0
            else:
                conditionLine = CFGDepdcy[conditionLine]

    return conditionLines


def getCFGDependencyLines(backWardRelatedLines, CFGLineDepdcy,
                          relatedLines_final, edges_final,
                          control_edge_visited):
    '''get backward cfg dependent lines

    using bfs to get backward cfg-related lines

    :param backWardRelatedLines:
    :param CFGLineDepdcy:
    :param relatedLines_final:
    :return:
    '''
    CFGDepdcyLines = set()
    queue = list()
    queue.extend(backWardRelatedLines)
    visited = set()
    visited = visited.union(backWardRelatedLines)
    while queue:
        fro = queue.pop(0)
        if fro not in relatedLines_final:
            CFGDepdcyLines.add(fro)
            relatedLines_final.add(fro)
        if fro not in CFGLineDepdcy:  # end parsing
            continue
        CFGLineDepdcyLineSet = CFGLineDepdcy[fro]

        for CFGLineDepdcyLine in list(CFGLineDepdcyLineSet):
            if (CFGLineDepdcyLine != fro):
                edge_tmp = str(CFGLineDepdcyLine) + "_" + str(fro)
                if edge_tmp not in control_edge_visited:
                    control_edge_visited.add(edge_tmp)
                    edges_final.append([CFGLineDepdcyLine, fro])
            if CFGLineDepdcyLine not in visited:

                visited.add(CFGLineDepdcyLine)
                queue.append(CFGLineDepdcyLine)

    return CFGDepdcyLines


def getCFGDependencyEdgeLines(backWardRelatedLines, CFGLineDepdcy,
                              relatedLines_final, controlFlowEdges):
    '''get backward cfg dependent lines and edges

    using bfs to get backward cfg-related lines and edges

    :param backWardRelatedLines:
    :param CFGLineDepdcy:
    :param relatedLines_final:
    :param controlFlowEdges:
    :return:
    '''
    CFGDepdcyLines = set()
    queue = list()
    queue.extend(backWardRelatedLines)
    visited = set()
    visited = visited.union(backWardRelatedLines)
    while queue:
        fro = queue.pop(0)
        if fro not in relatedLines_final:
            CFGDepdcyLines.add(fro)
            relatedLines_final.add(fro)
        if fro not in CFGLineDepdcy:  # end parsing
            continue
        CFGLineDepdcyLineSet = CFGLineDepdcy[fro]

        for CFGLineDepdcyLine in list(CFGLineDepdcyLineSet):
            cfEdge = str(CFGLineDepdcyLine) + "-" + str(fro)
            if cfEdge not in controlFlowEdges:
                controlFlowEdges.add(cfEdge)

            if CFGLineDepdcyLine not in visited:
                visited.add(CFGLineDepdcyLine)
                queue.append(CFGLineDepdcyLine)

    return CFGDepdcyLines


def getCFGInfluentLines(forWardRelatedLines, CFGLineInfluence,
                        forwardRelatedLines_final, edges_final,
                        control_edge_visited):
    '''get backward cfg influent lines

    using bfs to get forward cfg-related lines

    :param forWardRelatedLines:
    :param CFGLineInfluence:
    :param forwardRelatedLines_final:
    :return:
    '''
    CFGInfluentLines = set()
    queue = list()
    queue.extend(forWardRelatedLines)
    visited = set()
    visited = visited.union(forWardRelatedLines)
    while queue:
        fro = queue.pop(0)
        if fro not in forwardRelatedLines_final:
            CFGInfluentLines.add(fro)
            forwardRelatedLines_final.add(fro)
        if fro not in CFGLineInfluence:  # end parsing
            continue
        CFGLineInfluentLineSet = CFGLineInfluence[fro]

        for CFGLineInfluentLine in list(CFGLineInfluentLineSet):
            if (CFGLineInfluentLine != fro):
                edge_tmp = str(fro) + "_" + str(CFGLineInfluentLine)
                if edge_tmp not in control_edge_visited:
                    control_edge_visited.add(edge_tmp)
                    edges_final.append([fro, CFGLineInfluentLine])
            if CFGLineInfluentLine not in visited:

                visited.add(CFGLineInfluentLine)
                queue.append(CFGLineInfluentLine)

    return CFGInfluentLines


def getCFGInfluentEdgeLines(forWardRelatedLines, CFGLineInfluence,
                            forwardRelatedLines_final, controlFlowEdges):
    '''get backward cfg influent lines and edges

    using bfs to get forward cfg-related lines and edges

    :param forWardRelatedLines:
    :param CFGLineInfluence:
    :param forwardRelatedLines_final:
    :param controlFlowEdges:
    :return:
    '''
    CFGInfluentLines = set()
    queue = list()
    queue.extend(forWardRelatedLines)
    visited = set()
    visited = visited.union(forWardRelatedLines)
    while queue:
        fro = queue.pop(0)
        if fro not in forwardRelatedLines_final:
            CFGInfluentLines.add(fro)
            forwardRelatedLines_final.add(fro)
        if fro not in CFGLineInfluence:  # end parsing
            continue
        CFGLineInfluentLineSet = CFGLineInfluence[fro]

        for CFGLineInfluentLine in list(CFGLineInfluentLineSet):
            cfgEdge = str(fro) + "-" + str(CFGLineInfluentLine)
            if cfgEdge not in controlFlowEdges:
                controlFlowEdges.add(cfgEdge)
            if CFGLineInfluentLine not in visited:
                visited.add(CFGLineInfluentLine)
                queue.append(CFGLineInfluentLine)

    return CFGInfluentLines