https://www.waveshare.com/wiki/PoE_HAT_(B)

```
sudo raspi-config
# Interfacing Options -> I2C -> Yes

sudo reboot

sudo apt-get install build-essential
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
sudo make install

sudo apt-get install python3-pip
sudo apt-get install python3-smbus

pip -r requirements.txt

sudo python app/main.py
```