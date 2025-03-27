from boxsdk import Client, OAuth2

def look_into_folders(client,file,collab_file, folder_id, collaborators):
    items = client.folder(folder_id=folder_id).get_items()
    # list_items = list(items)
    file.write(f'started file look up for file: {folder_id}')
    # items_len = len(list(items))
    # print(f'items list: {list_items}')
    print(f'{client.folder(folder_id=folder_id).get().name}')
    file.write(f'{client.folder(folder_id=folder_id).get().name}\n')
    for item in items:
        type = item.type.capitalize()
        collaborations = client.folder(folder_id=folder_id).get_collaborations()
        #collaborations
        colabs_total =len(list(collaborations))
        if (type=="Folder" and colabs_total>17):
            print(f'>>{item.type.capitalize()} {item.id} is named "{item.name}\n')
            file.write(f'>>{item.type.capitalize()} {item.id} is named "{item.name}\n')
        
            # print(f'folder collaborations: {collaborations}\n')
            # print(f'****total colabs>17 ={colabs_total}\n')
            # file.write(f'****total colabs> 17 ={colabs_total}\n')
            collaborations = client.folder(folder_id=item.id).get_collaborations()
            for collab in collaborations:
                target = collab.accessible_by
                
                if(target.name not in collaborators):
                    collaborators.append(target.name)
                    print(f'****{target.type.capitalize()} {target.name} is collaborated on the folder {item.name}')
                    collab_file.write(f'****{target.type.capitalize()} {target.name} is collaborated on the folder  {item.name}\n\n')

        

    items = client.folder(folder_id=folder_id).get_items()
    for item in items:
        type = item.type.capitalize()
        if (type=="Folder"):
            look_into_folders(client,file, collab_file,item.id, collaborators)
   # look_into_folders(client,item.id)
        # else:
        #     file.write(f'{item.type.capitalize()} {item.id} is named "{item.name}"')




def main():
    
    print("started box connection")
    #Create Connection
    DEV_TOKEN = "QuJc2RjjNPsye7rz23TI1csKke1fsC0f"
    auth = OAuth2(client_id=None, client_secret=None, access_token=DEV_TOKEN)

    client = Client(auth)
    print(f'box connection made: {client}')

    #Get items in folder
    items = client.folder(folder_id='47596547829').get_items()
    item_ids= [item.id for item in items]
    print(item_ids)
    print("started file look up:")
    open("box_items_1.txt","w").close()
    open("colab_1.txt","w").close()
    with open("box_items_1.txt", "a", encoding="utf-8") as file:  # 'a' for append
        collaborators = []
        colab_file=open("colab_1.txt", "a", encoding="utf-8") 
        collaborations = client.folder(folder_id=item_ids[1]).get_collaborations()
        for collab in collaborations:
            target = collab.accessible_by
            
            if(target.name not in collaborators):
                collaborators.append(target.name)
                folder_name = client.folder(folder_id=item_ids[1]).get().name
                print(f'****{target.type.capitalize()} {target.name} is collaborated on the folder {folder_name}')
                colab_file.write(f'****{target.type.capitalize()} {target.name} is collaborated on the folder  {folder_name}\n\n')
        file.write("\n--- New Run ---\n")  # Separate old and new entries
        look_into_folders(client,file,colab_file,item_ids[1],collaborators)
    # for item in items:

    #     print(f'{item.type.capitalize()} {item.id} is named "{item.name}"')


    #Get collaborations
    # collaborations = client.folder(folder_id='47596547829').get_collaborations()
    # print(f'folder collaborations: {collaborations}')

    # for collab in collaborations:
    #     target = collab.accessible_by
    #     print(f'{target.type.capitalize()} {target.name} is collaborated on the folder')

    #Write into file
main()