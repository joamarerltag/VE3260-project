FROM baseimage:latest

ADD container3.cgi ../cgi-bin
RUN echo "ScriptAliasMatch .* /usr/local/apache2/cgi-bin/container3.cgi" >> ../conf/httpd.conf

EXPOSE 80/tcp

#Start apache server
CMD ["/usr/local/apache2/bin/httpd", "-D", "FOREGROUND"]

