FROM httpd:alpine3.16

RUN apk -U upgrade \
	&& apk add libxml2-utils curl findutils coreutils sed

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data

#Copy files in
RUN mkdir /usr/local/apache2/VE3260
WORKDIR /usr/local/apache2/VE3260
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> ../conf/httpd.conf
