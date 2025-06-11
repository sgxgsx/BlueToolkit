#!/bin/bash

sudo apt-get install libpulse0
sudo apt-get install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
sudo apt-get install libc-ares-dev 


# if won't work uncomment 
#sudo apt install g++ libglib2.0-dev libqt5multimedia5 libsnappy1v5 libsmi2ldbl libc-ares2 libnl-route-3-200  libfreetype6 graphviz libtbb-dev libxss1 libnss3 libspandsp2 libsbc1 libbrotli1 libnghttp2-14 libasound2 psmisc sshpass      libpulse0 libasound2 libpcre2-dev -y


wget https://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2.20_amd64.deb
rm -f libssl1.1_1.1.1f-1ubuntu2.20_amd64.deb

source /usr/share/BlueToolkit/.venv/bin/activate

cd /usr/share/BlueToolkit/modules/tools/braktooth/release

sudo python3 firmware.py flash /dev/ttyUSB1
cd ../

tar -I zstd -xf wdissector.tar.zst
cd wdissector
cat ./requirements.sh | sed -e 's/qt5-default//' > ./requirements2.sh
chmod +x ./requirements2.sh

sudo ./requirements2.sh
