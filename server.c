#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>

#define LOKAL_PORT 80
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler

// Struct for file type and corresponding extension
struct MimeEntry {
    char* extension;
    char* type;
    struct MimeEntry* next;
};

bool readMimeIntoMemory(struct MimeEntry** l_head);
bool sendFileContent(int ny_sd, char* filePath, char* buffer, char* contentType);
char* checkFileExtension(char* filePath, struct MimeEntry* l_head);
void cleanup(int ny_sd);

int main()
{
    FILE* errorLog = fopen("logs/stderr.txt", "w");
    if(errorLog < 0){
        perror("Couldn't open/create log file");
    }
    int errorFd = fileno(errorLog);
    dup2(errorFd, 2);
    fclose(errorLog);

    chdir("www/");
    chroot(".");

    struct MimeEntry* l_head;
    readMimeIntoMemory(&l_head);

    // Deaemonize
    if (fork() != 0) {
        exit(0);
    }

    pid_t setsid(void);

    signal(SIGHUP, SIG_IGN);

    if (fork() != 0) {
        exit(0);
    }

    // Prevent zombies
    signal(SIGCHLD, SIG_IGN); 

    struct sockaddr_in lok_adr;
    int sd, ny_sd;

    // Setter opp socket-strukturen
    sd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    // For at operativsystemet ikke skal holde porten reservert etter tjenerens død
    setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int));

    // Initierer lokal adresse
    lok_adr.sin_family = AF_INET;
    lok_adr.sin_port = htons((u_short)LOKAL_PORT);
    lok_adr.sin_addr.s_addr = htonl(INADDR_ANY);

    // Kobler sammen socket og lokal adresse
    if (0 == bind(sd, (struct sockaddr *)&lok_adr, sizeof(lok_adr)))
        fprintf(stderr, "Process %d is bound to port %d.\n", getpid(), LOKAL_PORT);
    else
        exit(1);

    setuid(1004);
    setgid(1005);

    // Venter på forespørsel om forbindelse
    listen(sd, BAK_LOGG);
    while (1)
    {
        // Aksepterer mottatt forespørsel
        ny_sd = accept(sd, NULL, NULL);

        if (0 == fork())
        {
            dup2(ny_sd, 1); // redirigerer socket til standard utgang

            // readFile(ny_sd);
            char buffer[1024];

            read(ny_sd, buffer, sizeof(buffer));

            // Fetches the second token delimited by space
            char* fileName;
            fileName = strtok(buffer, " ");
            fileName = strtok(NULL, " ");

            char filePath[1024] = { 0 };
            filePath[0] = '.';
            strcat(filePath, fileName); // Adds '.' to file path to create relative path

            char* contentType;
            if ((contentType = checkFileExtension(filePath, l_head)) == NULL || !sendFileContent(ny_sd, filePath, buffer, contentType)) {
                cleanup(ny_sd);
                exit(1);
            }

            cleanup(ny_sd);
            exit(0);
        }
        else
        {
            close(ny_sd);
        }
    }
    return 0;
}

bool readMimeIntoMemory(struct MimeEntry** l_head) {
    char* buffer = NULL; // Buffer to contain read line
    char* fileExtensions = NULL; // File extensions for content type
    char* contentType = NULL; // Content type of current line

    size_t   getLineBufSize = 0;    // Buffer length for getline
    int      count = 0;    // Number of characters read 
    int      typeLength = 0;    // Length of content type

    // Pointers for linked list
    *l_head = malloc(sizeof(struct MimeEntry));
    struct MimeEntry* l_current = *l_head;
    struct MimeEntry* l_tail = NULL; // Last element in list

    // aapner mimetype-fila
    FILE* mimeFile = fopen("/etc/mime.types", "r");

    while (0 < (count = getline(&buffer, &getLineBufSize, mimeFile))) {

        if (buffer[0] == '#')  continue; // Hopper over kommentarer
        if (count < 2)  continue; // Hopper over tomme linjer
        buffer[count - 1] = '\0';               // Fjerner linjeskift

        // Mimetypen (venstre kolonne)
        contentType = strtok(buffer, "\t ");
        typeLength = strlen(contentType);

        // Gjennomløper filendelsene
        while (0 != (fileExtensions = strtok(NULL, "\t "))) {

            // setter filendelse i liste-element
            l_current->extension = malloc(strlen(fileExtensions) + sizeof('\0'));
            strcpy(l_current->extension, fileExtensions);

            // setter mimetype i liste-element
            l_current->type = malloc(typeLength + sizeof('\0'));
            strcpy(l_current->type, contentType);

            // setter nytt tomt element i lista
            l_current->next = malloc(sizeof(struct MimeEntry));
            l_tail = l_current; // referanse til siste element med innhold
            l_current = l_current->next;
        }
    }

    // Lukker fila
    fclose(mimeFile);

    // Frigjør minne brukt av strtok
    free(buffer);

    // Fjerner siste element (som er tomt)
    l_tail->next = NULL;
    free(l_current);
}

