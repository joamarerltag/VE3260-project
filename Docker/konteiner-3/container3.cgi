#!/usr/bin/env sh

start_html(){
	echo "<!DOCTYPE html>"
	echo "<html>"
	echo "<body>"
}

end_html(){
	echo "</body>"
	echo "</html>"
}

login_form_to_xml(){
	INPUT=$(echo "$BODY" | sed s/\&/\\n/g | grep epost | cut -d'=' -f2)
	url_decode
	EPOST="$INPUT"
	PASSORD=$(echo "$BODY" | sed s/\&/\\n/g | grep passord | cut -d'=' -f2)
	XML=""
	XML="$XML<?xml version=\"1.0\"?>"
	XML="$XML<!DOCTYPE bruker SYSTEM \"http://$IP/files/dtd/post_login.dtd\">"
	XML="$XML<bruker>"
	XML="$XML<epostadresse>$EPOST</epostadresse>"
	XML="$XML<passord>$PASSORD</passord>"
	XML="$XML</bruker>"
}

insert_form_to_xml(){
	INPUT=$(echo -ne "$BODY" | sed -z 's/\n/\t/g' | sed -z 's/&/\n/g' | grep dikt | sed 's/\t/\n/g' | cut -z -d"=" -f2)
	url_decode
	DIKT="$INPUT"
	XML=""
	XML="$XML<?xml version=\"1.0\"?>"
	XML="$XML<!DOCTYPE dikt_entry SYSTEM \"http://$IP/files/dtd/post_insert.dtd\">"
	XML="$XML<dikt_entry><dikt>$DIKT</dikt></dikt_entry>"
}

url_decode(){
	INPUT=$(echo -ne "$INPUT" | sed 's/%0D%0A/\n/g' | sed 's/%0A/\n/g' | sed 's/%0d%0a/\n/g' | sed 's/%0a/\n/g')
	INPUT=$(echo -ne "$INPUT" | sed 's/+/\ /g')
	INPUT=$(echo -ne "$INPUT" | sed 's/%40/@/g')
}

IP="172.4.20.69"
ENDPOINT=$(echo "$REQUEST_URI" | cut -d'/' -f2)
CSESSION=$(echo "$HTTP_COOKIE" | xargs -d';' | grep sessionId | cut -d'=' -f2)
TRY_LOGIN=$(curl -b "sessionId=$CSESSION" -X PUT "http://$IP/dikt/0" | grep "innlogget")
if [ "$?" != "0" ]; then
	CSESSION=""
fi

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/html;charset=utf-8"

if [ "$ENDPOINT" != "login" ] || [ "$REQUEST_METHOD" != "POST" ]; then
	echo
   	start_html
fi



BODY=$(head -c $CONTENT_LENGTH)
if [ "$ENDPOINT" = "" ]; then
	if [ "$CSESSION" != "" ]; then
		echo "<h1>Logget inn</h1>"
		echo "<a href=\"/logout\">Logg ut</a>"
		echo "<a href=\"/add\">Legg til nytt dikt</a>"
		echo "<a href=\"/update\">Endre et av dine dikt</a>"
		echo "<a href=\"/delete\">Slett et av dine dikt</a>"
		echo "<a href=\"/deleteall\">Slett alle dine dikt</a>"
	else
		echo "<a href=\"/login\">Logg inn</a>"
	fi
	echo "<a href=\"/get\">Hent et bestemt dikt(krever at du vet diktID-en)</a>"
	echo "<a href=\"/getall\">Hent alle dikt</a>"
fi

