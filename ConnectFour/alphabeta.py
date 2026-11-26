import math
from game import tokens, makeMove , undoMove, copyBoard, getvalidCol, checkWinner, isFull

RED =tokens[0]
YELLOW =tokens[1]

def scoreL(line):
    red= line.count(RED)
    yellow= line.count(YELLOW)
    empty= line.count("")

    if yellow ==3 and empty==1:
        return 5
    if yellow ==2 and empty==2:
        return 2
    if red ==3 and empty==1:
        return -5
    if red ==2 and empty==2:
        return -2
    return 0

def evaluate(board):
    score=0

    #center
    for r in range(6):
        if board[r][3]==YELLOW:
            score+=3
        elif board[r][3]==RED:
            score-=3
    #horizontal
    for r in range(6):
        for c in range(4):
            line=[board[r][c],board[r][c+1],board[r][c+2],board[r][c+3]]
            score+=scoreL(line)

    #vertical   
    for c in range (7):
        for r in range(3):
            line=[board[r][c],board[r+1][c],board[r+2][c],board[r+3][c]]
            score+=scoreL(line)
    #diagonal1
    for r in range(3):
        for c in range(4):
            line=[board[r][c],board[r+1][c+1],board[r+2][c+2],board[r+3][c+3]]
            score+=scoreL(line)
    #diagonal2
    for r in range(3,6):
        for c in range(4):
            line=[board[r][c],board[r-1][c+1],board[r-2][c+2],board[r-3][c+3]]
            score+=scoreL(line)
    return score

def orderMoves(board):
    validcol=getvalidCol(board)
    order=[3,2,4,1,5,0,6]
    move=[]
    for c in order:
        if c in validcol:
            move.append(c)
    return move               

def alphabeta(board,depth,alpha,beta,isMax):
    if checkWinner(board,YELLOW):
        return 1000000
    if checkWinner(board,RED):
        return -1000000
    if isFull(board):
        return 0
    if depth==0:
        return evaluate(board)

    if isMax:
        best= -math.inf
        for c in orderMoves(board):
            makeMove(board,c,YELLOW)
            value = alphabeta(board,depth-1,alpha,beta,False)
            undoMove(board,c)
            best = max(best,value)
            alpha = max(alpha,best)
            if alpha >= beta:
                break              #prune
        return best
    else:
        best= math.inf
        for c in orderMoves(board):
            makeMove(board,c,RED)
            value = alphabeta(board,depth-1,alpha,beta,True)   
            undoMove(board,c)
            best = min(best,value)
            beta = min(beta,best)
            if beta <= alpha:
                break              #prune     
        return best

def getAlphaBetaMove(board,token,depth):
    tempBoard=copyBoard(board)
    validcol=orderMoves(tempBoard)
    bestcol=validcol[0]

    if token==YELLOW:
        bestval= -math.inf
    else:
        bestval= math.inf

    for c in validcol:
        makeMove(tempBoard,c,token)
        if token==YELLOW:
            value=alphabeta(tempBoard,depth-1,-math.inf,math.inf,False)
        else:
            value=alphabeta(tempBoard,depth-1,-math.inf,math.inf,True)
        undoMove(tempBoard,c)

        if token==YELLOW and value> bestval:
            bestval=value
            bestcol=c
        if token==RED and value< bestval:
            bestval=value
            bestcol=c
    return bestcol


