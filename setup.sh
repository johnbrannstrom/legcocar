#!/bin/bash

# Setup Linux environment for project

# Name of project
PROJECT="legcocar"

# List of packages to install with apt
APT_PACKAGES=(\
"python3=3.7.3-1" \
"openssl=1.1.1c-1" \
"build-essential=12.6" \
"tk-dev=8.6.9+1" \
"libncurses5-dev=6.1+20181013-2+deb10u2" \
"libncursesw5-dev=6.1+20181013-2+deb10u2" \
"libreadline-dev=7.0-5" \
"libgdbm-dev=1.18.1-4" \
"libsqlite3-dev=3.27.2-3" \
"libssl-dev=1.1.1d-0+deb10u2" \
"libbz2-dev=1.0.6-9.2~deb10u1" \
"libexpat1-dev=2.2.6-2+deb10u1" \
"liblzma-dev=5.2.4-1" \
"zlib1g-dev=1:1.2.11.dfsg-1" \
"libffi-dev=3.2.1-9" \
"uuid-dev=2.33.1-0.1" \
"python3-pip=18.1-5+rpt1" \
"apache2=2.4.38-3+deb10u3" \
"libapache2-mod-wsgi=4.6.5-1"
)

# List of packages to install with pip3
PIP3_PACKAGES=(\
"bricknil==0.9.3" \
"flask==1.1.1"
)

# Current location compared to script location
DIR=$(dirname "$(readlink -f "$0")")

# Run command and then echo command and status
# If the command did not run without error, we exit
run_echo () {
  eval $1 > /dev/null
  if [ "${?}" -eq "0" ]
  then
    echo -ne "[ \e[1;32m OK  \033[0m ] "
    echo "${1}"
  else
    echo -ne "[ \e[1;91mERROR\033[0m ] "
    echo "${1}"
  fi
}

# Set bash_aliases for root
sed -i "/alias ls='ls -lah --color=auto'/d" /root/.bashrc
run_echo "echo \"alias ls='ls -lah --color=auto'\" >> /root/.bashrc"

# Install packages with apt
run_echo "apt-get update"
for PACKAGE in "${APT_PACKAGES[@]}"
do
  run_echo "apt-get -y install ${PACKAGE}"
done

# Install packages with pip3
for PACKAGE in "${PIP3_PACKAGES[@]}"
do
  run_echo "pip3 install ${PACKAGE}"
done

# Create project user
run_echo "useradd -m ${PROJECT}"

# Create directories, move files, and set permissions
rm -Rf /srv/flask_wsgi
rm -Rf /srv/${PROJECT}
run_echo 'mkdir /srv/flask_wsgi'
run_echo "mkdir /srv/${PROJECT}"
run_echo "mv ${DIR}/html_static /srv/${PROJECT}/"
run_echo "mv ${DIR}/html_templates /srv/${PROJECT}/"
run_echo "mv ${DIR}/src/flaskserver.py /srv/${PROJECT}/"
run_echo "mv ${DIR}/src/wsgi.py /srv/flask_wsgi/"
run_echo "mv ${DIR}/other/000-default.conf /etc/apache2/sites-available/"
run_echo "chown -R ${PROJECT}:${PROJECT} /srv/flask_wsgi"
run_echo "chmod 755 /srv/flask_wsgi"
run_echo "chown -R ${PROJECT}:${PROJECT} /srv/${PROJECT}"
run_echo "chmod 755 /srv/${PROJECT}"

# Restart apache2 for settings to take affect
run_echo "service apache2 restart"
