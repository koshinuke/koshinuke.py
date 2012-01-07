# koshinuke.py/scripts/create_project.sh
#
# Sample script that create a project for koshinuke.py.
#
# copyright: (c) 2012 lanius
# license: Apache License, Version 2.0, see LICENSE for more details.

# Please note that this script is experimental.
# This script is tested on Ubuntu Server 10.10 in Amazon EC2 (ami-dcb400dd).
# A password may be required for sudo.

if [ $# -ne 1 ]; then
  echo "usage: sh create_project.sh <poject_name>"
  exit 1
fi

PROJECT_ROOT=/var/koshinuke
PROJECT=$PROJECT_ROOT/$1

sudo mkdir $PROJECT
sudo chown $USER $PROJECT
sudo chgrp knusers $PROJECT
chmod g+w $PROJECT
