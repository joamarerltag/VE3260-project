#!/bin/sh
# https://stackoverflow.com/questions/28138997/cgi-script-downloads-instead-of-running

#Global variables
DB="/var/www/data/VE3260-project/db/diktDB.db"

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/xml;charset=utf-8"

if [ "$REQUEST_METHOD" != "POST" ] || [ $(echo "$REQUEST_URI" | cut -d'/' -f2) != "login" ]; then
    # Skriver ut tom linje for å skille hodet fra kroppen
    echo
else
    LOGIN_REQUEST=1
fi

#Attempts to get current session id from cookie
CSESSION=$(echo "$HTTP_COOKIE" | xargs -d';' | grep sessionId | cut -d'=' -f2)
CSESSION_EPOST=$(echo "SELECT epostadresse FROM Sesjon WHERE sesjonsID=\"$CSESSION\"" | sqlite3 $DB)
#if [ "$LOGIN_REQUEST" = "" ]; then
#    if [ "$CSESSION_EPOST" != "" ]; then
#        echo "Current session: $CSESSION"
#        echo "Logged in as: $CSESSION_EPOST"
#        echo
#    else
#        echo "Not logged in"
#        echo
#        CSESSION=""
#    fi
#fi
if [ "$CSESSION_EPOST" = "" ]; then
    CSESSION=""
fi

ENDPOINT=$(echo "$REQUEST_URI" | cut -d'/' -f2)
if [ "$ENDPOINT" = "login" ]; then
    if [ "$REQUEST_METHOD" = "POST" ]; then
        BODY=$(head -c $CONTENT_LENGTH)

        EPOST=$(echo "$BODY" | xmllint --xpath "/bruker/epostadresse/text()" -)
        PASSORD=$(echo "$BODY" | xmllint --xpath "/bruker/passord/text()" - | md5sum | cut -d' ' -f1)
        PASSORDCHECK=$(echo "SELECT passordhash FROM Bruker WHERE epostadresse=\"$EPOST\";" | sqlite3 $DB)

        if [ "$PASSORD" = "$PASSORDCHECK" ]; then
            if [ "$CSESSION" != "" ]; then
                echo "DELETE FROM Sesjon WHERE sesjonsID=\"$CSESSION\"" | sqlite3 $DB
            fi
            SESSION=$(uuidgen)
            echo "INSERT INTO Sesjon VALUES (\"$SESSION\", \"$EPOST\");" | sqlite3 $DB
            echo "Set-Cookie: sessionId=$SESSION"
        fi

        # Skriver ut tom linje for å skille hodet fra kroppen
        echo
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
        echo "<respons>"
        echo -n "<operasjon>Logg inn</operasjon>"
        if [ "$SESSION" != "" ]; then
            echo -n "<tilbakemelding>GR8 SUCCESS</tilbakemelding>"
        else
            echo -n "<tilbakemelding>UNGR8 SUCCESS</tilbakemelding>"
        fi
        echo "</respons>"
    fi
elif [ "$ENDPOINT" = "logout" ]; then
    echo "<?xml version=\"1.0\"?>"
    echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
    echo "<respons>"
    echo -n "<operasjon>Logg ut</operasjon>"
    if [ "$CSESSION" != "" ]; then
        echo -n "DELETE FROM Sesjon WHERE sesjonsID=\"$CSESSION\"" | sqlite3 $DB
        echo -n "<tilbakemelding>GR8 SUCCESS</tilbakemelding>"
    else
        echo -n "<tilbakemelding>UNGR8 SUCCESS</tilbakemelding>"
    fi
    echo "</respons>"
