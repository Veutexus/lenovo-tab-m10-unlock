# A more advanced version of restore_oem.py that generates realistic MAC addresses for Wi-Fi and Bluetooth
# Credit to cursedverses@XDA

import random

# Create 1MB zero-filled block
data = bytearray(1024 * 1024)

def write_str(offset, text):
    encoded = text.encode('ascii')
    data[offset:offset+len(encoded)] = encoded

# Generate realistic Lenovo Wi-Fi MAC (using a real Lenovo OUI prefix)
wifi_mac = f"54:E4:3A:{random.randint(0x10, 0xEF):02X}:{random.randint(0x10, 0xEF):02X}:{random.randint(0x10, 0xEF):02X}"

# Generate Bluetooth MAC (increment the last octet of the Wi-Fi MAC by 1)
mac_parts = wifi_mac.split(':')
last_octet = int(mac_parts[-1], 16)
bt_last_octet = (last_octet + 1) % 256
mac_parts[-1] = f"{bt_last_octet:02X}"
bt_mac = ":".join(mac_parts)

print(f"Generated Wi-Fi MAC: {wifi_mac}")
print(f"Generated BT MAC:    {bt_mac}")

# Populate OEM Data Layout
write_str(0x00, "HA1MW91Y000000000000000")  # Board Number
write_str(0x20, "HA1MW91Y")                # Serial Number
write_str(0xA0, bt_mac)                    # Bluetooth MAC
write_str(0xC0, wifi_mac)                  # Wi-Fi MAC
write_str(0x0152, "HKXX")                  # Region Code
data[0x0172] = 0x01                        # Flag Byte

with open("oem_fixed.img", "wb") as f:
    f.write(data)

print("oem_fixed.img generated")