import wave
import struct
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

class AudioStego:
    @staticmethod
    def hide(carrier_path, secret_path, output_path, password=None):
        """Hide data in audio file"""
        try:
            if carrier_path.lower().endswith('.wav'):
                return AudioStego._hide_wav(carrier_path, secret_path, output_path, password)
            else:
                return AudioStego._hide_append(carrier_path, secret_path, output_path)
        except Exception as e:
            print(f"Error hiding audio: {e}")
            return False
    
    @staticmethod
    def _hide_wav(carrier_path, secret_path, output_path, password):
        """Hide in WAV using LSB"""
        try:
            with wave.open(carrier_path, 'rb') as song:
                params = song.getparams()
                frame_bytes = bytearray(list(song.readframes(song.getnframes())))
            
            with open(secret_path, 'rb') as f:
                secret_data = f.read()
            
            # Encrypt if password provided
            if password:
                secret_data = AudioStego._encrypt(secret_data, password)
            
            # Add length header
            data_len = len(secret_data)
            header = struct.pack('>I', data_len)
            full_data = header + secret_data
            
            # Convert to bits
            bits = []
            for byte in full_data:
                bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
            
            if len(bits) > len(frame_bytes):
                print("Not enough audio capacity")
                return False
            
            # Hide in LSB
            for i, bit in enumerate(bits):
                if i < len(frame_bytes):
                    frame_bytes[i] = (frame_bytes[i] & 0xFE) | bit
            
            # Save
            with wave.open(output_path, 'wb') as fd:
                fd.setparams(params)
                fd.writeframes(bytes(frame_bytes))
            
            return True
        except Exception as e:
            print(f"WAV hide error: {e}")
            return False
    
    @staticmethod
    def _hide_append(carrier_path, secret_path, output_path):
        """Append data to file"""
        try:
            with open(carrier_path, 'rb') as f:
                carrier_data = f.read()
            
            with open(secret_path, 'rb') as f:
                secret_data = f.read()
            
            # Add marker and data
            marker = b'AUDIO_STEGANO'
            combined = carrier_data + marker + struct.pack('>I', len(secret_data)) + secret_data
            
            with open(output_path, 'wb') as f:
                f.write(combined)
            
            return True
        except Exception as e:
            print(f"Append hide error: {e}")
            return False
    
    @staticmethod
    def extract(carrier_path, output_dir, password=None):
        """Extract hidden data from audio"""
        try:
            if carrier_path.lower().endswith('.wav'):
                success, path = AudioStego._extract_wav(carrier_path, output_dir, password)
                if success:
                    return success, path
            
            # Try append extraction
            success, path = AudioStego._extract_append(carrier_path, output_dir)
            return success, path
            
        except Exception as e:
            print(f"Extract error: {e}")
            return False, None
    
    @staticmethod
    def _extract_wav(carrier_path, output_dir, password):
        """Extract from WAV"""
        try:
            with wave.open(carrier_path, 'rb') as song:
                frame_bytes = bytearray(list(song.readframes(song.getnframes())))
            
            # Extract LSBs
            bits = []
            for byte in frame_bytes:
                bits.append(byte & 1)
            
            # Convert to bytes
            bytes_data = []
            for i in range(0, len(bits), 8):
                if i + 8 > len(bits):
                    break
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | bits[i + j]
                bytes_data.append(byte_val)
            
            # Check header
            if len(bytes_data) >= 4:
                data_len = struct.unpack('>I', bytes(bytes_data[:4]))[0]
                if 4 + data_len <= len(bytes_data):
                    secret_data = bytes(bytes_data[4:4 + data_len])
                    
                    # Decrypt if password
                    if password:
                        secret_data = AudioStego._decrypt(secret_data, password)
                    
                    output_path = os.path.join(output_dir, "extracted_audio.bin")
                    with open(output_path, 'wb') as f:
                        f.write(secret_data)
                    
                    return True, output_path
            
            return False, None
        except Exception as e:
            print(f"WAV extract error: {e}")
            return False, None
    
    @staticmethod
    def _extract_append(carrier_path, output_dir):
        """Extract appended data"""
        try:
            with open(carrier_path, 'rb') as f:
                data = f.read()
            
            marker = b'AUDIO_STEGANO'
            idx = data.rfind(marker)
            if idx == -1:
                return False, None
            
            size_start = idx + len(marker)
            data_len = struct.unpack('>I', data[size_start:size_start+4])[0]
            secret_data = data[size_start+4:size_start+4+data_len]
            
            output_path = os.path.join(output_dir, "extracted.bin")
            with open(output_path, 'wb') as f:
                f.write(secret_data)
            
            return True, output_path
        except Exception as e:
            print(f"Append extract error: {e}")
            return False, None
    
    @staticmethod
    def _encrypt(data, password):
        """Encrypt data"""
        key = hashlib.sha256(password.encode()).digest()[:16]
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        return cipher.iv + ct_bytes
    
    @staticmethod
    def _decrypt(data, password):
        """Decrypt data"""
        try:
            key = hashlib.sha256(password.encode()).digest()[:16]
            iv = data[:16]
            ct = data[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt
        except:
            return data