# koshinuke.py/scripts/run.sh
#
# Sample script to run server of koshinuke.py.
#
# copyright: (c) 2012 lanius
# license: Apache License, Version 2.0, see LICENSE for more details.

# Please note that this script is experimental.
# This script is tested on Ubuntu Server 10.10 in Amazon EC2 (ami-dcb400dd).
# A password may be required for sudo.

APPLICATION_ROOT=/opt/koshinuke
cd $APPLICATION_ROOT/koshinuke.py
sudo python koshinuke/koshinuke.py
