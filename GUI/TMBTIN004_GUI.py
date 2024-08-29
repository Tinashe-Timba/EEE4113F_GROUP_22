import cv2
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkinter import filedialog, Canvas, Scrollbar
from PIL import Image, ImageTk
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
from collections import Counter
from collections import defaultdict
import numpy as np
import threading
import time
import imagehash
import paramiko
from scp import SCPClient

# Global variables
mode = "dark"
current_image_index = 0
image_files = []
image_folder = None
directory = None
canvas = None
full_screen = False
cap = None

def download_images_scp():
    global image_folder
    if not image_folder:
        print("No directory specified. Please select the download directory first.")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname='lenkapi.local', username='mlenka', password='mlenka')
        stdin, stdout, stderr = ssh.exec_command('ls /home/mlenka/images/*.jpg')
        file_list = stdout.read().splitlines()
        with SCPClient(ssh.get_transport()) as scp:
            for file_path in file_list:
                filename = file_path.decode('utf-8').split('/')[-1]
                safe_filename = filename.replace(':', '-')
                local_file_path = os.path.join(image_folder, safe_filename)
                scp.get(file_path, local_path=local_file_path)
        print("All files downloaded and renamed successfully.")
    except Exception as e:
        print(f"Failed to download files: {str(e)}")
    finally:
        ssh.close()

def extract_date(filename):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return None

    try:
        with Image.open(filename) as img:
            exif_data = img._getexif()
            if not exif_data:
                print("No EXIF data found")
                return None

            date_str = exif_data.get(36868)
            if date_str:
                return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S").date()
            else:
                print("No relevant date information found in EXIF data")
                return None
    except IOError:
        print(f"Cannot open {filename}")
        return None

def extract_hour(filename):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return None

    try:
        with Image.open(filename) as img:
            exif_data = img._getexif()
            if not exif_data:
                print("No EXIF data found")
                return None

            date_str = exif_data.get(306)
            if date_str:
                try:
                    full_date_time = datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    return full_date_time.hour
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

    fig = Figure(figsize=(4, 4), dpi=100)  # Increase figure size
    ax = fig.add_subplot(111)

    ax.bar(range(len(sorted_dates)), [date_counts[date] for date in sorted_dates], color='red')
    ax.set_xticks(range(len(sorted_dates)))
    ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in sorted_dates], rotation=45, fontsize=6)  # Increase fontsize for x-axis labels

    ax.set_xlabel('Date', fontsize=14)  # Increase fontsize for x-axis label
    ax.set_ylabel('Number of Photos Taken', fontsize=14)  # Increase fontsize for y-axis label
    ax.set_title('Number of Photos Taken per Day', fontsize=16)  # Increase fontsize for title

    fig.tight_layout()  # Adjust layout to fit everything
    canvas = FigureCanvasTkAgg(fig, master=photost_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)




def plot_activity_heatmap(frame):
    hourly_counts = defaultdict(lambda: defaultdict(int))
    for filename in image_files:
        full_path = os.path.join(image_folder, filename)
        if os.path.exists(full_path):
            photo_date = extract_date(full_path)
            photo_hour = extract_hour(full_path)
            if photo_date and photo_hour is not None:
                hourly_counts[photo_date][photo_hour] += 1

    dates = sorted(hourly_counts.keys())
    hours = range(24)
    heatmap_data = [[hourly_counts[date].get(hour, 0) for hour in hours] for date in dates]

    fig = Figure(figsize=(4, 4), dpi=100)
    ax = fig.add_subplot(111)
    cax = ax.matshow(heatmap_data, interpolation='nearest', aspect='auto')
    fig.colorbar(cax)
    fig.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.15)

    ax.set_xticks(range(len(hours)))
    ax.set_xticklabels(hours, rotation=90, fontsize=10)  # Increase fontsize for x-axis
    ax.set_yticks(range(len(dates)))
    ax.set_yticklabels([date.strftime('%Y-%m-%d') for date in dates], fontsize=10)  # Increase fontsize for y-axis

    ax.set_title('Hourly Activity Heatmap', fontsize=14)  # Increase fontsize for title
    ax.set_xlabel('Hour of Day', fontsize=12)  # Increase fontsize for x-axis label
    ax.set_ylabel('Date', fontsize=12)  # Increase fontsize for y-axis label

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)



