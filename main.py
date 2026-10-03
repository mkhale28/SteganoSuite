import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from tkinter.font import Font

# Import our modules
sys.path.append('modules')
try:
    from modules.image_stego import ImageStego
    from modules.audio_stego import AudioStego
    from modules.video_stego import VideoStego
    from modules.document_stego import DocumentStego
    from modules.utils import FileUtils
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    print(f"Module import error: {e}")

class SteganoSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("SteganoSuite v1.0 - Universal Steganography Tool")
        self.root.geometry("1000x750")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.carrier_path = tk.StringVar()
        self.secret_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.password = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0)
        
        # File type options
        self.file_types = {
            "Image": [".bmp", ".png", ".jpg", ".jpeg", ".gif"],
            "Audio": [".wav", ".mp3"],
            "Video": [".avi", ".mp4"],
            "Document": [".txt", ".docx", ".pdf"]
        }
        
        self.current_file_type = "Image"
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.style.configure('Title.TLabel', 
                           background='#1e1e1e', 
                           foreground='white',
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Card.TFrame', 
                           background='#3c3c3c',
                           relief='raised',
                           borderwidth=2)
        
        self.style.configure('Action.TButton',
                           font=('Arial', 10, 'bold'),
                           padding=10)
        
        self.style.configure('Green.TButton',
                           background='#2ecc71',
                           foreground='white')
        
        self.style.configure('Red.TButton',
                           background='#e74c3c',
                           foreground='white')
        
        self.style.configure('Blue.TButton',
                           background='#3498db',
                           foreground='white')
        
    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_frame = ttk.Frame(main_container, style='Card.TFrame')
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        title = ttk.Label(title_frame, 
                         text="🔐 STEGANOSUITE - Universal Steganography Tool",
                         style='Title.TLabel',
                         padding=10)
        title.pack()
        
        subtitle = ttk.Label(title_frame,
                           text="Hide and extract data from images, audio, video, and documents",
                           foreground='#95a5a6',
                           background='#1e1e1e')
        subtitle.pack()
        
        # Left Panel - File Selection
        left_panel = ttk.LabelFrame(main_container, text="File Selection", padding=15)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # File Type Selection
        ttk.Label(left_panel, text="Select File Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.file_type_combo = ttk.Combobox(left_panel, 
                                          values=list(self.file_types.keys()),
                                          state="readonly",
                                          width=20)
        self.file_type_combo.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.file_type_combo.set("Image")
        self.file_type_combo.bind('<<ComboboxSelected>>', self.on_file_type_change)
        
        # Carrier File
        ttk.Label(left_panel, text="Carrier File:").grid(row=1, column=0, sticky=tk.W, pady=10)
        carrier_frame = ttk.Frame(left_panel)
        carrier_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)
        
        self.carrier_entry = ttk.Entry(carrier_frame, textvariable=self.carrier_path, width=40)
        self.carrier_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(carrier_frame, text="Browse", 
                  command=self.browse_carrier, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Secret File
        ttk.Label(left_panel, text="Secret File:").grid(row=2, column=0, sticky=tk.W, pady=10)
        secret_frame = ttk.Frame(left_panel)
        secret_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)
        
        self.secret_entry = ttk.Entry(secret_frame, textvariable=self.secret_path, width=40)
        self.secret_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(secret_frame, text="Browse", 
                  command=self.browse_secret, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Output File
        ttk.Label(left_panel, text="Output File:").grid(row=3, column=0, sticky=tk.W, pady=10)
        output_frame = ttk.Frame(left_panel)
        output_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=40)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(output_frame, text="Browse", 
                  command=self.browse_output, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Password
        ttk.Label(left_panel, text="Password (optional):").grid(row=4, column=0, sticky=tk.W, pady=10)
        ttk.Entry(left_panel, textvariable=self.password, show="*", width=25).grid(row=4, column=1, sticky=tk.W, pady=10)
        
        # Right Panel - Actions and Info
        right_panel = ttk.LabelFrame(main_container, text="Actions", padding=15)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Action Buttons
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.hide_btn = ttk.Button(btn_frame, text="HIDE DATA", 
                                  command=self.hide_data,
                                  style='Green.TButton',
                                  width=15)
        self.hide_btn.pack(side=tk.LEFT, padx=5)
        
        self.extract_btn = ttk.Button(btn_frame, text="EXTRACT DATA", 
                                     command=self.extract_data,
                                     style='Blue.TButton',
                                     width=15)
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="CLEAR ALL", 
                                   command=self.clear_all,
                                   style='Red.TButton',
                                   width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress Bar
        ttk.Label(right_panel, text="Progress:").pack(anchor=tk.W, pady=(20, 5))
        
        self.progress = ttk.Progressbar(right_panel, 
                                       variable=self.progress_value,
                                       length=300,
                                       mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status Label
        self.status_label = ttk.Label(right_panel, 
                                     textvariable=self.status_text,
                                     font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)
        
        # File Info
        info_frame = ttk.LabelFrame(right_panel, text="File Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, 
                                                  height=8,
                                                  width=40,
                                                  wrap=tk.WORD,
                                                  font=('Consolas', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Log Panel (Bottom)
        log_panel = ttk.LabelFrame(main_container, text="Operation Log", padding=10)
        log_panel.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_panel,
                                                 height=8,
                                                 wrap=tk.WORD,
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # Initial log message
        self.log("SteganoSuite v1.0 initialized")
        self.log(f"Python {sys.version}")
        if MODULES_LOADED:
            self.log("All modules loaded successfully")
        else:
            self.log("Warning: Some modules failed to load", "WARNING")
    
    def on_file_type_change(self, event=None):
        self.current_file_type = self.file_type_combo.get()
        self.log(f"Selected file type: {self.current_file_type}")
    
    def browse_carrier(self):
        file_types = []
        if self.current_file_type == "Image":
            file_types = [("Image files", "*.bmp *.png *.jpg *.jpeg *.gif")]
        elif self.current_file_type == "Audio":
            file_types = [("Audio files", "*.wav *.mp3")]
        elif self.current_file_type == "Video":
            file_types = [("Video files", "*.avi *.mp4")]
        elif self.current_file_type == "Document":
            file_types = [("Document files", "*.txt *.docx *.pdf")]
        
        filename = filedialog.askopenfilename(filetypes=file_types)
        if filename:
            self.carrier_path.set(filename)
            
            # Auto-generate output filename
            base, ext = os.path.splitext(filename)
            self.output_path.set(f"{base}_hidden{ext}")
            
            # Show file info
            self.show_file_info(filename)
    
    def browse_secret(self):
        filename = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if filename:
            self.secret_path.set(filename)
            self.log(f"Selected secret file: {os.path.basename(filename)}")
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".*")
        if filename:
            self.output_path.set(filename)
    
    def show_file_info(self, filepath):
        try:
            size = os.path.getsize(filepath)
            ext = os.path.splitext(filepath)[1].lower()
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"File: {os.path.basename(filepath)}\n")
            self.info_text.insert(tk.END, f"Size: {size:,} bytes ({size/1024:.1f} KB)\n")
            self.info_text.insert(tk.END, f"Type: {ext}\n")
            self.info_text.insert(tk.END, f"Path: {filepath}\n")
            
            # Show available techniques
            if ext in ['.bmp', '.png', '.jpg', '.jpeg']:
                self.info_text.insert(tk.END, "\nAvailable techniques:\n")
                self.info_text.insert(tk.END, "• LSB (Least Significant Bit)\n")
                self.info_text.insert(tk.END, "• EOF Append\n")
            elif ext in ['.wav', '.mp3']:
                self.info_text.insert(tk.END, "\nAvailable techniques:\n")
                self.info_text.insert(tk.END, "• LSB for WAV\n")
                self.info_text.insert(tk.END, "• Append for MP3\n")
            
        except Exception as e:
            self.log(f"Error getting file info: {e}", "ERROR")
    
    def hide_data(self):
        if not self.carrier_path.get():
            messagebox.showerror("Error", "Please select a carrier file!")
            return
        
        if not self.secret_path.get():
            messagebox.showerror("Error", "Please select a secret file to hide!")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file!")
            return
        
        # Start in thread to keep GUI responsive
        thread = threading.Thread(target=self._hide_data_thread)
        thread.daemon = True
        thread.start()
    
    def _hide_data_thread(self):
        try:
            self.progress_value.set(10)
            self.status_text.set("Hiding data...")
            self.log("\n" + "="*50)
            self.log("STARTING HIDE OPERATION")
            self.log(f"Carrier: {os.path.basename(self.carrier_path.get())}")
            self.log(f"Secret: {os.path.basename(self.secret_path.get())}")
            self.log(f"Output: {os.path.basename(self.output_path.get())}")
            
            carrier_ext = os.path.splitext(self.carrier_path.get())[1].lower()
            password = self.password.get() or None
            
            self.progress_value.set(30)
            
            # Route to appropriate module
            success = False
            if carrier_ext in ['.bmp', '.png', '.jpg', '.jpeg', '.gif']:
                success = ImageStego.hide(self.carrier_path.get(), 
                                         self.secret_path.get(), 
                                         self.output_path.get(), 
                                         password)
            elif carrier_ext in ['.wav', '.mp3']:
                success = AudioStego.hide(self.carrier_path.get(), 
                                         self.secret_path.get(), 
                                         self.output_path.get(), 
                                         password)
            elif carrier_ext in ['.avi', '.mp4']:
                success = VideoStego.hide(self.carrier_path.get(), 
                                         self.secret_path.get(), 
                                         self.output_path.get())
            elif carrier_ext in ['.txt', '.docx', '.pdf']:
                success = DocumentStego.hide(self.carrier_path.get(), 
                                           self.secret_path.get(), 
                                           self.output_path.get())
            else:
                self.log(f"Unsupported file type: {carrier_ext}", "ERROR")
                return
            
            self.progress_value.set(90)
            
            if success:
                self.progress_value.set(100)
                self.status_text.set("Success!")
                self.log("✓ Data hidden successfully!")
                messagebox.showinfo("Success", "Data hidden successfully!\n\n" +
                                  f"Output file: {self.output_path.get()}")
            else:
                self.status_text.set("Failed")
                self.log("✗ Failed to hide data", "ERROR")
                messagebox.showerror("Error", "Failed to hide data. Check the log for details.")
                
        except Exception as e:
            self.log(f"Error during hide operation: {str(e)}", "ERROR")
            self.status_text.set("Error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.progress_value.set(0)
    
    def extract_data(self):
        if not self.carrier_path.get():
            messagebox.showerror("Error", "Please select a carrier file!")
            return
        
        thread = threading.Thread(target=self._extract_data_thread)
        thread.daemon = True
        thread.start()
    
    def _extract_data_thread(self):
        try:
            self.progress_value.set(10)
            self.status_text.set("Extracting data...")
            self.log("\n" + "="*50)
            self.log("STARTING EXTRACT OPERATION")
            self.log(f"Carrier: {os.path.basename(self.carrier_path.get())}")
            
            carrier_ext = os.path.splitext(self.carrier_path.get())[1].lower()
            password = self.password.get() or None
            
            self.progress_value.set(30)
            
            # Ask where to save extracted file
            output_dir = filedialog.askdirectory(title="Select where to save extracted file")
            if not output_dir:
                self.log("Extraction cancelled by user")
                return
            
            # Route to appropriate module
            success = False
            extracted_path = None
            
            if carrier_ext in ['.bmp', '.png', '.jpg', '.jpeg', '.gif']:
                success, extracted_path = ImageStego.extract(self.carrier_path.get(), 
                                                           output_dir, password)
            elif carrier_ext in ['.wav', '.mp3']:
                success, extracted_path = AudioStego.extract(self.carrier_path.get(), 
                                                           output_dir, password)
            elif carrier_ext in ['.avi', '.mp4']:
                success, extracted_path = VideoStego.extract(self.carrier_path.get(), output_dir)
            elif carrier_ext in ['.txt', '.docx', '.pdf']:
                success, extracted_path = DocumentStego.extract(self.carrier_path.get(), output_dir)
            else:
                self.log(f"Unsupported file type: {carrier_ext}", "ERROR")
                return
            
            self.progress_value.set(90)
            
            if success and extracted_path:
                self.progress_value.set(100)
                self.status_text.set("Success!")
                self.log(f"✓ Data extracted to: {extracted_path}")
                messagebox.showinfo("Success", f"Data extracted successfully!\n\n" +
                                  f"Saved to: {extracted_path}")
            else:
                self.status_text.set("Failed")
                self.log("✗ No hidden data found or incorrect password", "ERROR")
                messagebox.showerror("Error", "No hidden data found or incorrect password.")
                
        except Exception as e:
            self.log(f"Error during extract operation: {str(e)}", "ERROR")
            self.status_text.set("Error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.progress_value.set(0)
    
    def clear_all(self):
        self.carrier_path.set("")
        self.secret_path.set("")
        self.output_path.set("")
        self.password.set("")
        self.info_text.delete(1.0, tk.END)
        self.status_text.set("Ready")
        self.log("All fields cleared")
    
    def log(self, message, level="INFO"):
        """Add message to log with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "ERROR":
            tag = "error"
            prefix = "[ERROR]"
            color = "red"
        elif level == "WARNING":
            tag = "warning"
            prefix = "[WARN]"
            color = "orange"
        else:
            tag = "info"
            prefix = "[INFO]"
            color = "green"
        
        log_entry = f"{timestamp} {prefix} {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Apply color tags if configured
        try:
            self.log_text.tag_configure(tag, foreground=color)
            start = self.log_text.index("end-2l linestart")
            end = self.log_text.index("end-1c")
            self.log_text.tag_add(tag, start, end)
        except:
            pass

def main():
    root = tk.Tk()
    app = SteganoSuite(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()