import time
import os
from game import tokens, makeMove, checkWinner, isFull, printGrid
from mcts import mctsMove
from alphabeta import getAlphaBetaMove

def makePlayer(name, playerType, value):
    return {"name": name, "type": playerType, "value": value}

def getMove(player, board, token):
    if player["type"] == "mcts":
        return mctsMove(board, token, player["value"])
    if player["type"] == "alphabeta":
        return getAlphaBetaMove(board, token, player["value"])
    raise ValueError("Unknown player type: " + player["type"])

def playMatch(firstPlayer, secondPlayer, show=False, maxSeconds=1800):
    #Plays one full game, the maximum time is 30 minutes (1800 seconds)
    board = [["" for c in range(7)] for r in range(6)]
    players = [firstPlayer, secondPlayer]
    times = [0, 0]
    movesCount = [0, 0]
    turn = 0
    winner = None
    timeout = False
    startTime = time.time()

    while not isFull(board):
        if time.time() - startTime > maxSeconds:
            timeout = True
            break
        moveStart = time.time()
        col = getMove(players[turn], board, tokens[turn])
        times[turn] += time.time() - moveStart
        movesCount[turn] += 1
        makeMove(board, col, tokens[turn])
        if show:
            printGrid(board)
        if checkWinner(board, tokens[turn]):
            winner = turn
            break
        turn = 1 - turn

    result = {"winner": winner, "moves": movesCount[0] + movesCount[1],
              "times": times, "movesCount": movesCount, "timeout": timeout,
              "totalTime": time.time() - startTime}
    return result

def runExperiment(playerA, playerB, games, fileName="results.csv"):
    winsA = 0
    winsB = 0
    draws = 0
    timeouts = 0
    totalMoves = 0
    totalTime = 0
    thinkA = 0
    thinkB = 0
    movesA = 0
    movesB = 0

    for g in range(games):
        #A and B take turns in playing first
        if g % 2 == 0:
            r = playMatch(playerA, playerB)
            idxA = 0
        else:
            r = playMatch(playerB, playerA)
            idxA = 1
        idxB = 1 - idxA

        if r["timeout"]:
            timeouts += 1
        elif r["winner"] is None:
            draws += 1
        elif r["winner"] == idxA:
            winsA += 1
        else:
            winsB += 1

        totalMoves += r["moves"]
        totalTime += r["totalTime"]
        thinkA += r["times"][idxA]
        thinkB += r["times"][idxB]
        movesA += r["movesCount"][idxA]
        movesB += r["movesCount"][idxB]

    avgMoves = totalMoves / games
    avgGameTime = totalTime / games
    avgMoveA = thinkA / movesA
    avgMoveB = thinkB / movesB

    print(playerA["name"], "vs", playerB["name"], "| games", games,
          "| A wins", winsA, "| B wins", winsB, "| draws", draws, "| timeouts", timeouts)
    print("   avg moves", round(avgMoves, 1), "| avg game time", round(avgGameTime, 2), "s",
          "| avg time per move: A", round(avgMoveA, 4), "s, B", round(avgMoveB, 4), "s")

    #Save the results in a csv file
    newFile = not os.path.exists(fileName)
    f = open(fileName, "a")
    if newFile:
        f.write("A,B,games,A wins,B wins,draws,timeouts,avg moves,avg game time,avg move time A,avg move time B\n")
    f.write(playerA["name"] + "," + playerB["name"] + "," + str(games) + "," + str(winsA) + "," +
            str(winsB) + "," + str(draws) + "," + str(timeouts) + "," + str(round(avgMoves, 1)) + "," +
            str(round(avgGameTime, 2)) + "," + str(round(avgMoveA, 4)) + "," + str(round(avgMoveB, 4)) + "\n")
    f.close()
