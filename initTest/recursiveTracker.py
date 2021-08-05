import sys
import os
import time

#events of filesystem
from watchdog.events import DirCreatedEvent
from watchdog.events import DirMovedEvent
from watchdog.events import DirModifiedEvent
from watchdog.events import DirDeletedEvent
from watchdog.events import FileCreatedEvent
from watchdog.events import FileMovedEvent
from watchdog.events import FileModifiedEvent
from watchdog.events import FileDeletedEvent

#module for deep copy of dictionary object
import copy

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
                else:
                    cur_pos[file]=['f',None,0]
                                
    os.chdir(cwd_tmp)

def dfs(tree):
    for x in tree:
        print(f'{x}, {tree[x][0]}, {tree[x][1]}',end='')
        if tree[x][0]=='d':
            dfs(tree[x][2])
        else:
            print(f', {tree[x][2]}',end='')
        print()

# class for recording tree directory structure on file/directory events
class fsTracker():
    def __init__(self,dir_root_path,record_start_time):
        self.dir_root_path=dir_root_path
        self.rel_path_start_index=len(dir_root_path)+1
        self.dir_tree={}
        self.makeDirTree(dir_root_path,self.dir_tree)
        self.record_start_time=record_start_time
    def makeDirTree(self,dir_root_path,cur_pos):
        cwd_tmp=os.getcwd()
        try:
            os.chdir(dir_root_path)
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
                        self.makeDirTree(file,cur_pos[file][2])
                    else:
                        cur_pos[file]=['f',None,0]
        os.chdir(cwd_tmp)
    def getContent(self):
        return self.dir_tree
    def delContent(self):
        del self.dir_tree
    def on_created(self,event):
        path_arr=self.getPathArr(event.src_path)
        if type(event) is DirCreatedEvent:
            # update dir tree structure and according flags of nodes properly
            self.dirTreeCreateDir(path_arr)
        elif type(event) is FileCreatedEvent:
            if self.FDExist(path_arr):
                prev_op_flag=self.getOpFlag(path_arr)
                if prev_op_flag==None:
                    print('[on created] file rewriting detected')
                    self.setOpFlag(path_arr,'m')
                    # !!!!!here, timestamp should be updated!!!!!
                    self.updateTimeStamp(path_arr)
                elif prev_op_flag=='c':
                    # !!!!!here, timestamp should be updated!!!!!
                    self.updateTimeStamp(path_arr)
                elif prev_op_flag=='m':
                    # !!!!!here, timestamp should be updated!!!!!
                    self.updateTimeStamp(path_arr)
                elif prev_op_flag=='d':
                    self.setOpFlag(path_arr,'m')
                    ## !!!!!then, timestamp should be updated!!!!!
                    self.updateTimeStamp(path_arr)
                else:
                    print('[on created] unexpected op flag error')
                    sys.exit(1)
            else:
                #in this case, make a new event record for the new file
                cur_time=time.time()-self.record_start_time #time stamp for file record
                cur_pos=self.dir_tree
                arr_len=len(path_arr)
                for i in range(arr_len):
                    x=path_arr[i]
                    if i<(arr_len-1):
                        if x not in cur_pos:
                            print('[on created] illegal file path error')
                            sys.exit(1)
                    elif i==(arr_len-1):
                        # !!!!!here, timestamp should be updated!!!!!
                        cur_pos[x]=['f','c',cur_time]
                    cur_pos=cur_pos[x][2]
        else:
            print(f'unexpected event type: {event}')
    def on_deleted(self,event):
        path_arr=self.getPathArr(event.src_path)
        if type(event) is DirDeletedEvent:
            if not self.pathExist(path_arr):
                print('[on moved] already treated as deleted folder detected')
                return
            self.dirTreeDeleteDir(path_arr)
        elif type(event) is FileDeletedEvent:
            if not self.pathExist(path_arr):
                print('[on moved] already treated as deleted file detected')
                return
            prev_op_flag=self.getOpFlag(path_arr)
            if prev_op_flag==None or prev_op_flag=='m':
                self.setOpFlag(path_arr,'d')
                # !!!!!here, timestamp should be updated!!!!!
                self.updateTimeStamp(path_arr)
            elif prev_op_flag=='c':
                # in this case, delete the file node from dir tree
                cur_pos=self.dir_tree
                arr_len=len(path_arr)
                for i in range(arr_len):
                    x=path_arr[i]
                    if x not in cur_pos:
                        print('[on deleted] illegal file path error')
                        sys.exit(1)
                    elif i==(arr_len-1):
                        del cur_pos[x]
                        return
                    cur_pos=cur_pos[x][2]
            elif prev_op_flag=='d':
                print('[on deleted] unexpected op sequence error: deletion after deletion')
                sys.exit(1)
            else:
                print('[on deleted] unexpected op flag error')
                sys.exit(1)
        else:
            print(f'unexpected event type: {event}')
    def on_modified(self,event):
        path_arr=self.getPathArr(event.src_path)
        if type(event) is DirModifiedEvent:
            pass
        elif type(event) is FileModifiedEvent:
            #modify the flag if necessary
            cur_time=time.time()-self.record_start_time # timestamp for file record
            cur_pos=self.dir_tree
            arr_len=len(path_arr)
            for i in range(arr_len):
                x=path_arr[i]
                if i<(arr_len-1):
                    if x not in cur_pos:
                        print('[on modified] illegal file path error')
                        sys.exit(1)
                elif i==(arr_len-1) and x==path_arr[-1]:
                    if cur_pos[x][1]==None:
                        cur_pos[x][1]='m'
                        # !!!!!here, timestamp should be updated!!!!!
                        cur_pos[x][2]=cur_time
                    elif cur_pos[x][1]=='c' or cur_pos[x][1]=='m':
                        # !!!!!here, timestamp should be updated!!!!!
                        cur_pos[x][2]=cur_time
                    elif cur_pos[x][1]=='d':
                        print('[on modified] illegal file op flag sequence error: modification after deletion')
                        sys.exit(1)
                    else:
                        print('[on modified] unexpected file op flag error')
                        sys.exit(1)
                cur_pos=cur_pos[x][2]
        else:
            print(f'unexpected event type: {event}')
    def on_moved(self,event):
        src_path_arr=self.getPathArr(event.src_path)
        dest_path_arr=self.getPathArr(event.dest_path)
        if type(event) is DirMovedEvent:
            subtree=None # subtree of renamed folder
            #-------- deletion of originally named folder in dir tree
            #check if there is tree path to event source path
            if not self.pathExist(src_path_arr):
                print('[on moved] already treated as deleted folder detected')
                return
            prev_op_flag=self.getOpFlag(src_path_arr)
            if prev_op_flag==None:
                #first, copy subtree which will be attached to the newly named folder
                subtree=copy.deepcopy(self.dirTreeGetSubtree(src_path_arr))
                # in this case, treat all sub files and directories as deleted
                cur_pos= self.setOpFlag(src_path_arr,'d') #subtree rooted at source path is returned
                ### here change flag of sub files and directories properly
                self.dirTreeRecordSubtreeDeletion(cur_pos)
                
            elif prev_op_flag=='c':
                #first, copy subtree which will be attached to the newly named folder
                subtree=copy.deepcopy(self.dirTreeGetSubtree(src_path_arr))
                # in this case, just delete new folder as a whole
                self.dirTreeRemoveSubtree(src_path_arr)
            elif prev_op_flag=='d':
