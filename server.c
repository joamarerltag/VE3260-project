#include <arpa/inet.h>
#include <unistd.h> 
#include <stdlib.h>
#include <stdio.h>

#define LOKAL_PORT 55556
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler 

int main ()
{

  struct sockaddr_in  lok_adr;
  int sd, ny_sd;

  // Setter opp socket-strukturen
  sd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

  // For at operativsystemet ikke skal holde porten reservert etter tjenerens død
  setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int));

  // Initierer lokal adresse
  lok_adr.sin_family      = AF_INET;
  lok_adr.sin_port        = htons((u_short)LOKAL_PORT); 
  lok_adr.sin_addr.s_addr = htonl(         INADDR_ANY);

  // Kobler sammen socket og lokal adresse
  if ( 0==bind(sd, (struct sockaddr *)&lok_adr, sizeof(lok_adr)) )
    fprintf(stderr, "Prosess %d er knyttet til port %d.\n", getpid(), LOKAL_PORT);
  else
    exit(1);

  // Venter på forespørsel om forbindelse
  listen(sd, BAK_LOGG); 
  while(1){ 

    // Aksepterer mottatt forespørsel
    ny_sd = accept(sd, NULL, NULL);    

    if(0==fork()) {

      dup2(ny_sd, 1); // redirigerer socket til standard utgang

      printf("HTTP/1.1 200 OK\n");
      printf("Content-Type: text/plain\n");
      printf("\n");
      printf("Hallo klient!\n");

      fflush(stdout);

      // Sørger for å stenge socket for skriving og lesing
      // NB! Frigjør ingen plass i fildeskriptortabellen
      shutdown(ny_sd, SHUT_RDWR);
      exit(0);
    }

    else {
      close(ny_sd);
    }
  }
  return 0;
}