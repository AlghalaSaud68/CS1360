import tkinter as tk
import math
import queue
import threading
import time
from game import tokens, makeMove, checkWinner, isFull, getvalidCol, copyBoard
from aivsai import makePlayer, getMove

BLUE = "#1D3FA8"
RED = "#E63946"
CREAM = "#FFF4D6"
GOLD = "#FFC914"
NAVY = "#0F1F5C"
GOLD_HOVER = "#FFD84D"

TOKEN_COLORS = {tokens[0]: RED, tokens[1]: GOLD}
GHOST_COLORS = {tokens[0]: "#F4A3AB", tokens[1]: "#FFE89A"}
NAMES = ["Red", "Yellow"]

ALGORITHMS = [
  {"name": "Alpha-Beta", "kind": "alphabeta", "label": "Search depth", "symbol": "k",
   "values": [2, 6, 10], "hints": ["quick", "smart", "very slow"]},
  {"name": "MCTS", "kind": "mcts", "label": "Simulations", "symbol": "s",
   "values": [100, 1000, 2000], "hints": ["quick", "smart", "strongest"]},
]

ROWS = 6
COLS = 7
CELL = 76
BOARD_WIDTH = COLS * CELL
BOARD_HEIGHT = ROWS * CELL
BOARD_LEFT = (700 - BOARD_WIDTH) // 2
BOARD_TOP = 165
DROP_Y = BOARD_TOP - 50

root = tk.Tk()
root.title('Connect 4')
root.geometry('700x700')
root.resizable(False, False)

canvas = tk.Canvas(root, height=700, width=700, highlightthickness=0)
canvas.pack(fill='both', expand=True)

board = [['' for _ in range(COLS)] for _ in range(ROWS)]
state = {
  "screen": "menu",
  "mode": None,
  "turn": 0,
  "over": False,
  "busy": False,
  "gen": 0,
  "players": [None, None],
  "win": [],
  "choices": [{"algo": 1, "mode": 1}, {"algo": 0, "mode": 1}],
  "humanFirst": True,
}


def drawSwirl(canvas, cx, cy, maxRaduis, numArms=12, twist=0.004, color1=RED, color2=CREAM, smoothness=40, tags=""):
  armAngle = 2 * math.pi / numArms

  for arm in range(numArms):
    color = color1 if arm % 2 == 0 else color2
    baseAngle = arm * armAngle

    leftEdge = []
    rightEdge = []

    for i in range(smoothness + 1):
      r = (i / (smoothness + 1)) * maxRaduis
      theta1 = baseAngle + r * twist
      theta2 = baseAngle + armAngle + r * twist

      leftEdge.append((cx + r * math.cos(theta1), cy + r * math.sin(theta1)))
      rightEdge.append((cx + r * math.cos(theta2), cy + r * math.sin(theta2)))

    polygon = leftEdge + rightEdge[::-1]
    canvas.create_polygon(polygon, fill=color, outline='', tags=tags)


def starPoints(cx, cy, r, inner=0.5):
  points = []
  for i in range(10):
    angle = math.pi / 2 + i * math.pi / 5
    radius = r if i % 2 == 0 else r * inner
    points.append(cx + radius * math.cos(angle))
    points.append(cy - radius * math.sin(angle))
  return points


def drawStar(cx, cy, r, color, tags, swirl=True):
  canvas.create_polygon(starPoints(cx, cy, r), fill=color, outline=NAVY, width=2, joinstyle="round", tags=tags)
  if swirl:
    drawSwirl(canvas, cx, cy, r * 0.46, numArms=6, twist=0.14, color1=BLUE, color2=CREAM, smoothness=10, tags=tags)