bool sendFileContent(int ny_sd, char* filePath, char* buffer, char* contentType) {
    int file = open(filePath, O_RDONLY); // Attempts to open file
    if (file < 0) {
        fprintf(stderr, "Error while opening file %s", filePath);
        perror("Error");
        //TODO: Send 404 response
        printf("HTTP/1.1 404 Not Found\n");
        printf("Content-Type: text/plain\n");
        printf("\n");
        printf("The requested file does not exist. Uuups.\n");
        return false;
    }

    if (strcmp(contentType, "asis") != 0) {
        struct stat statbuf;
        stat(filePath, &statbuf);

        printf("HTTP/1.1 200 OK\n");
        printf("Content-Type: %s\n", contentType);
        printf("Content-Length: %ld\n", statbuf.st_size);
        printf("\n");

        fflush(stdout);
    }

    int bytesRead;
    while ((bytesRead = read(file, buffer, sizeof(buffer))) > 0) {
        //fprintf(stderr, "Bytes read:%d", bytesRead);
        write(ny_sd, buffer, bytesRead); // Writes bytes to socket
    }
    if (bytesRead < 0) {
        perror("Error while reading file");
        return false;
    }

    close(file);

    return true;
}

char* checkFileExtension(char* filePath, struct MimeEntry* l_head) {
    char* extension = "asis";

    // Find file name - we need to consider /files/some.folder.with.dots/file.asis
    // Hence it is first needed to seek past the / symbols to the last field
    char* filePathCpy = malloc(strlen(filePath)+sizeof('\0'));
    strcpy(filePathCpy, filePath);

    char* previousToken = strtok(filePathCpy, "/");
    char* currentToken;
    while((currentToken = strtok(NULL, "/")) != NULL)
        previousToken = currentToken;

    // Then the rest is just to get the extension from the file name
    char* fileName = previousToken;
    strtok(fileName, ".");
    char* fileExtension = strtok(NULL, ".");

    if(fileExtension == NULL){
        perror("Unsupported file type");
        printf("HTTP/1.1 415 Unsupported Media Type\n");
        printf("Content-Type: text/plain\n");
        printf("\n");
        printf("The requested file type is not supported. Uuups.\n");
        return NULL;
    }


    if (strcmp(extension, fileExtension) == 0) {
        return "asis";
    }
    struct MimeEntry* l_current = l_head;
    while (l_current != NULL) {
        extension = strtok(l_current->extension, " ");
        while (extension != NULL) {
            if (strcmp(extension, fileExtension) == 0) {
                return l_current->type;
            }
            extension = strtok(NULL, " ");
        }
        l_current = l_current->next;
    }

    perror("Unsupported file type");
    printf("HTTP/1.1 415 Unsupported Media Type\n");
    printf("Content-Type: text/plain\n");
    printf("\n");
    printf("The requested file type is not supported. Uuups.\n");
    return NULL;
}

void cleanup(int ny_sd) {
    fflush(stdout);
    fflush(stderr);

    // Sørger for å stenge socket for skriving og lesing
    // NB! Frigjør ingen plass i fildeskriptortabellen
    shutdown(ny_sd, SHUT_RDWR);
}
