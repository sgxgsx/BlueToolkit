#!/bin/bash
sudo apt-get update
# Core Python and build essentials
sudo apt-get install -y python3 python3-dev python3-pip build-essential python3.11-venv python3-venv
# Bluetooth core dependencies
sudo apt-get install -y bluez bluetooth libbluetooth-dev
# PulseAudio Bluetooth module
sudo apt-get install -y pulseaudio-module-bluetooth
# Development, system utilities and Python dependencies
sudo apt-get install -y zstd unzip git python-is-python3 rfkill meson patchelf ubertooth adb python3-pip python3-dev python3-cairo-dev libcairo2-dev libgirepository1.0-dev libdbus-1-dev bluez-tools
# System libraries
sudo apt-get install -y libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev zlib1g-dev libncurses5-dev libnss3-dev libreadline-dev libffi-dev wget
# ARM and Android tools
sudo apt-get install -y binutils-arm-linux-gnueabi openjdk-17-jdk openjdk-17-jre android-sdk-platform-tools

# Configure Bluetooth adapter
sudo killall pulseaudio
sudo -u vagrant pulseaudio --start
sudo systemctl restart bluetooth

# Creating a base directory and assigning to a current user
mkdir /usr/share/BlueToolkit
sudo chown $USER:$USER /usr/share/BlueToolkit

# cloning bluekit
git clone https://github.com/sgxgsx/bluekit.git /usr/share/BlueToolkit/bluekit
mkdir /usr/share/BlueToolkit/bluekit/.logs 
mkdir /usr/share/BlueToolkit/modules
mkdir /usr/share/BlueToolkit/modules/tools -p

python3 -m venv /usr/share/BlueToolkit/.venv
source /usr/share/BlueToolkit/.venv/bin/activate
python3 -m pip install pwntools cmd2 pure-python-adb pyelftools==0.29 2to3 scapy psutil tqdm pyyaml setuptools #--break-system-packages
python3 -m pip install tabulate colorama 

# Install pybluez
python3 -m pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez #--break-system-packages

# installing bluekit
cd /usr/share/BlueToolkit/bluekit/
pip install .

## Installing tools in modules
cd /usr/share/BlueToolkit/modules

#### BluetoothAssistant
##### Needs access to the phone, it should be plugged in!!
git clone https://github.com/sgxgsx/BluetoothAssistant /usr/share/BlueToolkit/modules/BluetoothAssistant

cd BluetoothAssistant
chmod +x /usr/share/BlueToolkit/modules/install.sh
/usr/share/BlueToolkit/modules/BluetoothAssitant/install.sh
cd ..

#### Bdaddr
git clone https://github.com/thxomas/bdaddr /usr/share/BlueToolkit/modules/bdaddr

cd /usr/share/BlueToolkit/modules/bdaddr
make
cd ..


## Installing tools in modules/tools
cd /usr/share/BlueToolkit/modules/tools

#### Installing braktooth

wget https://github.com/Matheus-Garbelini/braktooth_esp32_bluetooth_classic_attacks/releases/download/v1.0.1/release.zip
mv release.zip braktooth.zip
mkdir /usr/share/BlueToolkit/modules/tools/braktooth
cd /usr/share/BlueToolkit/modules/tools/braktooth
unzip ../braktooth.zip
rm -f ../braktooth.zip

unzip esp32driver.zip
cd ..

#### Cannot install it as there might be no Braktooth connected to the machine

#### Installing bluing

mkdir /usr/share/BlueToolkit/modules/tools/bluing
cd /usr/share/BlueToolkit/modules/tools/bluing

wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
tar -xvf Python-3.10.0.tgz

cd Python-3.10.0
./configure --enable-optimizations
make -j 4
sudo make altinstall
cd ..

#wget https://salsa.debian.org/debian/dbus-python/-/archive/upstream/1.3.2/dbus-python-upstream-1.3.2.tar.gz
#tar -xvzf dbus-python-upstream-1.3.2.tar.gz
#cd dbus-python-upstream-1.3.2
#./configure
#make
#sudo make install
#sudo python3.10 setup.py install
#sudo cp -r dbus/ /usr/local/lib/python3.10/site-packages/
#cd ..


mkdir bluing
cd bluing

sudo python3.10 -m pip install --upgrade pip
sudo python3.10 -m pip install venv # would fail, but might be needed
sudo python3.10 -m venv bluing
source bluing/bin/activate