if [ "$ENDPOINT" = "login" ]; then
	if [ "$REQUEST_METHOD" = "GET" ]; then
		echo "<form action=\"/login\" method=\"post\">"
		echo "<label for=\"epost\">Epostadresse:</label>"
        echo "<input name=\"epost\" id=\"epost\" type=\"email\" placeholder=\"test@testus.gov\">"

		echo "<label for=\"passord\">Passord:</label>"
		echo "<input name=\"passord\" id=\"passord\" type=\"password\" placeholder=\"passord123\">"

		echo "<input type=\"submit\" value=\"Logg inn\">"
		echo "</form>"
	elif [ "$REQUEST_METHOD" = "POST" ]; then
		login_form_to_xml
		RESPONSE=$(curl -s -i -d "$XML" http://$IP/login)
		FCOOKIES=$(echo "$RESPONSE" | grep Set-Cookie)
		echo "$RESPONSE" | grep -q "SUCCESS"
		if [ "$?" = "0" ]; then
			echo $FCOOKIES
			echo
        	        start_html
			echo "<h1>Du har nå blitt logget inn</h1>"
		else
			echo
	                start_html
			echo "<h1>En feil oppsto under innlogging</h1>"
		fi
		echo "<a href=\"/\">Tilbake til hovedsiden</a>"
	fi
fi

if [ "$ENDPOINT" = "logout" ] && [ "$REQUEST_METHOD" = "GET" ]; then
	RESPONSE=$(curl -b "sessionId=$CSESSION" -X DELETE "http://$IP/logout")
	echo "$RESPONSE" | grep -q "SUCCESS"
	if [ "$?" = "0" ]; then
		echo "<h1>Du har nå blitt logget ut</h1>"
	else
		echo "<h1>En feil oppsto under utlogging</h1>"
	fi
    echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

if [ "$ENDPOINT" = "get" ]; then
	if [ "$REQUEST_METHOD" = "GET" ]; then
		echo "<form action=\"/get\" method=\"post\">"
		echo "<label for=\"diktid\">DiktID:</label>"
		echo "<input name=\"diktid\" id=\"diktid\">"
		echo "<input type=\"submit\" value=\"Hent dikt\">"
		echo "</form>"
	elif [ "$REQUEST_METHOD" = "POST" ]; then
		DIKTID="$(echo $BODY | cut -d'=' -f2)"
		RESPONS=$(curl "http://$IP/dikt/$DIKTID")
		echo "$RESPONS" | grep "FAIL"
		if [ "$?" != "0" ]; then
			EPOST="$(echo "$RESPONS" | xmllint --xpath '/dikt_entry/epostadresse/text()' - )"
			DIKT="$(echo "$RESPONS" | xmllint --xpath '/dikt_entry/dikt/text()' - )"

			echo "<h1>Her er diktet :):</h1>"
			echo "<p>DiktID:$DIKTID</p>"
			echo "<p>Skrevet av:$EPOST</p>"
			echo "<p>$DIKT</p>"
		else
			echo "<h1>En feil oppsto under henting av dikt</h1>"
		fi
	fi
	echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

if [ "$ENDPOINT" = "getall" ] && [ "$REQUEST_METHOD" = "GET" ]; then
	RESPONS="$(curl http://$IP/dikt/)"
	echo "$RESPONS" | grep "FAIL"
	if [ "$?" != "0" ]; then
		DIKT_COUNT=$(echo "$RESPONS" | xmllint --xpath 'count(/dikt_liste//dikt_entry)' -)
		for i in $(seq 1 $DIKT_COUNT)
		do
			DIKT_ENTRY=$(echo "$RESPONS" | xmllint --xpath "/dikt_liste//dikt_entry[$i]" -)
			DIKTID=$(echo "$DIKT_ENTRY" | xmllint --xpath '/dikt_entry/diktID/text()' -)
			EPOST=$(echo "$DIKT_ENTRY" | xmllint --xpath '/dikt_entry/epostadresse/text()' -)
			DIKT=$(echo "$DIKT_ENTRY" | xmllint --xpath '/dikt_entry/dikt/text()' -)
			echo "<p>DiktID:$DIKTID</p>"
			echo "<p>Skrevet av:$EPOST</p>"
			echo "<p>$DIKT</p>"
		done
	else
		echo "<h1>En feil oppsto under henting av alle dikt</h1>"
	fi
	echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

if [ "$ENDPOINT" = "add" ]; then
	if [ "$REQUEST_METHOD" = "GET" ]; then
		echo "<form action=\"/add\" method=\"post\">"
		echo "<label for=\"dikt\">Dikt</label>"
		echo "<textarea name=\"dikt\" id=\"dikt\" rows=\"7\" cols=\"50\" placeholder=\"Bacon ipsum\"></textarea>"
		echo "<input type=\"submit\" value=\"Legg til dikt\">"
		echo "</form>"
	elif [ "$REQUEST_METHOD" = "POST" ]; then
		insert_form_to_xml
		curl -b "sessionId=$CSESSION" -X POST -d "$XML" http://$IP/dikt | grep SUCCESS
		if [ "$?" = "0" ]; then
			echo "<h1>Diktet har nå blitt lagt til</h1>"
		else
			echo "<h1>En feil oppsto under opprettelse av dikt</h1>"
		fi
	fi
	echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

if [ "$ENDPOINT" = "update" ]; then
	if [ "$REQUEST_METHOD" = "GET" ]; then
		echo "<form action=\"/update\" method=\"post\">"
		echo "<label for=\"diktid\">DiktID:</label>"
		echo "<input name=\"diktid\" id=\"diktid\" type=\"text\" placeholder=\"ID for dikt\">"
		echo "<label for=\"dikt\">Dikt</label>"
		echo "<textarea name=\"dikt\" id=\"dikt\" rows=\"7\" cols=\"50\" placeholder=\"Bacon ipsum\"></textarea>"
		echo "<input type=\"submit\" value=\"Endre dikt\">"
		echo "</form>"
	elif [ "$REQUEST_METHOD" = "POST" ]; then
		insert_form_to_xml
		DIKTID="$(echo \"$BODY\"| sed s/\&/\\n/g | grep diktid | cut -d\"=\" -f2)"
		curl -b "sessionId=$CSESSION" -X PUT -d "$XML" http://$IP/dikt/$DIKTID | grep "SUCCESS"
		if [ "$?" = "0" ]; then
			echo "<h1>Diktet har nå blitt endret</h1>"
		else
			echo "<h1>EN feil oppsto under endring av diktet</h1>"
		fi
	fi
	echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

if [ "$ENDPOINT" = "delete" ]; then
	if [ "$REQUEST_METHOD" = "GET" ]; then
		echo "<form action=\"/deleteall\" method=\"post\">"
		echo "<label for=\"diktid\">DiktID:</label>"
		echo "<input name=\"diktid\" id=\"diktid\" type=\"text\" placeholder=\"ID for dikt\">"
		echo "<input type=\"submit\" value=\"Slett dikt\">"
		echo "</form>"
	elif [ "$REQUEST_METHOD" = "POST" ]; then
		DIKTID="$(echo \"$BODY\"| sed s/\&/\\n/g | grep diktid | cut -d\"=\" -f2)"
		curl -b "sessionId=$CSESSION" -X DELETE http://$IP/dikt/$DIKTID | grep "SUCCESS"
		if [ "$?" = "0" ]; then
			echo "<h1>Diktet har nå blitt slettet</h1>"
		else
			echo "<h1>En feil oppsto under sletting av dikt</h1>"
		fi
	fi
	echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

if [ "$ENDPOINT" = "deleteall" ]; then
	if [ "$REQUEST_METHOD" = "GET" ]; then
		echo "<h1>Ønsker du virkelig å slette alle dikt som tilhører deg?</h1>"
		echo "<form>"
		echo "<input type=\"submit\" value=\"Ja\">"
		echo "<a href=\"/\"><button>Nei</button></a>"
		echo "</form>"
	elif ["$REQUEST_METHOD" = "POST" ]; then
		curl -b "sessionId=$CSESSION" -X DELETE http://$IP/dikt/ | grep "SUCCESS"
		if [ "$?" = "0" ]; then
			echo "<h1>Alle dine dikt har nå blitt slettet</h1>"
		else
			echo "<h1>En feil oppsto under sletting av alle dine dikt</h1>"
		fi
	fi
	echo "<a href=\"/\">Tilbake til hovedsiden</a>"
fi

end_html