def save_observation():
    observation_text = observation_entry.get("1.0", "end-1c")
    if observation_text and observation_text != "Enter your observations here...":
        image_filename = image_files[current_image_index]
        observation_filename = os.path.join(image_folder, "Observations/observations.txt")

        with open(observation_filename, "a") as f:
            f.write(f"Image: {image_filename}\n")
            f.write(f"Observation: {observation_text}\n\n")

        print("Observation saved.")

def settings(choice, menu):
    global mode, image_folder
    if choice == "Choose Download Directory":
        image_folder = filedialog.askdirectory()
        print("Selected directory:", image_folder)
    elif choice == "Change Color Mode":
        if mode == "dark":
            ctk.set_appearance_mode("light")
            mode = "light"
        else:
            ctk.set_appearance_mode("dark")
            mode = "dark"
    
def change_color_mode():
    global mode
    if mode == "dark":
        ctk.set_appearance_mode("light")
        mode = "light"
    else:
        ctk.set_appearance_mode("dark")
        mode = "dark"
    update_text_color()

def display_media():
    global current_image_index, canvas, image_folder, image_files
    if current_image_index < len(image_files):
        media_path = os.path.join(image_folder, image_files[current_image_index])
        file_extension = media_path.split('.')[-1].lower()
        if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            display_image(media_path)
        elif file_extension in ['mp4', 'avi', 'mov']:
            display_video(media_path)

        # Check if observation box should show ghost text
        if observation_entry.get("1.0", "end-1c") == "":
            observation_entry.insert("1.0", "Enter your observations here...")
            observation_entry.configure(text_color="grey")
        else:
            update_text_color()

def display_image(image_path):
    for widget in image_frame.winfo_children():
        widget.destroy()

    image = Image.open(image_path)
    
    # Get the dimensions of the image_frame
    frame_width = image_frame.winfo_width()
    frame_height = image_frame.winfo_height()

    # Maintain the aspect ratio of the image
    aspect_ratio = image.width / image.height
    if frame_width / aspect_ratio <= frame_height:
        new_width = frame_width
        new_height = int(frame_width / aspect_ratio)
    else:
        new_height = frame_height
        new_width = int(frame_height * aspect_ratio)
    
    image = image.resize((new_width, new_height), Image.LANCZOS)
    photo_image = ImageTk.PhotoImage(image)
    
    image_label = ctk.CTkLabel(image_frame, image=photo_image)
    image_label.image = photo_image
    image_label.pack(fill="both", expand=True)


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

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def view_images():
    global image_files
    
    clear_frame(photost_frame)
    clear_frame(activity_frame)

    image_files = [file for file in os.listdir(image_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4', '.avi', '.mov'))]
    if image_folder:
        observation_folder = os.path.join(image_folder, "Observations")
        if not os.path.exists(observation_folder):
            os.makedirs(observation_folder)
    display_media()
    plot_photos_per_day()
    plot_activity_heatmap(activity_frame)
    show_frame(main_frame)

def display_video(video_path):
    for widget in image_frame.winfo_children():
        widget.destroy()

    cap = cv2.VideoCapture(video_path)
    play = [False]

    def toggle_play_pause(event=None):
        play[0] = not play[0]
        if play[0]:
            stream_video()

    def stream_video():
        while play[0] and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (image_frame.winfo_width(), image_frame.winfo_height()))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                label.image = photo
                label.configure(image=photo)
                image_frame.update_idletasks()
            else:
                break
            time.sleep(1 / 30)

    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (image_frame.winfo_width(), image_frame.winfo_height()))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        label = ctk.CTkLabel(image_frame, image=photo)
        label.image = photo
        label.pack(fill="both", expand=True)
        label.bind("<Button-1>", toggle_play_pause)

    return cap

