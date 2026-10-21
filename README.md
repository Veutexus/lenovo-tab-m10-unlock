# lenovo-tab-m10p-unlock
A comprehensive guide to unlock the bootloader of **Lenovo Tab M10 Plus (3rd Gen) Global (TB128FU)**, with instructions of rooting and unbricking. It is also reported to work with other models like the TB128XU, try it at your own risk.

> [!NOTE]
> This guide is a work in progress.

# Disclaimer
**Unlocking your bootloader and flashing custom software carries inherent risks, including permanent device damage (bricking), total data loss, voided warranties, and compromised security or app compatibility. This guide assumes you possess the necessary technical knowledge, common sense, and understanding to carry out low-level system modifications independently. By following these steps, you acknowledge that you are doing so entirely at your own risk; I assume no responsibility or liability under any circumstances for any loss, damage, hardware failure, or operational issues that may occur to your device or data.**

# Background
Lenovo decided to screw over it's global customers by completely removing the official bootloader unlocking mechanism for the global version of TB128FU. Fastboot unlock commands are ignored by the bootloader, making the official unlock method by flashing `sn.img` useless. But the chinese equivalent of this pad, Xiaoxin pad 2022 understands all fastboot commands as it should. This guide was created to provide a working workaround to bypass Lenovo’s restrictions and regain full control over your hardware.

