import random

lettersChoice = ["A","B","C","D","E","F","G"]
gameGrid=[["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""],
          ["","","","","","",""]]
rows=6
cols=7

def printGrid():
    print("\n   A   B   C   D   E   F   G", end="")
    for i in range(rows):
        print("\n   +-----+-----+-----+-----+-----+-----+-----+")
        print(i, " |    ", end="")
        for j in range(cols):
                print("", gameGrid[i][j], end="|    ")
    print("\n   +-----+-----+-----+-----+-----+-----+-----+")

def move(chosenSpace, turn):
    gameGrid[chosenSpace[0]][chosenSpace[1]] = turn

printGrid()
# This was my personal experiment to build the game grid, and it can be deleted later
#    for letter in lettersChoice:
#        if letter!="G":
#            print(letter+" ",end="")
#        else:
#            print(letter)
#    print("-------------")
#    for row in range(rows):
#        for col in range(cols):
#            cell = gameGrid[row][col]
#            print("."+" " if cell==""or cell is None else cell,end="")
#        print()
