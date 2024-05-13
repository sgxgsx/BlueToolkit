sudo apt-get install -y git

mkdir /usr/share/BlueToolkit
sudo chown $USER:$USER /usr/share/BlueToolkit

git clone  https://github.com/sgxgsx/BlueToolkit /usr/share/BlueToolkit --recurse-submodules
chmod +x /usr/share/BlueToolkit/install.sh
/usr/share/BlueToolkit/install.sh




