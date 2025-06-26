#!/usr/bin/env python3
"""
Legal Content Submission Tool for NYC Nightlife
Helps users submit their own content through official APIs
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
from PIL import Image, ImageTk
import os

class ContentSubmissionTool:
    def __init__(self, root):
        self.root = root
        self.root.title("NYC Nightlife Content Submission Tool")
        self.root.geometry("500x600")
        
        self.api_base = "http://localhost:8001"
        self.venues = []
        self.selected_file = None
        
        self.setup_ui()
        self.load_venues()
    
    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="🌃 NYC Nightlife Content Submission", 
                         font=("Arial", 16, "bold"))
        header.pack(pady=10)
        
        # Legal notice
        legal_frame = tk.Frame(self.root, bg="#fff3cd", relief="solid", bd=1)
        legal_frame.pack(fill="x", padx=10, pady=5)
        
        legal_text = tk.Label(legal_frame, 
                             text="⚠️ Only submit content you own or have permission to share",
                             bg="#fff3cd", font=("Arial", 10), wraplength=450)
        legal_text.pack(pady=5)
        
        # Main form
        form_frame = tk.Frame(self.root)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Content Type
        tk.Label(form_frame, text="Content Type:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.content_type = ttk.Combobox(form_frame, values=["story", "post"], state="readonly")
        self.content_type.set("story")
        self.content_type.pack(fill="x", pady=(0, 10))
        
        # Venue Selection
        tk.Label(form_frame, text="Venue:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.venue_combo = ttk.Combobox(form_frame, state="readonly")
        self.venue_combo.pack(fill="x", pady=(0, 10))
        
        # Caption
        tk.Label(form_frame, text="Caption:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.caption_text = tk.Text(form_frame, height=3)
        self.caption_text.pack(fill="x", pady=(0, 10))
        
        # File Selection
        tk.Label(form_frame, text="Media File:", font=("Arial", 12, "bold")).pack(anchor="w")
        file_frame = tk.Frame(form_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        
        self.file_label = tk.Label(file_frame, text="No file selected", 
                                  relief="sunken", bg="white")
        self.file_label.pack(side="left", fill="x", expand=True)
        
        tk.Button(file_frame, text="Browse", command=self.select_file).pack(side="right", padx=(5, 0))
        
        # OR URL Input
        tk.Label(form_frame, text="OR Media URL:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.url_entry = tk.Entry(form_frame)
        self.url_entry.pack(fill="x", pady=(0, 10))
        
        # Submit Button
        tk.Button(form_frame, text="Submit Content", command=self.submit_content,
                 bg="#007bff", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        
        # Status
        self.status_label = tk.Label(form_frame, text="Ready to submit content", 
                                    fg="green")
        self.status_label.pack()
    
    def load_venues(self):
        try:
            response = requests.get(f"{self.api_base}/api/venues")
            if response.status_code == 200:
                self.venues = response.json()
                venue_names = [f"{v['name']} - {v['neighborhood']}" for v in self.venues]
                self.venue_combo['values'] = venue_names
                if venue_names:
                    self.venue_combo.set(venue_names[0])
                self.status_label.config(text=f"Loaded {len(self.venues)} venues", fg="green")
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            self.status_label.config(text=f"Error loading venues: {e}", fg="red")
    
    def select_file(self):
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif"),
            ("Video files", "*.mp4 *.mov *.avi *.webm"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select media file",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_file = filename
            basename = os.path.basename(filename)
            self.file_label.config(text=basename)
            self.url_entry.delete(0, tk.END)  # Clear URL if file selected
    
    def submit_content(self):
        # Validate inputs
        if not self.venue_combo.get():
            messagebox.showerror("Error", "Please select a venue")
            return
        
        if not self.selected_file and not self.url_entry.get():
            messagebox.showerror("Error", "Please select a file or enter a URL")
            return
        
        # Get venue ID
        venue_index = self.venue_combo.current()
        if venue_index < 0:
            messagebox.showerror("Error", "Invalid venue selection")
            return
        
        venue_id = self.venues[venue_index]['id']
        
        # Prepare data
        data = {
            'venue_id': venue_id,
            'content_type': self.content_type.get(),
            'caption': self.caption_text.get("1.0", tk.END).strip()
        }
        
        try:
            self.status_label.config(text="Submitting...", fg="blue")
            self.root.update()
            
            if self.selected_file:
                # File upload
                with open(self.selected_file, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(f"{self.api_base}/api/content", 
                                           data=data, files=files)
            else:
                # URL upload
                data['file_url'] = self.url_entry.get()
                response = requests.post(f"{self.api_base}/api/content", data=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                messagebox.showinfo("Success", f"Content submitted successfully!\nID: {result['id']}")
                self.clear_form()
                self.status_label.config(text="Content submitted successfully!", fg="green")
            else:
                error_msg = response.text
                messagebox.showerror("Error", f"Submission failed: {error_msg}")
                self.status_label.config(text="Submission failed", fg="red")
                
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {e}")
            self.status_label.config(text=f"Error: {e}", fg="red")
    
    def clear_form(self):
        self.caption_text.delete("1.0", tk.END)
        self.url_entry.delete(0, tk.END)
        self.selected_file = None
        self.file_label.config(text="No file selected")

def main():
    root = tk.Tk()
    app = ContentSubmissionTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()