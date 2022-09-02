#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

#define LOKAL_PORT 55556
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler

// void readFile(int fd)
// {
//     char buffer[10];
//     int bytes_read;
//     int k = 0;
//     do
//     {
//         char t = 0;
//         bytes_read = read(fd, &t, 1);
//         buffer[k++] = t;
//         printf("%c", t);
//         if (t == '\n' && t == '\0')
//         {
//             printf("%d", atoi(buffer));
//             for (int i = 0; i < 10; i++)
//                 buffer[i] = '\0';
//             k = 0;
//         }
//     } while (bytes_read != 0);
// }

int main()
{

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
        fprintf(stderr, "Prosess %d er knyttet til port %d.\n", getpid(), LOKAL_PORT);
    else
        exit(1);

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
            char buffer[100];

            read(ny_sd, buffer, sizeof(buffer));

            // Printer ut et 200 svar
            printf("HTTP/1.1 200 OK\n");
            printf("Content-Type: text/plain\n");
            printf("\n");
            printf("Hallo klient!\n");

            // Vi kan bruke printf men foreløpig bruker vi en loop
            // printf("%s\n", buffer);
            
            int i = 0;
            for(i = 0; i < sizeof(buffer); i++) {
                printf("%c", buffer[i]);
            }


            fflush(stdout);

            // Sørger for å stenge socket for skriving og lesing
            // NB! Frigjør ingen plass i fildeskriptortabellen
            shutdown(ny_sd, SHUT_RDWR);
            exit(0);
        }

        else
        {
            close(ny_sd);
        }
    }
    return 0;
}