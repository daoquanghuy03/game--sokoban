from level import *
from attribute_sokoban import Game
import sys
import pygame
import string
import queue
import copy
import time

TIME_LIMITED = 1800

def validMove(state):
    x = 0
    y = 0
    move = []
    for step in ["U","D","L","R"]:
        if step == "U":
            x = 0
            y = -1
        elif step == "D":
            x = 0
            y = 1
        elif step == "L":
            x = -1
            y = 0
        elif step == "R":
            x = 1
            y = 0

        if state.can_move(x,y) or state.can_push(x,y):
            move.append(step)

    return move

''' Kiểm tra bế tắc: hộp ở góc tường hoặc hộp khác '''
def is_deadlock(state):
    box_list = state.box_list()
    for box in box_list:
        x = box[0]
        y = box[1]
        #corner up-left
        if state.get_content(x,y-1) in ['#','$','*'] and state.get_content(x-1,y) in ['#','$','*']:
            if state.get_content(x-1,y-1) in ['#','$','*']:
                return True
            if state.get_content(x,y-1) == '#' and state.get_content(x-1,y) =='#':
                return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x+1,y-1) == '#' and state.get_content(x-1,y+1) == '#':
                    return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x-1,y) == '#':
                if state.get_content(x+1,y-1) == '#':
                    return True
            if state.get_content(x,y-1) == '#' and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y+1) == '#':
                    return True
                
        #corner up-right
        if state.get_content(x,y-1) in ['#','$','*'] and state.get_content(x+1,y) in ['#','$','*']:
            if state.get_content(x+1,y-1) in ['#','$','*']:
                return True
            if state.get_content(x,y-1) == '#' and state.get_content(x+1,y) =='#':
                return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#' and state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x+1,y) == '#':
                if state.get_content(x-1,y-1) == '#':
                    return True
            if state.get_content(x,y-1) == '#' and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x+1,y+1) == '#':
                    return True


        #corner down-left
        elif state.get_content(x,y+1) in ['#','$','*'] and state.get_content(x-1,y) in ['#','$','*']:
            if state.get_content(x-1,y+1) in ['#','$','*']:
                return True
            if state.get_content(x,y+1) == '#' and state.get_content(x-1,y) =='#':
                return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#' and state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x-1,y) == '#':
                if state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) == '#' and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#':
                    return True
                

        #corner down-right
        elif state.get_content(x,y+1) in ['#','$','*'] and state.get_content(x+1,y) in ['#','$','*']:
            if state.get_content(x+1,y+1) in ['#','$','*']:
                return True
            if state.get_content(x,y+1) == '#' and state.get_content(x+1,y) =='#':
                return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x-1,y+1) == '#' and state.get_content(x+1,y-1) == '#':
                    return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x+1,y) == '#':
                if state.get_content(x-1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) == '#' and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x+1,y-1) == '#':
                    return True
                
    return False


def get_distance(state):
    sum = 0
    box_list = state.box_list()
    dock_list = state.dock_list()
    for box in box_list:
        for dock in dock_list:
            sum += (abs(dock[0] - box[0]) + abs(dock[1] - box[1]))
    return sum

def worker_to_box(state):
    p = 1000
    worker = state.worker()
    box_list = state.box_list()
    for box in box_list:
        if (abs(worker[0] - box[0]) + abs(worker[1] - box[1])) <= p:
            p = abs(worker[0] - box[0]) + abs(worker[1] - box[1])
    return p

''' Thuật toán trả về đường dẫn để thắng trò chơi theo kiểu chuỗi:
U: di chuyển lên
D: di chuyển xuống
L: di chuyển sang trái
R: di chuyển sang phải
Nếu không có giải pháp, trả về chuỗi "NoSol" '''



def playByBot(game,move):
    if move == "U":
        game.move(0,-1,False)
    elif move == "D":
        game.move(0,1,False)
    elif move == "L":
        game.move(-1,0,False)
    elif move == "R":
        game.move(1,0,False)
    else:
        game.move(0,0,False)



def print_game(matrix, screen):
    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == ' ':  # floor
                screen.blit(floor, (x, y))
            elif char == '#':  # wall
                screen.blit(wall, (x, y))
            elif char == '@':  # worker on floor
                screen.blit(worker, (x, y))
            elif char == '.':  # dock
                screen.blit(docker, (x, y))
            elif char == '*':  # box on dock
                screen.blit(box_docked, (x, y))
            elif char == '$':  # box
                screen.blit(box, (x, y))
            elif char == '+':  # worker on dock
                screen.blit(worker_docked, (x, y))
            x = x + 32
        x = 0
        y = y + 32

    font = pygame.font.Font(None, 36)
    text = font.render("Level " + str(level), True, (255, 255, 0))
    screen.blit(text, (10, 10))

def BFSsolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) # Parent Node                 
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Thời gian tìm giải pháp:",round(end -start,2))
        print("Số lượng nút đã truy cập:",node_generated)
        print("Không có giải pháp!")
        return "NoSol"
    stateSet = queue.Queue()    # Queue to store traversed nodes 
    stateSet.put(state)
    stateExplored = []          # list of visited node (store matrix of nodes)
    print("Đang xử lý...")
    '''Duyệt cho đến khi không còn nút nào khả dụng (Không có giải pháp)'''
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Hết giờ!")
            return "Hết giờ"                    
        currState = stateSet.get()                      # get the top node of the queue to be the current node
        move = validMove(currState)                     # find next valid moves of current node in type of list of char ["U","D","L","R"]
        stateExplored.append(currState.get_matrix())    # add matrix of current node to visited list
        ''' Đối với mỗi nước đi hợp lệ:
            Tạo các nút con bằng cách cập nhật nút hiện tại với nước đi
            Nếu nút con không được thăm và không dẫn đến bế tắc (hộp ở góc), hãy đưa nó vào hàng đợi các nút
            Nếu nút con là nút cuối cùng để thắng, hãy trả về đường dẫn của nó'''
        for step in move:                               
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
        
            if newState.is_completed():
                end = time.time()
                print("Thời gian tìm giải pháp:",round(end -start,2),"giây")
                print("Số lượng nút đã truy cập:",node_generated)
                print("Giải pháp:",newState.pathSol)
                print("Tổng số bước cần di chuyển:", len(newState.pathSol))
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                stateSet.put(newState)
    end = time.time()
    print("Thời gian tìm giải pháp:",round(end -start,2))
    print("Số lượng nút đã truy cập:",node_generated)
    print("Không có giải pháp!")
    return "NoSol"

def AstarSolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) # Parent Node
    state.heuristc = worker_to_box(state) + get_distance(state)
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Thời gian tìm giải pháp:",round(end -start,2))
        print("Số lượng nút đã truy cập:",node_generated)
        print("Không có giải pháp!")
        return "NoSol"                 
    stateSet = queue.PriorityQueue()    # Queue to store traversed nodes (low index -> high priority) 
    stateSet.put(state)
    stateExplored = []                 # list of visited node (store matrix of nodes)
    print("Đang xử lý...")
    '''Duyệt cho đến khi không còn nút nào khả dụng (Không có giải pháp)'''
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Hết giờ!")
            return "Hết giờ"                        
        currState = stateSet.get()                      # get the top node of the queue to be the current node
        move = validMove(currState)                     # find next valid moves of current node in type of list of char ["U","D","L","R"]
        stateExplored.append(currState.get_matrix())    # add matrix of current node to visited list
        
        ''' Đối với mỗi nước đi hợp lệ:
            Tạo các nút con bằng cách cập nhật nút hiện tại với nước đi
            Nếu nút con không được thăm và không dẫn đến bế tắc (hộp ở góc), hãy đưa nó vào hàng đợi các nút
            Nếu nút con là nút cuối cùng để thắng, hãy trả về đường dẫn của nó'''
        for step in move:                              
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
            newState.heuristic = worker_to_box(newState) + get_distance(newState)
        
            if newState.is_completed():
                end = time.time()
                print("Thời gian tìm giải pháp:",round(end -start,2),"giây")
                print("Số lượng nút đã truy cập:",node_generated)
                print("Giải pháp:",newState.pathSol)
                print("Tổng số bước cần di chuyển:", len(newState.pathSol))
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                stateSet.put(newState)
    end = time.time()
    print("Thời gian tìm giải pháp:",round(end -start,2))
    print("Số lượng nút đã truy cập:",node_generated)
    print("Không có giải pháp!")
    return "NoSol"
    
def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
      return event.key
    else:
      pass

def display_box(screen, message):
  "Print a message in a box in the middle of the screen"
  fontobject = pygame.font.Font(None,18)
  pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
  pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
  pygame.display.flip()

