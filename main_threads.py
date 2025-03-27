from boxsdk import Client, OAuth2
import threading

#GLOBAL VARIABLES
ROOT_FOLDER_ID = '47831431907'
DEV_TOKEN = "2IUdzrstSDBSlxVHf3T3nVyCjI5OTbhf"


lock = threading.Lock()

def find_folder(client,file,collab_file, folder_id, collaborators):
    look_into_folders(client,file,collab_file, folder_id, collaborators)

def look_into_folders(client,file,collab_file, folder_id, collaborators):
    thread_name = threading.current_thread().name
    log = f'[{thread_name}] started folder look up for folder: {client.folder(folder_id=folder_id).get().name} - {folder_id}\n'
    file.write(log)
    print(log)
    with lock:
        print(f'[{thread_name}] API call get_items\n')
        file.write(f'[{thread_name}] API call get_items\n')

        items = client.folder(folder_id=folder_id).get_items()
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
                collaborations = client.folder(folder_id=folder_id).get_collaborations()
                print(f'[{thread_name}] API call get_collaborations result: {collaborations}\n')
                file.write(f'[{thread_name}]API call get_collaborations result: {collaborations}\n')

            for collab in collaborations:
                user = collab.accessible_by
                if(user.name not in collaborators):
                    with lock:
                        collaborators.append(user.name)
                        print(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user.login},{item.id},{item.name},{collab.id}\n')
                        file.write(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user.login},{item.name},{item.name},{collab.id}\n')
                        collab_file.write(f'[{thread_name}],{user.type.capitalize()},{user.id},{user.name},{user.login},{item.name},{item.name},{collab.id}\n')
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
        file.write(f'[{thread_name}]API call get_items (2) result: {items}\n')

    #Recursive call look_into_folders from all the folders
    for item in items:
        type = item.type.capitalize()
        if (type=="Folder"):
            look_into_folders(client,file, collab_file,item.id, collaborators)

def main():

    #Open Files to log
    log_file_name= f'result/box_items_thread_{ROOT_FOLDER_ID}.txt'
    collab_file_name= f'result/collab_thread_{ROOT_FOLDER_ID}.txt'

    #Empty Files
    open(log_file_name,"w").close()
    open(collab_file_name,"w").close()

    #open for appending
    file=open(log_file_name, "a", encoding="utf-8") 
    collab_file=open(collab_file_name, "a", encoding="utf-8") 


    print("started box connection\n")
    file.write("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=DEV_TOKEN)
    client = Client(auth)
    print(f'box connection made: {client}\n')
    file.write(f'box connection made: {client}\n\n')

    
    print(f"started folder look up:{ROOT_FOLDER_ID}\n")
    file.write(f"started folder look up:{ROOT_FOLDER_ID}\n")
    
    #Create collaborators list to track who's been added
    collaborators = []

    print("[Thread-Main] API call get_collaborations\n")
    file.write("[Thread-Main] API call get_collaborations\n")   
    collaborations = client.folder(folder_id=ROOT_FOLDER_ID).get_collaborations()
    print(f"[Thread-Main] API call get_collaborations result:{collaborations}\n")
    file.write(f"[Thread-Main] API call get_collaborations result:{collaborations}\n") 
    for collab in collaborations:
        user = collab.accessible_by
        
        if(user.name not in collaborators):
            collaborators.append(user.name)
            print("[Thread-Main] API call get().name\n")
            file.write("[Thread-Main] API call get().name\n")  
            folder_name = client.folder(folder_id=ROOT_FOLDER_ID).get().name
            print(f"[Thread-Main] API call get().name result: {folder_name}\n")
            file.write(f"[Thread-Main] API call get().name result: {folder_name}\n")

            user_login = getattr(user, "login", None) 
            print(f'[Thread-Main],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            collab_file.write(f'[Thread-Main],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            file.write(f'[Thread-Main],{user.type.capitalize()},{user.id},{user.name},{user_login},{ROOT_FOLDER_ID},{folder_name},{collab.id}\n')
            

    #keep track of threads
    threads =[]
    print("[Thread-Main] API call get_items\n")
    file.write("[Thread-Main] API call get_items\n")   
    items = client.folder(folder_id=ROOT_FOLDER_ID).get_items()
    print(f"[Thread-Main] API call get_items result:{items}\n")
    file.write(f"[Thread-Main] API call get_items result:{items}\n") 

    for item in items:
        if(item.type =="folder"):
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

    #Join threads
    for thread in threads:
        print(f'[{thread.name}] - Joining Thread\n')
        file.write(f'[{thread.name}] - Joining Thread\n')
        thread.join()
    file.close()

main()