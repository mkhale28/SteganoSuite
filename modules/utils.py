import os
import hashlib

class FileUtils:
    @staticmethod
    def get_file_info(filepath):
        """Get file information"""
        try:
            stats = os.stat(filepath)
            return {
                'name': os.path.basename(filepath),
                'size': stats.st_size,
                'modified': stats.st_mtime,
                'extension': os.path.splitext(filepath)[1]
            }
        except:
            return None
    
    @staticmethod
    def calculate_hash(filepath, algorithm='md5'):
        """Calculate file hash"""
        try:
            hash_func = hashlib.new(algorithm)
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except:
            return None
    
    @staticmethod
    def format_size(size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"