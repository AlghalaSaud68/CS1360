import random

rows=6
cols=7
gameGrid = [["" for c in range(cols)] for r in range(rows)]
colChoice = [str(c) for c in range(cols)]
tokens=["❤️","💛"]
playerTypes=["Human","Human"]

def printGrid(board):
    print("\n     0     1     2     3     4     5     6", end="")
    for i in range(rows):
        print("\n   +-----+-----+-----+-----+-----+-----+-----+")
        print(i, " |", end="")
        for j in range(cols):
            if board[i][j] == "":
                print(board[i][j], end="     |")
            else:
                print(" ",board[i][j], end=" |")
    print("\n   +-----+-----+-----+-----+-----+-----+-----+")

def isFull(board):
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == "":
                return False
    return True

def checkWinner(board,token):
    #Check horizontal winner
    for r in range(rows):
        for c in range(cols-3):
            if board[r][c] == token and board[r][c+1] == token and board[r][c+2] == token and board[r][c+3] == token:
                return True
    #Check vertical winner
    for c in range(cols):
        for r in range(rows-3):
            if board[r][c] == token and board[r+1][c] == token and board[r+2][c] == token and board[r+3][c] == token:
                return True
    #Check for digonal winner upper left to lower right
    for c in range(cols-3):
        for r in range(rows - 3):
            if board[r][c] == token and board[r + 1][c+1] == token and board[r + 2][c+2] == token and board[r + 3][c+3] == token:
                return True
    # Check for digonal winner lower left to upper right
    for c in range(cols - 3):
        for r in range(3,rows):
            if board[r][c] == token and board[r - 1][c + 1] == token and board[r - 2][c + 2] == token and board[r - 3][c + 3] == token:
                return True
    return False

def validCol(board,col):
    col = col.strip()
    if  col not in colChoice or not col.isdigit():
        print("\nInvalid column choice. Please choose from 0 to 6")
        return False
    count = 0
    colIndex= int(col)
    for r in range(rows):
        if board[r][colIndex] == "":
            count+=1
    if count == 0:
        print(col, "is full")
        return False
    else:
        return True

def validMove(board,userMove):
    if isFull(board):
        print(" the grid is full, no valid moves available")
        return False
    userMove = userMove.strip()
    isValid = validCol(board,userMove)
    if isValid:
        return True
    else:
        return False

def dropGravity(board,userMove, turn):
    userMove = str(userMove).strip()
    isValid=validMove(board,userMove)
    if not isValid:
        return False
    userMove = int(userMove)
    return makeMove(board,userMove,turn) != -1

#List for AI to know what columns are not occupied
def getvalidCol(board):
    return [c for c in range(cols) if board[0][c]==""]

#copise current board for simulation
def copyBoard(board):
    return [row[:] for row in board]

def makeMove(board,userMove,token):
    for r in range(rows-1,-1,-1):
        if board[r][userMove] == "":
            board[r][userMove] = token
            return r
    return -1

def undoMove(board,userMove):
    for r in range(rows):
        if board[r][userMove] != "":
            board[r][userMove] = ""
            return r
    return -1

def isGameOver(board):
    return checkWinner(board,tokens[0]) or checkWinner(board,tokens[1]) or isFull(board)

def getAIMove(board,token):
    from mcts import mctsMove
    return mctsMove(board,token,1000)

def choseMode():
    print("Choose mode:\n1-Human vs Human\n2-Human vs AI\n3-AI vs AI")
    choice = input().strip()
    while choice not in ["1","2","3"]:
        print("Invalid choice. Please choose from 1 to 3")
        choice = input().strip()
    if choice == "1":
        return ["Human","Human"]
    if choice == "2":
        return ["Human","AI"]
    return ["AI","AI"]

def emptyGrid(board):
        for r in range(rows):
            for c in range(cols):
                board[r][c] = ""

def restartGame(board,wantRestart):
    if wantRestart:
        print("\nRestarting game")
        emptyGrid(board)
    else:
        print("the game is over. \nThank you for playing")

def playGame(board):
    playing = True
    while playing:
        playerTypes[:] = choseMode()
        printGrid(board)
        winnerFound=False
        turn = 0
        while not isFull(board):
            print("It is ",tokens[turn]," turn!")
            if playerTypes[turn] == "AI":
                aiCol=getAIMove(board,tokens[turn])
                if not dropGravity(board,aiCol,tokens[turn]):
                    aiCol=getvalidCol(board)[0]
                    dropGravity(board,aiCol,tokens[turn])
                print("AI picks column",aiCol)
            else:
                print("pick a column:)")
                userCol=input()
                userCol = userCol.strip()
                while True:
                        if not userCol.isdigit() or not userCol in colChoice:
                            print("Invalid column choice. Please choose from 0 to 6")
                            userCol = input()
                            userCol = userCol.strip()
                            continue
                        if not dropGravity(board,userCol, tokens[turn]):
                            print("Choose another column")
                            userCol = input().strip()
                            continue
                        break
            printGrid(board)
            winnerFound=checkWinner(board,tokens[turn])
            if winnerFound:
                print("\nGame over! \nCongrats ", tokens[turn], " has won!👑:)", )
                break
            turn= 1 -turn
        if not winnerFound and isFull(board):
         print("Game Over!\n Tied! no player has won:(")

        print("Do both players want to play again? \nY-for yes \nN-for no")
        playersChoice=input()
        playersChoice = playersChoice.lower().strip()
        while playersChoice not in ["yes","y","no","n"]:
            print("Invalid player choice. Please right yes or no")
            playersChoice = input()
            playersChoice = playersChoice.lower().strip()

        playing= playersChoice in ["yes","y"]
        restartGame(board,playing)
