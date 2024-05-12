import cv2
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkinter import filedialog  # Used for filedialog.askdirectory
from tkinter import Button
from tkinter import Canvas
from PIL import Image, ImageTk
import cv2
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime
from collections import Counter
from customtkinter import CTkImage
from collections import defaultdict
import numpy as np
import threading
import time
import imagehash
import paramiko
from scp import SCPClient
#gloabal variables
mode="dark"

current_image_index = 0
image_files = []
global image_folder
global directory
canvas = None
full_screen = False  
global cap  # 
cap = None  # 


# Function definitions remain unchanged
import paramiko
from scp import SCPClient
#Function definitions
def download_images_scp():
    global image_folder
    if not image_folder:
        print("No directory specified. Please select the download directory first.")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname='lenkapi.local', username='mlenka', password='mlenka')
        # Use SSH connection to list files in the directory first
        stdin, stdout, stderr = ssh.exec_command('ls /home/mlenka/images/*.jpg')
        file_list = stdout.read().splitlines()
        with SCPClient(ssh.get_transport()) as scp:
            for file_path in file_list:
                filename = file_path.decode('utf-8').split('/')[-1]
                safe_filename = filename.replace(':', '-')  #
                local_file_path = os.path.join(image_folder, safe_filename)
                # 
                scp.get(file_path, local_path=local_file_path)
        print("All files downloaded and renamed successfully.")
    except Exception as e:
        print(f"Failed to download files: {str(e)}")
    finally:
        ssh.close()


'''def extract_date(filename):
    with Image.open(filename) as img:
        exif_data = img._getexif()
        if not exif_data:
            print("No EXIF data found")
            return None

        date_str = exif_data.get(306) if 306 in exif_data else None  # Using 306 tag for DateTime
        if date_str:
            try:
                return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S").date()
            except ValueError as e:
                print(f"Error parsing date: {e}")
                return None
        else:
            print("No relevant date information found in EXIF data")
            return None'''

def extract_date(filename):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return None  # Skip non-image files

    try:
        with Image.open(filename) as img:
            exif_data = img._getexif()
            if not exif_data:
                print("No EXIF data found")
                return None

            date_str = exif_data.get(36868)  # Using 36868 tag for DateTime
            if date_str:
                return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S").date()
            else:
                print("No relevant date information found in EXIF data")
                return None
    except IOError:
        print(f"Cannot open {filename}")
        return None


'''def extract_hour(filename):
    with Image.open(filename) as img:
        exif_data = img._getexif()
        if not exif_data:
            print("No EXIF data found")
            return None

        # Extracting the DateTime string from the EXIF data
        date_str = exif_data.get(306)  # Using 36867 tag for DateTimeOriginal
        if date_str:
            try:
                # Parse the full datetime from the string
                full_date_time = datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                return full_date_time.hour  # Return just the hour part
            except ValueError as e:
                print(f"Error parsing date and time: {e}")
                return None
        else:
            print("No relevant date and time information found in EXIF data")
            return None'''

def extract_hour(filename):
    # Check if the file is an image before trying to open it
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return None  # Skip non-image files

    try:
        with Image.open(filename) as img:
            exif_data = img._getexif()
            if not exif_data:
                print("No EXIF data found")
                return None

            date_str = exif_data.get(306)  # Using tag 306 for DateTime
            if date_str:
                try:
                    full_date_time = datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    return full_date_time.hour  # Return just the hour part
                except ValueError as e:
                    print(f"Error parsing date and time: {e}")
                    return None
            else:
                print("No relevant date and time information found in EXIF data")
                return None
    except IOError:
        print(f"Cannot open {filename}")
        return None




def plot_photos_per_day():
    dates = [extract_date(os.path.join(image_folder, filename)) for filename in image_files if os.path.exists(os.path.join(image_folder, filename))]
    dates = [date for date in dates if date is not None]
    date_counts = Counter(dates)
    sorted_dates = sorted(date_counts.keys())

    fig = Figure(figsize=(4, 2), dpi=50)
    ax = fig.add_subplot(111)

    # Create a bar graph with dates on the x-axis and counts on the y-axis
    ax.bar(range(len(sorted_dates)), [date_counts[date] for date in sorted_dates], color='red')

    # Set the x-axis labels to the dates, rotated for better readability
    ax.set_xticks(range(len(sorted_dates)))  # Set x-ticks positions
    ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in sorted_dates], rotation=45)  # Set x-tick labels

    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Photos Taken')
    ax.set_title('Number of Photos Taken per Day')

    canvas = FigureCanvasTkAgg(fig, master=photost_frame)
    if canvas.get_tk_widget().winfo_ismapped():  # Check if widget is already drawn
        canvas.draw_idle()  # Update existing canvas
    else:
        canvas.draw()  # Draw new canvas
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True)



 #   plot_photos_per_day()

