import random

colChoice = ["0","1","2","3","4","5","6"]
gameGrid=[["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""]]
rows=6
cols=7

def printGrid():
    print("\n     0     1     2     3     4     5     6", end="")
    for i in range(rows):
        print("\n   +-----+-----+-----+-----+-----+-----+-----+")
        print(i, " |", end="")
        for j in range(cols):
            print(gameGrid[i][j], end="     |")
    print("\n   +-----+-----+-----+-----+-----+-----+-----+")

def isFull(gameGrid):
    for r in range(rows):
        for c in range(cols):
            if gameGrid[r][c] == "":
                return False
    return True

def checkWinner(token):
    vertwin=False
    horswin=False
    diwin=False
    #Check horizontal winner
    for r in range(rows):
        for c in range(cols-3):
            if gameGrid[r][c] == token and gameGrid[r][c+1] == token and gameGrid[r][c+2] == token and gameGrid[r][c+3] == token:
                print("\nGame over! \nCongrats ",token," has won!👑",)
                return True
    #Check vertical winner
    for c in range(cols):
        for r in range(rows-3):
            if gameGrid[r][c] == token and gameGrid[r+1][c] == token and gameGrid[r+2][c] == token and gameGrid[r+3][c] == token:
                print("\nGame over! \nCongrats ",token," has won!👑",)
                return True
    #Check for digonal winner upper left to lower right
    for c in range(cols-3):
        for r in range(rows - 3):
            if gameGrid[r][c] == token and gameGrid[r + 1][c+1] == token and gameGrid[r + 2][c+2] == token and gameGrid[r + 3][c+3] == token:
                print("\nGame over! \nCongrats ", token, " has won!👑", )
                return True
    # Check for digonal winner lower left to upper right
    for c in range(cols - 3):
        for r in range(3,rows):
            if gameGrid[r][c] == token and gameGrid[r - 1][c + 1] == token and gameGrid[r - 2][c + 2] == token and gameGrid[r - 3][c + 3] == token:
                print("\nGame over! \nCongrats ", token, " has won!👑", )
                return True
    return False

def validCol(userCol):
    userCol = userCol.strip()
    if  userCol not in colChoice or not userCol.isdigit():
        print("\nInvalid column choice. Please choose from 0 to 6")
        return False
    count = 0
    colIndex= int(userCol)
    for r in range(rows):
        if gameGrid[r][colIndex] == "":
            count+=1
    if count == 0:
        print(userCol, "is full")
        return False
    else:
        return True

def validMove(userMove):
    if isFull(gameGrid):
        print(" the grid is full, no valid moves available")
        return False
    userMove = userMove.strip()
    isValid = validCol(userMove)
    if isValid:
        return True
    else:
        return False

def dropGravity(userMove, turn):
    isValid=validMove(userMove)
    if not isValid:
        return False
    userMove = int(userMove)
    for r in range(rows -1,-1,-1):
        if gameGrid[r][userMove] == "":
            gameGrid[r][userMove] = turn
            return True
