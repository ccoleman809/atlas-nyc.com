#!/usr/bin/env python3
"""
Screen Capture Tool for NYC Nightlife Content
Legal way to capture and submit content from any source
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import cv2
import numpy as np
import tempfile
import os
import threading
import time

class ScreenCaptureTools:
    def __init__(self, root):
        self.root = root
        self.root.title("NYC Nightlife Screen Capture Tool")
        self.root.geometry("400x300")
        
        self.is_recording = False
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="📱 Screen Capture Tool", 
                         font=("Arial", 16, "bold"))
        header.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Capture screenshots or screen recordings\nto share on NYC Nightlife platform",
                               font=("Arial", 10), justify="center")
        instructions.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Screenshot button
        tk.Button(button_frame, text="📸 Take Screenshot", 
                 command=self.take_screenshot,
                 font=("Arial", 12), bg="#28a745", fg="white",
                 width=20, height=2).pack(pady=5)
        
        # Screen recording button
        self.record_btn = tk.Button(button_frame, text="🎥 Start Recording", 
                                   command=self.toggle_recording,
                                   font=("Arial", 12), bg="#dc3545", fg="white",
                                   width=20, height=2)
        self.record_btn.pack(pady=5)
        
        # Open mobile portal button
        tk.Button(button_frame, text="🌐 Open Mobile Portal", 
                 command=self.open_mobile_portal,
                 font=("Arial", 12), bg="#007bff", fg="white",
                 width=20, height=2).pack(pady=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to capture", fg="green")
        self.status_label.pack(pady=10)
    
    def take_screenshot(self):
        try:
            self.status_label.config(text="Taking screenshot in 3 seconds...", fg="blue")
            self.root.update()
            
            # Give user time to prepare
            time.sleep(3)
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save to temp file
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f"nyc_nightlife_screenshot_{int(time.time())}.png")
            screenshot.save(filename)
            
            self.status_label.config(text=f"Screenshot saved: {filename}", fg="green")
            
            # Ask if user wants to open mobile portal
            if messagebox.askyesno("Screenshot Taken", 
                                  f"Screenshot saved to:\n{filename}\n\nOpen mobile portal to upload?"):
                self.open_mobile_portal()
                
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        try:
            self.is_recording = True
            self.record_btn.config(text="⏹️ Stop Recording", bg="#dc3545")
            self.status_label.config(text="Recording will start in 3 seconds...", fg="blue")
            self.root.update()
            
            # Start recording in background thread
            self.recording_thread = threading.Thread(target=self.record_screen)
            self.recording_thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            self.is_recording = False
    
    def stop_recording(self):
        self.is_recording = False
        self.record_btn.config(text="🎥 Start Recording", bg="#28a745")
        self.status_label.config(text="Stopping recording...", fg="blue")
    
    def record_screen(self):
        try:
            # Give user time to prepare
            time.sleep(3)
            
            # Get screen dimensions
            screen_size = pyautogui.size()
            
            # Define codec and create VideoWriter
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f"nyc_nightlife_recording_{int(time.time())}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(filename, fourcc, 20.0, screen_size)
            
            while self.is_recording:
                # Capture screenshot
                img = pyautogui.screenshot()
                
                # Convert to numpy array and BGR format
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Write frame
                out.write(frame)
                
                # Small delay to control frame rate
                time.sleep(0.05)
            
            # Release everything
            out.release()
            cv2.destroyAllWindows()
            
            self.root.after(0, lambda: self.recording_finished(filename))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Recording error: {e}", fg="red"))
    
    def recording_finished(self, filename):
        self.status_label.config(text=f"Recording saved: {filename}", fg="green")
        
        # Ask if user wants to open mobile portal
        if messagebox.askyesno("Recording Complete", 
                              f"Recording saved to:\n{filename}\n\nOpen mobile portal to upload?"):
            self.open_mobile_portal()
    
    def open_mobile_portal(self):
        import webbrowser
        webbrowser.open("http://localhost:8001/mobile")

def main():
    # Check if required packages are available
    try:
        import pyautogui
        import cv2
    except ImportError:
        print("Required packages not installed. Run:")
        print("pip install pyautogui opencv-python pillow")
        return
    
    root = tk.Tk()
    app = ScreenCaptureTools(root)
    root.mainloop()

if __name__ == "__main__":
    main()