def on_closing():
    if cap:
        cap.release()
    root.destroy()

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
    for widget in duplicates_container.winfo_children():
        widget.destroy()
    for dup in duplicates:
        duplicate_label = ctk.CTkLabel(duplicates_container, text=f"{dup[0]} is a duplicate of {dup[1]}")
        duplicate_label.pack(fill="x", padx=5, pady=2)

def update_scroll_region(event):
    scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all"))

def resize_plot_canvas(event, canvas):
    if canvas is not None and canvas.figure is not None:
        new_width = event.width
        new_height = event.height
        canvas.get_tk_widget().configure(width=new_width, height=new_height)
        canvas.figure.set_size_inches(float(new_width) / canvas.figure.dpi, float(new_height) / canvas.figure.dpi)
        canvas.draw()

def setup_grid_weights():
    root.grid_rowconfigure(0, weight=1)

    root.grid_columnconfigure(0, weight=1)

def set_background_image(frame, image_path):
    # Load the image using PIL
    image = Image.open(image_path)
    
    # Create a CTkImage object with the size of the frame
    frame_width = frame.winfo_width()
    frame_height = frame.winfo_height()
    
    # If the frame size is not set yet, use a default size or retry later
    if frame_width == 1 or frame_height == 1:
        frame_width = 1900
        frame_height = 900
    
    photo = ctk.CTkImage(light_image=image, dark_image=image, size=(frame_width, frame_height))

    # Create a Label to place the image on
    background_label = ctk.CTkLabel(frame, image=photo)
    background_label.image = photo  # Keep a reference to avoid garbage collection
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    

def update_text_color():
    global mode
    if mode == "dark":
        if observation_entry.get("1.0", "end-1c") == "Enter your observations here...":
            observation_entry.configure(text_color="grey")
        else:
            observation_entry.configure(text_color="white")
    else:
        if observation_entry.get("1.0", "end-1c") == "Enter your observations here...":
            observation_entry.configure(text_color="grey")
        else:
            observation_entry.configure(text_color="black")

def on_focus_in(event):
    if observation_entry.get("1.0", "end-1c") == "Enter your observations here...":
        observation_entry.delete("1.0", "end")
        observation_entry.configure(text_color="white" if mode == "dark" else "black")

def on_focus_out(event):
    if observation_entry.get("1.0", "end-1c") == "":
        observation_entry.insert("1.0", "Enter your observations here...")
        observation_entry.configure(text_color="grey")

def go_back():
    show_frame(welcome_frame)

def show_frame(frame):
    frame.tkraise()