##                print(f'[on moved] unexpected op flag: deleted')
##                sys.exit(1)
                print('[on moved] already treated as deleted folder detected')
                return
            else:
                print(f'[on moved] unexpected op flag: {prev_op_flag}')
                sys.exit(1)
            #---------- creation of newly named folder in dir tree
            if self.FDExist(dest_path_arr):
                #---------- subtree handling part
                #compare the original folder's subtree and newly named folder's subtree to update newly named folder's one
                self.dirTreeRecordSubtreeCreation(self.dirTreeGetSubtree(dest_path_arr), subtree)
                del subtree # after comparing two subtrees, delete copy of original folder's subtree
                prev_op_flag=self.getOpFlag(dest_path_arr)
                if prev_op_flag==None or prev_op_flag=='c':
                    print(f'[on moved] unexpected op flag: {prev_op_flag}')
                    sys.exit(1)
                elif prev_op_flag=='d':
                    #in this case, set op flag as None
                    self.setOpFlag(dest_path_arr,None)
                else:
                    print(f'[on moved] unexpected op flag: {prev_op_flag}')
                    sys.exit(1)
            else:
                #---------- subtree handling part
                self.dirTreeRecordNewSubtreeCreation(subtree)
                #in this case, just make a subtree for that directory
                cur_pos=self.dir_tree
                arr_len=len(dest_path_arr)
                for i in range(arr_len):
                    x=dest_path_arr[i]
                    if i<(arr_len-1):
                        if x in cur_pos:
                            pass
                        else:
                            print('[on moved] created directory illegal path')
                            sys.exit(1)
                    elif i==(arr_len-1):
                        cur_pos[x]=['d','c',subtree] # attach pre-made subtree
                    cur_pos= cur_pos[x][2]
        elif type(event) is FileMovedEvent:
            if len(src_path_arr)!=len(dest_path_arr):
                print('[on moved] unexpected renaming event occurred: src and dest path len are different')
                sys.exit(1)
            if not self.pathExist(src_path_arr):
                print('[on moved] alreaty treated as deleted file detected')
                return
            else:
                if self.checkOnMovedFolderRenamed(src_path_arr,dest_path_arr):
                    print('[on moved] already treated as deleted file detected(brkpoint2)')
                    return
            # in this case, treat rename event as successive sequence of deletion of original file and creation of newly named file
            cur_time=time.time()-self.record_start_time
            cur_pos=self.dir_tree
            arr_len=len(src_path_arr)
            for i in range(arr_len):
                x=src_path_arr[i]
                if i<(arr_len-1):
                    if x not in cur_pos:
                        print('[on moved] illegal file path error')
                        sys.exit(1)
                elif i==(arr_len-1):
                    #here, treat deletion of original file and then creation of newly named file in dir tree structure
                    # -------deletion part
                    if cur_pos[x][1]==None or cur_pos[x][1]=='m':
                        cur_pos[x][1]='d'
                    elif cur_pos[x][1]=='c':
                        del cur_pos[x]
                    elif cur_pos[x][1]=='d':
                        print('[on moved] illegal sequence of file operation: renaming after deletion')
                        sys.exit(1)
                    else:
                        print('[on moved] unexpected file op flag error')
                        sys.exit(1)
                    # -------creation part
                    y=dest_path_arr[i] # new file name
                    if y in cur_pos:
                        if cur_pos[y][1]==None:
                            print('[on moved] file rewriting detected')
                            cur_pos[y][1]='m'
                            # !!!!!here, timestamp should be updated!!!!!
                            cur_pos[y][2]=cur_time
                        elif cur_pos[y][1]=='c':
                            print('[on moved] file rewriting detected')
                            # !!!!!here, timestamp should be updated!!!!!
                            cur_pos[y][2]=cur_time
                        elif cur_pos[y][1]=='m':
                            print('[on moved] file rewriting detected')
                            # !!!!!here, timestamp should be updated!!!!!
                            cur_pos[y][2]=cur_time
                        elif cur_pos[y][1]=='d':
                            cur_pos[y][1]='m'
                            # !!!!!here, timestamp should be updated!!!!!
                            cur_pos[y][2]=cur_time
                        else:
                            print('[on moved] unexpected file op flag error(brkpoint2)')
                            sys.exit(1)
                    else:
                        # make new file event record into dir tree structure
                        # !!!!!here, timestamp should be updated!!!!!
                        cur_pos[y]=['f','c',cur_time]
                    return
                cur_pos=cur_pos[x][2]
        else:
            print(f'unexpected event type: {event}')
    def getPathArr(self,event_path):
        rel_path=event_path[self.rel_path_start_index:]
        path_arr=rel_path.split(os.path.sep)
        if path_arr[0]=='':
            path_arr.pop(0)
        return path_arr
    def pathExist(self,path_arr):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if x not in cur_pos:
                return False
            cur_pos=cur_pos[x][2]
        return True
    def checkOnMovedFolderRenamed(self,src_path_arr,dest_path_arr):
        if len(src_path_arr)!=len(dest_path_arr):
            print('[checkOnMovedFolderRenamed] unexpected src and dest path arr received: different length')
            sys.exit(1)
        return src_path_arr[-1]==dest_path_arr[-1]
        
    def FDExist(self,path_arr):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if i<(arr_len-1):
                if x in cur_pos:
                    pass
                else:
                    print('[dirExist] illegal path error')
                    sys.exit(1)
            elif i==(arr_len-1) and x==path_arr[-1]:
                return x in cur_pos
            cur_pos=cur_pos[x][2]
    def updateTimeStamp(self,path_arr):
        cur_time=time.time()-self.record_start_time
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if i<(arr_len-1):
                if x not in cur_pos:
                    print('[updateTimeStamp] unexpected file path')
                    sys.exit(1)
                pass
            elif i==(arr_len-1) and x==path_arr[-1]:
                if cur_pos[x][0]=='d':
                    print('[updateTimeStamp] cannot update timestamp of directory')
                    sys.exit(1)
                elif cur_pos[x][0]=='f':
                    cur_pos[x][2]=cur_time
                    return
                else:
                    print('[updateTimeStamp] unexpected file/directory flag')
                    sys.exit(1)
            cur_pos=cur_pos[x][2]
    def getOpFlag(self,path_arr):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if x not in cur_pos:
                print('[getOpFlag] unexpected file path')
                sys.exit(1)
            elif i==(arr_len-1) and x==path_arr[-1]:
                return cur_pos[x][1]
            cur_pos= cur_pos[x][2]
        print('[getOpFlag] no file/directory object error')
        sys.exit(1)
    def setOpFlag(self,path_arr,flag):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if x not in cur_pos:
                print('[setOpFlag] unexpected file path')
                sys.exit(1)
            elif i==(arr_len-1) and x==path_arr[-1]:
                cur_pos[x][1]=flag
                return cur_pos[x][2] #return subtree
            cur_pos=cur_pos[x][2]
        print('[setOpFlag] no file/directory object error')
        sys.exit(1)
    def dirTreeGetSubtree(self,path_arr):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if x not in cur_pos:
                print('[dirTreeGetSubtree] unexpected file path')
                sys.exit(1)
            cur_pos=cur_pos[x][2]
        return cur_pos
    def dirTreeRemoveSubtree(self,path_arr):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if x not in cur_pos:
                print('[dirTreeRemoveSubtree] unexpected file path')
                sys.exit(1)
            elif i==(arr_len-1) and x==path_arr[-1]:
                del cur_pos[x]
                return
            cur_pos=cur_pos[x][2]
        print('[dirTreeRemoveSubtree] no file/directory object error')
        sys.exit(1)
    def dirTreeAttachSubtree(self,path_arr,subtree):
        cur_pos=self.dir_tree
        arr_len=len(path_arr)
        for i in range(arr_len):
            x=path_arr[i]
            if x not in cur_pos:
                print('[dirTreeAttachSubtree] unexpected file path')
                sys.exit(1)
            elif i==(arr_len-1) and x==path_arr[-1]:
                cur_pos[x][2]=subtree
                return
            cur_pos=cur_pos[x][2]
    def dirTreeRecordSubtreeCreation(self,target_subtree,cmp_subtree):
        target_cur_pos=target_subtree
        cmp_cur_pos=cmp_subtree
        for fdname in cmp_cur_pos:
            if cmp_cur_pos[fdname][0]=='f':
                if cmp_cur_pos[fdname][1]==None or cmp_cur_pos[fdname][1]=='c' or cmp_cur_pos[fdname][1]=='m':
                    if fdname in target_cur_pos:
                        if target_cur_pos[fdname][1]=='d':
                            target_cur_pos[fdname][1]='m'
                        else:
                            print('[dirTreeRecordSubtreeCreation] target tree illegal file flag error')
                            sys.exit(1)
                    else:
                        target_cur_pos[fdname]=['f','c',{}]
                elif cmp_cur_pos[fdname][1]=='d':
                    #for debug
                    if target_cur_pos[fdname][1]!='d':
                        print('[dirTreeRecordSubtreeCreation] target tree illegal file flag error(brkpoint2)')
                        sys.exit(1)
                else:
                    print('[dirTreeRecordSubtreeCreation] cmp tree illegal file flag error')
                    sys.exit(1)
            elif cmp_cur_pos[fdname][0]=='d':
                if cmp_cur_pos[fdname][1]==None or cmp_cur_pos[fdname][1]=='c':
                    if fdname in target_cur_pos:
                        target_cur_pos[fdname][1]=None
                    else:
                        target_cur_pos[fdname]=['d','c',{}]
                    self.dirTreeRecordSubtreeCreation(target_cur_pos[fdname][2],cmp_cur_pos[fdname][2])
                elif cmp_cur_pos[fdname][1]=='d':
                    #for debug
                    if target_cur_pos[fdname][1]!='d':
                        print('[dirTreeRecordSubtreeCreation] target tree illegal directory flag error(brkpoint2)')
                        sys.exit(1)
                else:
                    print('[dirTreeRecordSubtreeCreation] illegal directory flag error')
                    sys.exit(1)
            else:
                print('[dirTreeRecordSubtreeCreation] illegal file/directory flag error')
                sys.exit(1)
    def dirTreeRecordNewSubtreeCreation(self,subtree):
        fdnames=list(subtree.keys())
        for fdname in fdnames:
            if subtree[fdname][0]=='f':
                if subtree[fdname][1]==None:
                    subtree[fdname][1]='c'
                elif subtree[fdname][1]=='c':
                    pass
                elif subtree[fdname][1]=='m':
                    subtree[fdname][1]='c'
                elif subtree[fdname][1]=='d':
                    del subtree[fdname]
                else:
                    print('[dirTreeRecordNewSubtreeCreation] illegal file op flag error')
                    sys.exit(1)
            elif subtree[fdname][0]=='d':
                if subtree[fdname][1]==None:
                    subtree[fdname][1]='c'
                    self.dirTreeRecordNewSubtreeCreation(subtree[fdname][2])
                elif subtree[fdname][1]=='c':
                    self.dirTreeRecordNewSubtreeCreation(subtree[fdname][2])
                elif subtree[fdname][1]=='d':
                    del subtree[fdname]
                else:
                    print('[dirTreeRecordNewSubtreeCreation] illegal directory op flag error')
                    sys.exit(1)
            else:
                print('[dirTreeRecordNewSubtreeCreation] illegal file/directory flag error')
                sys.exit(1)
    def dirTreeRecordSubtreeDeletion(self,subtree):
        fdnames=list(subtree.keys())
        for fdname in fdnames:
            if subtree[fdname][0]=='f':
                if subtree[fdname][1]==None:
                    subtree[fdname][1]='d'
                elif subtree[fdname][1]=='c':
                    del subtree[fdname]
                elif subtree[fdname][1]=='m':
                    subtree[fdname][1]='d'
                elif subtree[fdname][1]=='d':
                    pass
                else:
                    print('[dirTreeRecordSubtreeDeletion] illegal file op flag error')
                    sys.exit(1)
            elif subtree[fdname][0]=='d':
                if subtree[fdname][1]==None:
                    subtree[fdname][1]='d'
                    self.dirTreeRecordSubtreeDeletion(subtree[fdname][2])
                elif subtree[fdname][1]=='c':
                    del subtree[fdname]
                elif subtree[fdname][1]=='d':
                    pass
                else:
                    print('[dirTreeRecordSubtreeDeletion] illegal directory op flag error')
                    sys.exit(1)
            else:
                print('[dirTreeRecordSubtreeDeletion] illegal file/directory flag error')
                sys.exit(1)
    def dirTreeCreateDir(self,path_arr):
        if self.FDExist(path_arr):
            prev_op_flag=self.getOpFlag(path_arr)
            if prev_op_flag==None or prev_op_flag=='c':
                print(f'[dirTreeCreateFolder] unexpected op flag: {prev_op_flag}')
                sys.exit(1)
            elif prev_op_flag=='d':
                #in this case, set op flag as None
                self.setOpFlag(path_arr,None)
            else:
                print(f'[dirTreeCreateFolder] unexpected op flag: {prev_op_flag}')
                sys.exit(1)
        else:
            #in this case, make a subtree for that directory
            cur_pos=self.dir_tree
            arr_len=len(path_arr)
            for i in range(arr_len):
                x=path_arr[i]
                if i<(arr_len-1):
                    if x in cur_pos:
                        pass
                    else:
                        print('[dirTreeCreateFolder] created directory illegal path')
                        sys.exit(1)
                elif i==(arr_len-1):
                    cur_pos[x]=['d','c',{}]
                    return
                cur_pos= cur_pos[x][2]
    def dirTreeDeleteDir(self,path_arr):
        prev_op_flag=self.getOpFlag(path_arr)
        if prev_op_flag==None:
            # in this case, treat all sub files and directories as deleted
            cur_pos= self.setOpFlag(path_arr,'d')
            ### here change flag of sub files and directories properly
            self.dirTreeRecordSubtreeDeletion(cur_pos)
        elif prev_op_flag=='c':
            # in this case, just delete new folder as a whole
            self.dirTreeRemoveSubtree(path_arr)
        elif prev_op_flag=='d':
            print(f'[dirTreeDeleteDir] unexpected op flag: deleted')
            sys.exit(1)
        else:
            print(f'[dirTreeDeleteDir] unexpected op flag: {prev_op_flag}')
            sys.exit(1)
    def getDirTree(self):
        return self.dir_tree

