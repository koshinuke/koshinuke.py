# koshinuke.py/scripts/create_repository.sh
#
# Sample script that create a repository for koshinuke.py.
#
# copyright: (c) 2012 lanius
# license: Apache License, Version 2.0, see LICENSE for more details.

# Please note that this script is experimental.
# This script is tested on Ubuntu Server 10.10 in Amazon EC2 (ami-dcb400dd).
# A password may be required for sudo.

if [ $# -ne 2 ]; then
  echo "usage: sh create_repository.sh <project_name> <repository_name>"
  exit 1
fi

PROJECT_ROOT=/var/koshinuke
PROJECT=$PROJECT_ROOT/$1
REPOSITORY=$PROJECT/$2.git

git init $REPOSITORY --bare
sudo chgrp knusers $REPOSITORY -R
chmod g+w $REPOSITORY -R
