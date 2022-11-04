#!/bin/sh
# https://stackoverflow.com/questions/28138997/cgi-script-downloads-instead-of-running

#Global variables
DB="/var/www/data/VE3260-project/db/diktDB.db"

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/xml;charset=utf-8"

ENDPOINT=$(echo "$REQUEST_URI" | cut -d'/' -f2)

if [ "$REQUEST_METHOD" != "POST" ] || [ "$ENDPOINT" != "login" ]; then
    # Skriver ut tom linje for å skille hodet fra kroppen
    echo
else
    LOGIN_REQUEST=1
fi

#Attempts to get current session id from cookie
CSESSION=$(echo "$HTTP_COOKIE" | xargs -d';' | grep sessionId | cut -d'=' -f2)
CSESSION_EPOST=$(echo "SELECT epostadresse FROM Sesjon WHERE sesjonsID=\"$CSESSION\"" | sqlite3 $DB)
if [ "$CSESSION_EPOST" = "" ]; then
    CSESSION=""
fi

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
            echo "PRAGMA FOREIGN_KEYS=ON;INSERT INTO Sesjon VALUES (\"$SESSION\", \"$EPOST\");" | sqlite3 $DB
            echo "Set-Cookie: sessionId=$SESSION"
        fi

        # Skriver ut tom linje for å skille hodet fra kroppen
        echo
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
        echo "<respons>"
        echo -n "<operasjon>Logg inn</operasjon>"
        if [ "$SESSION" != "" ]; then
            echo -n "<tilbakemelding>SUCCESS</tilbakemelding>"
        else
            echo -n "<tilbakemelding>FAIL</tilbakemelding>"
        fi
        echo "</respons>"
    fi
