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




    def look_into_folders(client,refresh_token,file,collab_file, parent_folder, folder , collaborators,start):
    end = time.time()
    print(f'{end}- {start} = {end-start}')
    if (end -start) >= TIME_TO_REFRESH:
        ACCESS_TOKEN, refresh_token= api_connect.refresh_token(refresh_token)

    thread_name = threading.current_thread().name

    folder_id = getattr(folder, "id", None) 
    #Find the Collabs of current folder
    for item in find_items(thread_name, client,file, folder_id):
        type = item.type.capitalize()
        if (folder_id is not None and type=="Folder"):
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
    """
