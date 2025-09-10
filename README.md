# Xiaomi M365 Pro - How it started?

My e-bike started giving me the **error 21** message and the annoying beep sound.  This is an indication of BMS communication failing.
I ended up with buying a new battery for my scooter.  This battery didn't have a BMS and the error21 is still there. 

## How to fix it?

After reading only for solutions all of them stated you need to flash a base firmware and problem should be fixed.   It wasn't that easy.
These are the steps I needed to take to solve it.

First, I searched for a repository which walked through the process of flashing the firmware on the DRV board. 
After searching on duckduckgo for M365 and custom firmware this following github repository seemed promising. 
It shows with images the SWD connector and expect output when running the scripts.
It's based on OpenOCD and the repo also have driver installation executable for ST_Link device.

  `git clone https://github.com/CamiAlfa/M365_DRV_STLINK`

It turned out that the repo focused on running on Windows command window.  With Python and drivers.  First I tried to use WSL-1 but it couldn't talk with the ST Link device with OpenOCD.  The second thing with the repo was the scripts is made for Python2. Thirdly there is a local copy of openocd which is v0.10.0.  Fourthly the scrips are in windows batch style.

This is why I made this repository since it contains the changes I needed to make and setup to successfully flash the DRV board using Ubuntu 24.04.

All thanks to the original repo author for his efforts.  

With that said,  let's get started!


# What is needed?

You need a ST Link V2 or similar device in order to program the stm32f1x chip on the DRV board.
You need four dupont wires to connect to the DRV board and the ST Link device.
I soldered some headers to the DRV board for easy of use.

The DRV board uses 5V and SWD.    You can use other flashing devices than a ST Link v2 but I went with buying some cheap ones on Amazon. 



# Xiaomi M365 Pro - how to flash it


## Install drivers - ST_LINK V2  - WINDOWS
In this repo there is a windows executable with the installer / drivers for ST LINK v2.
Install it if needed. Your computer will now identify your device correct afterwards.

`ST_LINK_SETUP.exe` 

I kept it here since I use a virtual machine to run Ubuntu and needed my HOST OS to properly identify the device.

The rest of my notes is for running two terminals on Ubuntu.


## Install OpenOCD - LINUX / Ubuntu 24.04

Open On-Chip Debugger, OpenOCD, must be install on your machine, current version is: `v0.12.0`

```sh
sudo apt install openocd
```


## Enable Pyhton3 venv

Activate the virtual Pyhton environment by running

```sh
source venv/bin/activate
```

## Install python3 requirements
We use the pyhton module for OpenOCD,  which is version: `v0.3.0`

```sh
python3 -m pip install -r requirements.txt
```

## Modify serial number in script

Use your favorite editor and modify the script that targets your e-bike.

Modify following line to match what is printed on the sticker 

```
serial = '16132/00224040'
```


## Terminal 1 - Running OpenOCD server

```sh
./start_ocd_STLINKV2.sh
```

or run it manually

```sh
openocd -f interface/stlink.cfg -c "transport select hla_swd" -f target/stm32f1x.cfg
```
* Modify this bash script if you want to target a different ST LINK device or a complete different device like Segger J-Link.


### Successful execution looks like this:

```
Open On-Chip Debugger 0.12.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
hla_swd
Info : The selected transport took over low-level target control. The results might differ compared to plain JTAG/SWD
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : clock speed 1000 kHz
Info : STLINK V2J37S7 (API v2) VID:PID 0483:3748
Info : Target voltage: 3.257143
Info : [stm32f1x.cpu] Cortex-M3 r1p1 processor detected
Info : [stm32f1x.cpu] target has 6 breakpoints, 4 watchpoints
Info : starting gdb server for stm32f1x.cpu on 3333
Info : Listening on port 3333 for gdb connections
Info : accepting 'tcl' connection on tcp/6666
```

## Terminal 2 - Running flash script

Run the correct python script for your e-bike model. I have a M365 Pro so I run

```sh 
python3 flash_m365_PRO.py 
```

### Successful execution looks like this in Terminal 2.

```
(venv) osboxes@osboxes:~/projects/M365_DRV_STLINK$ python3 flash_m365_PRO.py 

Connecting to OPENOCD at <localhost:6666>
Unsecuring device...
ok
Reading UUID...
done: 0670ff34 3437584e 43244613

Preparing scooter data...
Flashing scooter data...
ok
Reading UUID2...
done: 0670ff34 3437584e 43244613
```


### Successful execution looks like this in Terminal 1.
```
[stm32f1x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0xfffffffe msp: 0xfffffffc
0x670ff34 0x3437584e 0x43244613
Info : dropped 'tcl' connection
Info : accepting 'tcl' connection on tcp/6666
[stm32f1x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0xfffffffe msp: 0xfffffffc
stm32x unlocked.
INFO: a reset or power cycle is required for the new settings to take effect.

[stm32f1x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0xfffffffe msp: 0xfffffffc
0x670ff34 0x3437584e 0x43244613
[stm32f1x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0xfffffffe msp: 0xfffffffc
** Programming Started **
Warn : Adding extra erase range, 0x08000c20 .. 0x08000fff
** Programming Finished **
** Verify Started **
** Verified OK **
[stm32f1x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x08000120 msp: 0x20000550
** Programming Started **
Warn : Adding extra erase range, 0x08007ab8 .. 0x08007bff
** Programming Finished **
** Verify Started **
** Verified OK **
[stm32f1x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x08000120 msp: 0x20000550
** Programming Started **
Warn : Adding extra erase range, 0x0800fa00 .. 0x0800fbff
** Programming Finished **
** Verify Started **
** Verified OK **
0x670ff34 0x3437584e 0x43244613
shutdown command invoked
```


Script will shutdown OpenOCD server running in terminal 1.


## Disable Pyhton3 venv 

Disable the virtual Pyhton environment by running

`deactivate`


# Now you have a BASE FIRMWARE

Now you have a "base firmware" onto your DRV board.
Connect everything back to the e-bike,  and start it up. 
Be really careful.  The DRV board case is in aluminum and will cause a short circut if your capacitors is charged up or battery is connected.

# Custom Firmware Generation - ANDROID

The modding community has done much and I found the scooter hacking one quite good.
To install a custom firwmare it now became all about Android related and bluetooth.

Their tools to generate a encrypted custom firmware that you can't flash using ST Link.  :(

Using the site:   https://wiki.scooterhacking.org/doku.php?id=start

You can install their android app from playstore or install their .apk package.

## Create your legacy firmware
Now you need to create a custom firmware from their WEB API.
 
https://mi.cfw.sh/#


There are many options but the most important one is that since my replacement battery doesn't have a BMS. 
I must enable the checkbox:  **"Disable BMS communication"**


## Download your legacy encrypted custom firmware 

Click "Download LEGACY ZIP (v1 & v2)". 

You now have a firmware file and you must use their App to flash it onto your e-bike.

## Push file to your Android phone.
When doing this you must first have enabled USB-Debugging and also allowed adb to run.

First use `adb.exe` or `adb` to  upload the encrypted firmware zip package to download folder on your phone.

  `adb.exe push c:\OnePlus\ESC1_DRV155-0x68bf330f.zip /sdcard/Download`

## Install APK on your Android phone.

`adb.exe install  <name_of_app.apk>`

## Flash your legacy encrypted custom firmware
- Start the android app and choose "flash custom" 
- select your zip file 

and the app will complain that this is a legacy zip.
You now must "enable legacy", once done, select firmware file and flash it.

It takes quite a long time. 

# All done!

Start up Your e-bike and no more **error 21**!

_success!_