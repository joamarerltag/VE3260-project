FROM baseimage:latest

RUN apk -U upgrade \
	&& apk add sqlite uuidgen

ADD restAPI-test.cgi ../cgi-bin
ADD create.sql .
RUN echo "ScriptAliasMatch .* /usr/local/apache2/cgi-bin/restAPI-test.cgi" >> ../conf/httpd.conf
RUN echo "<Directory />" >> ../conf/httpd.conf
RUN echo "    Header set Access-Control-Allow-Origin http://138.68.92.43" >> ../conf/httpd.conf
RUN echo "    Header set Access-Control-Allow-Headers Content-Type" >> ../conf/httpd.conf
RUN echo "    Header set Access-Control-Allow-Methods POST,PUT,DELETE" >> ../conf/httpd.conf
RUN echo "    Header set Access-Control-Allow-Credentials true" >> ../conf/httpd.conf
RUN echo "</Directory>" >> ../conf/httpd.conf

#Make db folder and creates db
RUN mkdir db
RUN cat create.sql | sqlite3 db/diktDB.db
RUN chmod g+w db/diktDB.db
RUN chown -R www-data:www-data ../VE3260

EXPOSE 80/tcp

#Start apache server
CMD ["/usr/local/apache2/bin/httpd", "-D", "FOREGROUND"]

