# Mount hadrdrive
First install ntfs support:
```
sudo apt-get install ntfs-3g
```
Then create a mount-point:
```
sudo mkdir /media/usb_seagate
```
Then actually mount the HDD:
```
sudo mount /dev/sda /media/usb_seagate/
```

# Install python3 and packages
```
sudo apt-get install python3-pip
pip3 install yaml
```

# Install pymongo
Install through the rasbian repo
```
sudo apt-get install mongodb
pip3 install pymongo=2.9.5
```

# Set-up selenium and webdrivers
## Selenium
```
pip3 install selenium
```
## geckodriver
```
wget https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-arm7hf.tar.gz
tar -xf geckodriver-v0.17.0-arm7hf.tar.gz
rm geckodriver-v0.17.0-arm7hf.tar.gz
mv geckodriver /usr/local/bin/geckodriver
```
## Firefox and virtual x-buffer
```
sudo apt-get install firefox-esr
sudo apt-get install xvfb
```
Run commands with xvfb-run
