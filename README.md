# Lenovo Tab M10 Plus (3rd Gen) Bootloader Unlock

A comprehensive guide to unlocking the bootloader of the **Lenovo Tab M10 Plus (3rd Gen) Global (TB128FU)**, with instructions for rooting and unbricking. It has also been reported to work on other models, such as the TB128XU; try it at your own risk.

> [!NOTE]
> This guide is a work in progress.

# Disclaimer

**Unlocking your bootloader and flashing custom software carries inherent risks, including permanent device damage (bricking), total data loss, voided warranties, and compromised security or app compatibility. This guide assumes that you possess the necessary technical knowledge, common sense, and understanding to carry out low-level system modifications independently. By following these steps, you acknowledge that you are doing so entirely at your own risk. I assume no responsibility or liability under any circumstances for any loss, damage, hardware failure, or operational issues that may occur to your device or data.**

# Background

Lenovo decided to screw over its global customers by completely removing the official bootloader unlocking mechanism from the global version of the TB128FU. Fastboot unlock commands are ignored by the bootloader, making the official unlock method (flashing `sn.img`) useless. The Chinese equivalent of this tablet, the Xiaoxin Pad 2022, understands all fastboot commands as it should. This guide provides a working workaround to bypass Lenovo's restrictions and regain full control over your hardware.

