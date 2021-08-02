import sys
import os

import zipfile
import shutil
import datetime
##from datetime import datetime

#paths: global varaibles
PROG_PATH=''
TARGET_PATH=''
ARCHIVE_PATH=''
##TIME_FORMAT='%Y%m%d%H%M%S'

#debug constants
# DEBUG_PORT=3500
# DEBUG_IP_ADDR='127.0.0.1'
# DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

def setPaths(prog_path,target_path):
    global PROG_PATH,TARGET_PATH,ARCHIVE_PATH
    PROG_PATH=prog_path
    TARGET_PATH=target_path
    ARCHIVE_PATH=os.path.join(PROG_PATH,'syncPro','backup')
    print(PROG_PATH,TARGET_PATH,ARCHIVE_PATH)

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
    

def backupDir(target_path,archive_path=ARCHIVE_PATH):
    """
    :param target_path:
    :param archive_path:
    :return:
    """
    time=str(datetime.datetime.now()).replace(":", "-")[:-3]
    # file_list= getOnlyFileList(target_path)
    zip_file_path= os.path.join(target_path,time+'.zip')

    backup_zip=zipfile.ZipFile(zip_file_path,'w')
    #save cwd
    #cwd_tmp= os.getcwd()

    # os.chdir(target_path)
    # for fname in file_list:
    #     backup_zip.write(fname)
    # print(f">>>>>>>>>> TARGET PATH: {target_path}")
    for folder, subfolders, files in os.walk(TARGET_PATH):
        for file in files:
            backup_zip.write(os.path.join(folder, file),
                          os.path.relpath(os.path.join(folder, file), TARGET_PATH),
                          compress_type=zipfile.ZIP_DEFLATED)
    backup_zip.close()

    #restore cwd
    #os.chdir(cwd_tmp)



def restoreDir(archive_path, target_path,zip_name):
    # #save cwd
    # cwd_tmp= os.getcwd()

    # #--------------------delete process
    # #get file name list in backup zip file and in target directory
    # zip_file_path= os.path.join(archive_path,zip_name)
    # with zipfile.ZipFile(zip_file_path,'r') as f:
    #     zip_file_list=f.namelist()
    #     f.close()
    # #get file name list in target directory
    # target_file_list= getOnlyFileList(target_path)
    #
    # #delete files
    # deleteList= list(set(target_file_list)-set(zip_file_list))
    # os.chdir(target_path)
    # for fname in deleteList:
    #     os.remove(fname)
    #
    # #----------------------extract compressed zip file into target path
    # zipfile.ZipFile(zip_file_path).extractall(target_path)
    #
    # #restore cwd
    # os.chdir(cwd_tmp)


    # remove all files in targetDir
    target_dir_list=os.listdir(TARGET_PATH)
    for filename in target_dir_list:
        path=os.path.join(TARGET_PATH,filename)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    # success to remove all files in targetDir

    # run restore
    print("===     RESTORE   ===")
    filename = os.path.join(archive_path, zip_name)
    with zipfile.ZipFile(os.path.join(archive_path,filename), 'r') as recov_zip:
        recov_zip.extractall(TARGET_PATH)

    print("=== RESTORE SUCCESS ===")