elif [ "$ENDPOINT" = "logout" ]; then
    if [ "REQUEST_METHOD" = "DELETE" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
        echo "<respons>"
        echo -n "<operasjon>Logg ut</operasjon>"
        if [ "$CSESSION" != "" ]; then
            echo -n "DELETE FROM Sesjon WHERE sesjonsID=\"$CSESSION\"" | sqlite3 $DB
            echo -n "<tilbakemelding>SUCCESS</tilbakemelding>"
        else
            echo -n "<tilbakemelding>FAIL</tilbakemelding>"
        fi
        echo "</respons>"
    fi
elif [ "$ENDPOINT" = "dikt" ]; then
    if [ "$REQUEST_METHOD" = "GET" ]; then
        ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
        if [ "$ID" = "" ]; then
            QUERY=$(echo "SELECT * FROM Dikt;" | sqlite3 $DB)
            if [ "$?" = "1" ]; then
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
                echo "<respons>"
                echo "<operasjon>Hent $REQUEST_URI</operasjon>"
                echo "<tilbakemelding>FAIL</tilbakemelding>"
                echo "</respons>"
            else
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE dikt_liste SYSTEM \"http://138.68.92.43/files/dtd/respons_dikt_liste.dtd\">"
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
                echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
                echo "<respons>"
                echo "<operasjon>Hent $REQUEST_URI</operasjon>"
                echo "<tilbakemelding>Finnes ikke</tilbakemelding>"
                echo "</respons>"
            else
                echo "<?xml version=\"1.0\"?>"
                echo "<!DOCTYPE dikt_entry SYSTEM \"http://138.68.92.43/files/dtd/respons_dikt.dtd\">"
                DIKT=$(echo $QUERY | cut -d '|' -f 2)
                EPOST=$(echo $QUERY | cut -d '|' -f 3)

                echo -n "<dikt><diktID>$ID</diktID><dikt>$DIKT</dikt><epostadresse>$EPOST</epostadresse></dikt>"
            fi
        fi
    fi
    if [ "$REQUEST_METHOD" = "POST" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
        echo "<respons>"
        if [ "$CSESSION" != "" ]; then
            echo -n "<operasjon>Sett inn i $REQUEST_URI</operasjon>"

            # skriver HTTP-kropp (hodet er allerede lest av web-tjeneren)
            # skriver-hode
            BODY=$(head -c $CONTENT_LENGTH)
            DIKT=$(echo "$BODY" | xmllint --xpath "/dikt_entry/dikt/text()" -)
	    echo "PRAGMA FOREIGN_KEYS=ON;INSERT INTO Dikt (dikt, epostadresse) VALUES (\"$DIKT\", \"$CSESSION_EPOST\");" | sqlite3 $DB
            if [ "$?" = "0" ]; then
                echo -n "<tilbakemelding>SUCCESS</tilbakemelding>"
            else
                echo -n "<tilbakemelding>FAIL</tilbakemelding>"
            fi
        else
            echo -n "<tilbakemelding>FAIL:Må være logget inn</tilbakemelding>"
        fi
        echo "</respons>"
    fi
    if [ "$REQUEST_METHOD" = "PUT" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
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
                        STATUS1="SET DIKT:SUCCESS"
                    else
                        STATUS1="SET DIKT:FAIL"
                    fi
                fi
                if [ "$EPOST" != "" ]; then
                    echo "PRAGMA FOREIGN_KEYS=ON;UPDATE Dikt SET epostadresse=\"$EPOST\" WHERE diktID=$ID;" | sqlite3 $DB
                    if [ "$?" = "0" ]; then
                        STATUS2="SET EPOST:SUCCESS"
                    else
                        STATUS2="SET EPOST:FAIL"
                    fi
                fi
                echo -n "<tilbakemelding>$STATUS1 | $STATUS2</tilbakemelding>"
            else
                echo -n "<tilbakemelding>FAIL:Dikt tilhører ikke innlogget bruker</tilbakemelding>"
            fi
        else
            echo -n "<tilbakemelding>FAIL:Må være logget inn</tilbakemelding>"
        fi
        echo "</respons>"
    fi
    if [ "$REQUEST_METHOD" = "DELETE" ]; then
        echo "<?xml version=\"1.0\"?>"
        echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
        echo "<respons>"
        echo -n "<operasjon>Slett $REQUEST_URI</operasjon>"
        if [ "$CSESSION" != "" ]; then
            ID=$(echo $REQUEST_URI | cut -d '/' -f 3)
            if [ "$ID" != "" ]; then
                EPOST_OWNER=$(echo "SELECT epostadresse FROM Dikt WHERE diktID=\"$ID\";" | sqlite3 $DB)
                if [ "$EPOST_OWNER" = "$CSESSION_EPOST" ]; then
                    echo "DELETE FROM Dikt WHERE diktID=$ID;" | sqlite3 $DB
                    if [ "$?" = "0" ]; then
                        echo -n "<tilbakemelding>SUCCESS</tilbakemelding>"
                    else
                        echo -n "<tilbakemelding>FAIL</tilbakemelding>"
                    fi
                else
                    echo -n "<tilbakemelding>FAIL:Dikt tilhører ikke innlogget bruker</tilbakemelding>"
                fi
            else
                echo "DELETE FROM Dikt WHERE epostadresse=\"$CSESSION_EPOST\";" | sqlite3 $DB
                if [ "$?" = "0" ]; then
                    echo -n "<tilbakemelding>SUCCESS</tilbakemelding>"
                else
                    echo -n "<tilbakemelding>FAIL</tilbakemelding>"
                fi
            fi
        else
            echo -n "<tilbakemelding>FAIL:Må være logget inn</tilbakemelding>"
        fi
        echo "<respons>"
    fi
else
    echo "<?xml version=\"1.0\"?>"
    echo "<!DOCTYPE respons SYSTEM \"http://138.68.92.43/files/dtd/respons.dtd\">"
    echo "<respons>"
    echo "<operasjon>IKKE DEFINERT</operasjon>"
    echo "<tilbakemelding>FAIL:Finnes ikke noe slikt endepunkt</tilbakemelding>"
    echo -n "</respons>"
fi
