from boxsdk import Client, OAuth2, BoxAPIException
import threading
import api_connect
#GLOBAL VARIABLES
ROOT_FOLDER_ID = '49834143891'
ACCESS_TOKEN = ''
REFRESH_TOKEN= ''
DEV_TOKEN = "RWDCrLKnpnpewYslUrXK1bft3qqxv3Ph"
token_url = "https://api.box.com/oauth2/token"
USE_TOKEN = ACCESS_TOKEN

lock = threading.Lock()
thread_base= 1


def find_folder(client,file,collab_file, folder_id, collaborators):
    thread_name = threading.current_thread().name
    look_into_folders(client,file,collab_file, folder_id, collaborators)
    print(f"[{thread_name}] Finished running\n")
    file.write(f"[{thread_name}] Finished running\n")

def look_into_folders(client,file,collab_file, folder_id, collaborators):
    thread_name = threading.current_thread().name
    try:
        log = f'[{thread_name}] started folder look up for folder: {client.folder(folder_id=folder_id).get().name} - {folder_id}\n'
    except BoxAPIException as e:
        api_connect.handle_box_exception(file,e)
    file.write(log)
    print(log)
    with lock:
        print(f'[{thread_name}] API call get_items\n')
        file.write(f'[{thread_name}] API call get_items\n')
        try:
            items = client.folder(folder_id=folder_id).get_items()
        except BoxAPIException as e:
            print(f'[{thread_name}] ERROR - Exception was thrown. Ready to handle: {e}\n')
            file.write(f'[{thread_name}] ERROR - Exception was thrown. Ready to handle: {e}\n')
            api_connect.handle_box_exception(file,e)
            print(f'[{thread_name}] ERROR - Exception was thrown. Finished handling: {e}\n')
            file.write(f'[{thread_name}] ERROR - Exception was thrown. Finished handling: {e}\n')
        print(f'[{thread_name}] API call get_items result: {items}\n')
        file.write(f'[{thread_name}]API call get_items result: {items}\n')

    for item in items:
        type = item.type.capitalize()
        if (type=="Folder"):

            print(f'[{thread_name}]  >>Parent {folder_id} - Child: {item.type.capitalize()} {item.id} -> {item.name}\n')
            file.write(f'[{thread_name}]  >>Parent {folder_id} - Child: {item.type.capitalize()} {item.id} -> {item.name}\n')
            with lock:
                print(f'[{thread_name}] API call get_collaborations\n')
                file.write(f'[{thread_name}] API call get_collaborations\n')
                try:
                    collaborations = client.folder(folder_id=folder_id).get_collaborations()
                except BoxAPIException as e:
                    print(f'[{thread_name}] ERROR - Exception was thrown. Ready to handle: {e}\n')
                    file.write(f'[{thread_name}] ERROR - Exception was thrown. Ready to handle: {e}\n')
                    api_connect.handle_box_exception(file,e)
                    print(f'[{thread_name}] ERROR - Exception was thrown. Finished handling: {e}\n')
                    file.write(f'[{thread_name}] ERROR - Exception was thrown. Finished handling: {e}\n')                
                file.write(f'[{thread_name}]API call get_collaborations result: {collaborations}\n')
                print(f'[{thread_name}] API call get_collaborations result: {collaborations}\n')
                

            for collab in collaborations:
                user = collab.accessible_by
                if(user.name not in collaborators):
                    with lock:
                        collaborators.append(user.name)
                        user_login = getattr(user, "login", None) 

                        print(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{item.id},{item.name},{collab.id}\n')
                        file.write(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{item.id},{item.name},{collab.id}\n')
                        collab_file.write(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{item.id},{item.name},{collab.id}\n')
            with lock:
                print(f'[{thread_name}] Flushing write to files\n')
                file.write(f'[{thread_name}] Flusing write to flies\n')
                collab_file.flush()
                file.flush()
    with lock:
        #Get Items
        print(f'[{thread_name}] API call get_items (2)\n')
        file.write(f'[{thread_name}] API call get_items (2)\n')
        items = client.folder(folder_id=folder_id).get_items()
        print(f'[{thread_name}] API call get_items (2) result: {items}\n')
        file.write(f'[{thread_name}] API call get_items (2) result: {items}\n')

    #Recursive call look_into_folders from all the folders
    for item in items:
        type = item.type.capitalize()
        if (type=="Folder"):
            look_into_folders(client,file, collab_file,item.id, collaborators)

def main(access_token, folder_id,thread_base):
    thread_base = thread_base

    main_thread_name = 'Thread-Main'

    ACCESS_TOKEN = access_token
    USE_TOKEN = ACCESS_TOKEN

    ROOT_FOLDER_ID = folder_id

    print("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=USE_TOKEN)
    client = Client(auth)
    print("[{main_thread_name}] API call get().name\n")
    try:
        folder_name = client.folder(folder_id=ROOT_FOLDER_ID).get().name
    except BoxAPIException as e:
        print(f'[{main_thread_name}] ERROR - Exception was thrown. Ready to handle: {e}\n')
        api_connect.handle_box_exception(2,e)
        print(f'[{main_thread_name}] ERROR - Exception was thrown. Finished handling: {e}\n')

    #Open Files to log
    log_file_name= f'result/log_{folder_name}_{ROOT_FOLDER_ID}.txt'
    collab_file_name= f'result/collab_{folder_name}_{ROOT_FOLDER_ID}.csv'

    #Empty Files
    open(log_file_name,"w").close()
    open(collab_file_name,"w").close()

    #open for appending
    file=open(log_file_name, "a", encoding="utf-8") 
    collab_file=open(collab_file_name, "a", encoding="utf-8") 
    collab_file.write("thread,user,user_id,name,email,folder_id,folder_name,collab_id\n")

    
    print(f'box connection made: {client}\n')
    file.write(f'box connection made: {client}\n\n')

    
    print(f"started folder look up:{ROOT_FOLDER_ID}\n")
    file.write(f"started folder look up:{ROOT_FOLDER_ID}\n")
    
    #Create collaborators list to track who's been added
    collaborators = []
    print(f"[{main_thread_name}] API call get_collaborations\n")
    file.write(f"[{main_thread_name}] API call get_collaborations\n")
    collaborations = client.folder(folder_id=ROOT_FOLDER_ID).get_collaborations()
    print(f"[{main_thread_name}] API call get_collaborations result:{collaborations}\n")
    file.write(f"[{main_thread_name}] API call get_collaborations result:{collaborations}\n") 
    for collab in collaborations:
        user = collab.accessible_by
        
        if(user.name not in collaborators):
            collaborators.append(user.name)
            print("[{main_thread_name}] API call get().name\n")
            file.write("[{main_thread_name}] API call get().name\n")  
            folder_name = client.folder(folder_id=ROOT_FOLDER_ID).get().name
            print(f"[{main_thread_name}] API call get().name result: {folder_name}\n")
            file.write(f"[{main_thread_name}] API call get().name result: {folder_name}\n")

            user_login = getattr(user, "login", None) 
            print(f'[{main_thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            collab_file.write(f'[{main_thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            file.write(f'[{main_thread_name}],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            

    #keep track of threads
    threads =[]
    print("[Thread-Main] API call get_items\n")
    file.write("[Thread-Main] API call get_items\n")
    items = client.folder(folder_id=ROOT_FOLDER_ID).get_items()
   
    print(f"[Thread-Main] API call get_items result:{items}\n")
    file.write(f"[Thread-Main] API call get_items result:{items}\n") 
    file.flush()
    collab_file.flush()
    for item in items:
        if(item.type =="folder"):
            if thread_base==1:
                #Create thread
                thread = threading.Thread(target=find_folder,args=(client,file,collab_file,item.id,collaborators))
                file.write(f'[{thread.name}] Started\n')  # Separate old and new entries
                print(f'[{thread.name}] Started\n')
                file.write(f'{item.type.capitalize()} {item.id}: {item.name}\n')
                print(f'{item.type.capitalize()} {item.id}: {item.name}\n')
                #Add to threads 
                threads.append(thread)
                #Start Thread
                thread.start()
            else:
                find_folder(client,file,collab_file,item.id,collaborators)

    #Join threads
    for thread in threads:
        print(f'[{thread.name}] - Joining Thread\n')
        file.write(f'[{thread.name}] - Joining Thread\n')
        thread.join()
    file.close()
    collab_file.close()

