from boxsdk import Client, OAuth2, BoxAPIException
import time
import threading
import api_connect
import json
#GLOBAL VARIABLES
ACCESS_TOKEN = ''
REFRESH_TOKEN= ''
DEV_TOKEN = "5183QNqjzhEaOdwGoGq4IKZiQCq5mYAd"
token_url = "https://api.box.com/oauth2/token"
USE_TOKEN = ACCESS_TOKEN
TIME_TO_REFRESH = 50*60

lock = threading.Lock()
thread_base= 1

def find_collabs(thread_name,client, file,collab_file,parent_folder_id, folder_id, folder_name):

    parent_collab_ids =[]
    print(f'[{thread_name}] API call get_collaborations\n')
    file.write(f'[{thread_name}] API call get_collaborations\n')
    collaborations = client.folder(folder_id=folder_id).get_collaborations()
    if parent_folder_id is not None:
        parent_collaborations = client.folder(folder_id=parent_folder_id).get_collaborations()
        parent_collab_ids = [c.accessible_by.id for c in parent_collaborations]

    file.write(f'[{thread_name}]API call get_collaborations result: {collaborations}\n')
    print(f'[{thread_name}] API call get_collaborations result: {collaborations}\n')

    for collab in collaborations:
        user = collab.accessible_by
        if (user.id not in parent_collab_ids):
        # if(user.name not in collaborators):
            # collaborators.append(user.name)
            user_login = getattr(user, "login", None) 

            print(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{folder_id},{folder_name},{collab.id}\n')
            file.write(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{folder_id},{folder_name},{collab.id}\n')
            collab_file.write(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{folder_id},{folder_name},{collab.id}\n')

def find_items(thread_name,client, file, folder_id):

    print(f'[{thread_name}] API call get_items\n')
    file.write(f'[{thread_name}] API call get_items\n')
    items = client.folder(folder_id=folder_id).get_items(sort="size", direction="DESC")
    print(f'[{thread_name}] API call get_items result: {items}\n')
    file.write(f'[{thread_name}]API call get_items result: {items}\n')
    return items

def look_into_folders(client,refresh_token,file,collab_file, parent_folder, folder , collaborators,start):
    end = time.time()
    print(f'{end}- {start} = {end-start}')
    if (end -start) >= TIME_TO_REFRESH:
        ACCESS_TOKEN, refresh_token= api_connect.refresh_token(refresh_token)
    thread_name = threading.current_thread().name
    # log = f'[{thread_name}] started folder look up for folder: {folder.name} - {folder.id}\n'
    # file.write(log)
    # print(log)
    folder_id = getattr(folder, "id", None) 
    #Find the Collabs of current folder
    for item in find_items(thread_name, client,file, folder_id):
        type = item.type.capitalize()
        if (type=="Folder"):
            print(f'[{thread_name}]  >>Parent {folder_id} - Child: {item.type.capitalize()} {item.id} -> {item.name}\n')
            file.write(f'[{thread_name}]  >>Parent {folder_id} - Child: {item.type.capitalize()} {item.id} -> {item.name}\n')
            find_collabs(thread_name, client, file, collab_file, folder_id,item.id,item.name, collaborators)
    #Flush current collabs found
    collab_file.flush()
    file.flush()
    #Recursive call look_into_folders from all the folders
    for item in find_items(thread_name, client,file, folder_id):
        type = item.type.capitalize()
        if (type=="Folder"):
            look_into_folders(client,refresh_token,file, collab_file,folder,item, collaborators,start)

def main(access_token, refresh_token,folder_id,thread_base):
    thread_base = thread_base

    ACCESS_TOKEN = access_token
    USE_TOKEN = ACCESS_TOKEN
    REFRESH_TOKEN=refresh_token

    print("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=USE_TOKEN)
    client = Client(auth)
    start= time.time()

    print("[{main_thread_name}] API call get().name\n")
    folder_name = client.folder(folder_id=folder_id).get().name
    
    #Open Files to log
    log_file_name= f'result/collab/log_{folder_name}_{folder_id}.txt'
    collab_file_name= f'result/collab/collab_{folder_name}_{folder_id}.csv'

    #Empty Files
    open(log_file_name,"w").close()
    open(collab_file_name,"w").close()

    #open for appending
    file=open(log_file_name, "a", encoding="utf-8") 
    collab_file=open(collab_file_name, "a", encoding="utf-8") 
    collab_file.write("thread,user,user_id,name,email,folder_id,folder_name,collab_id\n")

    
    print(f'box connection made: {client}\n')
    file.write(f'box connection made: {client}\n\n')

    collaborators = []
    print(f"started folder look up:{folder_id}\n")
    file.write(f"started folder look up:{folder_id}\n")


    folder = client.folder(folder_id=folder_id).get()
    #Find parent folder collabs
    find_collabs("thread_name", client, file, collab_file, None, folder_id, folder_name)
    #Try with stack instead of Recursive
    folder_stack = []
    folder_stack.append((folder_id,None))
    while len(folder_stack) !=0:
        #Check time to refresh token
        end = time.time()
        print(f'{end}- {start} = {end-start}')
        if (end -start) >= TIME_TO_REFRESH:
            start = time.time()
            ACCESS_TOKEN, refresh_token= api_connect.refresh_token(refresh_token)
            print(f"finished refreshing token sleeping 5 secs start: {start}\n")
            time.sleep(5)
        working_folder = folder_stack.pop()
        working_folder_name = client.folder(folder_id=working_folder[0]).get().name
        find_collabs("stack_loop", client, file, collab_file,working_folder[1], working_folder[0],working_folder_name)

        items = find_items("stack_loop", client,file, working_folder[0])
        # sorted_items = sorted(items, key=lambda x: x.size)  # Sort by name, case-insensitive

        for item in items:
            type = item.type.capitalize()
            if (type=="Folder"):
                folder_stack.append((item.id,working_folder[0]))
        file.flush()
        collab_file.flush()
        
        # folder_ids = [i for i in list(folders)]
    # look_into_folders(client,refresh_token,file,collab_file,None,folder,collaborators, start)
    file.close()
    collab_file.close()


    #Thead code
    """
    # #Create collaborators list to track who's been added
    # collaborators = []
    # print(f"[{main_thread_name}] API call get_collaborations\n")
    # file.write(f"[{main_thread_name}] API call get_collaborations\n")
    # collaborations = client.folder(folder_id=ROOT_FOLDER_ID).get_collaborations()
    # print(f"[{main_thread_name}] API call get_collaborations result:{collaborations}\n")
    # file.write(f"[{main_thread_name}] API call get_collaborations result:{collaborations}\n") 
    # for collab in collaborations:
    #     user = collab.accessible_by
        
    #     if(user.name not in collaborators):
    #         collaborators.append(user.name)
    #         print("[{main_thread_name}] API call get().name\n")
    #         file.write("[{main_thread_name}] API call get().name\n")  
    #         folder_name = client.folder(folder_id=ROOT_FOLDER_ID).get().name
    #         print(f"[{main_thread_name}] API call get().name result: {folder_name}\n")
    #         file.write(f"[{main_thread_name}] API call get().name result: {folder_name}\n")

    #         user_login = getattr(user, "login", None) 
    #         print(f'[{main_thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
    #         collab_file.write(f'[{main_thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
    #         file.write(f'[{main_thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            

    # #keep track of threads
    # threads =[]
    # print("[Thread-Main] API call get_items\n")
    # file.write("[Thread-Main] API call get_items\n")
    # items = client.folder(folder_id=ROOT_FOLDER_ID).get_items()
   
    # print(f"[Thread-Main] API call get_items result:{items}\n")
    # file.write(f"[Thread-Main] API call get_items result:{items}\n") 
    # file.flush()
    # collab_file.flush()
    # for item in items:
    #     if(item.type =="folder"):
    #         if thread_base==1:
    #             #Create thread
    #             thread = threading.Thread(target=look_into_folders,args=(client,file,collab_file,item.id,collaborators))
    #             file.write(f'[{thread.name}] Started\n')  # Separate old and new entries
    #             print(f'[{thread.name}] Started\n')
    #             file.write(f'{item.type.capitalize()} {item.id}: {item.name}\n')
    #             print(f'{item.type.capitalize()} {item.id}: {item.name}\n')
    #             #Add to threads 
    #             threads.append(thread)
    #             #Start Thread
    #             thread.start()
    #         else:
    #             look_into_folders(client,file,collab_file,item.id,collaborators)

    # #Join threads
    # for thread in threads:
    #     print(f'[{thread.name}] - Joining Thread\n')
    #     file.write(f'[{thread.name}] - Joining Thread\n')
    #     thread.join()"
    """
#Uncaomment to Test Local
# main(DEV_TOKEN,"qojxwOZXo18YQybg1EmWWPX1lRlLHPUM","47596547829",0)
