#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <curl/curl.h>
#include <json-c/json.h>
#include <semaphore.h>

#define ACCESS_TOKEN "oYiZ1Ox4lsnP3cbvS81xA3g53aWgUIrZ"
#define MAX_COLLABORATORS 100 // Adjust as needed
#define MAX_FOLDERS 100
typedef struct
{
    char folder_id[50];
    int level_counter;
    int level_depth;
    FILE file;
    int num_collaborators;
    char *collaborators[MAX_COLLABORATORS * sizeof(char *)];

} StructArgs;

typedef struct 
{
    char * name[50];
    char * folder_name[50];
    char * given_by[50];
    char * on[50];
} CollabStruct;

struct MemoryStruct
{
    char *memory;
    size_t size;
};
int verbose = 0;

char * response;
const char **collaborators;
int num_collaborators;

pthread_mutex_t file_mutex;
pthread_mutex_t collab_mutex;
void * thread_handler(void*);


size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)userp;

    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if (ptr == NULL)
        return 0;

    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
}

char *make_api_request(const char *url)
{
    CURL *curl;
    CURLcode res;
    struct MemoryStruct chunk;
    chunk.memory = malloc(1);
    chunk.size = 0;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if (!curl)
        return NULL;

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

    if (res != CURLE_OK)
    {
        free(chunk.memory);
        return NULL;
    }

    return chunk.memory;
}

int is_name_in_list(const char **collaborators, const char *name, int num_collaborators)
{
    printf("name %s\n", name);

    for (int i = 0; i < num_collaborators; i++)
    {
        printf("collab #%d of %d %s\n", i, num_collaborators, collaborators[i]);

        if (strcmp(collaborators[i], name) == 0)
        {
            return 1; // in list
        }
    }

    return 0; // not it list
}

struct json_object* get_collabs(char* folder_id)
{
    char url[256];
    snprintf(url, sizeof(url), "https://api.box.com/2.0/folders/%s/collaborations",folder_id);
    char *response = make_api_request(url);

    struct json_object *parsed_json = json_tokener_parse(response);
    struct json_object *entries;
    
    if (json_object_object_get_ex(parsed_json, "entries", &entries))
    {
        if (verbose) printf("entries: %s\n",entries);
        free(response);
        return entries;
    } 
    json_object_put(parsed_json);
    return NULL;
}

struct json_object *get_folders(char *folder_id)
{
    char **folders = malloc(MAX_FOLDERS * sizeof(char *));
    char url2[256];
    snprintf(url2, sizeof(url2), "https://api.box.com/2.0/folders/%s/items", folder_id);
    response = make_api_request(url2);
    if (!response)
        return NULL;

    struct json_object *parsed_json = json_tokener_parse(response);
    struct json_object *entries;
    
    if (json_object_object_get_ex(parsed_json, "entries", &entries))
    {    
        free(response);
        return entries;
    }
    json_object_put(parsed_json);

    return NULL;
}

void parse_collabs(struct json_object *entries){

    int array_len = json_object_array_length(entries);
    for (int i = 0; i < array_len; i++)
    {
        struct json_object *item = json_object_array_get_idx(entries, i);
        struct json_object *user, *role, *given_by, *date, *item_type;
        struct json_object *name, *given_by_name, *item_name;


        json_object_object_get_ex(item, "accessible_by", &user);
        json_object_object_get_ex(user, "name", &name);
        json_object_object_get_ex(item, "item", &item_type);
        json_object_object_get_ex(item_type, "name", &item_name);

        // name check

        const char *name_ = json_object_get_string(name);

        int already_added = is_name_in_list(collaborators, name_, num_collaborators);
        printf("added: %d\n", already_added);

        json_object_object_get_ex(item, "role", &role);
        json_object_object_get_ex(item, "created_by", &given_by);
        json_object_object_get_ex(given_by, "name", &given_by_name);
        json_object_object_get_ex(item, "modified_at", &date);

        const char *item_name_ = json_object_get_string(item_name);
        const char *role_ = json_object_get_string(role);
        const char *given_by_name_ = json_object_get_string(given_by_name);
        const char *date_ = json_object_get_string(date);
        if (verbose)
        {
            printf("Collaborator: %s\nof file: %s\n\n", name_, item_name_);
        }
        if (already_added == 0)
        {
            collaborators[num_collaborators] = strdup(name_);
            num_collaborators++;
            if (verbose)
            {
                printf("writing to file: %s\n", item_name_);
            }

            char filename[50];
            sprintf(filename,"collabs/collaborators.txt");
            FILE *file = fopen(filename, "a"); 
            fprintf(file, "folder: %s\nname: %s\nrole: %s\ngiven by: %s\non: %s\n\n", item_name_, name_, role_, given_by_name_, date_);
            fclose(file);

        }
        else
        {
            continue;
        }
    }
}

