FROM httpd:alpine3.16

RUN apk -U upgrade \
	&& apk add libxml2-utils curl sqlite uuidgen findutils coreutils

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data

#Copy files inn
RUN mkdir /usr/local/apache2/VE3260
WORKDIR /usr/local/apache2/VE3260
ADD restAPI-test.cgi ../cgi-bin
ADD create.sql .
RUN echo "ScriptAliasMatch .* /usr/local/apache2/cgi-bin/restAPI-test.cgi" >> ../conf/httpd.conf
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> ../conf/httpd.conf

#Make db folder and creates db
RUN mkdir db
RUN cat create.sql | sqlite3 db/diktDB.db
RUN chmod g+w db/diktDB.db
RUN chown -R www-data:www-data ../VE3260

EXPOSE 80/tcp

#Start apache server
CMD ["/usr/local/apache2/bin/httpd", "-D", "FOREGROUND"]