def plot_activity_heatmap(frame):
    
    hourly_counts = defaultdict(lambda: defaultdict(int))  # day -> hour -> count
    for filename in image_files:
        full_path = os.path.join(image_folder, filename)
        if os.path.exists(full_path):
            photo_date = extract_date(full_path)
            photo_hour = extract_hour(full_path)  # Assuming this function exists
            if photo_date and photo_hour is not None:
                hourly_counts[photo_date][photo_hour] += 1
    
    # Prepare data for the heatmap
    dates = sorted(hourly_counts.keys())
    hours = range(24)  # 0 to 23 hours
    heatmap_data = [[hourly_counts[date].get(hour,0) for hour in hours] for date in dates]

    fig = Figure(figsize=(4, 4), dpi=100)
    ax = fig.add_subplot(111)
    cax = ax.matshow(heatmap_data, interpolation='nearest', aspect='auto')
    fig.colorbar(cax)
    fig.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.15) 

    # Set the ticks and labels for the x-axis (hours)
    ax.set_xticks(range(len(hours)))  # Setting tick positions explicitly
    ax.set_xticklabels(hours, rotation=90)  # Apply hour labels to the defined ticks

    # Set the ticks and labels for the y-axis (dates)
    ax.set_yticks(range(len(dates)))  # Setting tick positions explicitly
    ax.set_yticklabels([date.strftime('%Y-%m-%d') for date in dates])  # Apply date labels to the defined ticks

    ax.set_title('Hourly Activity Heatmap')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Date')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)





def save_observation():
   
    observation_text = observation_entry.get("1.0", "end-1c")
    if observation_text:
        image_filename = image_files[current_image_index]
        observation_filename = os.path.join(image_folder, "Observations/observations.txt")

        with open(observation_filename, "a") as f:
            f.write(f"Image: {image_filename}\n")
            f.write(f"Observation: {observation_text}\n\n")

        print("Observation saved.")

def settings(choice):
    global mode, image_folder
    if choice == "Choose Download Directory":
        image_folder = filedialog.askdirectory()
        print("Selected directory:", image_folder)
      
    elif choice == "Change Color Mode":
        # Placeholder function for changing color mode
        if mode == "dark":
            ctk.set_appearance_mode("light")
            mode = "light"
        else:
            ctk.set_appearance_mode("dark")
            mode = "dark"  
def setup_grid_weights():
    root.grid_rowconfigure(0, weight=0)  
    root.grid_columnconfigure(0, weight=0)  
   

'''def toggle_full_screen(event=None):
    global full_screen
    full_screen = not full_screen  # Toggle the state
    if full_screen:
        # Expand the image_frame to cover the entire grid
        image_frame.grid(row=0, column=0, sticky="nsew", columnspan=100, rowspan=100)  # Use large spans to cover grid
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
    else:
        # Restore the original grid configuration
        image_frame.grid(row=0, column=2, sticky="nsew", columnspan=1, rowspan=1)
        setup_grid_weights()  # Restore the original grid weights configuration

    display_image()  # Update the image display according to new frame size'''




def display_media():
    global current_image_index, canvas, image_folder, image_files
    if current_image_index < len(image_files):
        media_path = os.path.join(image_folder, image_files[current_image_index])
        file_extension = media_path.split('.')[-1].lower()
        if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            display_image(media_path)
        elif file_extension in ['mp4', 'avi', 'mov']:
            display_video(media_path)

def display_image(image_path):
    for widget in image_frame.winfo_children():
        widget.destroy()
    image = Image.open(image_path)
    image.thumbnail((image_frame.winfo_width(), image_frame.winfo_height()), Image.LANCZOS)
    photo_image = ImageTk.PhotoImage(image)
    image_label = ctk.CTkLabel(image_frame, image=photo_image)
    image_label.image = photo_image  # Keep a reference
    image_label.pack(fill="both", expand=True)




'''def display_image():
    for widget in image_frame.winfo_children():
        widget.destroy()

    if current_image_index < len(image_files):
        image_path = os.path.join(image_folder, image_files[current_image_index])
        image = Image.open(image_path)

        # Determine the size based on the current size of the image frame
        size = (image_frame.winfo_width(), image_frame.winfo_height())

        image.thumbnail(size, Image.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)

        image_label = ctk.CTkLabel(image_frame, image=photo_image)
        image_label.image = photo_image  # Keep a reference!
        image_label.pack(fill="both", expand=True)'''