void parse_folders(struct json_object * folders){

    int array_len = json_object_array_length(folders);

    pthread_t threads[array_len];
    StructArgs thread_args[array_len];

    for (int i = 0; i < array_len; i++){

        struct json_object *item = json_object_array_get_idx(folders, i);
        struct json_object *type, *id;

        if (folders)
        {
            if (verbose) printf("start folder parse #%d of %d\n",i, array_len);

            struct json_object *item = json_object_array_get_idx(folders, i);
            struct json_object *type, *id, *name;

            json_object_object_get_ex(item, "type", &type);
            json_object_object_get_ex(item, "id", &id);
            json_object_object_get_ex(item, "name", &name);

            const char * folder_id_ = json_object_get_string(id);
            const char * type_ = json_object_get_string(type);
            const char * name_ = json_object_get_string(name);

            if (strcmp(type_, "folder") == 0)
            {
                pthread_mutex_init(&file_mutex, NULL);
                pthread_mutex_init(&collab_mutex, NULL);
                
                pthread_create(&threads[i], NULL, thread_handler, &folder_id_);
            }
        }
        
    }
    // for (int i = 0; i < array_len; i++)
    //     {
    //         if (verbose) printf("start folder parse #%d of %d\n",i, array_len);

    //         pthread_join(threads[i], NULL);
    //     }
}
void *thread_handler(void * argv)
{
    char*folder_id = (char *)argv;
    
    parse_collabs(get_collabs(folder_id));
    //struct json_object * folders =get_folders(args->folder_id);

    return NULL;
}

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        printf("Usage: %s <folder_id> <level_depth>\n", argv[0]);
        return 1;
    }
    if (argc == 4 && strcmp(argv[3], "v") == 0)
    {
        printf("verbose activated\n");
        verbose = 1;
    }

    //Parse argvs
    char folder_id[50];
    snprintf(folder_id, sizeof(folder_id), "%s", argv[1]);
    int max_depth = atoi(argv[2]);
    collaborators = malloc(MAX_COLLABORATORS * sizeof(char *));
    num_collaborators = 0;

    if (verbose)
    {
        printf("folder id argv[1]== %s\n", argv[1]);
        printf("max depth argv[2]== %d\n\n", atoi(argv[2]));
    }
    /*
    StructArgs args;
    FILE *file = fopen("collabs/collaborators.txt", "w"); // Open for writing (creates a new file)
    snprintf(args.folder_id, sizeof(args.folder_id), "%s", argv[1]);
    args.level_counter = 0;
    args.level_depth = atoi(argv[2]);
    args.file = *file;
    */

    printf("test first get_collabs\n");
    struct json_object *collabs = get_collabs(folder_id);

    parse_collabs(collabs);

    printf("finish test first get_collabs\n\n");

    printf("test first get_folders\n");
        // Go through folders

    struct json_object *folders = get_folders(folder_id);
    parse_folders(folders);
    printf("finish test first get_folders\n\n");

    pthread_mutex_destroy(&file_mutex);
    pthread_mutex_destroy(&collab_mutex);
}