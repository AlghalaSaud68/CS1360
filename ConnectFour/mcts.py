import math
import random
import time
from game import tokens, getvalidCol, copyBoard, makeMove, checkWinner, isFull

def otherToken(token):
    if token == tokens[0]:
        return tokens[1]
    return tokens[0]

def makeNode(board, mover, parent, move):
    node = {
        "board": board,
        "mover": mover,
        "parent": parent,
        "move": move,
        "children": [],
        "untried": getvalidCol(board),
        "visits": 0,
        "wins": 0
    }
    return node

def isTerminalNode(node):
    return checkWinner(node["board"], node["mover"]) or isFull(node["board"])

def ucb1Score(child, parentVisits, c):
    average = child["wins"] / child["visits"]
    curiosity = c * math.sqrt(math.log(parentVisits) / child["visits"])
    return average + curiosity

def pickBestChild(node, c):
    bestChild = None
    bestScore = -1
    for child in node["children"]:
        score = ucb1Score(child, node["visits"], c)
        if score > bestScore:
            bestScore = score
            bestChild = child
    return bestChild

def randomGame(board, lastMover):
    board = copyBoard(board)
    if checkWinner(board, lastMover):
        return lastMover
    player = otherToken(lastMover)
    while True:
        validCols = getvalidCol(board)
        if not validCols:
            return None
        col = random.choice(validCols)
        makeMove(board, col, player)
        if checkWinner(board, player):
            return player
        player = otherToken(player)

def mctsMove(board, token, simulations=1000, c=1.41):
    validCols = getvalidCol(board)
    if not validCols:
        return -1
    if len(validCols) == 1:
        return validCols[0]

    root = makeNode(copyBoard(board), otherToken(token), None, None)

    for i in range(simulations):
        node = root

        while len(node["untried"]) == 0 and len(node["children"]) > 0 and not isTerminalNode(node):
            node = pickBestChild(node, c)

        if len(node["untried"]) > 0 and not isTerminalNode(node):
            col = random.choice(node["untried"])
            node["untried"].remove(col)
            newBoard = copyBoard(node["board"])
            newMover = otherToken(node["mover"])
            makeMove(newBoard, col, newMover)
            child = makeNode(newBoard, newMover, node, col)
            node["children"].append(child)
            node = child

        winner = randomGame(node["board"], node["mover"])

        while node is not None:
            node["visits"] += 1
            if winner is None:
                node["wins"] += 0.5
            elif winner == node["mover"]:
                node["wins"] += 1
            node = node["parent"]

    bestChild = root["children"][0]
    for child in root["children"]:
        if child["visits"] > bestChild["visits"]:
            bestChild = child
    return bestChild["move"]

if __name__ == "__main__":
    emptyBoard = [["" for c in range(7)] for r in range(6)]
    for s in [100, 1000, 2000]:
        startTime = time.time()
        col = mctsMove(emptyBoard, tokens[1], s)
        print(s, "simulations -> column", col, "time", round(time.time() - startTime, 3), "s")
