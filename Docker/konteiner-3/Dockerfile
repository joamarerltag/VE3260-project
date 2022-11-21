FROM httpd:alpine3.16

RUN apk -U upgrade \
	&& apk add libxml2-utils curl findutils sed coreutils

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data

#Copy files inn
RUN mkdir /usr/local/apache2/VE3260
WORKDIR /usr/local/apache2/VE3260
ADD container3.cgi ../cgi-bin

RUN echo "ScriptAliasMatch .* /usr/local/apache2/cgi-bin/container3.cgi" >> ../conf/httpd.conf
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> ../conf/httpd.conf

EXPOSE 80/tcp

#Start apache server
CMD ["/usr/local/apache2/bin/httpd", "-D", "FOREGROUND"]