Compared with the [hex edit method](https://xdaforums.com/t/unlock-bootloader-without-proper-unlock-file-xiaoxin-pad-pro-2021-tb-j716f.4488343/), which is considerably harder, this is a fairly easy alternative for unlocking the bootloader. ([4PDA forum](https://4pda.to/forum/index.php?showtopic=1047797&st=660#entry116826199))

# Unlocking the Bootloader

> [!WARNING]
> Not every file in this repository is required to unlock the tablet. The `sn.img` bundled here is device-specific (see Step 4), and the `Modules/` folder is unrelated to unlocking. Read the instructions before flashing anything.

## Prerequisites

- CN ROM `TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714` (not necessarily this build; it is the one used in this guide)
- ADB and fastboot tools, and the corresponding drivers
- QFIL (Qualcomm Flash Image Loader) and the Qualcomm USB drivers installed
- Rescue and Smart Assistant (RSA)

Please download these tools yourself; this guide does not provide links to them.

## Method Overview

This unlocking procedure works by replacing the restricted global (ROW) Android Bootloader (ABL) with a firmware build from the Chinese (CN) region that retains functional unlock parameters.

### Technical Workflow

1. Flash the official CN ROM `TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714` using QFIL in EDL mode.
2. Reboot the device into fastboot mode.
3. Retrieve the required ZUI unlock identifier using fastboot commands.
4. Download the generated bootloader key (`sn.img`) from Lenovo's CDN server.
5. Flash the unlock key and execute the OEM unlock command.
6. Restore the global (ROW) firmware to get a bootable system again.

> [!NOTE]
> The standard 8-character hardware serial number printed on the device or shown in **Settings** will not generate a valid unlock file. On the ROW ABL, `fastboot getvar unlock_id` returns `GetVar Variable Not found`. The CN ABL generates a distinct 8-character unlock identifier that Lenovo's ZUI token service requires. This code can only be generated and retrieved once the tablet is running the CN bootloader.

> [!WARNING]
> Back up everything before you start. Sign out of any Google accounts and remove any device protection.

## Step 1: Flash the CN Firmware with QFIL (EDL Mode)

1. Remove any screen lock, Google account, and device protection from the tablet, then enable **OEM unlocking** in **Developer options**, and finally power the tablet off completely. A locked FRP account can block the first boot after flashing.
2. Download and extract the CN ROM package (`TB128FU_CN_OPEN_USER_Q00012.0_S_ZUI_14.0.714`). The extracted folder should contain the firehose programmer (often `prog_firehose_ddr.elf`), the partition XML files (`rawprogram*.xml`, `patch*.xml`), and the image files.
3. Install **QFIL** and the **Qualcomm USB drivers** on your PC.
4. With the tablet powered off and not connected to USB, hold **Volume Up** and plug in the USB cable. Keep holding **Volume Up** until Windows **Device Manager** shows **Qualcomm HS-USB QDLoader 9008 (COMx)** under *Ports (COM & LPT)*.
   - If Windows shows an unknown device or a yellow warning icon, reinstall or find the correct Qualcomm USB driver. On units where the **Volume Up** combination does not work, use the EDL test point while connecting USB.
5. Open **QFIL** and select **Port**, then choose the `9008` COM port.
6. Select **Flat Build**.
7. In **Programmer Path**, browse to the firehose programmer from the extracted firmware. The filename varies by package; use the one that came with the ROM.
8. Click **Load XML** and select the firmware's `rawprogram0.xml` and `patch0.xml`. Leave **Erase All Before Download** unchecked in **FireHose Configuration**, otherwise you will wipe partitions you need (see [Recovering the Wiped OEM Partition](#recovering-the-wiped-oem-partition)).
9. Click **Download**. Do not unplug the tablet, close QFIL, or let the PC sleep while it is flashing.
10. Wait for the download to finish and do not boot into the CN firmware.

> [!NOTE]
> Flashing the CN ROM only gives you the CN ABL; it does not unlock the bootloader. The tablet is still locked at this point.

## Step 2: Boot into Fastboot

1. Power the tablet off.
2. Immediately hold **Volume Down** + **Power** until the fastboot screen appears.
3. Connect the tablet to the PC and confirm that `fastboot devices` lists it.

## Step 3: Retrieve the Unlock ID

> [!NOTE]
> Normally, you would enter the serial code on the ZUI unlock site, but this guide uses the `unlock_id` instead. That site also requires an accessible Chinese email address, and the email containing the `sn.img` file is often never delivered, so do not waste time on it.

Once the tablet is in fastboot mode with the CN ABL active, retrieve your unlock identifier:
```bash
fastboot getvar unlock_id
```

This should output an 8-character code (in this case, `69acbd04`). Note it down.

> [!NOTE]
> If this returns `GetVar Variable Not found`, the CN ABL is not active. Re-check that you flashed the CN firmware package and not the ROW package, or manually load the `abl.elf` from the CN firmware into both slots using QFIL.

## Step 4: Download Your `sn.img`

Replace `<unlock_id>` in the following URL with the identifier returned in Step 3 to download your unique unlock token:
```
http://cdn.zui.lenovomm.com/developer/tabletboot/<unlock_id>/sn.img
```

For example, with `unlock_id` `69acbd04`:
```
http://cdn.zui.lenovomm.com/developer/tabletboot/69acbd04/sn.img
```

Do not reuse the `sn.img` bundled in this repository unless your `unlock_id` is also `69acbd04`; the token is tied to the device that generated it.

> [!NOTE]
> The CDN endpoint uses plain HTTP. The token is signed, but only flash a token that you generated for your own `unlock_id`.

## Step 5: Flash the Unlock Token

Flash the downloaded `sn.img` to complete the bootloader unlock:
```bash
fastboot flash unlock sn.img
fastboot oem unlock-go
```

A successful run should look like this:

<img width="806" height="87" alt="Output of a successful fastboot oem unlock-go" src="https://github.com/user-attachments/assets/2a233768-3333-418f-978c-3623d9f77f3a"/>

> [!WARNING]
> `fastboot oem unlock-go` erases all user data, so make sure everything is backed up before running it. If the command fails, check that **OEM unlocking** is still enabled in **Developer options** and that the `sn.img` matches this tablet's `unlock_id`.

## Step 6: Restore the ROW Firmware

The system will not boot after the unlock and will display a "device is corrupt" or "hardware not supported" warning, because the tablet cannot boot the mismatched CN firmware. This is expected; the unlock itself has already succeeded.

- **Recommended:** Use Lenovo **RSA** in **Rescue Mode** to download and flash the global (ROW) firmware for the TB128FU. RSA handles the full partition set for you.
- **Alternative:** Flash the full ROW firmware with QFIL using the same EDL procedure as in Step 1, but with the ROW package. This method is harder because ROW firmware uses the `.x` file format and is encrypted.

## Step 7: Done

Congratulations, you have successfully unlocked the bootloader!

> [!WARNING]
> Do not relock the bootloader while the device is running mismatched firmware; it can brick the tablet. Keep it unlocked unless you have fully restored matching stock firmware and know exactly what you are doing.

# Rooting

With the bootloader unlocked, you have full control over your device. To gain root access, extract the boot image from the stock firmware or directly from the device, patch it with Magisk, KernelSU, or another root manager, and flash it following that root manager's guide.

*Unfinished*

# Flashing a GSI/Custom ROM

*Unfinished*

# Custom Recovery

Tested with the [unofficial TWRP 3.7.x for the TB128FU](https://xdaforums.com/t/recovery-tb128fu-unofficial-twrp-3-7-x-for-lenovo-tab-m10-plus-gen-3-sdm680.4538035/).

*Unfinished*

# Recovering the Wiped OEM Partition

> [!WARNING]
> This manual reconstruction method should be used as a **last resort**. Manual editing can only generate placeholder network parameters and basic flag entries. Before attempting it, try Lenovo's official recovery software, or flash an exact 1:1 partition backup dumped from a working unit of the same model.

Using QFIL with **Erase All Before Download** enabled wipes critical low-level partitions, strips out hardware identifiers (serial number, MAC addresses, region codes), and causes **Settings** and **Developer options** to crash.

This guide covers how to restore the device when official tools cannot recover the hardware identity parameters.

## Prerequisites

- Your device's **serial number** (e.g. `HA1MW91Y`), from the device label or its box
- A clean `persist.img` dump for the **TB128FU** (your own backup, or one from a working unit)
- Python installed on your PC, or somewhere you can run the scripts

## Step 1: Try Official Lenovo Software Recovery

Before manually editing binary files, attempt to recover your tablet using official software:

1. Download and install RSA (Lenovo's official repair software) on your PC.
2. Connect your device and select **Rescue Mode**.
3. Follow the on-screen instructions to automatically download and reflash official firmware for the TB128FU.

> [!NOTE]
> RSA is unlikely to recover deleted critical low-level partitions.

## Step 2: Generate a New Image

Because a wiped `oem` partition is filled with zeroes, you must inject your hardware data at the correct binary offsets.

### OEM Offset Map

| Offset (Hex) | Field Name | Format | Example Value |
| :--- | :--- | :--- | :--- |
| `0x00` | Board Number | 23 ASCII chars | `HA1MW91Y000000000000000` |
| `0x20` | Serial Number | 8 ASCII chars | `HA1MW91Y` |
| `0xA0` | Bluetooth MAC | 17 ASCII chars (`XX:XX:XX:XX:XX:XX`) | `54:E4:3A:1B:2C:3F` |
| `0xC0` | Wi-Fi MAC | 17 ASCII chars (`XX:XX:XX:XX:XX:XX`) | `54:E4:3A:1B:2C:3E` |
| `0x0152` | Region Code | ASCII, up to 4 chars | `HKXX` (also `GBXX`, `ROW`) |
| `0x0172` | Flag Byte | 1 byte | `0x01` |

Use one of the scripts in the [`Scripts/`](Scripts/) folder to create the image (credit to the community for mapping the layout structure):

- `Scripts/restore_oem.py` writes fixed placeholder values.
- `Scripts/restore_oem_advanced.py` generates a realistic Lenovo MAC pair, prints it, and derives the second MAC from the first.

Both scripts write a fixed-size (1 MB) `oem_fixed.img` to the current directory; neither creates `persist.img`.

> [!WARNING]
> The scripts are templates, not a one-click repair. They write a hard-coded serial number (`HA1MW91Y`), board number, and region code (`HKXX`), plus placeholder or randomly generated MAC addresses. Edit every value to match your own device before running, and prefer the MAC addresses printed on your device label or shown by your router over random ones.

> [!NOTE]
> Back up `oem` (if it still holds data) and `persist` before overwriting them, and confirm that the 1 MB image matches your partition layout before loading it with QFIL.

## Step 3: Flash via QFIL Partition Manager

> [!NOTE]
> Avoid using `fastboot` to flash `oem`, as it may fail due to dynamic partition restrictions.

1. Power off the tablet and boot into **EDL mode (Qualcomm 9008)** by holding **Volume Up** or using the EDL test point while plugging in the USB cable.
2. Open QFIL and select **Tools** > **Partition Manager**.
3. Right-click `oem` > **Manage Partition** > **Load Image** > select `oem_fixed.img`.
4. Right-click `persist` > **Manage Partition** > **Load Image** > select the clean `persist.img`.
5. Close **Partition Manager** and disconnect the tablet.

## Step 4: Factory Reset

1. Boot into **Recovery**.
2. Select **Wipe data/factory reset**.
3. Reboot into the system.

## Verification

- Go to **Settings** > **About tablet** to verify that the serial number and MAC addresses appear correctly.
- Open **Developer options** to confirm that it launches without crashing.
- Turn Wi-Fi and Bluetooth on to confirm that both radios work.
