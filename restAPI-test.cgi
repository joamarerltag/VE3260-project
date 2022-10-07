#!/bin/sh
# https://stackoverflow.com/questions/28138997/cgi-script-downloads-instead-of-running
# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/plain;charset=utf-8"

# Skriver ut tom linje for å skille hodet fra kroppen
echo


echo REQUEST_URI:    $REQUEST_URI 
echo REQUEST_METHOD: $REQUEST_METHOD
echo

if [ "$REQUEST_METHOD" = "GET" ]; then
    echo $REQUEST_URI skal hentes

    ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
fi

if [ "$REQUEST_METHOD" = "POST" ]; then
    echo Følgende skal settes inn i $REQUEST_URI:
    echo

    # skriver HTTP-kropp (hodet er allerede lest av web-tjeneren)
    # skriver-hode
    BODY=$(head -c $CONTENT_LENGTH)
    echo "$BODY"
    echo

    ID=$(echo "$BODY" | xmllint --xpath "/dikt/diktID/text()" -)
    DIKT=$(echo "$BODY" | xmllint --xpath "/dikt/dikt/text()" -)
    EPOST=$(echo "$BODY" | xmllint --xpath "/dikt/epostadresse/text()" -)
    echo INSERT INTO Dikt VALUES \("$ID", \""$DIKT"\", \""$EPOST"\"\)\; | sqlite3 /var/www/data/VE3260-project/db/diktDB.db
fi

if [ "$REQUEST_METHOD" = "PUT" ]; then
    echo $REQUEST_URI skal endres slik:
    echo

    # skriver-hode
    BODY=$(head -c $CONTENT_LENGTH)
    echo "$BODY"
    echo 

    ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
    DIKT=$(echo "$BODY" | xmllint --xpath "/dikt/dikt/text()" -)
    EPOST=$(echo "$BODY" | xmllint --xpath "/dikt/epostadresse/text()" -)
    echo UPDATE Dikt SET dikt=\""$DIKT"\", epostadresse=\""$EPOST"\" WHERE diktID="$ID"\; | sqlite3 /var/www/data/VE3260-project/db/diktDB.db
fi

if [ "$REQUEST_METHOD" = "DELETE" ]; then
    echo $REQUEST_URI skal slettes

    ID=$(echo $REQUEST_URI | cut -d '/' -f 3)

    echo DELETE FROM Dikt WHERE diktID=$ID\; | sqlite3 /var/www/data/VE3260-project/db/diktDB.db
fi