def next_image(event=None):
    global current_image_index
    if current_image_index < len(image_files) - 1:
        current_image_index += 1
        display_media()

def prev_image(event=None):
     global current_image_index
     if current_image_index > 0:
        current_image_index -= 1
        display_media()

'''def view_images():
    
     # List image files in the selected folder
   global image_files 
   image_files= [file for file in os.listdir(image_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
   if image_folder:
        observation_folder = os.path.join(image_folder, "Observations")
        if not os.path.exists(observation_folder):
            os.makedirs(observation_folder)
   display_image()
   plot_photos_per_day()
   # Assume 'activity_frame' is already defined in your GUI as a ctk.CTkFrame or similar
   plot_activity_heatmap(activity_frame)'''
def view_images():
    global image_files
    image_files = [file for file in os.listdir(image_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4', '.avi', '.mov'))]
    if image_folder:
        observation_folder = os.path.join(image_folder, "Observations")
        if not os.path.exists(observation_folder):
            os.makedirs(observation_folder)
    display_media()
    plot_photos_per_day()
    plot_activity_heatmap(activity_frame)



#adding video playing capapbilities:
'''def display_video(video_path)
    for widget in image_frame.winfo_children():
        widget.destroy()

    cap = cv2.VideoCapture(video_path)
    play = [True]  # Use list to manipulate play status inside nested function

    def toggle_play_pause(event=None):
        play[0] = not play[0]  # Toggle play status
        if play[0]:  # If toggling to play, start the stream
            stream_video()

    def stream_video():
        while play[0] and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (image_frame.winfo_width(), image_frame.winfo_height()))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=frame)
                if 'label' not in locals():
                    label = ctk.CTkLabel(image_frame, image=photo)
                    label.image = photo
                    label.pack(fill="both", expand=False)
                    label.bind("<Button-1>", toggle_play_pause)
                else:
                    label.configure(image=photo)
                    label.image = photo
            else:
                break
            
    def start_streaming():
        threading.Thread(target=stream_video, daemon=True).start()

    start_streaming()'''

def display_video(video_path):
    for widget in image_frame.winfo_children():
        widget.destroy()

    cap = cv2.VideoCapture(video_path)
    play = [False]  # Start with video paused

    def toggle_play_pause(event=None):
        play[0] = not play[0]  # Toggle play status
        if play[0]:  # If toggling to play, start the stream
            stream_video()

    def stream_video():
        # Only process frames if the video is in the "play" state
        while play[0] and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (image_frame.winfo_width(), image_frame.winfo_height()))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                label.image = photo
                label.configure(image=photo)
                image_frame.update_idletasks()  # Minor GUI updates
            else:
                break
            time.sleep(1/30)  # Adjust playback to frame rate 

    # Set up the initial display to show first frame and wait for play
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (image_frame.winfo_width(), image_frame.winfo_height()))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        label = ctk.CTkLabel(image_frame, image=photo)
        label.image = photo
        label.pack(fill="both", expand=True)
        label.bind("<Button-1>", toggle_play_pause)  # Bind mouse click to toggle play/pause

    return cap  # Return the capture object for proper cleanup later

# Proper resource management
def on_closing():
    if cap:  # If there's a video capture object
        cap.release()
    root.destroy()
    
#function to detect duplicated photos
def find_duplicate_images(image_folder):
    hashes = {}
    duplicates = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_path = os.path.join(image_folder, filename)
            with Image.open(file_path) as img:
                hash = str(imagehash.average_hash(img))
            if hash in hashes:
                duplicates.append((filename, hashes[hash]))
            else:
                hashes[hash] = filename
    return duplicates

   
def display_duplicates():
    duplicates = find_duplicate_images(image_folder)
    duplicate_text = "\n".join([f"{dup[0]} is a duplicate of {dup[1]}" for dup in duplicates])
    duplicates_label.configure(text=duplicate_text)

def update_scroll_region(event):
    scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all"))
    scrollable_canvas_frame.bind("<Configure>", update_scroll_region)       

def resize_plot_canvas(event, canvas):
       if canvas is not None and canvas.figure is not None:
        # Get the new width and height from the event
        new_width = event.width
        new_height = event.height

        #  new size of the canvas
        canvas.get_tk_widget().configure(width=new_width, height=new_height)

        # Adjust the figure size 
        canvas.figure.set_size_inches(float(new_width) / canvas.figure.dpi, float(new_height) / canvas.figure.dpi)

        # Redraw the plot with the updated dimensions
        canvas.draw()

# Main application window (using CTk)
root = ctk.CTk()
root.title("Drongo Activity Monitoring System")
root.geometry("1500x1500")

