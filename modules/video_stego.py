import struct
import os

class VideoStego:
    @staticmethod
    def hide(carrier_path, secret_path, output_path):
        """Hide data in video file"""
        try:
            print(f"Hiding {secret_path} in video {carrier_path}")
            
            with open(carrier_path, 'rb') as f:
                carrier_data = f.read()
            
            with open(secret_path, 'rb') as f:
                secret_data = f.read()
            
            # Add marker and combine
            marker = b'VIDEO_STEGANO'
            combined = carrier_data + marker + struct.pack('>I', len(secret_data)) + secret_data
            
            with open(output_path, 'wb') as f:
                f.write(combined)
            
            print(f"Data hidden in {output_path}")
            return True
            
        except Exception as e:
            print(f"Error hiding video: {e}")
            return False
    
    @staticmethod
    def extract(carrier_path, output_dir):
        """Extract hidden data from video"""
        try:
            print(f"Extracting from video {carrier_path}")
            
            with open(carrier_path, 'rb') as f:
                data = f.read()
            
            marker = b'VIDEO_STEGANO'
            idx = data.rfind(marker)
            
            if idx == -1:
                print("No hidden data found")
                return False, None
            
            size_start = idx + len(marker)
            data_len = struct.unpack('>I', data[size_start:size_start+4])[0]
            secret_data = data[size_start+4:size_start+4+data_len]
            
            output_path = os.path.join(output_dir, "extracted_video.bin")
            with open(output_path, 'wb') as f:
                f.write(secret_data)
            
            print(f"Data extracted to {output_path}")
            return True, output_path
            
        except Exception as e:
            print(f"Error extracting video: {e}")
            return False, None