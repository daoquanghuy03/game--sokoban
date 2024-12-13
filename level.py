import sys
def map_open(filename, level):
    matrix = []
#   if level < 1 or level > 45:
    if int(level) < 1 or int(level) >= 45:
        print("LỖI: Level "+str(level)+" nằm ngoài phạm vi")
        sys.exit(1)
    else:
        file = open(filename,'r')
        level_found = False
        for line in file:
            row = []
            if not level_found:
                if  "Level "+str(level) == line.strip():
                    level_found = True
            else:
                if line.strip() != "":
                    row = []
                    for c in line:
                        if c != '\n' and c in [' ','#','@','+','$','*','.']:
                            row.append(c)
                        elif c == '\n': 
                            continue
                        else:
                            print("LỖI: Level "+str(level)+" có giá trị không hợp lệ "+c)
                            sys.exit(1)
                    matrix.append(row)
                else:
                    break
        return matrix