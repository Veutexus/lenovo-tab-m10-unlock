# lenovo-tab-m10-unlock
My attempt and now a guide to unlock the bootloader of Lenovo Tab M10 Plus 3rd Gen Global (TB128FU).

> [!CAUTION]
> **Disclaimer:** I am not responsible for any damage, bricked devices, or lost data resulting from the use of this guide. Proceed at your own risk.




# Recovering Wiped OEM & Persist Partitions

> [!WARNING]
> **Important Warning:** This manual reconstruction method should be used as a **last resort**. Manual editing generates placeholder network parameters and basic flag entries. Before attempting this, always try Lenovo's official recovery software first, or flash an exact 1:1 partition backup dumped from a working unit of the same model.

Using QFIL with **"Erase All Before Download"** wipes critical low-level partitions (`oem` and `persist`), stripping out hardware identifiers (Serial Number, MAC addresses, region codes) and causing **Settings** and **Developer Options** to force-close continuously.

This guide covers how to restore the device if official tools cannot recover the hardware identity parameters.

---

## Prerequisites
* A Windows PC with **Qualcomm QFIL** and Qualcomm USB drivers installed.
* Your device's **Serial Number** (e.g., `HA1MW91Y`).
* A clean `persist.img` dump for the **TB128FU**.
* **Python** installed on your PC or somewhere you can run the program.

---

## Step 1: Try Official Lenovo Software Recovery
Before manually editing binary files, attempt to recover your tablet using official software:

1. Download and install **Rescue and Smart Assistant (RSA)** (Lenovo's official repair software) on your PC.
2. Connect your device and select **Rescue Mode**.
3. Follow the on-screen instructions to automatically download and reflash official firmware for the TB128FU.

RSA most likely cannot help you to recover deleted partitions, proceed with the manual recovery steps below.

---

## Step 2: Generate `oem_fixed.img`
Because a wiped `oem` partition is filled with zeroes (`00`), you must inject your hardware data at precise binary offsets.

### OEM Offset Map
| Offset (Hex) | Field Name | Format | Example Value |
| :--- | :--- | :--- | :--- |
| **`0x00`** | Board Number | 23 ASCII chars | `HA1MW91Y000000000000000` |
| **`0x20`** | Serial Number | 8 ASCII chars | `HA1MW91Y` |
| **`0xA0`** | Bluetooth MAC | 17 ASCII chars (`XX:XX:XX:XX:XX:XX`) | `54:E4:3A:1B:2C:3F` |
| **`0xC0`** | Wi-Fi MAC | 17 ASCII chars (`XX:XX:XX:XX:XX:XX`) | `54:E4:3A:1B:2C:3E` |
| **`0x0152`**| Region Code | 4 ASCII chars | `HKXX` (or `ROW`, `GBXX`) |
| **`0x0172`**| Flag Byte | `0x01` byte value | `01` |

Use the generator script located in the `Scripts/` folder to automatically create `oem_fixed.img` *(Credit to the community for finding the layout structure)*.

---

## Step 3: Flash via QFIL Partition Manager
> [!NOTE]
> Avoid using `fastboot` to flash `oem`, as it may fail due to dynamic partition restrictions.

1. Power off the tablet and boot into **EDL Mode (Qualcomm 9008)** (`Vol Up` or EDL test point while plugging in the USB cable).
2. Open **QFIL** and select **Tools** > **Partition Manager**.
3. Right-click **`oem`** $\rightarrow$ **Manage Partition** $\rightarrow$ **Load Image** $\rightarrow$ Select `oem_fixed.img`.
4. Right-click **`persist`** $\rightarrow$ **Manage Partition** $\rightarrow$ **Load Image** $\rightarrow$ Select clean `persist.img`.
5. Close Partition Manager and disconnect the tablet.

---

## Step 4: Factory Reset
1. Boot into stock **Recovery Mode**.
2. Select **Wipe Data / Factory Reset**.
3. Reboot into system.

---

## Verification
* Go to **Settings > About Tablet** to verify your serial number and MAC addresses appear correctly.
* Open **Developer Options** to confirm it launches without crashing.
