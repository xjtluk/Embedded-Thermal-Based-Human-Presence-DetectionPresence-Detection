import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os  # Add import for directory and file handling

# File name and frame dimensions
csv_file = "dataset/person/data_person.csv"
# csv_file = "dataset/empty/data_empty.csv"
frame_width = 32
frame_height = 24

# Read data from CSV file
def read_csv_data(file):
    frames = []
    with open(file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip rows containing non-numeric data
            if any(not item.replace('.', '', 1).isdigit() for item in row):
                continue
            if len(row) == frame_width * frame_height:
                frame = np.array(row, dtype=float).reshape((frame_height, frame_width))
                frames.append(frame)
    return frames

# Plot thermal imaging
def plot_frames(frames):
    fig, ax = plt.subplots()
    im = ax.imshow(frames[0], cmap="inferno", interpolation="nearest", aspect="auto")
    plt.colorbar(im, ax=ax, label="Temperature (°C)")

    def update(frame):
        im.set_array(frame)
        return [im]

    ani = FuncAnimation(fig, update, frames=frames, interval=250, blit=True)
    plt.title("Thermal Imaging")
    plt.show()

# Save frames as images
def save_frames_as_images(frames, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        plt.imsave(f"{output_dir}/frame_{i+1}.png", frame, cmap="inferno")
    print(f"All frames have been saved to directory: {output_dir}")

# Main program
if __name__ == "__main__":
    frames = read_csv_data(csv_file)
    if frames:
        print(f"Successfully loaded {len(frames)} frames of data")
        output_dir = "output_images"  # Specify the output directory
        save_frames_as_images(frames, output_dir)  # Save frames as images
        plot_frames(frames)  # Plot the frames
    else:
        print("No valid data found, please check the CSV file!")