This is a fairly easy alternative method for unlocking the bootloader compared to the [hex edit method](https://xdaforums.com/t/unlock-bootloader-without-proper-unlock-file-xiaoxin-pad-pro-2021-tb-j716f.4488343/), which is considerably harder. ([4PDA thread](https://4pda.to/forum/index.php?showtopic=1047797&st=660#entry116826199))

# Repository contents

Not everything in this repository is required to unlock the tablet. Read the warnings before flashing anything.

| Path | What it is | Warning / status |
| :--- | :--- | :--- |
| `README.md` | This guide. | Rooting, GSI and custom recovery sections are unfinished. |
| `abl.elf` | Qualcomm ABL bootloader image (ELF32 ARM, Lenovo-signed). | Not referenced by the steps below, and its exact model/firmware build is not documented. Do not flash it unless you have verified it against a known-good dump. |
| `sn.img` | ZUI unlock token containing `unlock_id` `69acbd04`. | Device-specific. It is only useful for the author's device; generate your own token. |
| `Scripts/restore_oem.py` | Generates a 1 MB `oem_fixed.img` with hard-coded identity values. | The serial number is hard-coded to an example value and the MAC addresses are placeholders. Edit them before running. |
| `Scripts/restore_oem_advanced.py` | Same as above, but generates random MAC addresses. | Still hard-codes the serial number. Prefer the MACs printed on your device label. |
| `Modules/default-screen-rotation/` and `.zip` | Optional Magisk module that sets `ro.sf.hwrotation=90`. | Not required for unlocking. Its module id is still `disable-hw-overlays`, which may conflict with other modules; test it before relying on it. |
| `Modules/Grass-perf@0910-102621.zip` | AnyKernel3 kernel package. | **Do not flash on TB128FU.** Its `version` file identifies it as a Samsung Galaxy A51 (A515F, Exynos 9611) kernel, not a Snapdragon 680 kernel. `do.devicecheck=0` means it will not check the device. |

# Unlocking the bootloader

## Prerequisites
- CN ROM `TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714` (Not necessarily this one, but the one I used)
- ADB and fastboot tools, drivers
- QFIL (Qualcomm Flash Image Loader) and Qualcomm USB drivers installed
- Rescue and Smart Assistant (RSA) (Optional)

Please download them yourself; this guide will not provide links to these tools.

## Method overview

This unlocking procedure works by replacing the restricted global (ROW) Android Bootloader (ABL) with a firmware build from the Chinese (CN) region that retains functional unlock parameters.

### Technical workflow

1. Flash the official CN ROM `TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714` using QFIL in EDL mode.
2. Reboot the device into fastboot mode.
3. Retrieve the required ZUI unlock identifier using fastboot commands.
4. Download the generated bootloader key (`sn.img`) from Lenovo's CDN server.
5. Flash the unlock key and execute the OEM unlock command.

> [!NOTE]
> The standard 8-digit hardware serial number printed on the device or shown in global settings will not work to generate a valid unlock file. On ROW ABL, running `fastboot getvar unlock_id` returns `GetVar Variable Not found`. The China ABL generates a distinct 8-digit
> unlock identifier string required specifically by Lenovo's ZUI token service. This code can only be generated and retrieved once the tablet is running the China bootloader.

> [!WARNING]
> Please backup everything before you start! Logout any Google accounts and remove any device protection.

### Steps

#### Step 1: Flash the CN firmware with QFIL (EDL mode)

1. Enable **OEM unlocking** in Developer options, then power the tablet off completely. Remove any screen lock, Google account and device protection first; a locked FRP account can block the first boot after flashing.
2. Download and extract the CN ROM package (`TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714`). The extracted folder should contain the firehose programmer (often `prog_firehose_ddr.elf`), the partition XML files (`rawprogram*.xml`, `patch*.xml`) and the image files.
3. Install **QFIL** and the **Qualcomm USB drivers** on your PC.
4. With the tablet powered off and **not** connected to USB, hold **Volume Up** and plug in the USB cable. Keep holding Volume Up until Windows **Device Manager** shows **Qualcomm HS-USB QDLoader 9008 (COMx)** under *Ports (COM & LPT)*. That is EDL mode; release the button.
   - If Windows shows an unknown device or a yellow warning icon, install the Qualcomm USB driver. On units where the Volume Up combination does not work, use the EDL test point while connecting USB.
5. Open **QFIL**. Select Port and choose the `9008` COM port.
6. Select **Flat Build**.
7. In **Programmer Path**, browse to the firehose programmer from the extracted firmware. The filename varies by package, use the one that came with the ROM.
8. Click **Load XML** and select the firmware's `rawprogram0.xml` and `patch0.xml`, remember to leave **Erase All Before Download** UNCHECKED in FireHose Configuration.
9. Click **Download**. Do not unplug the tablet, close QFIL or let the PC sleep while it is flashing.
10. Wait for the download to finish. Do not boot into the CN firmware.

> [!NOTE]
> Flashing the CN ROM only gives you the CN ABL; it does not unlock the bootloader. The tablet is still locked at this point.

#### Step 2: Boot into fastboot

1. Power the tablet off.
2. Hold **Volume Down** + **Power** until the fastboot screen appears.
3. Connect to PC.

#### Step 3: Retrieve the unlock ID

> [!NOTE]
> Normally, you would input the serial code directly into the ZUI unlock site, but this time we use the `unlock_id` instead.

Once booted into fastboot mode on the CN firmware, retrieve your unlock identifier:
```bash
fastboot getvar unlock_id
```

This should output an 8-digit code (in this case, `69acbd04`). Note it down.

> [!NOTE]
> If this returns `GetVar Variable not found`, the CN ABL is not active. Re-check that you actually flashed the CN firmware package and not the ROW package. Or you can manually load the `abl.elf` from the CN firmware to both slots using QFIL.

> [!NOTE]
> Normally, you would input this code directly into the ZUI unlock site, but don't waste time doing that. You would need an accessible Chinese email address, and most of the time the email containing the `sn.img` file is never delivered.

---

#### Step 4: Download your `sn.img`

Insert the returned 8-digit identifier into the following URL parameter to download your unique unlock token. Do not reuse the `sn.img` bundled in this repository unless your `unlock_id` is also `69acbd04`; the token is tied to the device that generated it.
```
http://cdn.zui.lenovomm.com/developer/tabletboot/[unlock_id]/sn.img
```

For example, for `unlock_id` `69acbd04`:
```
http://cdn.zui.lenovomm.com/developer/tabletboot/69acbd04/sn.img
```

> [!NOTE]
> The CDN endpoint is plain HTTP. The token is signed, but only flash a token you generated for your own `unlock_id`.

---

#### Step 5: Flash the unlock token

Flash the downloaded `sn.img` and complete the bootloader unlock:
```bash
fastboot flash unlock sn.img
fastboot oem unlock-go
```
It should look like this if successful.
<img width="806" height="87" alt="image" src="https://github.com/user-attachments/assets/2a233768-3333-418f-978c-3623d9f77f3a"/>

> [!WARNING]
> `fastboot oem unlock-go` erases all user data. Make sure everything is backed up before running it. If the command fails, check that **OEM unlocking** is still enabled in Developer options and that the `sn.img` matches this tablet's `unlock_id`.

---

#### Step 6: Restore the ROW firmware

The system will not boot and will display a "device is corrupt" or "Can't load Android system" warning after the unlock because the device can no longer boot the mismatched CN firmware. This is expected; the unlock itself has already succeeded.

- **Recommended:** use Lenovo **RSA** in Rescue Mode to download and flash the global (ROW) firmware for the TB128FU. RSA handles the full partition set for you.
- **Alternative:** flash the full ROW firmware with QFIL using the same EDL procedure as Step 1, but with the ROW package. A verified ROW `abl` image can also be restored through QFIL Partition Manager, but a full ROW firmware flash is safer.

#### Step 7: Done

Congrats, you have successfully unlocked the bootloader!

> [!WARNING]
> Do not relock the bootloader (`fastboot oem lock` / `fastboot flashing lock`) while the device is running mismatched firmware. Relocking can brick the tablet and is not required for normal use. Keep it unlocked unless you have fully restored a matching stock firmware and know exactly what you are doing.

> [!NOTE]
> An unlocked bootloader can affect OTA updates, Widevine L1 playback and some banking/DRM apps. These are normal trade-offs of unlocking, not bugs in this guide.

# Rooting
With the bootloader unlocked, you now have full control over your device. To gain root access, simply extract boot images from the stock firmware or directly from the device, patch it using Magisk, KernelSU, or another root manager, and flash it following their respective guides.

*Unfinished*

# Flash GSI/custom rom

*Unfinished*

# Custom recovery

Tested: https://xdaforums.com/t/recovery-tb128fu-unofficial-twrp-3-7-x-for-lenovo-tab-m10-plus-gen-3-sdm680.4538035/

*Unfinished*

# Recovering wiped oem partition

> [!WARNING]
> **Important:** This manual reconstruction method should be used as a **last resort**. Manual editing can only generates placeholder network parameters and basic flag entries. Before attempting this, always try Lenovo's official recovery software first, or flash an exact 1:1 partition backup dumped from a working unit of the same model.

Using QFIL with **"Erase All Before Download"** wipes critical low-level partitions, stripping out hardware identifiers (Serial Number, MAC addresses, region codes) and causing **Settings** and **Developer Options** to crash.

This guide covers how to restore the device if official tools cannot recover the hardware identity parameters.

---

## Prerequisites
- Your device's **Serial Number** (e.g., `HA1MW91Y`).
- A clean `persist.img` dump for the **TB128FU**.
- Python installed on your PC or somewhere you can run the program.

---

## Step 1: Try official Lenovo software recovery
Before manually editing binary files, attempt to recover your tablet using official software:

1. Download and install RSA (Lenovo's official repair software) on your PC.
2. Connect your device and select **Rescue Mode**.
3. Follow the on-screen instructions to automatically download and reflash official firmware for the TB128FU.

> [!NOTE]
> RSA is unlikely to recover deleted critical low-level partitions.

---

## Step 2: Generate new image
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

Use the scripts located in the [Scripts/](Scripts/) folder to automatically create one *(Credit to the community for finding the layout structure)*.

> [!WARNING]
> The scripts are templates, not a one-click repair. They write a hard-coded serial number (`HA1MW91Y`) and placeholder or randomly generated MAC addresses. Edit the values to match your own device before running. Prefer the MAC addresses printed on your device label or shown by your router over random ones.

> [!NOTE]
> The scripts generate a fixed 1 MB image. Back up your existing `oem` and `persist` partitions first, and confirm the image size matches your partition layout before loading it with QFIL.

---

## Step 3: Flash via QFIL Partition Manager
> [!NOTE]
> Avoid using `fastboot` to flash `oem`, as it may fail due to dynamic partition restrictions.

1. Power off the tablet and boot into **EDL Mode (Qualcomm 9008)** (`Vol Up` or EDL test point while plugging in the USB cable)
2. Open QFIL and select Tools > Partition Manager
3. Right-click `oem` > Manage Partition > Load Image > Select `oem_fixed.img`
4. Right-click `persist` > Manage Partition > Load Image > Select clean `persist.img`
5. Close Partition Manager and disconnect the tablet

---

## Step 4: Factory Reset
1. Boot into stock **Recovery Mode**
2. Select **Wipe Data / Factory Reset**
3. Reboot into system

---

## Verification
* Go to Settings > About Tablet to verify your serial number and MAC addresses appear correctly
* Open Developer Options to confirm it launches without crashing