def display_end(screen,msg):
    if msg == "Done":
        message = "Level Completed"
    elif msg == "Cannot":
        message = "No Solution"
    elif msg == "Out":
        message = "Time Out! Cannot find solution"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + ": " + "".join(current_string))
  while 1:
    inkey = get_key()
    if inkey == pygame.K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == pygame.K_RETURN:
      break
    elif inkey == pygame.K_MINUS:
      current_string.append("_")
    elif inkey <= 127:
      current_string.append(chr(inkey))
    display_box(screen, question + ": " + "".join(current_string))
  return "".join(current_string)
def display_end(screen,msg):
    if msg == "Done":
        message = "Level Completed"
    elif msg == "Cannot":
        message = "No Solution"
    elif msg == "Out":
        message = "Time Out! Cannot find solution"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    
    # Add a button to return to the start screen
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 50,
                    (screen.get_height() / 2) + 20,
                    100,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 52,
                    (screen.get_height() / 2) + 18,
                    104,24), 1)
    screen.blit(fontobject.render("Return", 1, (255,255,255)),
                ((screen.get_width() / 2) - 45, (screen.get_height() / 2) + 20))
    
    pygame.display.flip()
    
    # Wait for the user to click the button
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (screen.get_width() / 2) - 50 < event.pos[0] < (screen.get_width() / 2) + 50 and (screen.get_height() / 2) + 20 < event.pos[1] < (screen.get_height() / 2) + 40:
                    waiting = False


    pygame.display.flip()

def start_game():
    start = pygame.display.set_mode((320,320))
    total_levels = count_levels('.\levels')
    level = ask(start,"Chon level (1-" + str(total_levels) + ")")
    if int(level) > 0 and int(level) <= total_levels:
        return level
    else:
        print("ERROR: Cấp độ không hợp lệ: "+str(level))
        sys.exit(2)
def count_levels(filename):
    count = 0
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith("Level"):
                count += 1
    return count
wall = pygame.image.load('.\images\wall.png')
floor = pygame.image.load('.\images/floor.png')
box = pygame.image.load('.\images/box.png')
box_docked = pygame.image.load('.\images/box_docked.png')
worker = pygame.image.load('.\images\worker.png')
worker_docked = pygame.image.load('.\images\worker_dock.png')
docker = pygame.image.load('.\images\dock.png')
background = 44, 232, 193
pygame.init()


level = start_game()
game = Game(map_open('.\levels',level))
size = game.load_size()
screen = pygame.display.set_mode(size)
sol = ""
#sol = BFSsolution(game)
#sol = AstarSolution(game)
i = 0
flagAuto = 0
end_screen = False
while 1:
    if not end_screen:
        print_game(game.get_matrix(),screen)

        if sol == "NoSol":
            display_end(screen,"Cannot")
            end_screen = True
        if sol == "TimeOut":
            display_end(screen,"Out")
            end_screen = True
        if game.is_completed():
            display_end(screen,"Done")
            end_screen = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    sol = AstarSolution(game)
                    flagAuto = 1
                elif event.key == pygame.K_b:
                    sol = BFSsolution(game)
                    flagAuto = 1
                elif event.key == pygame.K_UP: game.move(0,-1, True)
                elif event.key == pygame.K_DOWN: game.move(0,1, True)
                elif event.key == pygame.K_LEFT: game.move(-1,0, True)
                elif event.key == pygame.K_RIGHT: game.move(1,0, True)
                elif event.key == pygame.K_q: sys.exit(0)
                elif event.key == pygame.K_d: game.unmove()
                elif event.key == pygame.K_c: sol = ""
                elif event.key == pygame.K_o:
                    end_screen = False
                    level = start_game()
                    game = Game(map_open('.\levels',level))
                    size = game.load_size()
                    screen = pygame.display.set_mode(size)
                    sol = ""
                    i = 0
                    flagAuto = 0
        if (flagAuto) and (i < len(sol)):
            playByBot(game,sol[i])
            i += 1
            if i == len(sol): flagAuto = 0
            time.sleep(0.1)

        pygame.display.update()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (screen.get_width() / 2) - 50 < event.pos[ 0] < (screen.get_width() / 2) + 50 and (screen.get_height() / 2) + 20 < event.pos[1] < (screen.get_height() / 2) + 40:
                    end_screen = False
                    level = start_game()
                    game = Game(map_open('.\levels',level))
                    size = game.load_size()
                    screen = pygame.display.set_mode(size)
                    sol = ""
                    i = 0
                    flagAuto = 0