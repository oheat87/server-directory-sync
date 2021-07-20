import sys
import os

import zipfile
##from datetime import datetime

#paths: global varaibles
PROG_PATH=''
TARGET_PATH=''
ARCHIVE_PATH=''
##TIME_FORMAT='%Y%m%d%H%M%S'

#debug constants
DEBUG_PORT=3500
DEBUG_IP_ADDR='127.0.0.1'
DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

def setPaths(prog_path,target_path):
    global PROG_PATH,TARGET_PATH,ARCHIVE_PATH
    PROG_PATH=prog_path
    TARGET_PATH=target_path
    ARCHIVE_PATH=os.path.join(PROG_PATH,'syncPro','backup')

def getOnlyFileList(target_path):
    #save cwd
    cwd_tmp=os.getcwd()
    
    os.chdir(target_path)
    #get file list and remove directory name from the list
    file_list= os.listdir()
    for fname in file_list:
        if os.path.isdir(fname): file_list.remove(fname)

    #restore cwd
    os.chdir(cwd_tmp)
    return file_list  
    

def backupDir(archive_path,target_path):
    file_list= getOnlyFileList(target_path)
    zip_file_path= os.path.join(archive_path,'backup'+'_prev'+str(1)+'.zip')
    with zipfile.ZipFile(zip_file_path,'w') as backup_zip:
        #save cwd
        cwd_tmp= os.getcwd()

        os.chdir(target_path)
        for fname in file_list:
            backup_zip.write(fname)

        #restore cwd
        os.chdir(cwd_tmp)
        
        backup_zip.close()

def restoreDir(archive_path, target_path,restore_step=1):
    #save cwd
    cwd_tmp= os.getcwd()

    #--------------------delete process
    #get file name list in backup zip file and in target directory
    zip_file_path= os.path.join(archive_path,'backup'+'_prev'+str(restore_step)+'.zip')
    with zipfile.ZipFile(zip_file_path,'r') as f:
        zip_file_list=f.namelist()
        f.close()
    #get file name list in target directory
    target_file_list= getOnlyFileList(target_path)

    #delete files
    deleteList= list(set(target_file_list)-set(zip_file_list))
    os.chdir(target_path)
    for fname in deleteList:
        os.remove(fname)

    #----------------------extract compressed zip file into target path
    zipfile.ZipFile(zip_file_path).extractall(target_path)

    #restore cwd
    os.chdir(cwd_tmp)

