# verification_system.py
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import face_recognition
import numpy as np
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

class VerificationSystem:
    def __init__(self):
        self.registration_folder = "registered_users"
        self.cap = None
        self.registered_pil_image = None
        
        self.root = tk.Tk()
        self.root.title("Exam Verification")
        self.root.geometry("400x200")
        
        self.create_ui()
        self.root.mainloop()

    def create_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        self.student_id_var = tk.StringVar()
        
        ttk.Label(main_frame, text="Enter Student ID:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(main_frame, textvariable=self.student_id_var, width=25).grid(row=0, column=1, pady=5)
        
        ttk.Button(main_frame, text="Start Verification", 
                 command=self.start_verification).grid(row=1, column=0, columnspan=2, pady=10)
        
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)

    def start_verification(self):
        student_id = self.student_id_var.get().strip()
        if not student_id:
            self.status_label.config(text="Please enter Student ID!")
            return
        
        image_path = os.path.join(self.registration_folder, f"{student_id}.jpg")
        if not os.path.exists(image_path):
            self.status_label.config(text="No registration found for this ID!")
            return
        
        try:
            # Load registered image and keep it for display
            registered_image = face_recognition.load_image_file(image_path)
            self.registered_encoding = face_recognition.face_encodings(registered_image)[0]
            self.registered_pil_image = Image.fromarray(registered_image)
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {str(e)}")
            return
        
        self.start_webcam_verification()

    def start_webcam_verification(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not access webcam")
            return
        
        self.verification_window = tk.Toplevel(self.root)
        self.verification_window.title("Face Verification - Live vs Registered")
        
        self.video_label = ttk.Label(self.verification_window)
        self.video_label.pack(padx=10, pady=10)
        
        self.status_label = ttk.Label(self.verification_window, 
                                   font=("Helvetica", 12))
        self.status_label.pack(pady=10)
        
        self.verify_faces()

    def verify_faces(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # Create split-screen comparison
        live_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        live_pil = Image.fromarray(live_rgb)
        
        # Resize registered image to match live frame size
        registered_resized = self.registered_pil_image.resize(live_pil.size)
        
        # Create combined image with labels
        combined_width = live_pil.width + registered_resized.width
        combined_height = max(live_pil.height, registered_resized.height)
        combined_image = Image.new('RGB', (combined_width, combined_height))
        
        # Paste images side by side
        combined_image.paste(live_pil, (0, 0))
        combined_image.paste(registered_resized, (live_pil.width, 0))
        
        # Add text labels
        draw = ImageDraw.Draw(combined_image)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "Live Camera", fill=(255, 255, 0), font=font)
        draw.text((live_pil.width + 10, 10), "Registered Image", fill=(255, 255, 0), font=font)
        
        # Convert to Tkinter compatible format
        imgtk = ImageTk.PhotoImage(image=combined_image)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        # Face recognition logic
        face_locations = face_recognition.face_locations(live_rgb)
        face_encodings = face_recognition.face_encodings(live_rgb, face_locations)
        
        match = False
        for face_encoding in face_encodings:
            results = face_recognition.compare_faces([self.registered_encoding], face_encoding)
            if True in results:
                match = True
                break
        
        if match:
            self.status_label.config(text="Verification Successful! Starting exam...", foreground="green")
            self.cap.release()
            self.verification_window.after(2000, self.start_exam)
            return
        else:
            self.status_label.config(text="Face Not Recognized - Try Again", foreground="red")
        
        self.verification_window.after(10, self.verify_faces)

    def start_exam(self):
        self.verification_window.destroy()
        messagebox.showinfo("Exam Started", "You may now begin your exam!")
        # Add exam starting logic here

if __name__ == "__main__":
    VerificationSystem()
