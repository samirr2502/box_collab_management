#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <curl/curl.h>
#include <json-c/json.h>
#include <semaphore.h>


#define ACCESS_TOKEN "VhZe58IrpOkU9q8lQJu2hzifmOZ8y7yO"
#define MAX_COLLABORATORS 100  // Adjust as needed

typedef struct {
    char folder_id[50];
    int level_counter;
    int level_depth;
    FILE file;
    int num_collaborators;
    char* collaborators[MAX_COLLABORATORS * sizeof(char*)];

} ThreadArgs;

struct MemoryStruct {
    char *memory;
    size_t size;
};
int verbose =0;
pthread_mutex_t file_mutex;
pthread_mutex_t collab_mutex;

size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)userp;

    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if (ptr == NULL) return 0;

    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
}

char *make_api_request(const char *url) {
    CURL *curl;
    CURLcode res;
    struct MemoryStruct chunk;
    chunk.memory = malloc(1);
    chunk.size = 0;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if (!curl) return NULL;

    struct curl_slist *headers = NULL;
    char auth_header[256];
    snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", ACCESS_TOKEN);
    headers = curl_slist_append(headers, auth_header);
    headers = curl_slist_append(headers, "Accept: application/json");

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    res = curl_easy_perform(curl);

    curl_easy_cleanup(curl);
    curl_slist_free_all(headers);
    curl_global_cleanup();

    if (res != CURLE_OK) {
        free(chunk.memory);
        return NULL;
    }

    return chunk.memory;
}
int is_name_in_list(char** collaborators, const char* name, int num_collaborators) {
    printf("name %s\n", name);

    for (int i = 0; i < num_collaborators; i++) {
        printf("collab #%d of %d %s\n", i, num_collaborators,collaborators[i]);

        if (strcmp(collaborators[i], name) == 0) {
            return 1; //in list
        }
    }

    return 0; //not it list
}

void get_collabs(void *arg) {
    char url[256];
    ThreadArgs *args = (ThreadArgs *)arg;

    snprintf(url, sizeof(url), "https://api.box.com/2.0/folders/%s/collaborations", args->folder_id);
    char *response = make_api_request(url);
    
    // if (response) {
    //     // printf("Collaborators for folder %s: %s\n", folder_id, response);
    //     free(response);
    // }
    struct json_object *parsed_json = json_tokener_parse(response);
    struct json_object *entries;
    if (json_object_object_get_ex(parsed_json, "entries", &entries)) {
        int array_len = json_object_array_length(entries);
        pthread_mutex_lock(&collab_mutex);

       for (int i = 0; i < array_len; i++) {
            
            struct json_object *item = json_object_array_get_idx(entries, i);
            struct json_object *user, *role, *given_by, *date, *item_type;
            struct json_object *name, *given_by_name, *item_name;
            json_object_object_get_ex(item, "accessible_by", &user);
            json_object_object_get_ex(user, "name", &name);
            json_object_object_get_ex(item, "item", &item_type);
            json_object_object_get_ex(item_type, "name", &item_name);
        
            //name check

            const char* name_ = json_object_get_string(name);
            
           int already_added= is_name_in_list(args->collaborators, name_, args->num_collaborators);
           printf("added: %d\n",already_added);
            
            json_object_object_get_ex(item, "role", &role);
            json_object_object_get_ex(item, "created_by", &given_by);
            json_object_object_get_ex(given_by, "name", &given_by_name);
            json_object_object_get_ex(item, "modified_at", &date); 

            const char* item_name_ = json_object_get_string(item_name);
            const char* role_ = json_object_get_string(role);
            const char* given_by_name_ = json_object_get_string(given_by_name);
            const char* date_ = json_object_get_string(date);
            if(verbose){
                // Write to file safely
                printf("Collaborator: %s\nof file: %s\n\n", name_,item_name_);
            }
            if (already_added==0) {
                pthread_mutex_lock(&file_mutex);

                args->collaborators[args->num_collaborators] = strdup(name_);
                args->num_collaborators++;
                if(verbose){
                    printf("writing to file: %ld\n", args->file);
                }
                FILE *file = fopen("collabs/collaborators.txt", "a");  // Open in append mode

                fprintf(file, "folder: %s\nname: %s\nrole: %s\ngiven by: %s\non: %s\n\n", item_name_, name_, role_, given_by_name_, date_);               
                fclose(file);
                pthread_mutex_unlock(&file_mutex);

            } else {
                continue;
            }
            
        }
        pthread_mutex_unlock(&collab_mutex);

       /*
        char url_2[256];
        snprintf(url_2, sizeof(url_2), "https://api.box.com/2.0/folders/%s/items", args->folder_id);
        char *local_response = make_api_request(url_2);
        struct json_object *parsed_json = json_tokener_parse(local_response);
        struct json_object *entries;
        ThreadArgs thread_args[array_len];

        if (json_object_object_get_ex(parsed_json, "entries", &entries)) {

            for (int i=0; i< array_len; i++){
                struct json_object *item = json_object_array_get_idx(entries, i);
                struct json_object *type, *id;

                json_object_object_get_ex(item, "type", &type);
                json_object_object_get_ex(item, "id", &id);
                
                if (strcmp(json_object_get_string(type), "folder") == 0) {
                    snprintf(thread_args[i].folder_id, sizeof(thread_args[i].folder_id), "%s", json_object_get_string(id));
                    thread_args[i].level_counter = args->level_counter + 1;
                    thread_args[i].level_depth = args->level_depth;
                    get_collabs(&thread_args[i]);
                }
            }
                
        
    }
            //*/
            
    /*/    for (int i = 0; i < array_len; i++) {
    //     struct json_object *item = json_object_array_get_idx(entries, i);
    //     struct json_object *user, *name;
    //     json_object_object_get_ex(item, "accessible_by", &user);
    //     json_object_object_get_ex(user, "name", &name);

    //     const char* name_ = json_object_get_string(name);
        
    //     pthread_mutex_lock(&collab_mutex);
    //     if (!is_name_in_list(args->collaborators, name_, args->num_collaborators)) {
    //         args->collaborators[args->num_collaborators] = strdup(name_);
    //         args->num_collaborators++;
    //     } else {
    //         pthread_mutex_unlock(&collab_mutex);
    //         continue;
    //     }
    //     pthread_mutex_unlock(&collab_mutex);

    //     // Write to file safely
    //     pthread_mutex_lock(&file_mutex);
    //     fprintf(&args->file, "Collaborator: %s\n", name_);
    //     pthread_mutex_unlock(&file_mutex);
    */
    }
    
    json_object_put(parsed_json);
    free(response);
}

