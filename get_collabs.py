from boxsdk import Client, OAuth2, BoxAPIException
import time
from datetime import datetime
import api_connect
import json
#GLOBAL VARIABLES
REFRESH_TOKEN= ''
DEV_TOKEN = "GcDK9FKHuyJgy1MvPDJRtKDylT2z0M2Z"
TIME_TO_REFRESH = 50*60


def find_collabs(work_type,client, log_file,collab_file,path,parent_folder_id, folder_id, folder_name):
    
    #find parent collaborators:
    parent_collab_ids =[]
    if parent_folder_id is not None:
        parent_collaborations = client.folder(folder_id=parent_folder_id).get_collaborations()
        parent_collab_ids = [c.accessible_by.id for c in parent_collaborations if c is not None]

    #Find Item collaborators
    collaborations = client.folder(folder_id=folder_id).get_collaborations()
    folder = client.folder(folder_id=folder_id).get()
    owner = getattr(folder.created_by, "name", None) 
            
    for collab in collaborations:
        user = collab.accessible_by
        access_given_by = getattr(collab.created_by, "name", None) 
        if (user is not None and user.id not in parent_collab_ids):
            user_login = getattr(user, "login", None) 
            print(f'    >> Found collab:\n')
            print(f'            >[{work_type}],{user.type.capitalize()},{user.id},{user.name},{user_login},{folder_id},{folder_name},{owner},{access_given_by},{path},{collab.id}\n')
            log_file.write(f'       >>[{work_type}],{user.type.capitalize()},{user.id},{user.name},{user_login},{folder_id},{folder_name},{owner},{access_given_by},{path},{collab.id}\n')
            collab_file.write(f'[{work_type}],{user.type.capitalize()},{user.id},{user.name},{user_login},{folder_id},{folder_name},{owner},{access_given_by},{path},{collab.id}\n')



def find_items(work_type,client, log_file, folder_id):

    items = client.folder(folder_id=folder_id).get_items(sort="size", direction="DESC")
    return items


def start_connection(access_token, refresh_token):
    REFRESH_TOKEN = refresh_token

    print("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=access_token)
    client = Client(auth)
    print(f'box connection made: {client}\n')
    return client

def open_files(client, folder_id):
    
    print(">>Get Folder name to name the files API call get().name\n")
    folder_name = client.folder(folder_id=folder_id).get().name
    
    #Open Files to log
    date= datetime.now()
    date =str(date).replace(" ","_")
    date =str(date).replace(":","_")

    log_file_name= f'result/collab/log_{folder_name}_{folder_id}_{date}.txt'
    collab_file_name= f'result/collab/collab_{folder_name}_{folder_id}_{date}.csv'

    #Empty Files
    open(log_file_name,"w").close()
    open(collab_file_name,"w").close()

    #open for appending
    log_file=open(log_file_name, "a", encoding="utf-8") 
    collab_file=open(collab_file_name, "a", encoding="utf-8") 
    
    collab_file.write("work_type,user,user_id,name,email,folder_id,folder_name,folder_owner,access_given_by,collab_id\n")
    return log_file, collab_file, log_file_name, collab_file_name


def main(access_token, refresh_token,folder_id, exclude_folder_ids):
    #start connection
    client = start_connection(access_token,refresh_token)
    #start timer
    start= time.time()
    #open files
    files = open_files(client, folder_id)
    log_file = files[0]
    collab_file=files[1]
    log_file_name = files[2]
    collab_file_name = files[3]

    #Find parent folder collabs

    folder_stack = []
    folder_stack.append((folder_id,None,[]))
    print(f"started folder look up:{folder_id}\n")
    log_file.write(f"started folder look up:{folder_id}\n")
    while len(folder_stack) !=0:    
        #Check time to refresh token

        end = time.time()
        print(f'{end}- {start} = {end-start}')
        if (end -start) >= TIME_TO_REFRESH:
            print(f"time limit meet. refreshing token {start}\n")
            start = time.time()
            _, refresh_token= api_connect.refresh_token(refresh_token)
            print(f"finished refreshing token sleeping 5 secs before restarting. start: {start}\n")
            time.sleep(5)
        
        working_folder = folder_stack.pop()
        working_folder_name = client.folder(folder_id=working_folder[0]).get().name

        print(f'Folder: {working_folder[0]} {working_folder_name}. Level: {len(working_folder[2])}\n  Path: {working_folder[2]}\n')
        log_file.write(f'Folder: {working_folder[0]} {working_folder_name}. Level: {len(working_folder[2])}\n  Path: {working_folder[2]}\n')        
        
        #find collabs of working folder:
        print(f'    Collaborators: \n')
        log_file.write(f'   Collaborators: \n')
        find_collabs("stack_loop", client, log_file, collab_file,working_folder[2],working_folder[1], working_folder[0],working_folder_name)

        print(f'    Items: \n')
        log_file.write(f'   Items: \n')


        #find items under working folder        
        items = find_items("stack_loop", client, log_file, working_folder[0])
        
        #Exclude folders:
        for item in items:
            type = item.type.capitalize()
            if (type=="Folder") and item.id not in exclude_folder_ids.split(","):
                print(f'    **Item {item.id} {item.name} level: {len(working_folder[2])+1}\n')
                log_file.write(f'    **Item {item.id} {item.name}  level: {len(working_folder[2])+1}\n')
                new_path = [(working_folder[0],working_folder_name)]
                new_path.extend(working_folder[2])
                folder_stack.append((item.id,working_folder[0],new_path))

        log_file.flush()
        collab_file.flush()
    results_box_folder_id=317785398433

    
    new_collab_file = client.folder(folder_id =results_box_folder_id).upload(collab_file_name)
    new_log_file = client.folder(folder_id =results_box_folder_id).upload(log_file_name)

    print(f'File "{new_collab_file.name}" uploaded to Box with file ID {new_collab_file.id}')
    print(f'File "{new_log_file.name}" uploaded to Box with file ID {new_log_file.id}')

    log_file.close()
    collab_file.close()


# Uncaomment to Test Local
# main(DEV_TOKEN,"qojxwOZXo18YQybg1EmWWPX1lRlLHPUM","47831431907")