def syncDirectories(dir_root_path,my_tree,other_tree):
    tmp_cwd=os.getcwd()
    os.chdir(dir_root_path)
    other_tree_fdname_list=list(other_tree.keys())
    for fdname in other_tree_fdname_list:
        if other_tree[fdname][0]=='d':
            if fdname in my_tree:
                if other_tree[fdname][1]==None:
                    if my_tree[fdname][1]==None:
                        syncDirectories(os.path.join(dir_root_path,fdname),my_tree[fdname][2],other_tree[fdname][2])
                    elif my_tree[fdname][1]=='c':
                        print('[syncDirectories] unexpected directory op flags pair: c-None')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='d':
                        #delete subtrees from both of the trees
                        del my_tree[fdname]
                        del other_tree[fdname]
                    else:
                        print('[syncDirectories] unexpected directory op flag')
                        sys.exit(1)
                elif other_tree[fdname][1]=='c':
                    if my_tree[fdname][1]==None:
                        print('[syncDirectories] unexpected directory op flags pair: None-c')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='c':
                        syncDirectories(os.path.join(dir_root_path,fdname),my_tree[fdname][2],other_tree[fdname][2])
                    elif my_tree[fdname][1]=='d':
                        print('[syncDirectories] unexpected directory op flags pair: d-c')
                        sys.exit(1)
                    else:
                        print('[syncDirectories] unexpected directory op flag')
                        sys.exit(1)
                elif other_tree[fdname][1]=='d':
                    if my_tree[fdname][1]==None:
                        shutil.rmtree(os.path.join(dir_root_path,fdname))
                        #delete subtrees from both of the trees
                        del my_tree[fdname]
                        del other_tree[fdname]
                    elif my_tree[fdname][1]=='c':
                        print('[syncDirectories] unexpected directory op flags pair: c-d')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='d':
                        #delete subtrees from both of the trees
                        del my_tree[fdname]
                        del other_tree[fdname]
                    else:
                        print('[syncDirectories] unexpected directory op flag')
                        sys.exit(1)
                else:
                    print('[syncDirectories] unexpected directory op flag')
                    sys.exit(1)
            else:
                if other_tree[fdname][1]==None:
                    print('[syncDirectories] not synchronized in previous step error: x-None')
                    sys.exit(1)
                elif other_tree[fdname][1]=='c':
                    os.mkdir(fdname)
                    my_tree[fdname]=['d','c',{}]
                    # !!!! here flag jobs should be done
                    syncDirectories(os.path.join(dir_root_path,fdname),my_tree[fdname][2],other_tree[fdname][2])
                elif other_tree[fdname][1]=='d':
                    print('[syncDirectories] not synchronized in previous step error: x-None')
                    sys.exit(1)
                else:
                    print('[syncDirectories] unexpected directory op flag')
                    sys.exit(1)
        else:
            #if current node is file node, pass
            pass
    os.chdir(tmp_cwd)