elif [ "$ENDPOINT" = "dikt" ]; then
    if [ "$REQUEST_METHOD" = "GET" ]; then
        ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
        if [ "$ID" = "" ]; then
            QUERY=$(echo "SELECT * FROM Dikt;" | sqlite3 $DB)
            if [ "$?" = "1" ]; then
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
                echo "<respons>"
                echo "<operasjon>Hent $REQUEST_URI</operasjon>"
                echo "<tilbakemelding>UNGR8 SUCCESS</tilbakemelding>"
                echo "</respons>"
            else
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE dikt_liste SYSTEM \"respons_dikt_liste.dtd\">"
                LINES=$(echo "$QUERY" | wc -l)
                echo -n "<dikt>"
                for VARIABLE in $(seq 1 $LINES)
                do
                    LINE=$(echo "$QUERY" | head -$VARIABLE | tail -1)
                    ID=$(echo $LINE | cut -d '|' -f 1)
                    DIKT=$(echo $LINE | cut -d '|' -f 2)
                    EPOST=$(echo $LINE | cut -d '|' -f 3)
                    echo -n "<dikt><diktID>$ID</diktID><dikt>$DIKT</dikt><epostadresse>$EPOST</epostadresse></dikt>"
                done
                echo -n "</dikt>"
                ID=""
            fi
        else
            QUERY=$(echo "SELECT * FROM Dikt WHERE diktID=$ID;" | sqlite3 $DB )
            if [ "$QUERY" = "" ]; then
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
                echo "<respons>"
                echo "<operasjon>Hent $REQUEST_URI</operasjon>"
                echo "<tilbakemelding>Finnes ikke</tilbakemelding>"
                echo "</respons>"
            else
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE dikt_entry SYSTEM \"respons_dikt.dtd\">"
                DIKT=$(echo $QUERY | cut -d '|' -f 2)
                EPOST=$(echo $QUERY | cut -d '|' -f 3)

                echo -n "<dikt><diktID>$ID</diktID><dikt>$DIKT</dikt><epostadresse>$EPOST</epostadresse></dikt>"
            fi
        fi
    fi
    if [ "$REQUEST_METHOD" = "POST" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
        echo "<respons>"
        if [ "$CSESSION" != "" ]; then
            echo -n "<operasjon>Sett inn i $REQUEST_URI</operasjon>"

            # skriver HTTP-kropp (hodet er allerede lest av web-tjeneren)
            # skriver-hode
            BODY=$(head -c $CONTENT_LENGTH)
            DIKT=$(echo "$BODY" | xmllint --xpath "/dikt_entry/dikt/text()" -)
	    echo "INSERT INTO Dikt (dikt, epostadresse) VALUES (\"$DIKT\", \"$CSESSION_EPOST\");" | sqlite3 $DB
            if [ "$?" = "0" ]; then
                echo -n "<tilbakemelding>GR8 SUCCESS</tilbakemelding>"
            else
                echo -n "<tilbakemelding>UNGR8 SUCCESS</tilbakemelding>"
            fi
        else
            echo -n "<tilbakemelding>FEIL:Må være logget inn</tilbakemelding>"
        fi
        echo "</respons>"
    fi
    if [ "$REQUEST_METHOD" = "PUT" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
        echo "<respons>"
        echo -n "<operasjon>Endre $REQUEST_URI</operasjon>"
        if [ "$CSESSION" != "" ]; then
            # skriver-hode
            BODY=$(head -c $CONTENT_LENGTH)
            ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
            EPOST_OWNER=$(echo "SELECT epostadresse FROM Dikt WHERE diktID=$ID;" | sqlite3 $DB)
            if [ "$EPOST_OWNER" = "$CSESSION_EPOST" ]; then
                DIKT=$(echo "$BODY" | xmllint --xpath "/dikt_entry/dikt/text()" -)
                EPOST=$(echo "$BODY" | xmllint --xpath "/dikt_entry/epostadresse/text()" -)
                if [ "$DIKT" != "" ]; then
                    echo "UPDATE Dikt SET dikt=\"$DIKT\" WHERE diktID=$ID;" | sqlite3 $DB
                    if [ "$?" = "0" ]; then
                        STATUS1="SET DIKT:GR8 SUCCESS"
                    else
                        STATUS1="SET DIKT:UNGR8 SUCCESS"
                    fi
                fi
                if [ "$EPOST" != "" ]; then
                    echo "UPDATE Dikt SET epostadresse=\"$EPOST\" WHERE diktID=$ID;" | sqlite3 $DB
                    if [ "$?" = "0" ]; then
                        STATUS2="SET EPOST:GR8 SUCCESS"
                    else
                        STATUS2="SET EPOST:UNGR8 SUCCESS"
                    fi
                fi
                echo -n "<tilbakemelding>$STATUS1 | $STATUS2</tilbakemelding>"
            else
                echo -n "<tilbakemelding>FEIL:Dikt tilhører ikke innlogget bruker</tilbakemelding>"
            fi
        else
            echo -n "<tilbakemelding>FEIL:Må være logget inn</tilbakemelding>"
        fi
        echo "</respons>"
    fi
    if [ "$REQUEST_METHOD" = "DELETE" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
        echo "<respons>"
        echo -n "<operasjon>Slett $REQUEST_URI</operasjon>"
        if [ "$CSESSION" != "" ]; then
            ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
            if [ "$ID" != "" ]; then
                EPOST_OWNER=$(echo "SELECT epostadresse FROM Dikt WHERE diktID=\"$ID\";" | sqlite3 $DB)
                if [ "$EPOST_OWNER" = "$CSESSION_EPOST" ]; then
                    echo "DELETE FROM Dikt WHERE diktID=$ID;" | sqlite3 $DB
                    if [ "$?" = "0" ]; then
                        echo -n "<tilbakemelding>GR8 SUCCESS</tilbakemelding>"
                    else
                        echo -n "<tilbakemelding>UNGR8 SUCCESS</tilbakemelding>"
                    fi
                else
                    echo -n "<tilbakemelding>FEIL:Dikt tilhører ikke innlogget bruker</tilbakemelding>"
                fi
            else
                echo "DELETE FROM Dikt WHERE epostadresse=\"$CSESSION_EPOST\";" | sqlite3 $DB
                if [ "$?" = "0" ]; then
                    echo -n "<tilbakemelding>GR8 SUCCESS</tilbakemelding>"
                else
                    echo -n "<tilbakemelding>UNGR8 SUCCESS</tilbakemelding>"
                fi
            fi
        else
            echo -n "<tilbakemelding>FEIL:Må være logget inn</tilbakemelding>"
        fi
        echo "<respons>"
    fi
else
    echo "<?xml version=\"1.0\"?>"
    echo "<!DOCTYPE respons SYSTEM \"respons.dtd\">"
    echo "<respons>"
    echo "<operasjon>IKKE DEFINERT</operasjon>"
    echo "<tilbakemelding>FEIL:Finnes ikke noe slikt endepunkt</tilbakemelding>"
    echo -n "</respons>"
fi
