# This is a simple script to generate a fixed oem.img file with specific values for people who accidentally deleted oem partition like me lol ;)
# Credit to cursedverses@XDA

# Create 1MB zero-filled block
data = bytearray(1024 * 1024)

def write_str(offset, text):
    encoded = text.encode('ascii')
    data[offset:offset+len(encoded)] = encoded

# Serial Number at 0x20
write_str(0x20, "HA1MW91Y")

# Board Number at 0x0 (use SN prefix padded or blank)
write_str(0x00, "HA1MW91Y000000000000000")

# Bluetooth & Wi-Fi MACs
write_str(0xA0, "00:11:22:33:44:55")
write_str(0xC0, "00:11:22:33:44:56")

# Region Code
write_str(0x0152, "HKXX")

# Flag byte at 0x0172
data[0x0172] = 0x01

with open("oem_fixed.img", "wb") as f:
    f.write(data)

print("oem_fixed.img generated")