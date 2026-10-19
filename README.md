# lenovo-tab-m10p-unlock
A comprehensive guide to unlock the bootloader of **Lenovo Tab M10 Plus (3rd Gen) Global (TB128FU)**, with instructions of rooting and unbricking.

# Disclaimer
**Unlocking your bootloader and flashing custom software carries inherent risks, including permanent device damage ("bricking"), total data loss, voided warranties, and compromised security or app compatibility. This guide assumes you possess the necessary technical knowledge, common sense, and understanding to carry out low-level system modifications independently. By following these steps, you acknowledge that you are doing so entirely at your own risk; I assume no responsibility or liability under any circumstances for any loss, damage, hardware failure, or operational issues that may occur to your device or data.**

# Background
Lenovo decided to screw over it's global customers by completely removing the official bootloader unlocking mechanism for the global version of TB128FU. Fastboot unlock commands are ignored by the bootloader, making the official unlock method by flashing `sn.img` useless. But the chinese equivalent of this pad, Xiaoxin pad 2022 understands all fastboot commands as it should. This guide was created to provide a working workaround to bypass Lenovo’s restrictions and regain full control over your hardware.

This is an alternative and easier method to unlock bootloader compared to the HxD method. https://xdaforums.com/t/unlock-bootloader-without-proper-unlock-file-xiaoxin-pad-pro-2021-tb-j716f.4488343/

# Unlocking the bootloader

## Prerequisite
- CN Rom `TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714` (May not be specifally to this one, but the one I used)
- ADB and fastboot tools, drivers
- QFIL (Qualcomm Flash Image Loader)
- Rescue and Smart Assistant (RSA)

Please search them up yourself, this guide will not provide any links or supports to these software.

## Method Overview

This unlocking procedure works by replacing the restricted global (ROW) Android Bootloader (ABL) with a firmware build from the Chinese (CN) region that retains functional unlock parameters.

### Technical Workflow

1. Flash the official CN firmware build `TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714` using QFIL in EDL mode.
2. Reboot the device into fastboot mode.
3. Retrieve the required ZUI unlock identifier using fastboot commands.
4. Download the generated bootloader key (`sn.img`) from Lenovo's CDN server.
5. Flash the unlock key and execute the OEM unlock command.

> [!NOTE]
> The standard 8-digit hardware serial number printed on the device or shown in global settings will not work to generate a valid unlock file. On ROW ABL, running `fastboot getvar unlock_id` returns `GetVar Variable Not found`. The China ABL generates a distinct 8-digit
> unlock identifier string required specifically by Lenovo's ZUI token service. This code can only be generated and retrieved once the tablet is running the China bootloader.

### Steps
1. Once booted into fastboot mode on the CN firmware, retrieve your device-specific unlock identifier:
```bash
fastboot getvar unlock_id
```

This should split out a 8-digit code, in this case it is `69acbd04`, note it down.

> [!NOTE]
> Normally, you put this code directly in zui unlock site, but don't waste time doing that as you need a reachable Chinese email and most of the time you will not receive the email for the `sn.img`.

2. After that, insert the returned 8-digit identifier into the following URL parameter to download your unique unlock token:
```
http://cdn.zui.lenovomm.com/developer/tabletboot/[unlock_id]/sn.img

In this case:
http://cdn.zui.lenovomm.com/developer/tabletboot/69acbd04/sn.img
```

3. Flash the downloaded sn.img file and complete the bootloader unlock.
```bash
fastboot flash unlock sn.img
fastboot oem unlock-go
```
It should look like this if successful.
<img width="806" height="87" alt="image" src="https://github.com/user-attachments/assets/2a233768-3333-418f-978c-3623d9f77f3a" />

4. You are almost there. Now the system won't boot and shown as corrupted, because the device won't recognize a mismatched CN rom, you can either reflash a ROW ABL using QFIL or just use the Lenovo RSA to rescue and revert to global ROM.
5. Congrats, you have succesfully unlocked the bootloader!

# Rooting
With the bootloader unlcoked, you now have full control of your device. To gain root, simply extract `boot.img` from stock firmware or directly from device, patch it via Magisk/KernelSU or any other root manager, please follow their respective guides.

*Unfinished*

# Flash GSI/Custom rom

*Unfinished*

# Recovering wiped oem partition

> [!WARNING]
> **Important Warning:** This manual reconstruction method should be used as a **last resort**. Manual editing can only generates placeholder network parameters and basic flag entries. Before attempting this, always try Lenovo's official recovery software first, or flash an exact 1:1 partition backup dumped from a working unit of the same model.

Using QFIL with **"Erase All Before Download"** WILL wipes critical low-level partitions, stripping out hardware identifiers (Serial Number, MAC addresses, region codes) and causing **Settings** and **Developer Options** to crash.

This guide covers how to restore the device if official tools cannot recover the hardware identity parameters.

---

## Prerequisites
* A Windows PC with **Qualcomm QFIL** and Qualcomm USB drivers installed.
* Your device's **Serial Number** (e.g., `HA1MW91Y`).
* A clean `persist.img` dump for the **TB128FU**.
* **Python** installed on your PC or somewhere you can run the program.

---

## Step 1: Try official Lenovo software recovery
Before manually editing binary files, attempt to recover your tablet using official software:

1. Download and install **Rescue and Smart Assistant (RSA)** (Lenovo's official repair software) on your PC.
2. Connect your device and select **Rescue Mode**.
3. Follow the on-screen instructions to automatically download and reflash official firmware for the TB128FU.

RSA is unlikely to help you recover deleted critical low-level partitions.

---

## Step 2: Generate `oem_fixed.img`
Because a wiped `oem` partition is filled with zeroes, you must inject your hardware data at correct binary offsets.

### OEM Offset Map
| Offset (Hex) | Field Name | Format | Example Value |
| :--- | :--- | :--- | :--- |
| `0x00` | Board Number | 23 ASCII chars | `HA1MW91Y000000000000000` |
| `0x20` | Serial Number | 8 ASCII chars | `HA1MW91Y` |
| `0xA0` | Bluetooth MAC | 17 ASCII chars (`XX:XX:XX:XX:XX:XX`) | `54:E4:3A:1B:2C:3F` |
| `0xC0` | Wi-Fi MAC | 17 ASCII chars (`XX:XX:XX:XX:XX:XX`) | `54:E4:3A:1B:2C:3E` |
| `0x0152` | Region Code | 4 ASCII chars | `HKXX` (or `ROW`, `GBXX`) |
| `0x0172`| Flag Byte | `0x01` byte value | |

Use the script located in the [/Scripts/] folder to automatically create one *(Credit to the community for finding the layout structure)*

---

## Step 3: Flash via QFIL Partition Manager
> [!NOTE]
> Avoid using `fastboot` to flash `oem`, as it may fail due to dynamic partition restrictions.

1. Power off the tablet and boot into **EDL Mode (Qualcomm 9008)** (`Vol Up` or EDL test point while plugging in the USB cable)
2. Open QFIL and select Tools > Partition Manager
3. Right-click `oem` > **Manage Partition > Load Image > Select `oem_fixed.img`
4. Right-click `persist` > **Manage Partition > Load Image > Select clean `persist.img`
5. Close Partition Manager and disconnect the tablet

---

## Step 4: Factory Reset
1. Boot into stock **Recovery Mode**
2. Select **Wipe Data / Factory Reset**
3. Reboot into system

---

## Verification
* Go to **Settings > About Tablet** to verify your serial number and MAC addresses appear correctly
* Open **Developer Options** to confirm it launches without crashing