def getJobList(dir_root_path,my_tree,other_tree):
    deleteList,sendList,receiveList=[],[],[]
    my_tree_fdname_list=list(my_tree.keys())
    other_tree_fdname_list=list(other_tree.keys())
    # first, compare two tree structure with respect to other tree
    for fdname in other_tree_fdname_list:
        if other_tree[fdname][0]=='d':
            if fdname not in my_tree:
                print('[getJobList] directory structure not synchronized error')
                sys.exit(1)
            tmp_dList,tmp_sList,tmp_rList=getJobList(os.path.join(dir_root_path,fdname),my_tree[fdname][2],other_tree[fdname][2])
            deleteList.extend(tmp_dList)
            sendList.extend(tmp_sList)
            receiveList.extend(tmp_rList)
            del tmp_dList
            del tmp_sList
            del tmp_rList
        elif other_tree[fdname][0]=='f':
            if fdname in my_tree:
                if other_tree[fdname][1]==None:
                    if my_tree[fdname][1]==None:
                        continue
                    elif my_tree[fdname][1]=='c':
                        print('[getJobList] unexpected file op flag pair detected: c-None')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='m':
                        # a file will be sent detected
                        sendList.append(os.path.join(dir_root_path,fdname,'m'))
                    elif my_tree[fdname][1]=='d':
                        continue
                    else:
                        print('[getJobList] unexpected file op flag error(brkpoint1)')
                        sys.exit(1)
                elif other_tree[fdname][1]=='c':
                    if my_tree[fdname][1]==None:
                        print('[getJobList] unexpected file op flag pair detected: None-c')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='c':
                        if my_tree[fdname][2]>other_tree[fdname][2]:
                            # a file will be sent detected
                            sendList.append(os.path.join(dir_root_path,fdname,'c'))
                        else:
                            # a file will be received detected
                            receiveList.append(os.path.join(dir_root_path,fdname))
                    elif my_tree[fdname][1]=='m':
                        print('[getJobList] unexpected file op flag pair detected: m-c')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='d':
                        print('[getJobList] unexpected file op flag pair detected: d-c')
                        sys.exit(1)
                    else:
                        print('[getJobList] unexpected file op flag error(brkpoint2)')
                        sys.exit(1)
                elif other_tree[fdname][1]=='m':
                    if my_tree[fdname][1]==None:
                        # a file will be received detected
                        receiveList.append(os.path.join(dir_root_path,fdname))
                    elif my_tree[fdname][1]=='c':
                        print('[getJobList] unexpected file op flag pair detected: c-m')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='m':
                        if my_tree[fdname][2]>other_tree[fdname][2]:
                            # a file will be sent detected
                            sendList.append(os.path.join(dir_root_path,fdname,'m'))
                        else:
                            # a file will be received detected
                            receiveList.append(os.path.join(dir_root_path,fdname))
                    elif my_tree[fdname][1]=='d':
                        continue
                    else:
                        print('[getJobList] unexpected file op flag error(brkpoint3)')
                        sys.exit(1)
                elif other_tree[fdname][1]=='d':
                    if my_tree[fdname][1]==None or my_tree[fdname][1]=='m':
                        # a file will be deleted detected
                        deleteList.append(os.path.join(dir_root_path,fdname))
                    elif my_tree[fdname][1]=='c':
                        print('[getJobList] unexpected file op flag pair detected: c-d')
                        sys.exit(1)
                    elif my_tree[fdname][1]=='d':
                        continue
                    else:
                        print('[getJobList] unexpected file op flag error(brkpoint4)')
                        sys.exit(1)
                else:
                    print('[getJobList] unexpected file op flag error')
                    sys.exit(1)
            else:
                if other_tree[fdname][1]==None or other_tree[fdname][1]=='m' or other_tree[fdname][1]=='d':
                    print('[getJobList] unexpected file op flag error: unsynchronized file detected(brkpoint1)')
                    sys.exit(1)
                elif other_tree[fdname][1]=='c':
                    # a file will be received detected
                    receiveList.append(os.path.join(dir_root_path,fdname))
                else:
                    print('[getJobList] unexpected file op flag error(brkpoint5)')
                    sys.exit(1)
        else:
            print('[getJobList] unexpected file/directory flag')
            sys.exit(1)

    # second, compare two tree structure with respect to my tree
    for fdname in my_tree_fdname_list:
        if my_tree[fdname][0]=='d':
            # this case is already handled in the previous for loop
            continue
        elif my_tree[fdname][0]=='f':
            if fdname in other_tree:
                # this case is also already handled in the previous for loop
                continue
            else:
                if my_tree[fdname][1]==None or my_tree[fdname][1]=='m' or my_tree[fdname][1]=='d':
                    print('[getJobList] unexpected file op flag error: unsynchronized file detected(brkpoint2)')
                    sys.exit(1)
                elif my_tree[fdname][1]=='c':
                    # a file will be sent detected
                    sendList.append(os.path.join(dir_root_path,fdname,'c'))
                else:
                    print('[getJobList] unexpected file op flag error(brkpoint6)')
                    sys.exit(1)
        else:
            print('[getJobList] unexpected file/directory flag')
            sys.exit(1)

    return [deleteList,sendList,receiveList]
