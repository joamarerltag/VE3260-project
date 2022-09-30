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
fi

if [ "$REQUEST_METHOD" = "POST" ]; then
    echo Følgende skal settes inn i $REQUEST_URI:
    echo

    # skriver HTTP-kropp (hodet er allerede lest av web-tjeneren)
    head -c $CONTENT_LENGTH
    echo 
fi

if [ "$REQUEST_METHOD" = "PUT" ]; then
    echo $REQUEST_URI skal endres slik:
    echo

    # skriver-hode
    head -c $CONTENT_LENGTH
    echo 
fi

if [ "$REQUEST_METHOD" = "DELETE" ]; then
    echo $REQUEST_URI skal slettes
fi