sudo python3.10 -m pip install dbus-python==1.2.18
sudo python3.10 -m pip install --no-dependencies bluing PyGObject docopt btsm btatt bluepy configobj btl2cap pkginfo xpycommon halo pyserial bthci btgatt log_symbols colorama spinners six termcolor

cd ../..
source /usr/share/BlueToolkit/.venv/bin/activate

#### Installing BLUR

cd /usr/share/BlueToolkit/modules/tools
git clone https://github.com/francozappa/blur

#### Installing Internalblue, blueborne, bleedingteeth, custom_exploits

git clone https://github.com/sgxgsx/bluetoothexploits /usr/share/BlueToolkit/modules/tools/blueexploits

cp -R /usr/share/BlueToolkit/modules/tools/blueexploits/custom_exploits /usr/share/BlueToolkit/modules/tools/custom_exploits
cp -R /usr/share/BlueToolkit/modules/tools/blueexploits/bleedingtooth /usr/share/BlueToolkit/modules/tools/bleedingtooth
cp -R /usr/share/BlueToolkit/modules/tools/blueexploits/blueborne /usr/share/BlueToolkit/modules/tools/blueborne
cp -R /usr/share/BlueToolkit/modules/tools/blueexploits/hi_my_name_is_keyboard /usr/share/BlueToolkit/modules/tools/hi_my_name_is_keyboard
rm -rf /usr/share/BlueToolkit/modules/tools/blueexploits

gcc -o /usr/share/BlueToolkit/modules/tools/bleedingtooth/poc_badchoice_cve_2020_12352 /usr/share/BlueToolkit/modules/tools/bleedingtooth/poc_badchoice_cve_2020_12352.c -lbluetooth
gcc -o /usr/share/BlueToolkit/modules/tools/bleedingtooth/poc_badkarma_cve_2020_12351 /usr/share/BlueToolkit/modules/tools/bleedingtooth/poc_badkarma_cve_2020_12351.c -lbluetooth
gcc -o /usr/share/BlueToolkit/modules/tools/bleedingtooth/poc_badvibes_cve_2020_24490 /usr/share/BlueToolkit/modules/tools/bleedingtooth/poc_badvibes_cve_2020_24490.c -lbluetooth
gcc -o /usr/share/BlueToolkit/modules/tools/bleedingtooth/exploit /usr/share/BlueToolkit/modules/tools/bleedingtooth/exploit.c -lbluetooth

#### Internal Blue

cd /usr/share/BlueToolkit/modules/tools/
git clone https://github.com/seemoo-lab/internalblue /usr/share/BlueToolkit/modules/tools/internalblue

cp /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect.py /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_0a_00.py 
cp /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect.py /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_16_0b.py 
cp /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect.py /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_20_17.py 
rm -f /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect.py
sed -i 's/LMP_VSC_CMD_START = 0x0f/LMP_VSC_CMD_START = 0x0a/' /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_0a_00.py
sed -i 's/LMP_VSC_CMD_END = 0x06/LMP_VSC_CMD_END = 0x00/' /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_0a_00.py
sed -i 's/LMP_VSC_CMD_START = 0x0f/LMP_VSC_CMD_START = 0x16/' /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_16_0b.py
sed -i 's/LMP_VSC_CMD_END = 0x06/LMP_VSC_CMD_END = 0x0b/' /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_16_0b.py
sed -i 's/LMP_VSC_CMD_START = 0x0f/LMP_VSC_CMD_START = 0x20/' /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_20_17.py
sed -i 's/LMP_VSC_CMD_END = 0x06/LMP_VSC_CMD_END = 0x17/' /usr/share/BlueToolkit/modules/tools/internalblue/examples/nexus5/CVE_2018_19860_Crash_on_Connect_20_17.py

python3 -m pip install https://github.com/seemoo-lab/internalblue/archive/master.zip # --break-system-packages

#### Blueborne 

cd /usr/share/BlueToolkit/modules/tools/blueborne
git clone https://github.com/sgxgsx/blueborne-CVE-2017-1000251 /usr/share/BlueToolkit/modules/tools/blueborne/blueborne-CVE-2017-1000251
cd /usr/share/BlueToolkit/modules/tools/blueborne/blueborne-CVE-2017-1000251
gcc -o blueborne_cve_2017_1000251 blueborne.c -lbluetooth
export PYTHONPATH=$PYTHONPATH:$(pwd)/tools/blueborne

# create wrapper script
cat > /usr/local/bin/bluekit << 'EOF'
#!/bin/bash
source /usr/share/BlueToolkit/.venv/bin/activate
bluekit "$@"
EOF
sudo chmod +x /usr/local/bin/bluekit
