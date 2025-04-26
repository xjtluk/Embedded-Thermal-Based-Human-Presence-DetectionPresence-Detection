import serial, csv, time, os

port, baudrate = "COM6", 115200
num_frames, num_pixels = 20, 768
ser = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)

# Ensure directories exist
os.makedirs("dataset/person", exist_ok=True)
os.makedirs("dataset/empty", exist_ok=True)

while True:
    label = input("Mode (person/empty), exit to quit: ").strip().lower()
    if label == "exit":
        break
    csv_path = f"dataset/{label}/data_{label}.csv"
    with open(csv_path, "a", newline="") as file:
        writer = csv.writer(file)
        frame_count, buffer = 0, []
        print(f"Starting to collect {num_frames} frames for {label}...")
        while frame_count < num_frames:
            line = ser.readline().decode().strip()
            if line in ("START_FRAME","END_FRAME") or not line:
                continue
            buffer.extend(line.split(","))
            if len(buffer) >= num_pixels:
                writer.writerow(buffer[:num_pixels])
                buffer = buffer[num_pixels:]
                frame_count += 1
                print(f"  Collected {frame_count}/{num_frames}")
        print(f"{label} data collection complete, saved to {csv_path}\n")
ser.close()
