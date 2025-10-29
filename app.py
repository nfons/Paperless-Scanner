import os
import yaml
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
from lib.scanner import list_scanners, scan_image, upload_to_paperlessngx
from lib.ai import get_recommended_filename_from_pil_image, get_recommended_filename_from_pil_image_gemini
from configwindow import ConfigWindow

class PaperlessScanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paperless Scan App")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        self.root.load_config = self.load_config
        
        # Initialize variables
        self.scanned_image_path = None
        self.scanned_image = None
        self.photo_image = None
        self.api_url = None
        self.api_token = None
        self.openai_api_key = None
        self.gemini_api_key = None
        self.filename = ""
        # Center the window
        self.center_window()
        self.load_config()
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title label
        title_label = tk.Label(
            main_frame, 
            text="Paperless Scan App", 
            font=("Arial", 24, "bold"),
            fg='#333333',
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # Scanner info frame
        scanner_frame = tk.Frame(main_frame, bg='#f0f0f0')
        scanner_frame.pack(pady=10, fill='x')
        
        # Scanner dropdown
        scanner_label = tk.Label(
            scanner_frame,
            text="Available Scanners:",
            font=("Arial", 10, "bold"),
            fg='#333333',
            bg='#f0f0f0'
        )
        scanner_label.pack(side='left', padx=(0, 10))
        
        self.scanner_var = tk.StringVar()
        self.scanner_combo = ttk.Combobox(
            scanner_frame,
            textvariable=self.scanner_var,
            state="readonly",
            width=30
        )
        self.scanner_combo.pack(side='left')
        
        # Refresh scanners button
        refresh_button = tk.Button(
            scanner_frame,
            text="Refresh",
            command=self.refresh_scanners,
            font=("Arial", 9),
            bg='#2196F3',
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        )
        refresh_button.pack(side='left', padx=(10, 0))
        
        # Filename input frame (initially hidden) - now in scanner frame
        self.filename_frame = tk.Frame(scanner_frame, bg='#f0f0f0')
        
        # Filename label
        filename_label = tk.Label(
            self.filename_frame,
            text="Filename:",
            font=("Arial", 10, "bold"),
            fg='#333333',
            bg='#f0f0f0'
        )
        filename_label.pack(side='left', padx=(10, 10))
        
        # Filename entry
        self.filename_var = tk.StringVar()
        self.filename_entry = tk.Entry(
            self.filename_frame,
            textvariable=self.filename_var,
            font=("Arial", 10),
            width=20
        )
        self.filename_entry.pack(side='left', padx=(0, 10))
        
        # Save button
        self.save_button = tk.Button(
            self.filename_frame,
            text="Save",
            command=self.save_scanned_image,
            font=("Arial", 9),
            bg='#4CAF50',
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        )
        self.save_button.pack(side='left')
        
        # Image display frame
        self.image_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        self.image_frame.pack(pady=10, fill='both', expand=True)
        
        # Placeholder for image
        self.image_label = tk.Label(
            self.image_frame,
            text="No image scanned yet.\nClick 'Scan Document' to start.",
            font=("Arial", 12),
            fg='#999999',
            bg='white'
        )
        self.image_label.pack(expand=True)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Scan button
        scan_button = tk.Button(
            button_frame,
            text="Scan Document",
            command=self.scan_document,
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        scan_button.pack(side='left', padx=10)
        
        # Upload button
        self.upload_button = tk.Button(
            button_frame,
            text="Select Document",
            command=self.upload_to_paperless,
            font=("Arial", 12),
            bg='#FF9800',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            state='normal'
        )
        self.upload_button.pack(side='left', padx=10)
        
        # Settings button
        settings_button = tk.Button(
            button_frame,
            text="Settings",
            command=self.open_settings,
            font=("Arial", 12),
            bg='#9C27B0',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        settings_button.pack(side='left', padx=10)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.exit_app,
            font=("Arial", 12),
            bg='#f44336',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        exit_button.pack(side='left', padx=10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Ready to scan",
            font=("Arial", 10),
            fg='#666666',
            bg='#f0f0f0'
        )
        self.status_label.pack(pady=5)
        
        # Bind hover effects
        scan_button.bind('<Enter>', lambda e: scan_button.configure(bg='#45a049'))
        scan_button.bind('<Leave>', lambda e: scan_button.configure(bg='#4CAF50'))
        self.upload_button.bind('<Enter>', lambda e: self.upload_button.configure(bg='#e68900') if self.upload_button['state'] != 'disabled' else None)
        self.upload_button.bind('<Leave>', lambda e: self.upload_button.configure(bg='#FF9800') if self.upload_button['state'] != 'disabled' else None)
        exit_button.bind('<Enter>', lambda e: exit_button.configure(bg='#da190b'))
        exit_button.bind('<Leave>', lambda e: exit_button.configure(bg='#f44336'))
        refresh_button.bind('<Enter>', lambda e: refresh_button.configure(bg='#1976D2'))
        refresh_button.bind('<Leave>', lambda e: refresh_button.configure(bg='#2196F3'))
        self.save_button.bind('<Enter>', lambda e: self.save_button.configure(bg='#45a049'))
        self.save_button.bind('<Leave>', lambda e: self.save_button.configure(bg='#4CAF50'))
        settings_button.bind('<Enter>', lambda e: settings_button.configure(bg='#7B1FA2'))
        settings_button.bind('<Leave>', lambda e: settings_button.configure(bg='#9C27B0'))
        
        # Initialize scanners
        self.refresh_scanners()
    
    def open_settings(self):
        """Open the configuration settings window"""
        ConfigWindow(self.root)
    

    def cleanup(self):
         if os.path.exists('tmp.jpg'):
            os.remove('tmp.jpg')

    def exit_app(self):
        # clean up the temp file
        self.cleanup()
        self.root.quit()

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def refresh_scanners(self):
        """Refresh the list of available scanners"""
        try:
            scanners = list_scanners()
            if scanners:
                self.scanner_combo['values'] = scanners
                self.scanner_combo.set(scanners[0])
                self.status_label.config(text=f"Found {len(scanners)} scanner(s)")
            else:
                self.scanner_combo['values'] = ["No scanners found"]
                self.scanner_combo.set("No scanners found")
                self.status_label.config(text="No scanners detected")
        except Exception as e:
            self.status_label.config(text=f"Error detecting scanners: {str(e)}")
    
    def scan_document(self):
       # scan the document
        try:
            self.status_label.config(text="Scanning document...")
            self.root.update()
            

            # clear out existing file if its there...
            self.cleanup()
            # Scan the image and get PIL Image object
            self.scanned_image = scan_image()
            
            if self.scanned_image is not None:
                # Display the image
                self.display_image_object(self.scanned_image)

                # get the filename based on the api key type...
                if self.openai_api_key:
                    self.filename = get_recommended_filename_from_pil_image(self.scanned_image, self.openai_api_key)
                elif self.gemini_api_key:
                    self.filename = get_recommended_filename_from_pil_image_gemini(self.scanned_image, self.gemini_api_key)
                else:
                    self.filename = ""
                # Show filename input frame
                self.filename_frame.pack(side='left', padx=(10, 0))
                self.filename_var.set(self.filename or "")  # Clear previous filename
                self.filename_entry.focus()  # Set focus to filename entry
                self.scanned_image_path = 'tmp.jpg'
                self.status_label.config(text="Document scanned successfully! Enter filename to save.")
                # Enable upload button, change text
                self.upload_button.config(state='normal')
                self.upload_button.config(text="Upload to Paperless")
            else:
                self.status_label.config(text="Scan cancelled or failed")
                messagebox.showinfo("Scan Cancelled", "Scan was cancelled or failed")
                
        except Exception as e:
            self.status_label.config(text=f"Scan error: {str(e)}")
            messagebox.showerror("Scan Error", f"Error during scanning: {str(e)}")
    
    def save_scanned_image(self):
        """Save the scanned image with the specified filename"""
        if self.scanned_image is None:
            messagebox.showerror("Save Error", "No scanned image to save")
            return
            
        filename = self.filename_var.get().strip()
        
        if not filename:
            messagebox.showwarning("Filename Required", "Please enter a filename")
            return
        
        # Add .jpg extension if not provided
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            filename += '.jpg'
        
        try:
            # Save the image
            self.filename = filename
            
            # Hide filename frame
            self.filename_frame.pack_forget()
                        
            self.status_label.config(text=f"Document saved as '{filename}'")
            messagebox.showinfo("Save Success", f"Document saved as '{filename}'")
            
        except Exception as e:
            self.status_label.config(text=f"Save error: {str(e)}")
            messagebox.showerror("Save Error", f"Error saving document: {str(e)}")
    
    def display_image_object(self, pil_image):
        """Display a PIL Image object in the app"""
        try:
            # Get frame dimensions
            frame_width = self.image_frame.winfo_width() - 20
            frame_height = self.image_frame.winfo_height() - 20
            
            if frame_width <= 1 or frame_height <= 1:
                # Frame not yet sized, use default
                frame_width = 1000
                frame_height = 900
            
            # Calculate resize ratio to fit in frame
            img_width, img_height = pil_image.size
            ratio = min(frame_width / img_width, frame_height / img_height)
            
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # Resize image
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(resized_image)
            
            # Update label
            self.image_label.config(image=self.photo_image, text="")
            
        except Exception as e:
            self.status_label.config(text=f"Error displaying image: {str(e)}")
    
    def display_image(self, image_path):
        """Display the scanned image from file path in the app"""
        try:
            # Load and resize image
            image = Image.open(image_path)
            self.display_image_object(image)
            
        except Exception as e:
            self.status_label.config(text=f"Error displaying image: {str(e)}")
    
    def upload_to_paperless(self):
        """Upload the scanned document to Paperless-ngx"""
        if not self.scanned_image_path or not os.path.exists(self.scanned_image_path):
            selectfile = messagebox.askokcancel("Upload Error", "No scanned document to upload, want to select an existing file?")

            if selectfile:
            # Show file selector dialog for manual selection
                file_path = filedialog.askopenfilename(title="Select Document to Upload", 
                                                        filetypes=[("All Files", "*.*")])
            if not file_path:
                return
            self.scanned_image_path = file_path
        try:
            self.status_label.config(text="Uploading to Paperless...")
            self.root.update()
             
            # Upload the document with filename
            success, status_code, response = upload_to_paperlessngx(self.scanned_image_path, self.api_url, self.api_token, self.filename)
            if success:
                self.status_label.config(text="Document uploaded successfully!")
                messagebox.showinfo("Upload Success", "Document uploaded to Paperless-ngx!")
            else:
                self.status_label.config(text="Upload failed")
                messagebox.showerror("Upload Error", f"Error uploading document: {response}")
                print(f"Upload failed: {status_code} {response}")
            
        except Exception as e:
            self.status_label.config(text=f"Upload error: {str(e)}")
            messagebox.showerror("Upload Error", f"Error uploading document: {str(e)}")


    def load_config(self):
        # load the config file
        config_file = 'config.yaml'
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                self.api_url = config['api_url']
                self.api_token = config['api_token']
                self.openai_api_key = config.get('openai_api_key', None)
                self.gemini_api_key = config.get('gemini_api_key', None)
            return config
        else:
            return None

def main():
    # check if the temp file exists, and remove it if it does
    if os.path.exists('tmp.jpg'):
        os.remove('tmp.jpg')

    root = tk.Tk()
    # root.iconbitmap('docs/images/icon.ico')
    app = PaperlessScanApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()