def create_ticket_button(canvas, x0, y0, x1, y1, text, tag, on_click, base=GOLD, textColor=NAVY):
  rect_tag = f"{tag}_rect"
  hover = GOLD_HOVER if base == GOLD else base
  canvas.create_rectangle(x0, y0, x1, y1, fill=base, outline=NAVY, width=3, tags=(tag, rect_tag))
  canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=text, fill=textColor, font=("Arial", 14, "bold"), tags=tag)

  def handle_enter(event):
    canvas.itemconfig(rect_tag, fill=hover)
    canvas.config(cursor="hand2")

  def handle_leave(event):
    canvas.itemconfig(rect_tag, fill=base)
    canvas.config(cursor="")

  canvas.tag_bind(tag, "<Button-1>", on_click)
  canvas.tag_bind(tag, "<Enter>", handle_enter)
  canvas.tag_bind(tag, "<Leave>", handle_leave)


def later(ms, fn):
  gen = state["gen"]

  def run():
    if gen == state["gen"]:
      fn()

  root.after(ms, run)


def cellCenter(r, c):
  return BOARD_LEFT + c * CELL + CELL / 2, BOARD_TOP + r * CELL + CELL / 2


def resetBoard():
  for r in range(ROWS):
    for c in range(COLS):
      board[r][c] = ''
  state["turn"] = 0
  state["over"] = False
  state["busy"] = False
  state["win"] = []


def winningCells(token):
  for r in range(ROWS):
    for c in range(COLS):
      for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
        cells = [(r + i * dr, c + i * dc) for i in range(4)]
        if all(0 <= a < ROWS and 0 <= b < COLS and board[a][b] == token for a, b in cells):
          return cells
  return []


def setStatus(text):
  canvas.delete("status")
  canvas.create_text(352, 47, text=text, font=("Jokerman", 20, "bold"), fill=BLUE, tags="status")
  canvas.create_text(350, 45, text=text, font=("Jokerman", 20, "bold"), fill=GOLD, tags="status")


def setInfo(text):
  canvas.delete("info")
  canvas.create_text(350, 665, text=text, font=("Arial", 12, "bold"), fill=CREAM, tags="info")


def drawBoard():
  canvas.delete("board")
  pad = 14
  radius = CELL * 0.4

  canvas.create_rectangle(
      BOARD_LEFT - pad,
      BOARD_TOP - pad,
      BOARD_LEFT + BOARD_WIDTH + pad,
      BOARD_TOP + BOARD_HEIGHT + pad,
      fill=BLUE,
      outline=GOLD,
      width=4,
      tags="board",
  )

  for r in range(ROWS):
    for c in range(COLS):
      cx, cy = cellCenter(r, c)
      canvas.create_oval(
          cx - radius,
          cy - radius,
          cx + radius,
          cy + radius,
          fill=CREAM,
          outline=NAVY,
          width=2,
          tags="board",
      )
      cell_value = board[r][c]
      if cell_value != '':
        drawStar(cx, cy, radius, TOKEN_COLORS[cell_value], "board")

  for r, c in state["win"]:
    cx, cy = cellCenter(r, c)
    ring = CELL * 0.46
    canvas.create_oval(cx - ring, cy - ring, cx + ring, cy + ring, outline=CREAM, width=4, tags="board")


def humanTurn():
  if state["screen"] != "game" or state["over"] or state["busy"]:
    return False
  return state["players"][state["turn"]]["type"] == "human"