void *thread_handler(void *arg) {
    ThreadArgs *args = (ThreadArgs *)arg;
    
    if (args->level_counter >= args->level_depth) { 
        // pthread_t thread_id = pthread_self();
        // char filename[50]; 
        // sprintf(filename, "collabs/collaborators%ld.txt", (long)thread_id);
        // FILE *file = fopen(filename, "w"); 
        // args->file = *file;
        get_collabs(args);
        return NULL;
    }

    char url[256];
    snprintf(url, sizeof(url), "https://api.box.com/2.0/folders/%s/items", args->folder_id);
    char *response = make_api_request(url);
    if (!response) return NULL;

    struct json_object *parsed_json = json_tokener_parse(response);
    struct json_object *entries;
    if (json_object_object_get_ex(parsed_json, "entries", &entries)) {
        int array_len = json_object_array_length(entries);
        pthread_t threads[array_len];
        ThreadArgs thread_args[array_len];
        
        for (int i = 0; i < array_len; i++) {
            struct json_object *item = json_object_array_get_idx(entries, i);
            struct json_object *type, *id;
            
            json_object_object_get_ex(item, "type", &type);
            json_object_object_get_ex(item, "id", &id);
            
            if (strcmp(json_object_get_string(type), "folder") == 0) {
                snprintf(thread_args[i].folder_id, sizeof(thread_args[i].folder_id), "%s", json_object_get_string(id));
                thread_args[i].level_counter = args->level_counter + 1;
                thread_args[i].level_depth = args->level_depth;
                pthread_create(&threads[i], NULL, thread_handler, &thread_args[i]);
            }
        }
        for (int i = 0; i < array_len; i++) {
            pthread_join(threads[i], NULL);
        }
    }
    
    json_object_put(parsed_json);
    free(response);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <folder_id> <level_depth>\n", argv[0]);
        return 1;
    }
    if (argc ==4 && strcmp(argv[3],"v")== 0){
        printf("verbose activated\n");
        verbose =1;
    }
    int max_depth = atoi(argv[2]);
    if (verbose){
        printf("folder id argv[1]== %s\n", argv[1]);
        printf("max depth argv[2]== %d\n", atoi(argv[2]));
    }
    const char** collaborators =malloc(MAX_COLLABORATORS * sizeof(char*));
    int num_collaborators =0;

    pthread_mutex_init(&file_mutex, NULL);
    pthread_mutex_init(&collab_mutex, NULL);

    ThreadArgs args;
    FILE *file = fopen("collabs/collaborators.txt", "w");  // Open for writing (creates a new file)
    snprintf(args.folder_id, sizeof(args.folder_id), "%s", argv[1]);
    args.level_counter = 0;
    args.level_depth = atoi(argv[2]);
    args.file = *file;
    //get collabs before creating threads:
    //printing 
    printf("test first call\n");
    get_collabs(&args);
    printf("finish test first call\n");

    pthread_t root_thread;
    pthread_create(&root_thread, NULL, thread_handler, &args);
    pthread_join(root_thread, NULL);


    pthread_mutex_destroy(&file_mutex);
    pthread_mutex_destroy(&collab_mutex);
    fclose(file);
    return 0;
}