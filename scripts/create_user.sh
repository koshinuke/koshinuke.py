# koshinuke.py/scripts/create_user.sh
#
# Sample script that create a user for koshinuke.py.
#
# copyright: (c) 2012 lanius
# license: Apache License, Version 2.0, see LICENSE for more details.

# Please note that this script is experimental.
# This script is tested on Ubuntu Server 10.10 in Amazon EC2 (ami-dcb400dd).
# A password may be required for sudo.

if [ $# -ne 2 ]; then
  echo "usage: sh create_user.sh <user_name> <authorized_key>"
  exit 1
fi

NEWUSER=$1
AUTHKEY=$2

sudo adduser $NEWUSER
sudo gpasswd -a $NEWUSER knusers

SSH_DIR=/home/$NEWUSER/.ssh
KEYS_FILE=$SSH_DIR/authorized_keys

sudo mkdir $SSH_DIR
sudo chown $NEWUSER $SSH_DIR
sudo chgrp $NEWUSER $SSH_DIR
sudo chmod 700 $SSH_DIR

echo $AUTHKEY | sudo tee -a $KEYS_FILE
sudo chown $NEWUSER $KEYS_FILE
sudo chgrp $NEWUSER $KEYS_FILE
sudo chmod 600 $KEYS_FILE
