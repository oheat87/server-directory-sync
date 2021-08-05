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
                            # directory
                            if os.path.isdir(file):
                                    cur_pos[file]=['d',None,{}]
                                    getDirTree(file,cur_pos[file][2])
                            # files
                            if os.path.isfile(file):
                                    cur_pos[file]=['f',None]
                                    # getDirTree(path,cur_pos[file][2])
    os.chdir(cwd_tmp)


def dfs(tree,filelist,dirlist,path=''):
    for x in tree:
        path=os.path.join(path,x)
        if tree[x][0]=='d':
            # print(f'{path}, {tree[x][0]}, {tree[x][1]}')
            dirlist.append(path)
            dfs(tree[x][2],filelist,dirlist,path)
            path='' # init path
        elif tree[x][0]=='f':
            # print(f'{path}, {tree[x][0]}')
            filelist.append(path)
            path=path.replace(x,"") # 경로 뒤로가기
            # dfs(tree[x][1])