import sys
import os

def getDirTree(path,cur_pos):
    cwd_tmp=os.getcwd()
    try:
            os.chdir(path)
    except PermissionError:
            return
    else:
            try:
                    files=os.listdir()
            except PermissionError:
                    return
            else:
                    for file in files:
                            if os.path.isdir(file):
                                    cur_pos[file]=['d',None,{}]
                                    getDirTree(file,cur_pos[file][2])
    os.chdir(cwd_tmp)

def dfs(tree):
    for x in tree:
        print(f'{x}, {tree[x][0]}, {tree[x][1]}')
        dfs(tree[x][2])