def main():
    global root, welcome_frame, main_frame, image_frame, photost_frame, activity_frame, observation_entry, duplicates_canvas, duplicates_frame, settings_menu, scrollable_canvas, duplicates_container

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Observation System")
    root.geometry("1200x800")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    setup_grid_weights()

    # Initialize frames
    welcome_frame = ctk.CTkFrame(root)
    main_frame = ctk.CTkFrame(root)

    for frame in (welcome_frame, main_frame):
        frame.grid(row=0, column=0, sticky='nsew')

    # Ensure frames take the full window
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Set background image for welcome_frame
    set_background_image(welcome_frame, 'bb.webp')
       
    


    # Welcome frame
    welcome_label = ctk.CTkLabel(welcome_frame, text="Drongo Monitoring System", font=("Helvetica", 60), fg_color="transparent")
    welcome_label.place(relx=0.5, rely=0.1, anchor='center')

    button_width = 200  # Standard button width

    download_dir_button = ctk.CTkButton(welcome_frame, text="Select Download Directory", command=lambda: settings("Choose Download Directory", None), width=button_width)
    download_dir_button.place(relx=0.5, rely=0.4, anchor='center')

    download_images_button = ctk.CTkButton(welcome_frame, text="Download Images", command=download_images_scp, width=button_width)
    download_images_button.place(relx=0.5, rely=0.5, anchor='center')

    view_images_button = ctk.CTkButton(welcome_frame, text="View Images and Analytics", command=view_images, width=button_width)
    view_images_button.place(relx=0.5, rely=0.6, anchor='center')

    # Main frame
    main_frame.grid_rowconfigure(0, weight=0)
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_rowconfigure(2, weight=0)
    main_frame.grid_rowconfigure(3, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)
    main_frame.grid_columnconfigure(3, weight=1)
    main_frame.grid_columnconfigure(4, weight=1)

    button_container = ctk.CTkFrame(main_frame)
    button_container.grid(row=0, column=0, columnspan=2, sticky="nw", padx=5, pady=5)

    # Add the "Back" and "Change Color Mode" buttons to the button container frame
    back_button = ctk.CTkButton(button_container, text="Back", command=go_back, width=100)
    back_button.grid(row=0, column=0, padx=(0, 5))  # Add some padding to the right of the button

    change_color_mode_button = ctk.CTkButton(button_container, text="Switch Color Mode", command=change_color_mode)
    change_color_mode_button.grid(row=0, column=1)

    image_frame = ctk.CTkFrame(main_frame, width=600, height=300)
    image_frame.grid(row=1, column=0, rowspan=1, columnspan=3, sticky="nsew")

    button_frame = ctk.CTkFrame(main_frame)
    button_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    prev_button = ctk.CTkButton(button_frame, text="◀", command=prev_image, width=100)
    prev_button.grid(row=0, column=0)

    next_button = ctk.CTkButton(button_frame, text="▶", command=next_image, width=100)
    next_button.grid(row=0, column=2)

    observation_label = ctk.CTkLabel(main_frame, text="Record Observation:",font=("Helvetica", 20), fg_color="transparent")
    observation_label.grid(row=0, column=4, sticky="n", padx=5, pady=5)

    observation_entry = ctk.CTkTextbox(main_frame, width=300, height=300)
    observation_entry.grid(row=1, column=4, sticky="nsew", padx=5, pady=5)
    observation_entry.insert("1.0", "Enter your observations here...")
    observation_entry.configure(text_color="grey")
    observation_entry.bind("<FocusIn>", on_focus_in)
    observation_entry.bind("<FocusOut>", on_focus_out)

    save_observation_button = ctk.CTkButton(main_frame, text="Save", command=save_observation, width=100)
    save_observation_button.grid(row=2, column=4, padx=5, pady=5)

    bottom_frame = ctk.CTkFrame(main_frame)
    bottom_frame.grid(row=3, column=0, columnspan=5, sticky="ew")
    bottom_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_columnconfigure(2, weight=1)

    photost_frame = ctk.CTkFrame(bottom_frame, width=300, height=300)
    photost_frame.grid(row=0, column=0, sticky="nsew")

    activity_frame = ctk.CTkFrame(bottom_frame, width=300, height=300)
    activity_frame.grid(row=0, column=1, sticky="nsew")

    #duplicates_frame = ctk.CTkFrame(bottom_frame, width=300, height=300)
   # duplicates_frame.grid(row=0, column=2, sticky="nsew")

    # Scrollable canvas for duplicates
    scrollable_canvas = Canvas(bottom_frame)
    scrollable_canvas.grid(row=0, column=2, sticky="nsew")

    scrollbar = Scrollbar(bottom_frame, orient="vertical", command=scrollable_canvas.yview)
    scrollbar.grid(row=0, column=3, sticky="ns")

    scrollable_canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_canvas.bind("<Configure>", update_scroll_region)

    duplicates_container = ctk.CTkFrame(scrollable_canvas)
    scrollable_canvas.create_window((0, 0), window=duplicates_container, anchor="nw")

    # Create a frame inside the duplicates_container to hold the button and other content
    button_container = ctk.CTkFrame(duplicates_container)
    button_container.pack(side="bottom", fill="x", pady=5)

    # Add the check duplicates button at the bottom and center of the duplicates frame
    check_duplicates_button = ctk.CTkButton(scrollable_canvas, text="Check Duplicates", command=display_duplicates)
    check_duplicates_button.pack(side="bottom", pady=5, padx=5)


    root.bind("<Right>", next_image)
    root.bind("<Left>", prev_image)

    show_frame(welcome_frame)

    root.mainloop()

if __name__ == "__main__":
    main()