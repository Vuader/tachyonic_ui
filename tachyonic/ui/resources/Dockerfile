FROM ubuntu
RUN apt-get update 
RUN apt-get --assume-yes install apache2 
RUN apt-get --assume-yes install apache2-dev
RUN apt-get --assume-yes install apache2-utils
RUN apt-get --assume-yes install libcurl4-openssl-dev libssl-dev
RUN apt-get --assume-yes install python3
RUN apt-get --assume-yes install python3-dev
RUN apt-get --assume-yes install python3-pip
RUN echo "mysql-server-5.6 mysql-server/root_password password password" | debconf-set-selections
RUN echo "mysql-server-5.6 mysql-server/root_password_again password password" | debconf-set-selections
RUN apt-get --assume-yes install mysql-server
RUN apt-get --assume-yes install git
RUN apt-get clean 

RUN pip3 install mod-wsgi
RUN echo 'LoadModule wsgi_module "/usr/local/lib/python3.5/dist-packages/mod_wsgi/server/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so"' > /etc/apache2/mods-available/wsgi.load
RUN a2enmod wsgi

WORKDIR /root
ADD https://api.github.com/repos/TachyonicProject/tachyonic/git/refs/heads/development /root/tachyonic.json
RUN git clone https://github.com/TachyonicProject/tachyonic.git
ADD https://api.github.com/repos/TachyonicProject/tachyonic_neutrino/git/refs/heads/development /root/tachyonic_neutrino.json
RUN git clone -b development https://github.com/TachyonicProject/tachyonic_neutrino.git
ADD https://api.github.com/repos/TachyonicProject/tachyonic_api/git/refs/heads/development /root/tachyonic_api.json
RUN git clone -b development https://github.com/TachyonicProject/tachyonic_api.git
ADD https://api.github.com/repos/TachyonicProject/tachyonic_ui/git/refs/heads/development /root/tachyonic_ui.json
RUN git clone https://github.com/TachyonicProject/tachyonic_ui.git
WORKDIR /root/tachyonic
RUN pip3 install .
WORKDIR /root/tachyonic_neutrino
RUN pip3 install .
WORKDIR /root/tachyonic_api
RUN pip3 install .
WORKDIR /root/tachyonic_ui
RUN pip3 install .
WORKDIR /var/www
RUN mkdir tachyonic_api
RUN tachyonic -s tachyonic.api tachyonic_api
RUN mkdir tachyonic_ui
RUN tachyonic -s tachyonic.ui tachyonic_ui
RUN chown -R www-data:www-data tachyonic_api/tmp
RUN chown -R www-data:www-data tachyonic_ui/tmp

RUN (chown -R mysql:mysql /var/lib/mysql /var/run/mysqld \
             && service mysql start; service mysql start \
             && mysql -ppassword -e "create database tachyon;" \
             && mysql -ppassword -e "grant all on tachyon.* to tachyon identified by 'password';" \
             && mysql -ppassword -e "flush privileges;" \
             && mysql -ppassword tachyon < /root/tachyonic_api/db.sql)

ADD https://raw.githubusercontent.com/TachyonicProject/tachyonic/development/000-default.conf /etc/apache2/sites-available/

EXPOSE 80
CMD service apache2 start && (chown -R mysql:mysql /var/lib/mysql /var/run/mysqld && service mysql start) && bash
