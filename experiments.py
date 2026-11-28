from aivsai import makePlayer, runExperiment

ab2 = makePlayer("AlphaBeta 2", "alphabeta", 2)
ab6 = makePlayer("AlphaBeta 6", "alphabeta", 6)
ab10 = makePlayer("AlphaBeta 10", "alphabeta", 10)
mcts100 = makePlayer("MCTS 100", "mcts", 100)
mcts1000 = makePlayer("MCTS 1000", "mcts", 1000)
mcts2000 = makePlayer("MCTS 2000", "mcts", 2000)

#Alpha-Beta always plays the same game, so 2 games are enough (each player starts once)
gamesA = 2
#MCTS uses random moves, so we need more games to get reliable results
gamesB = 50
#Alpha-Beta with depth 10 is slow, so we use only 10 games
gamesC = 10

#How to use this file:
#1: choose 4 to run experiments 1 and 2 (Alpha-Beta vs Alpha-Beta and MCTS vs MCTS)
#2: from the results, find the best Alpha-Beta depth and the best MCTS simulations
#3: write them in the two lines below
#4: choose 3 to run experiment 3 (best Alpha-Beta vs best MCTS)
bestAlphaBeta = ab10
bestMCTS = mcts2000

def experimentA():
    runExperiment(ab2, ab2, gamesA)
    runExperiment(ab6, ab6, gamesA)
    runExperiment(ab10, ab10, gamesA)
    runExperiment(ab2, ab6, gamesA)
    runExperiment(ab2, ab10, gamesA)
    runExperiment(ab6, ab10, gamesA)

def experimentB():
    runExperiment(mcts100, mcts100, gamesB)
    runExperiment(mcts1000, mcts1000, gamesB)
    runExperiment(mcts2000, mcts2000, gamesB)
    runExperiment(mcts100, mcts1000, gamesB)
    runExperiment(mcts100, mcts2000, gamesB)
    runExperiment(mcts1000, mcts2000, gamesB)

def experimentC():
    runExperiment(bestAlphaBeta, bestMCTS, gamesC)

def choseExperiment():
    print("Choose experiment:\n1-Alpha-Beta vs Alpha-Beta\n2-MCTS vs MCTS\n3-Best Alpha-Beta vs Best MCTS\n4-Experiments 1 and 2 together")
    choice = input().strip()
    while choice not in ["1","2","3","4"]:
        print("Invalid choice. Please choose from 1 to 4")
        choice = input().strip()
    return choice

if __name__ == "__main__":
    choice = choseExperiment()
    if choice == "1":
        experimentA()
    elif choice == "2":
        experimentB()
    elif choice == "3":
        experimentC()
    else:
        experimentA()
        experimentB()
