import tkinter as tk
from tkinter import messagebox, ttk
import os
import yaml

class ConfigWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Configuration Settings")
        self.window.geometry("600x500")
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Load current config
        self.config = self.load_config()
        
        # Create main frame
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title label
        title_label = tk.Label(
            main_frame, 
            text="Configuration Settings", 
            font=("Arial", 18, "bold"),
            fg='#333333',
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # Create scrollable frame for config entries
        canvas = tk.Canvas(main_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configuration entries
        self.entries = {}
        
        # Paperless-ngx Configuration Section
        paperless_frame = tk.LabelFrame(
            scrollable_frame,
            text="Paperless-ngx Configuration",
            font=("Arial", 12, "bold"),
            fg='#333333',
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        paperless_frame.pack(fill='x', pady=10, padx=10)
        
        # API URL
        self.create_config_entry(paperless_frame, "api_url", "API URL:", 
                               self.config.get('api_url', ''), 
                               "Paperless-ngx API URL (e.g., http://localhost:8010)")
        
        # API Token
        self.create_config_entry(paperless_frame, "api_token", "API Token:", 
                               self.config.get('api_token', ''), 
                               "Paperless-ngx API Token", is_password=True)
        
        # AI Configuration Section
        ai_frame = tk.LabelFrame(
            scrollable_frame,
            text="AI Configuration (Optional)",
            font=("Arial", 12, "bold"),
            fg='#333333',
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        ai_frame.pack(fill='x', pady=10, padx=10)
        
        # AI Provider Toggle Frame
        toggle_frame = tk.Frame(ai_frame, bg='#f0f0f0')
        toggle_frame.pack(fill='x', pady=5)
        
        # Toggle label
        toggle_label = tk.Label(
            toggle_frame,
            text="AI Provider:",
            font=("Arial", 10, "bold"),
            fg='#333333',
            bg='#f0f0f0'
        )
        toggle_label.pack(side='left', padx=(0, 10))
        
        # AI Provider toggle variable
        self.ai_provider = tk.StringVar()
        
        # Determine initial toggle state based on existing config
        if self.config.get('openai_api_key'):
            self.ai_provider.set('openai')
        elif self.config.get('gemini_api_key'):
            self.ai_provider.set('gemini')
        else:
            self.ai_provider.set('none')
        
        # OpenAI Radio Button
        openai_radio = tk.Radiobutton(
            toggle_frame,
            text="OpenAI",
            variable=self.ai_provider,
            value='openai',
            font=("Arial", 10),
            fg='#333333',
            bg='#f0f0f0',
            command=self.on_ai_provider_change
        )
        openai_radio.pack(side='left', padx=(0, 20))
        
        # Gemini Radio Button
        gemini_radio = tk.Radiobutton(
            toggle_frame,
            text="Google Gemini",
            variable=self.ai_provider,
            value='gemini',
            font=("Arial", 10),
            fg='#333333',
            bg='#f0f0f0',
            command=self.on_ai_provider_change
        )
        gemini_radio.pack(side='left', padx=(0, 20))
        
        # None Radio Button
        none_radio = tk.Radiobutton(
            toggle_frame,
            text="None",
            variable=self.ai_provider,
            value='none',
            font=("Arial", 10),
            fg='#333333',
            bg='#f0f0f0',
            command=self.on_ai_provider_change
        )
        none_radio.pack(side='left')
        
        # OpenAI API Key Frame
        self.openai_frame = tk.Frame(ai_frame, bg='#f0f0f0')
        self.openai_frame.pack(fill='x', pady=5)
        
        # OpenAI API Key
        self.create_config_entry(self.openai_frame, "openai_api_key", "OpenAI API Key:", 
                               self.config.get('openai_api_key', ''), 
                               "OpenAI API Key for filename generation")
        
        # Gemini API Key Frame
        self.gemini_frame = tk.Frame(ai_frame, bg='#f0f0f0')
        self.gemini_frame.pack(fill='x', pady=5)
        
        # Gemini API Key
        self.create_config_entry(self.gemini_frame, "gemini_api_key", "Gemini API Key:", 
                               self.config.get('gemini_api_key', ''), 
                               "Google Gemini API Key for filename generation")
        
        # Info label
        info_label = tk.Label(
            scrollable_frame,
            text="Note: Only one AI provider can be active at a time. Select 'None' to disable AI filename generation.",
            font=("Arial", 9),
            fg='#666666',
            bg='#f0f0f0',
            wraplength=550
        )
        info_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save Configuration",
            command=self.save_config,
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        save_button.pack(side='left', padx=10)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.close_window,
            font=("Arial", 12),
            bg='#f44336',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        cancel_button.pack(side='left', padx=10)
        
        # Bind hover effects
        save_button.bind('<Enter>', lambda e: save_button.configure(bg='#45a049'))
        save_button.bind('<Leave>', lambda e: save_button.configure(bg='#4CAF50'))
        cancel_button.bind('<Enter>', lambda e: cancel_button.configure(bg='#da190b'))
        cancel_button.bind('<Leave>', lambda e: cancel_button.configure(bg='#f44336'))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Initialize AI provider visibility
        self.on_ai_provider_change()
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_set()
        self.window.wait_window()
    
    def on_ai_provider_change(self):
        """Handle AI provider toggle changes"""
        provider = self.ai_provider.get()
        
        # Show/hide appropriate API key fields
        if provider == 'openai':
            self.openai_frame.pack(fill='x', pady=5)
            self.gemini_frame.pack_forget()
            # Clear Gemini key when OpenAI is selected
            if 'gemini_api_key' in self.entries:
                self.entries['gemini_api_key'].delete(0, tk.END)
        elif provider == 'gemini':
            self.openai_frame.pack_forget()
            self.gemini_frame.pack(fill='x', pady=5)
            # Clear OpenAI key when Gemini is selected
            if 'openai_api_key' in self.entries:
                self.entries['openai_api_key'].delete(0, tk.END)
        else:  # none
            self.openai_frame.pack_forget()
            self.gemini_frame.pack_forget()
            # Clear both keys when none is selected
            if 'openai_api_key' in self.entries:
                self.entries['openai_api_key'].delete(0, tk.END)
            if 'gemini_api_key' in self.entries:
                self.entries['gemini_api_key'].delete(0, tk.END)
    
    def center_window(self):
        """Center the window on the screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_config_entry(self, parent, key, label_text, default_value, tooltip_text, is_password=False):
        """Create a configuration entry field"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill='x', pady=5)
        
        # Label
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            fg='#333333',
            bg='#f0f0f0',
            anchor='w'
        )
        label.pack(anchor='w')
        
        # Entry field
        if is_password:
            entry = tk.Entry(
                frame,
                font=("Arial", 10),
                show="*",
                width=50
            )
        else:
            entry = tk.Entry(
                frame,
                font=("Arial", 10),
                width=50
            )
        
        entry.insert(0, default_value)
        entry.pack(fill='x', pady=2)
        
        # Tooltip label
        tooltip = tk.Label(
            frame,
            text=tooltip_text,
            font=("Arial", 8),
            fg='#666666',
            bg='#f0f0f0',
            anchor='w',
            wraplength=500
        )
        tooltip.pack(anchor='w')
        
        # Store entry reference
        self.entries[key] = entry
    
    def load_config(self):
        """Load configuration from file"""
        config_file = 'config.yaml'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as file:
                    return yaml.safe_load(file) or {}
            except Exception as e:
                messagebox.showerror("Config Error", f"Error loading config: {str(e)}")
                return {}
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Collect values from entries
            config = {}
            for key, entry in self.entries.items():
                value = entry.get().strip()
                if value:  # Only save non-empty values
                    config[key] = value
            
            # Handle AI provider toggle logic
            provider = self.ai_provider.get()
            if provider == 'openai':
                # Only save OpenAI key, remove Gemini key
                if 'gemini_api_key' in config:
                    del config['gemini_api_key']
            elif provider == 'gemini':
                # Only save Gemini key, remove OpenAI key
                if 'openai_api_key' in config:
                    del config['openai_api_key']
            else:  # none
                # Remove both AI keys
                if 'openai_api_key' in config:
                    del config['openai_api_key']
                if 'gemini_api_key' in config:
                    del config['gemini_api_key']
            
            # Save to file
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
            # Update parent app's config
            if hasattr(self.parent, 'load_config'):
                self.parent.load_config()
            
            self.close_window()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving configuration: {str(e)}")
    
    def close_window(self):
        """Close the configuration window"""
        self.window.destroy()
