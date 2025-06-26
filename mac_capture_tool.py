#!/usr/bin/env python3
"""
Mac Screen Capture Tool for NYC Nightlife
Native macOS screen capture with automatic upload
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import tempfile
import os
import requests
import json
import threading
from datetime import datetime

class MacCaptureTools:
    def __init__(self, root):
        self.root = root
        self.root.title("NYC Nightlife - Mac Capture Tool")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        
        self.api_base = "http://localhost:8001"
        self.venues = []
        self.captured_file = None
        
        self.setup_ui()
        self.load_venues()
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🌃 NYC Nightlife Capture Tool", 
                        font=("SF Pro Display", 18, "bold"), 
                        fg="white", bg="#2c3e50")
        title.pack(expand=True)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Capture section
        capture_frame = tk.LabelFrame(main_frame, text="📱 Capture Options", 
                                     font=("SF Pro Display", 14, "bold"),
                                     bg="#f0f0f0", padx=10, pady=10)
        capture_frame.pack(fill="x", pady=(0, 20))
        
        # Screenshot buttons
        btn_frame1 = tk.Frame(capture_frame, bg="#f0f0f0")
        btn_frame1.pack(fill="x", pady=5)
        
        tk.Button(btn_frame1, text="📸 Screenshot (Selection)", 
                 command=lambda: self.mac_screenshot("selection"),
                 font=("SF Pro Display", 12), bg="#007AFF", fg="white",
                 width=20, height=2, relief="flat").pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame1, text="🖥️ Screenshot (Full Screen)", 
                 command=lambda: self.mac_screenshot("fullscreen"),
                 font=("SF Pro Display", 12), bg="#34C759", fg="white",
                 width=20, height=2, relief="flat").pack(side="left")
        
        # Screen recording button
        btn_frame2 = tk.Frame(capture_frame, bg="#f0f0f0")
        btn_frame2.pack(fill="x", pady=5)
        
        self.record_btn = tk.Button(btn_frame2, text="🎥 Screen Recording", 
                                   command=self.mac_screen_record,
                                   font=("SF Pro Display", 12), bg="#FF3B30", fg="white",
                                   width=42, height=2, relief="flat")
        self.record_btn.pack()
        
        # Upload section
        upload_frame = tk.LabelFrame(main_frame, text="📤 Upload to NYC Nightlife", 
                                    font=("SF Pro Display", 14, "bold"),
                                    bg="#f0f0f0", padx=10, pady=10)
        upload_frame.pack(fill="both", expand=True)
        
        # File display
        file_frame = tk.Frame(upload_frame, bg="#f0f0f0")
        file_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(file_frame, text="Selected File:", font=("SF Pro Display", 12, "bold"),
                bg="#f0f0f0").pack(anchor="w")
        
        self.file_label = tk.Label(file_frame, text="No file captured yet", 
                                  relief="sunken", bg="white", anchor="w",
                                  font=("SF Pro Display", 11))
        self.file_label.pack(fill="x", pady=(5, 0))
        
        # Browse for existing file
        tk.Button(file_frame, text="📁 Browse Existing File", 
                 command=self.browse_file,
                 font=("SF Pro Display", 11), bg="#8E8E93", fg="white",
                 relief="flat").pack(anchor="w", pady=(5, 0))
        
        # Venue selection
        venue_frame = tk.Frame(upload_frame, bg="#f0f0f0")
        venue_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(venue_frame, text="Venue:", font=("SF Pro Display", 12, "bold"),
                bg="#f0f0f0").pack(anchor="w")
        
        self.venue_combo = ttk.Combobox(venue_frame, font=("SF Pro Display", 11))
        self.venue_combo.pack(fill="x", pady=(5, 10))
        
        # Content type
        type_frame = tk.Frame(upload_frame, bg="#f0f0f0")
        type_frame.pack(fill="x")
        
        tk.Label(type_frame, text="Content Type:", font=("SF Pro Display", 12, "bold"),
                bg="#f0f0f0").pack(anchor="w")
        
        self.content_type = ttk.Combobox(type_frame, values=["story", "post"], 
                                        font=("SF Pro Display", 11))
        self.content_type.set("story")
        self.content_type.pack(fill="x", pady=(5, 10))
        
        # Caption
        tk.Label(upload_frame, text="Caption (optional):", font=("SF Pro Display", 12, "bold"),
                bg="#f0f0f0").pack(anchor="w")
        
        self.caption_text = tk.Text(upload_frame, height=3, font=("SF Pro Display", 11))
        self.caption_text.pack(fill="x", pady=(5, 10))
        
        # Upload button
        self.upload_btn = tk.Button(upload_frame, text="🚀 Upload to NYC Nightlife", 
                                   command=self.upload_content,
                                   font=("SF Pro Display", 13, "bold"), 
                                   bg="#FF9500", fg="white",
                                   height=2, relief="flat")
        self.upload_btn.pack(fill="x", pady=(10, 0))
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to capture content", 
                                    font=("SF Pro Display", 11), fg="#34C759", bg="#f0f0f0")
        self.status_label.pack(pady=5)
    
    def load_venues(self):
        try:
            response = requests.get(f"{self.api_base}/api/venues", timeout=5)
            if response.status_code == 200:
                self.venues = response.json()
                venue_names = [f"{v['name']} - {v['neighborhood']}" for v in self.venues]
                self.venue_combo['values'] = venue_names
                if venue_names:
                    self.venue_combo.set(venue_names[0])
                self.status_label.config(text=f"✅ Loaded {len(self.venues)} venues", fg="#34C759")
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            self.status_label.config(text=f"⚠️ Could not connect to API: {e}", fg="#FF3B30")
    
    def mac_screenshot(self, mode):
        try:
            self.status_label.config(text="📸 Taking screenshot...", fg="#007AFF")
            self.root.update()
            
            # Create temp file
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(temp_dir, f"nyc_nightlife_screenshot_{timestamp}.png")
            
            if mode == "selection":
                # Interactive selection (Cmd+Shift+4)
                cmd = ["screencapture", "-i", filename]
            else:
                # Full screen (Cmd+Shift+3)
                cmd = ["screencapture", filename]
            
            # Run screencapture command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(filename):
                self.captured_file = filename
                self.file_label.config(text=os.path.basename(filename))
                self.status_label.config(text="✅ Screenshot captured successfully!", fg="#34C759")
            else:
                self.status_label.config(text="❌ Screenshot cancelled or failed", fg="#FF3B30")
                
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {e}", fg="#FF3B30")
    
    def mac_screen_record(self):
        try:
            self.status_label.config(text="🎥 Starting screen recording...", fg="#007AFF")
            self.root.update()
            
            # Create temp file
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(temp_dir, f"nyc_nightlife_recording_{timestamp}.mov")
            
            # macOS screen recording command (requires user permission)
            # This will open the native screen recording interface
            cmd = ["screencapture", "-v", filename]
            
            # Run in background thread
            def record():
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0 and os.path.exists(filename):
                        self.root.after(0, lambda: self.recording_complete(filename))
                    else:
                        self.root.after(0, lambda: self.status_label.config(
                            text="❌ Recording cancelled or failed", fg="#FF3B30"))
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"❌ Recording error: {e}", fg="#FF3B30"))
            
            threading.Thread(target=record).start()
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {e}", fg="#FF3B30")
    
    def recording_complete(self, filename):
        self.captured_file = filename
        self.file_label.config(text=os.path.basename(filename))
        self.status_label.config(text="✅ Screen recording completed!", fg="#34C759")
    
    def browse_file(self):
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.heic"),
            ("Video files", "*.mp4 *.mov *.avi *.webm"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select media file",
            filetypes=filetypes
        )
        
        if filename:
            self.captured_file = filename
            self.file_label.config(text=os.path.basename(filename))
            self.status_label.config(text="✅ File selected", fg="#34C759")
    
    def upload_content(self):
        # Validate inputs
        if not self.captured_file:
            messagebox.showerror("Error", "Please capture or select a file first")
            return
        
        if not os.path.exists(self.captured_file):
            messagebox.showerror("Error", "Selected file no longer exists")
            return
        
        if not self.venue_combo.get():
            messagebox.showerror("Error", "Please select a venue")
            return
        
        # Get venue ID
        venue_index = self.venue_combo.current()
        if venue_index < 0:
            messagebox.showerror("Error", "Invalid venue selection")
            return
        
        venue_id = self.venues[venue_index]['id']
        
        try:
            self.status_label.config(text="🚀 Uploading content...", fg="#007AFF")
            self.upload_btn.config(state="disabled")
            self.root.update()
            
            # Prepare data
            data = {
                'venue_id': venue_id,
                'content_type': self.content_type.get(),
                'caption': self.caption_text.get("1.0", tk.END).strip()
            }
            
            # Upload file
            with open(self.captured_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.api_base}/api/content", 
                                       data=data, files=files, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                messagebox.showinfo("Success", 
                                   f"Content uploaded successfully!\n\nID: {result['id']}\n\nView at: http://localhost:8001/public")
                self.clear_form()
                self.status_label.config(text="✅ Upload successful!", fg="#34C759")
            else:
                error_msg = response.text
                messagebox.showerror("Upload Failed", f"Error: {error_msg}")
                self.status_label.config(text="❌ Upload failed", fg="#FF3B30")
                
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", "Upload timed out. Please try again.")
            self.status_label.config(text="⏱️ Upload timed out", fg="#FF9500")
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {e}")
            self.status_label.config(text=f"❌ Error: {e}", fg="#FF3B30")
        finally:
            self.upload_btn.config(state="normal")
    
    def clear_form(self):
        self.caption_text.delete("1.0", tk.END)
        self.captured_file = None
        self.file_label.config(text="No file captured yet")

def main():
    root = tk.Tk()
    app = MacCaptureTools(root)
    
    # Set app icon if available
    try:
        # You can add an icon file here
        # root.iconbitmap('app_icon.ico')
        pass
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()