download_button = ctk.CTkButton(root, text="Download Images",command=download_images_scp) #, command=download_images
download_button.pack(padx=(10, 0), pady=(0, 10))  # Pack at top with padding
# Top frame (using CTkFrame)
top_frame = ctk.CTkFrame(root)
top_frame.pack(fill="both", expand=True)  # Fill remaining space
# Download button (using CTkButton)



# Frame for displaying images (using CTkFrame)
image_frame = ctk.CTkFrame(top_frame, width=640, height=420)
image_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")  # Grid placement
image_frame.grid_propagate(False) # will stop from resizing


# Bottom frame (using most of the space)
bot_frame = ctk.CTkFrame(root)
bot_frame.pack(fill="both", expand=True)

# Frames within bottom frame
photost_frame = ctk.CTkFrame(bot_frame)
photost_frame.pack(side="left", fill="both", expand=True)

health_frame = ctk.CTkFrame(bot_frame)
health_frame.pack(side="left", fill="both", expand=True)

scrollable_frame = ctk.CTkFrame(health_frame)
scrollable_canvas =Canvas(scrollable_frame)
scrollable_canvas.pack(side="left", fill="both", expand=True)
scrollbar = ctk.CTkScrollbar(scrollable_frame, command=scrollable_canvas.yview)
scrollbar.pack(side="right", fill="y")
scrollable_canvas.configure(yscrollcommand=scrollbar.set)
scrollable_canvas_frame = ctk.CTkFrame(scrollable_canvas)
scrollable_canvas.create_window((0, 0), window=scrollable_canvas_frame, anchor="nw")

duplicates_label = ctk.CTkLabel(scrollable_canvas_frame, text="", wraplength=400)
duplicates_label.pack(pady=10, padx=10, fill='both', expand=True)
scrollable_frame.pack(fill='both', expand=True)

check_duplicates_button = ctk.CTkButton(health_frame, text="Check Duplicates", command=display_duplicates)
check_duplicates_button.pack(pady=10)


activity_frame = ctk.CTkFrame(bot_frame)
activity_frame.pack(side="right", fill="both", expand=True)

#activity_label = ctk.CTkLabel(activity_frame, text="Drongo Activity")
#activity_label.pack(padx=10, pady=10)  # Pack with padding within activity_frame



'''# 
toggle_button = ctk.CTkButton(top_frame, text="Toggle Full Screen", command=toggle_full_screen)
toggle_button.grid(row=1, column=0, padx=10, pady=10) '''


'''# Key binding for full screen toggle
root.bind("<F11>", toggle_full_screen)  # Press F11 to toggle full screen
root.bind("<Escape>", lambda event: toggle_full_screen() if full_screen else None)  # Press Escape to exit full screen if in full screen mode'''


View = ctk.CTkButton(top_frame, text="View Images", command=view_images)
View.grid(row=1, column=3, padx=10, pady=10, sticky="nsew") # Pack at top with padding



# Scrolling buttons
next_button = ctk.CTkButton(top_frame, text="Next", command=next_image)
next_button.grid(row=0, column=3, padx=10, pady=10)  # Grid placement

prev_button = ctk.CTkButton(top_frame, text="Previous", command=prev_image)
prev_button.grid(row=0, column=0, padx=10, pady=10)  # Grid placement

# Text entry for recording observations (using CTkLabel and CTkEntry)
observation_label = ctk.CTkLabel(top_frame, text="Record Observation:")
observation_label.grid(row=0, column=4, padx=10, pady=10, sticky="w")  # Grid placement, anchor west

observation_entry = ctk.CTkTextbox(top_frame, height=300, width=300)
observation_entry.grid(row=0, column=5, padx=50, pady=50, sticky="ew")  # Grid placement, expand horizontally

# Save button for recording observations (using CTkButton)
save_button = ctk.CTkButton(top_frame, text="Save Observation", command=save_observation)
save_button.grid(row=1, column=5, padx=10, pady=10, sticky="e")  # Grid placement, anchor east
#Settings Menu
# Create a menu bar for settings 
options=["Choose Download Directory","Change Color Mode"]
# Creating a settings dropdown (using CTkOptionMenu)
settings_menu = ctk.CTkOptionMenu(root,values=options,command=settings)
settings_menu.place(x=10, y=10)






#events 
# Path to the folder containing images
#image_folder = "C:/Users/3520/Desktop/Tinashe Timba 0539/"

root.bind("<Configure>", lambda event, canvas=canvas: resize_plot_canvas(event, canvas))
root.protocol("WM_DELETE_WINDOW", on_closing)



root.mainloop()


