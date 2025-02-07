#!/bin/bash

# Parse command line arguments
DEV_MODE=false
while [[ $# -gt 0 ]]; do
  case $1 in
    -dev)
      DEV_MODE=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

sudo apt-get update
# Core Python and build essentials
sudo apt-get install -y python3 python3-dev python3-pip build-essential python3.11-venv python3-venv
# Bluetooth core dependencies
sudo apt-get install -y bluez bluetooth libbluetooth-dev
# PulseAudio Bluetooth module
sudo apt-get install -y pulseaudio-module-bluetooth
# Development, system utilities and Python dependencies
sudo apt-get install -y zstd unzip git python-is-python3 rfkill meson patchelf ubertooth adb python3-pip python3-dev python3-cairo-dev libcairo2-dev libgirepository1.0-dev libdbus-1-dev bluez-tools bluez-hcidump
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

if [ "$DEV_MODE" = true ]; then
    echo "Installing bluekit in development mode..."
    pip install -e .
else
    echo "Installing bluekit..."
    pip install .
fi

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
./configure #--enable-optimizations
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

# Scapy PATCH (Github - I get a python error during the blueborne scan #12)
PYTHON_VERSION=$(find /usr/share/BlueToolkit/.venv/lib/ -maxdepth 1 -type d -name "python3.*" -printf "%f\n" | head -n 1)
FILE_PATH="/usr/share/BlueToolkit/.venv/lib/${PYTHON_VERSION}/site-packages/scapy/layers/bluetooth.py"
## First update ConfReq
perl -i -p0e 's/class L2CAP_ConfReq.*?fields_desc.*?\n\n/class L2CAP_ConfReq(Packet):\n    name = "L2CAP Conf Req"\n    fields_desc = [ LEShortField("dcid",0),\n                    LEShortField("flags",0),\n                    ByteField("type",0),\n                    ByteField("length",0),\n                    ByteField("identifier",0),\n                    ByteField("servicetype",0),\n                    LEShortField("sdusize",0),\n                    LEIntField("sduarrtime",0),\n                    LEIntField("accesslat",0),\n                    LEIntField("flushtime",0)]\n\n/s' "$FILE_PATH"
## Then update ConfResp with much more specific boundaries
perl -i -p0e 's/class L2CAP_ConfResp.*?fields_desc.*?\].*?\]/class L2CAP_ConfResp(Packet):\n    name = "L2CAP Conf Resp"\n    fields_desc = [ LEShortField("scid",0),\n                    LEShortField("flags",0),\n                    LEShortField("result",0),\n                    ByteField("type0",0),\n                    ByteField("length0",0),\n                    LEShortField("option0",0),\n                    ByteField("type1",0),\n                    ByteField("length1",0),\n                    LEShortField("option1",0),\n                    ByteField("type2",0),\n                    ByteField("length2",0),\n                    LEShortField("option2",0),\n                    ByteField("type3",0),\n                    ByteField("length3",0),\n                    LEShortField("option3",0),\n                    ByteField("type4",0),\n                    ByteField("length4",0),\n                    LEShortField("option4",0),\n                    ByteField("type5",0),\n                    ByteField("length5",0),\n                    LEShortField("option5",0),\n                    ByteField("type6",0),\n                    ByteField("length6",0),\n                    LEShortField("option6",0),\n                    ByteField("type7",0),\n                    ByteField("length7",0),\n                    LEShortField("option7",0),\n                    ByteField("type8",0),\n                    ByteField("length8",0),\n                    LEShortField("option8",0),\n                    ByteField("type9",0),\n                    ByteField("length9",0),\n                    LEShortField("option9",0),\n                    ByteField("type10",0),\n                    ByteField("length10",0),\n                    LEShortField("option10",0),\n                    ByteField("type11",0),\n                    ByteField("length11",0),\n                    LEShortField("option11",0),\n                    ByteField("type12",0),\n                    ByteField("length12",0),\n                    LEShortField("option12",0),\n                    ByteField("type13",0),\n                    ByteField("length13",0),\n                    LEShortField("option13",0),\n                    ByteField("type14",0),\n                    ByteField("length14",0),\n                    LEShortField("option14",0),\n                    ByteField("type15",0),\n                    ByteField("length15",0),\n                    LEShortField("option15",0),\n                    ByteField("type16",0),\n                    ByteField("length16",0),\n                    LEShortField("option16",0),\n                    ByteField("type17",0),\n                    ByteField("length17",0),\n                    LEShortField("option17",0),\n                    ByteField("type18",0),\n                    ByteField("length18",0),\n                    LEShortField("option18",0),\n                    ByteField("type19",0),\n                    ByteField("length19",0),\n                    LEShortField("option19",0),\n                    ByteField("type20",0),\n                    ByteField("length20",0),\n                    LEShortField("option20",0),\n                    ByteField("type21",0),\n                    ByteField("length21",0),\n                    LEShortField("option21",0),\n                    ByteField("type22",0),\n                    ByteField("length22",0),\n                    LEShortField("option22",0),\n                    ByteField("type23",0),\n                    ByteField("length23",0),\n                    LEShortField("option23",0),\n                    ByteField("type24",0),\n                    ByteField("length24",0),\n                    LEShortField("option24",0),\n                    ByteField("type25",0),\n                    ByteField("length25",0),\n                    LEShortField("option25",0),\n                    ByteField("type26",0),\n                    ByteField("length26",0),\n                    LEShortField("option26",0),\n                    ByteField("type27",0),\n                    ByteField("length27",0),\n                    LEShortField("option27",0),\n                    ByteField("type28",0),\n                    ByteField("length28",0),\n                    LEShortField("option28",0),\n                    ByteField("type29",0),\n                    ByteField("length29",0),\n                    LEShortField("option29",0),\n                    ByteField("type30",0),\n                    ByteField("length30",0),\n                    LEShortField("option30",0),\n                    ByteField("type31",0),\n                    ByteField("length31",0),\n                    LEShortField("option31",0),\n                    ByteField("type32",0),\n                    ByteField("length32",0),\n                    LEShortField("option32",0),\n                    ByteField("type33",0),\n                    ByteField("length33",0),\n                    LEShortField("option33",0),\n                    ByteField("type34",0),\n                    ByteField("length34",0),\n                    LEShortField("option34",0),\n                    ByteField("type35",0),\n                    ByteField("length35",0),\n                    LEShortField("option35",0),\n                    ByteField("type36",0),\n                    ByteField("length36",0),\n                    LEShortField("option36",0),\n                    ByteField("type37",0),\n                    ByteField("length37",0),\n                    LEShortField("option37",0),\n                    ByteField("type38",0),\n                    ByteField("length38",0),\n                    LEShortField("option38",0),\n                    ByteField("type39",0),\n                    ByteField("length39",0),\n                    LEShortField("option39",0),\n                    ByteField("type40",0),\n                    ByteField("length40",0),\n                    LEShortField("option40",0),\n                    ByteField("type41",0),\n                    ByteField("length41",0),\n                    LEShortField("option41",0),\n                    ByteField("type42",0),\n                    ByteField("length42",0),\n                    LEShortField("option42",0),\n                    ByteField("type43",0),\n                    ByteField("length43",0),\n                    LEShortField("option43",0),\n                    ByteField("type44",0),\n                    ByteField("length44",0),\n                    LEShortField("option44",0),\n                    ByteField("type45",0),\n                    ByteField("length45",0),\n                    LEShortField("option45",0),\n                    ByteField("type46",0),\n                    ByteField("length46",0),\n                    LEShortField("option46",0),\n                    ByteField("type47",0),\n                    ByteField("length47",0),\n                    LEShortField("option47",0),\n                    ByteField("type48",0),\n                    ByteField("length48",0),\n                    LEShortField("option48",0),\n                    ByteField("type49",0),\n                    ByteField("length49",0),\n                    LEShortField("option49",0),\n                    ByteField("type50",0),\n                    ByteField("length50",0),\n                    LEShortField("option50",0),\n                    ByteField("type51",0),\n                    ByteField("length51",0),\n                    LEShortField("option51",0),\n                    ByteField("type52",0),\n                    ByteField("length52",0),\n                    LEShortField("option52",0),\n                    ByteField("type53",0),\n                    ByteField("length53",0),\n                    LEShortField("option53",0),\n                    ByteField("type54",0),\n                    ByteField("length54",0),\n                    LEShortField("option54",0),\n                    ByteField("type55",0),\n                    ByteField("length55",0),\n                    LEShortField("option55",0),\n                    ByteField("type56",0),\n                    ByteField("length56",0),\n                    LEShortField("option56",0),\n                    ByteField("type57",0),\n                    ByteField("length57",0),\n                    LEShortField("option57",0),\n                    ByteField("type58",0),\n                    ByteField("length58",0),\n                    LEShortField("option58",0),\n                    ByteField("type59",0),\n                    ByteField("length59",0),\n                    LEShortField("option59",0),\n                    ByteField("type60",0),\n                    ByteField("length60",0),\n                    LEShortField("option60",0),\n                    ByteField("type61",0),\n                    ByteField("length61",0),\n                    LEShortField("option61",0),\n                    ByteField("type62",0),\n                    ByteField("length62",0),\n                    LEShortField("option62",0),\n                    ByteField("type63",0),\n                    ByteField("length63",0),\n                    LEShortField("option63",0),\n                    ByteField("type64",0),\n                    ByteField("length64",0),\n                    LEShortField("option64",0),\n                    ByteField("type65",0),\n                    ByteField("length65",0),\n                    LEShortField("option65",0),\n                    ByteField("type66",0),\n                    ByteField("length66",0),\n                    LEShortField("option66",0),\n                    ByteField("type67",0),\n                    ByteField("length67",0),\n                    LEShortField("option67",0),\n                    ByteField("type68",0),\n                    ByteField("length68",0),\n                    LEShortField("option68",0),\n                    ByteField("type69",0),\n                    ByteField("length69",0),\n                    LEShortField("option69",0)]\n/s' "$FILE_PATH"
