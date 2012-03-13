# koshinuke.py/scripts/install.sh
#
# Sample script to install koshinuke.py.
#
# copyright: (c) 2012 lanius
# license: Apache License, Version 2.0, see LICENSE for more details.

# Please note that this script is experimental.
# This script is tested on Ubuntu Server 10.10 in Amazon EC2 (ami-dcb400dd).
# A password may be required for sudo.

# Install necessary tools
echo "--- Install necessary tools ---"
sudo aptitude install git -y
sudo aptitude install python-pip -y
sudo aptitude install subversion  -y  # for checkout closure-library

# Create koshinuke user group
echo "--- Create koshinuke user group ---"
sudo addgroup knusers

# Create project root
echo "--- Create project root ---"
PROJECT_ROOT=/var/koshinuke
sudo mkdir $PROJECT_ROOT
sudo chown $USER $PROJECT_ROOT  # change owner/group temporarily
sudo chgrp $USER $PROJECT_ROOT

# Setting chroot for koshinuke users
echo "--- Setting chroot for koshinuke users ---"
echo "Match Group knusers" | sudo tee -a /etc/ssh/sshd_config
echo "  ChrootDirectory /var/koshinuke" | sudo tee -a /etc/ssh/sshd_config
sudo service ssh restart

# Copy bash, git, git-upload-pack, git-receive-pack, 
# and necessary objects for using git on chroot. 
# It can be found out by command "ldd \`which git\`" for example::
mkdir $PROJECT_ROOT/bin
mkdir $PROJECT_ROOT/usr/bin -p
mkdir $PROJECT_ROOT/lib
mkdir $PROJECT_ROOT/lib64

sudo cp /bin/bash $PROJECT_ROOT/bin/bash
sudo cp /usr/bin/git $PROJECT_ROOT/usr/bin/git
sudo cp /usr/bin/git-upload-pack $PROJECT_ROOT/usr/bin/git-upload-pack
sudo cp /usr/bin/git-receive-pack $PROJECT_ROOT/usr/bin/git-receive-pack

sudo cp /lib/libz.so.1 $PROJECT_ROOT/lib/libz.so.1
sudo cp /lib/libpthread.so.0 $PROJECT_ROOT/lib/libpthread.so.0
sudo cp /lib/libncurses.so.5 $PROJECT_ROOT/lib/libncurses.so.5
sudo cp /lib/libdl.so.2 $PROJECT_ROOT/lib/libdl.so.2
sudo cp /lib/libc.so.6 $PROJECT_ROOT/lib/libc.so.6
sudo cp /lib64/ld-linux-x86-64.so.2 $PROJECT_ROOT/lib64/ld-linux-x86-64.so.2

# Project root must be owned by root user for chroot. 
# For this reason, sadly need to use sudo to create koshinuke project later::
sudo chown root $PROJECT_ROOT

# Download koshinuke.py source code and install python module
echo "--- Download koshinuke.py source code and install python module ---"
APPLICATION_ROOT=/opt/koshinuke
sudo mkdir $APPLICATION_ROOT
sudo chown $USER $APPLICATION_ROOT
sudo chgrp $USER $APPLICATION_ROOT
cd $APPLICATION_ROOT
git clone git://github.com/koshinuke/koshinuke.py.git
cd koshinuke.py
sudo pip install -r requirements.txt

# Download koshinuke client source code and closure-library
echo "--- Download koshinuke client source code and closure-library ---"
cd $APPLICATION_ROOT
git clone git://github.com/koshinuke/koshinuke.git
cd koshinuke
TEMPLATE_DIR=$APPLICATION_ROOT/koshinuke.py/koshinuke/templates
mkdir $TEMPLATE_DIR
cp *.html $TEMPLATE_DIR
cp static $APPLICATION_ROOT/koshinuke.py/koshinuke/ -R
cd $APPLICATION_ROOT/koshinuke.py/koshinuke/static
svn co http://closure-library.googlecode.com/svn/trunk/ closure-library

# Complete
echo "KoshiNuke is installed."
echo "Please edit '$APPLICATION_ROOT/koshinuke.py/koshinuke/config.py'"
echo "to suit your environment. "
