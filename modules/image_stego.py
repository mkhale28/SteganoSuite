from PIL import Image
import struct
import os

class ImageStego:
    @staticmethod
    def hide(carrier_path, secret_path, output_path, password=None):
        """Hide data in image using LSB technique"""
        try:
            print(f"Hiding {secret_path} in {carrier_path}")
            
            # Open carrier image
            img = Image.open(carrier_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            pixels = img.load()
            
            # Read secret data
            with open(secret_path, 'rb') as f:
                secret_data = f.read()
            
            # Add header with data length
            data_len = len(secret_data)
            header = struct.pack('>I', data_len)
            full_data = header + secret_data
            
            # Convert to bits
            bits = []
            for byte in full_data:
                bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
            
            # Check capacity
            max_bits = width * height * 3  # 3 channels (RGB)
            if len(bits) > max_bits:
                print(f"Not enough capacity: need {len(bits)} bits, have {max_bits}")
                return False
            
            # Hide bits in LSB
            bit_idx = 0
            for y in range(height):
                for x in range(width):
                    if bit_idx >= len(bits):
                        break
                    
                    r, g, b = pixels[x, y]
                    
                    # Modify LSBs
                    if bit_idx < len(bits):
                        r = (r & 0xFE) | bits[bit_idx]
                        bit_idx += 1
                    if bit_idx < len(bits):
                        g = (g & 0xFE) | bits[bit_idx]
                        bit_idx += 1
                    if bit_idx < len(bits):
                        b = (b & 0xFE) | bits[bit_idx]
                        bit_idx += 1
                    
                    pixels[x, y] = (r, g, b)
            
            img.save(output_path)
            print(f"Data hidden successfully in {output_path}")
            return True
            
        except Exception as e:
            print(f"Error hiding data: {e}")
            return False
    
    @staticmethod
    def extract(carrier_path, output_dir, password=None):
        """Extract hidden data from image"""
        try:
            print(f"Extracting data from {carrier_path}")
            
            img = Image.open(carrier_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            pixels = img.load()
            
            # Extract bits from LSB
            bits = []
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    bits.append(r & 1)
                    bits.append(g & 1)
                    bits.append(b & 1)
            
            # Convert bits to bytes
            bytes_data = []
            for i in range(0, len(bits), 8):
                if i + 8 > len(bits):
                    break
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | bits[i + j]
                bytes_data.append(byte_val)
            
            # Check for header (4 bytes for length)
            if len(bytes_data) >= 4:
                data_len = struct.unpack('>I', bytes(bytes_data[:4]))[0]
                if 4 + data_len <= len(bytes_data):
                    secret_data = bytes(bytes_data[4:4 + data_len])
                    
                    output_path = os.path.join(output_dir, "extracted_data.bin")
                    with open(output_path, 'wb') as f:
                        f.write(secret_data)
                    
                    print(f"Data extracted to {output_path}")
                    return True, output_path
            
            print("No hidden data found")
            return False, None
            
        except Exception as e:
            print(f"Error extracting data: {e}")
            return False, None