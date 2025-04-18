from boxsdk import Client, OAuth2, BoxAPIException
import threading
import api_connect
#GLOBAL VARIABLES
ACCESS_TOKEN = ''
REFRESH_TOKEN= ''
DEV_TOKEN = "r1WKmG7Pdt8iRhZF9s3W0PCJ78JcXJWl"
token_url = "https://api.box.com/oauth2/token"
USE_TOKEN = ACCESS_TOKEN

lock = threading.Lock()


def look_into_folders(client,file,removed_from, user_id,folder_id):

    log = f'[{work_type}] started folder look up for folder: {client.folder(folder_id=folder_id).get().name} - {folder_id}\n'
    file.write(log)
    print(log)

    print(f"[{work_type}] API call get_collaborations\n")
    file.write(f"[{work_type}] API call get_collaborations\n")

    collaborations = client.folder(folder_id = folder_id).get_collaborations()

    print(f"[{work_type}] API call get_collaborations result:{collaborations}\n")
    file.write(f"[{work_type}] API call get_collaborations result:{collaborations}\n") 
    
    collabs = [c.id for c in collaborations if c.accessible_by.id == user_id]

    print(f'collabs: {collabs}')
    file.write(f'collabs: {collabs}')
    for collab in collabs:
        print(f'deleting collab: {collab}')
        file.write(f'deleting collab: {collab}')
        client.collaboration(collab).delete()
            
    
    print(f'[{work_type}] API call get_items\n')
    file.write(f'[{work_type}] API call get_items\n')
    
    items = client.folder(folder_id=folder_id).get_items()

    print(f'[{work_type}] API call get_items result: {items}\n')
    file.write(f'[{work_type}]API call get_items result: {items}\n')

    #Recursive call look_into_folders from all the folders
    for item in items:
        type = item.type.capitalize()
        if (type=="Folder"):
            look_into_folders(client,file, removed_from,user_id, item.id)

def main(access_token,user_id, folder_id):

    ACCESS_TOKEN = access_token
    USE_TOKEN = ACCESS_TOKEN


    print("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=USE_TOKEN)
    client = Client(auth)
    print("[] API call get().name from user{user_id}\n")
    

    folder_name = client.folder(folder_id=folder_id).get().name
    user_name = "test"
    #Open Files to log
    log_file_name= f'result/remove/log_del_u_{user_id}_f{folder_id}.txt'
    removed_from_name= f'result/remove/del_u_{user_id}_f_{folder_id}.csv'

    #Empty Files
    open(log_file_name,"w").close()
    open(removed_from_name,"w").close()

    #open for appending
    file=open(log_file_name, "a", encoding="utf-8") 
    removed_from =open(removed_from_name, "a", encoding="utf-8") 
    removed_from.write("thread,user,user_id,name,email,folder_id,folder_name,collab_id\n")

    
    print(f'box connection made: {client}\n')
    file.write(f'box connection made: {client}\n\n')

    
    print(f"started folder look up:{folder_id}\n")
    file.write(f"started folder look up:{folder_id}\n")
    
    #Make recursive call
    look_into_folders("[stack loop]",client,file,removed_from,user_id,folder_id)

    file.close()
    removed_from.close()


#local test
# main(DEV_TOKEN, "23663698729","314801509226",0)