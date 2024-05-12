import cv2
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog

import customtkinter


#function for functionality 
def download_images():
    # Placeholder function for downloading images
    print("Downloading images...")

def save_observation():
    observation = observation_entry.get("1.0", "end-1c")
    # Placeholder function for saving observation
    print("Saving observation:", observation)

def open_directory():
    directory = filedialog.askdirectory()
    print("Selected directory:", directory)

def change_color_mode():
    # Placeholder function for changing color mode
    print("Changing color mode...")

#button style 
button_style = {"font": ("Tahoma", 12, "bold"), "bg": "black", "fg": "white", "relief": "raised", "borderwidth": 3, 
                "highlightbackground": "#3E4149", "highlightcolor": "#3E4149", "highlightthickness": 3}
# Styling for frame titles
frame_title_style = {"font": ("Tahoma", 14, "bold"), "fg": "white", "bg": "#3E4149", "padx": 2, "pady": 2}


#Main application window 
root = tk.Tk()
root.title("Drongo Activity Monitoring System")

 #Download button
download_button = tk.Button(root, text="Download Images", command=download_images,**button_style)
download_button.pack(padx=(10, 0), pady=(0, 10))

top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x")

# Frame for displaying images
image_frame = tk.Frame(top_frame, width=640, height=420, bg="white")
image_frame.pack(side="left", padx=(10), pady=(10, 0))

# Text entry for recording observations
# Text entry for recording observations
observation_label = tk.Label(top_frame, text="Record Observation:", **frame_title_style)
observation_label.pack( padx=(0, 10), pady=(10, 0))

observation_entry = tk.Text(top_frame, height=5, width=50)
observation_entry.pack(pady=(0, 10), fill="both", expand=True)

# Save button for recording observations
save_button = tk.Button(top_frame, text="Save Observation", command=save_observation,**button_style)
save_button.pack(side="left", pady=10)


#frame for the analytics tab
bot_frame = tk.Frame(root)
bot_frame.pack(side="bottom", fill="both", expand=True)


# Frame for analytics: Number of photos taken on a particular day
photost_frame = tk.Frame(bot_frame, width=200, height=200, bg="blue")
photost_frame.pack(side="left",padx=10, pady=10, fill="y")
photost_label = tk.Label(photost_frame, text="Analytics: Number of Photos Taken on a Particular Day", **frame_title_style)
photost_label.pack(padx=(0, 10), pady=(10, 0))



# Frame for analytics: Camera health
health_frame = tk.Frame(bot_frame, width=200, height=200, bg="white")
health_frame.pack(side="right", padx=10, pady=10,fill="y")
health_label = tk.Label(health_frame, text="Analytics: Camera Health", **frame_title_style)
health_label.pack(padx=(0, 10), pady=(10, 0))

# Frame for analytics: Drongo activity
activity_frame = tk.Frame(bot_frame, width=200, height=200, bg="black")
activity_frame.pack(anchor="s", padx=0, pady=10, fill="y")
activity_label = tk.Label(activity_frame, text="Analytics: Drongo Activity", **frame_title_style)
activity_label.pack(padx=(0, 10), pady=(10, 0))



# Create a menu bar for settings 
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

 #Creating  a settings dropdown
settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Choose Download Directory", command=open_directory)
settings_menu.add_command(label="Change Color Mode", command=change_color_mode)


# Run the application
root.mainloop()