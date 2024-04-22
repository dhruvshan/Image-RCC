import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageOps
import os
import threading

def resize_and_convert(input_directory, output_directory, target_width, target_height, preserve_aspect_ratio, output_format, compression_quality):
    total_size_before = 0
    total_size_after = 0

    try:
        image_count = 0
        total_images = sum(len(files) for _, _, files in os.walk(input_directory))
        for root, _, files in os.walk(input_directory):
            for filename in files:
                if filename.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                    input_path = os.path.join(root, filename)
                    output_path = os.path.join(output_directory, os.path.relpath(input_path, input_directory))
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with Image.open(input_path) as img:
                        # Calculate size before compression
                        if img.mode == "P":
                            img = img.convert("RGB")
                        total_size_before += os.path.getsize(input_path)

                        if preserve_aspect_ratio:
                            # Preserve aspect ratio and resize
                            img.thumbnail((target_width, target_height))
                            output_img = img
                        else:
                            # Force resize to exact dimensions
                            output_img = img.resize((target_width, target_height))

                        # Save resized image with compression quality
                        output_img.save(output_path, format=output_format, quality=compression_quality)

                        # Calculate size after compression
                        total_size_after += os.path.getsize(output_path)
                        image_count += 1
                        progress = (image_count / total_images) * 100
                        progress_var.set(progress)

        # Show total size before and after compression
        total_size_label.config(text=f"Total size before: {total_size_before / (1024*1024):.2f} MB\nTotal size after: {total_size_after / (1024*1024):.2f} MB")
        messagebox.showinfo("Success", "Images resized and converted successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def start_processing_thread():
    input_directory = input_entry.get()
    output_directory = output_entry.get()
    target_width_str = width_entry.get()

    preserve_aspect_ratio = preserve_aspect_ratio_var.get()
    output_format = format_entry.get().upper()
    compression_quality = compression_slider.get()

    if not input_directory:
        messagebox.showerror("Error", "Input directory is empty.")
        return
    
    # Validate output directory
    if not output_directory:
        messagebox.showerror("Error", "Output directory is empty.")
        return
    
    # Validate target width
    if not target_width_str:
        messagebox.showerror("Error", "Target width is empty.")
        return
    try:
        target_width = int(target_width_str)
    except ValueError:
        messagebox.showerror("Error", "Invalid target width. Please enter a valid integer value.")
        return
    
    # Validate target height
    if preserve_aspect_ratio_var.get():
        # If preserving aspect ratio, height is not needed
        target_height = int(target_width_str)
    else:
        target_height_str = height_entry.get()
        if not target_height_str:
            messagebox.showerror("Error", "Target height is empty.")
            return
        try:
            target_height = int(target_height_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid target height. Please enter a valid integer value.")
            return
    
    # Validate output format
    valid_formats = ["JPEG", "PNG", "GIF", "WEBP"]
    if not output_format:
        messagebox.showerror("Error", "Output format is empty.")
        return
    output_format = output_format.upper()
    if output_format not in valid_formats:
        messagebox.showerror("Error", f"Invalid output format '{output_format}'. Please enter one of: {', '.join(valid_formats)}")
        return

    processing_thread = threading.Thread(target=resize_and_convert, args=(input_directory, output_directory, target_width, target_height, preserve_aspect_ratio, output_format, compression_quality))
    processing_thread.start()

def toggle_height_entry():
    if preserve_aspect_ratio_var.get():
        height_label.grid_remove()
        height_entry.grid_remove()
    else:
        height_label.grid()
        height_entry.grid()
    
    if preserve_aspect_ratio_var.get() and width_entry.get():
        height_entry.delete(0, tk.END)

# Create main window
root = tk.Tk()
root.title("Resize, Convert and Compress Images")

root.configure(background="#f0f0f0")

# Input directory
input_label = tk.Label(root, text="Input Directory:")
input_label.grid(row=0, column=0, padx=5, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
browse_input_button = tk.Button(root, text="Browse", command=lambda: input_entry.insert(tk.END, filedialog.askdirectory()))
browse_input_button.grid(row=0, column=2, padx=5, pady=5)

# Output directory
output_label = tk.Label(root, text="Output Directory:")
output_label.grid(row=1, column=0, padx=5, pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
browse_output_button = tk.Button(root, text="Browse", command=lambda: output_entry.insert(tk.END, filedialog.askdirectory()))
browse_output_button.grid(row=1, column=2, padx=5, pady=5)

# Target width
width_label = tk.Label(root, text="Target Width (px):")
width_label.grid(row=2, column=0, padx=5, pady=5)
width_entry = tk.Entry(root, width=10)
width_entry.grid(row=2, column=1, padx=5, pady=5)

# Target height
height_label = tk.Label(root, text="Target Height (px):")
height_label.grid(row=3, column=0, padx=5, pady=5)
height_entry = tk.Entry(root, width=10)
height_entry.grid(row=3, column=1, padx=5, pady=5)

# Preserve aspect ratio option
preserve_aspect_ratio_var = tk.BooleanVar()
preserve_aspect_ratio_var.set(True)  # Default to preserving aspect ratio
preserve_aspect_ratio_checkbutton = tk.Checkbutton(root, text="Preserve Aspect Ratio", variable=preserve_aspect_ratio_var, command=toggle_height_entry)
preserve_aspect_ratio_checkbutton.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Compression quality
compression_label = tk.Label(root, text="Compression Quality:")
compression_label.grid(row=5, column=0, padx=5, pady=5)
compression_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
compression_slider.set(85)  # Default compression quality
compression_slider.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

# Output format
format_label = tk.Label(root, text="Output Format (png, jpeg, webp, gif):")
format_label.grid(row=6, column=0, padx=5, pady=5)
format_entry = tk.Entry(root, width=10)
format_entry.grid(row=6, column=1, padx=5, pady=5)

# Total size label
total_size_label = tk.Label(root, text="")
total_size_label.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

toggle_height_entry()

# Resize and convert button
convert_button = tk.Button(root, text="Resize, Convert, Compress", command=start_processing_thread)
convert_button.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

progress_var = tk.DoubleVar()
progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate', variable=progress_var)
progress_bar.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

# Run the GUI
root.mainloop()