def columnAt(x, y):
  if y < BOARD_TOP - 80 or y > BOARD_TOP + BOARD_HEIGHT:
    return None
  col = int((x - BOARD_LEFT) // CELL)
  if 0 <= col < COLS:
    return col
  return None


def onMotion(event):
  canvas.delete("ghost")
  if not humanTurn():
    return
  col = columnAt(event.x, event.y)
  if col is None or board[0][col] != '':
    return
  token = tokens[state["turn"]]
  drawStar(BOARD_LEFT + col * CELL + CELL / 2, DROP_Y, CELL * 0.4, GHOST_COLORS[token], "ghost", swirl=False)


def onClick(event):
  if not humanTurn():
    return
  col = columnAt(event.x, event.y)
  if col is None or board[0][col] != '':
    return
  dropToken(col)


def animateDrop(col, row, token, done):
  x = BOARD_LEFT + col * CELL + CELL / 2
  y1 = cellCenter(row, col)[1]
  drawStar(x, DROP_Y, CELL * 0.4, TOKEN_COLORS[token], "fall")
  steps = 8 + 2 * row
  position = {"y": DROP_Y}

  def step(i):
    y = DROP_Y + (y1 - DROP_Y) * (i / steps) ** 2
    canvas.move("fall", 0, y - position["y"])
    position["y"] = y
    if i < steps:
      later(14, lambda: step(i + 1))
    else:
      canvas.delete("fall")
      done()

  step(0)


def dropToken(col):
  state["busy"] = True
  canvas.delete("ghost")
  row = next(r for r in range(ROWS - 1, -1, -1) if board[r][col] == '')
  token = tokens[state["turn"]]
  animateDrop(col, row, token, lambda: land(col))


def land(col):
  turn = state["turn"]
  token = tokens[turn]
  makeMove(board, col, token)

  if checkWinner(board, token):
    state["over"] = True
    state["win"] = winningCells(token)
    drawBoard()
    setStatus(f"{NAMES[turn]} star wins!")
    showAgainButton()
    return

  drawBoard()

  if isFull(board):
    state["over"] = True
    setStatus("It's a draw!")
    showAgainButton()
    return

  state["turn"] = 1 - turn
  later(150, startTurn)


def showAgainButton():
  create_ticket_button(canvas, 560, 20, 680, 65, "Again", "btn_again", on_again_click)


def startTurn():
  if state["over"]:
    return
  turn = state["turn"]
  player = state["players"][turn]
  if player["type"] == "human":
    setStatus(f"{NAMES[turn]} star: your turn")
    state["busy"] = False
  else:
    setStatus(f"{NAMES[turn]} star is thinking...")
    state["busy"] = True
    thinkAI(player)


def thinkAI(player):
  gen = state["gen"]
  snapshot = copyBoard(board)
  token = tokens[state["turn"]]
  results = queue.Queue()

  def work():
    start = time.time()
    try:
      col = getMove(player, snapshot, token)
    except Exception:
      col = None
    results.put((col, time.time() - start))

  threading.Thread(target=work, daemon=True).start()
  pollAI(results, gen, player)


def pollAI(results, gen, player):
  if gen != state["gen"]:
    return
  try:
    col, secs = results.get_nowait()
  except queue.Empty:
    root.after(40, pollAI, results, gen, player)
    return
  valid = getvalidCol(board)
  if col not in valid:
    col = valid[0]
  setInfo(f"{player['name']} chose column {col} in {secs:.2f}s")
  dropToken(col)


def showMenu():
  state["screen"] = "menu"
  state["gen"] += 1
  canvas.delete("all")
  canvas.config(cursor="")

  drawSwirl(canvas, 350, 350, 500)

  canvas.create_text(353, 143, text="Let's Play\nConnect Four!", font=("Jokerman", 36, "bold"), fill=BLUE, justify="center")
  canvas.create_text(350, 140, text="Let's Play\nConnect Four!", font=("Jokerman", 36, "bold"), fill=GOLD, justify="center")

  create_ticket_button(canvas, 225, 290, 475, 345, "Human vs AI", "btn_human_ai", on_human_ai_click)
  create_ticket_button(canvas, 225, 370, 475, 425, "AI vs AI", "btn_ai_ai", on_ai_ai_click)


def makeChoice(choice):
  algo = ALGORITHMS[choice["algo"]]
  value = algo["values"][choice["mode"]]
  return makePlayer(f"{algo['name']} {algo['symbol']}={value}", algo["kind"], value)


def showPicker():
  state["screen"] = "picker"
  state["gen"] += 1
  canvas.delete("all")
  canvas.config(cursor="")

  canvas.create_rectangle(0, 0, 700, 700, fill=NAVY, outline="")
  create_ticket_button(canvas, 20, 20, 140, 65, "Back", "btn_back", on_menu_click)

  humanMode = state["mode"] == "human_ai"
  title = "Pick your opponent" if humanMode else "Pick both players"
  canvas.create_text(353, 113, text=title, font=("Jokerman", 28, "bold"), fill=BLUE)
  canvas.create_text(350, 110, text=title, font=("Jokerman", 28, "bold"), fill=GOLD)

  if humanMode:
    columns = [(175, 525)]
  else:
    columns = [(30, 335), (365, 670)]
    canvas.create_text(182, 165, text="Red star (moves first)", font=("Arial", 14, "bold"), fill=CREAM)
    canvas.create_text(517, 165, text="Yellow star", font=("Arial", 14, "bold"), fill=CREAM)

  for colIndex, (x0, x1) in enumerate(columns):
    choice = state["choices"][colIndex]
    algo = ALGORITHMS[choice["algo"]]
    half = (x1 - x0 - 10) / 2

    for a, option in enumerate(ALGORITHMS):
      left = x0 + a * (half + 10)
      isSelected = choice["algo"] == a
      create_ticket_button(
          canvas, left, 190, left + half, 240, option["name"], f"algo_{colIndex}_{a}",
          lambda event, c=colIndex, n=a: on_algo_click(c, n),
          base=RED if isSelected else GOLD,
          textColor=CREAM if isSelected else NAVY,
      )

    canvas.create_text((x0 + x1) / 2, 272, text=f"{algo['label']} ({algo['symbol']})", font=("Arial", 13, "bold"), fill=CREAM)

    for m, value in enumerate(algo["values"]):
      y0 = 295 + m * 66
      isSelected = choice["mode"] == m
      create_ticket_button(
          canvas, x0, y0, x1, y0 + 56, f"{algo['symbol']} = {value}  ({algo['hints'][m]})", f"mode_{colIndex}_{m}",
          lambda event, c=colIndex, n=m: on_mode_click(c, n),
          base=RED if isSelected else GOLD,
          textColor=CREAM if isSelected else NAVY,
      )

  if humanMode:
    label = "You move: first" if state["humanFirst"] else "You move: second"
    create_ticket_button(canvas, 225, 540, 475, 585, label, "btn_first", on_first_click)

  create_ticket_button(canvas, 225, 610, 475, 660, "Start!", "btn_start", on_start_click)


def showGame():
  state["screen"] = "game"
  state["gen"] += 1
  resetBoard()
  canvas.delete("all")
  canvas.config(cursor="")

  canvas.create_rectangle(0, 0, 700, 700, fill=NAVY, outline="")

  create_ticket_button(canvas, 20, 20, 140, 65, "Menu", "btn_menu", on_menu_click)
  drawBoard()
  startTurn()


def on_human_ai_click(event):
  state["mode"] = "human_ai"
  showPicker()


def on_ai_ai_click(event):
  state["mode"] = "ai_ai"
  showPicker()


def on_algo_click(colIndex, a):
  state["choices"][colIndex]["algo"] = a
  showPicker()


def on_mode_click(colIndex, m):
  state["choices"][colIndex]["mode"] = m
  showPicker()


def on_first_click(event):
  state["humanFirst"] = not state["humanFirst"]
  showPicker()


def on_start_click(event):
  if state["mode"] == "human_ai":
    ai = makeChoice(state["choices"][0])
    human = makePlayer("Human", "human", 0)
    state["players"] = [human, ai] if state["humanFirst"] else [ai, human]
  else:
    state["players"] = [makeChoice(state["choices"][0]), makeChoice(state["choices"][1])]
  showGame()


def on_again_click(event):
  showGame()


def on_menu_click(event):
  showMenu()


canvas.bind("<Button-1>", onClick)
canvas.bind("<Motion>", onMotion)
canvas.bind("<Leave>", lambda event: canvas.delete("ghost"))

showMenu()

root.mainloop()