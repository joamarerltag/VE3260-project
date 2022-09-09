#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/types.h>
#include <signal.h>

#define LOKAL_PORT 80
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler

bool sendFileContent(int ny_sd, char* filePath, char* buffer);
bool checkFileExtension(char* filePath);
void cleanup(int ny_sd);

int main()
{
    int errorLog = open("logs/stderr.txt", O_WRONLY | O_CREAT);
    dup2(errorLog, 2);
    close(errorLog);

    chdir("www/");
    chroot(".");

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

            if (!checkFileExtension(filePath) || !sendFileContent(ny_sd, filePath, buffer)) {
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

bool sendFileContent(int ny_sd, char* filePath, char* buffer) {
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

bool checkFileExtension(char* filePath) {
    int fileIndex = strlen(filePath) - 1;
    char* extension = "asis";
    int extensionIndex = strlen(extension) - 1;
    while (filePath[fileIndex] != '.') {
        if (extensionIndex < 0 || filePath[fileIndex] != extension[extensionIndex]) {
            perror("Unsupported file type");
            printf("HTTP/1.1 415 Unsupported Media Type\n");
            printf("Content-Type: text/plain\n");
            printf("\n");
            printf("The requested file type is not supported. Uuups.\n");
            return false;
        }
        fileIndex -= 1;
        extensionIndex -= 1;
    }
    return true;
}

void cleanup(int ny_sd) {
    fflush(stdout);
    fflush(stderr);

    // Sørger for å stenge socket for skriving og lesing
    // NB! Frigjør ingen plass i fildeskriptortabellen
    shutdown(ny_sd, SHUT_RDWR);
}
