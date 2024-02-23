based on https://www.waveshare.com/wiki/PoE_HAT_(B)

```
git clone https://github.com/solo-yolo/poe-hat-display-app.git /var/lib/poe-hat-display-app
cd /var/lib/poe-hat-display-app

sudo apt-get install python3-pip
sudo pip install -r requirements.txt

sudo cp poe-hat-display.service /etc/systemd/system/poe-hat-display.service
sudo systemctl daemon-reload
sudo systemctl enable poe-hat-display.service
sudo systemctl start poe-hat-display.service
```