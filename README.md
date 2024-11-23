# Pandas Digital Scale
a Python-based application designed to streamline inventory cycle counting by leveraging weight-based calculations. Ideal for businesses managing thousands of SKUs, this system integrates a digital scale with a pandas data frame, allowing for quick and accurate quantity measurements without the need for repetitive sampling.

Hardware Requirement
- Raspberry Pi (Zero/Zero W/Zero 2 W/4/5)
- Micro SD card (8GB and above)
- OLED Screen (Waveshare 2.4)
- Barcode Scanner
- Digital Scale with (RS232/USB port)
- Micro USB cable
- 5.5V USB Adapter
- PC or Mac to download Raspberry Pi OS

## Step 1. Setup Raspberry Pi
You may setup using a HDMI or an headless (without monitor).
- Please see https://www.youtube.com/watch?v=9fEnvDgxwbI&t=217s or anyother link to setup your Raspberry Pi OS.

## Step 2. Download the Pandas Digital Scale and install dependencies using setup.sh
```
sudo apt-get install git
git clone https://github.com/hanklokyaw/Pandas-Digital-Scale.git
cd Pandas-Digital-Scale
sudo chmod +x setup.sh
./setup.sh
```

## Step 3. Reboot the machine to use the app
```
sudo reboot
```

Please feel free to contact me at hank.lo.kyaw@gmail.com if you face any issues with the app.
