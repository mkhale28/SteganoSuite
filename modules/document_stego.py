import struct
import os

class DocumentStego:
    @staticmethod
    def hide(carrier_path, secret_path, output_path):
        """Hide data in document"""
        try:
            print(f"Hiding {secret_path} in document {carrier_path}")
            
            with open(carrier_path, 'rb') as f:
                carrier_data = f.read()
            
            with open(secret_path, 'rb') as f:
                secret_data = f.read()
            
            # Add marker and combine
            marker = b'DOC_STEGANO'
            combined = carrier_data + marker + struct.pack('>I', len(secret_data)) + secret_data
            
            with open(output_path, 'wb') as f:
                f.write(combined)
            
            print(f"Data hidden in {output_path}")
            return True
            
        except Exception as e:
            print(f"Error hiding document: {e}")
            return False
    
    @staticmethod
    def extract(carrier_path, output_dir):
        """Extract hidden data from document"""
        try:
            print(f"Extracting from document {carrier_path}")
            
            with open(carrier_path, 'rb') as f:
                data = f.read()
            
            marker = b'DOC_STEGANO'
            idx = data.rfind(marker)
            
            if idx == -1:
                print("No hidden data found")
                return False, None
            
            size_start = idx + len(marker)
            data_len = struct.unpack('>I', data[size_start:size_start+4])[0]
            secret_data = data[size_start+4:size_start+4+data_len]
            
            output_path = os.path.join(output_dir, "extracted_doc.bin")
            with open(output_path, 'wb') as f:
                f.write(secret_data)
            
            print(f"Data extracted to {output_path}")
            return True, output_path
            
        except Exception as e:
            print(f"Error extracting document: {e}")
            return False, None