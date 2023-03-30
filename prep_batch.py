#########
#########prepare some folders#########
#########
import os
print("Creating the correct directory structure.")
folders = ["exports", "data", "models"]

for folder_name in folders:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder '{folder_name}'")
    else:
        print(f"Folder '{folder_name}' already exists")
#########
#########create a list#########
#########
import os
import csv
print("Creating a list of audio file pairs.")
folder_path = "materials/"

file_list = os.listdir(folder_path)

name_set = set()

for file_name in file_list:
    if file_name.endswith("_In.wav") or file_name.endswith("_Out.wav"):
        name_without_suffix = '_'.join(file_name.split('_')[:-1])
        name_set.add(name_without_suffix)

unique_names = sorted(list(name_set))

output_dir = ""

output_file = os.path.join(output_dir, "list.csv")
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for name in unique_names:
        writer.writerow([name])
#########
#########determine the audio file alignment values#########
#########
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from data import wav_to_np
from typing import Optional

print("Calculating the delay between input and output audio.")

_V1_BLIP_LOCATIONS = 12_000, 36_000

def _calibrate_delay_v1(input_path, output_path) -> int:
    lookahead = 1_000
    lookback = 10_000
    safety_factor = 4

    # Calibrate the trigger:
    y = wav_to_np(output_path)[:48_000]
    background_level = np.max(np.abs(y[:6_000]))
    trigger_threshold = max(background_level + 0.01, 1.01 * background_level)

    delays = []
    for blip_index, i in enumerate(_V1_BLIP_LOCATIONS, 1):

        start_looking = i - lookahead
        stop_looking = i + lookback
        y_scan = y[start_looking:stop_looking]
        triggered = np.where(np.abs(y_scan) > trigger_threshold)[0]
        if len(triggered) == 0:
            msg = (
                f"No response activated the trigger in response to blip "
                f"{blip_index}. Is something wrong with the reamp?"
            )
            print(msg)
            print("SHARE THIS PLOT IF YOU ASK FOR HELP")
            plt.figure()
            plt.plot(np.arange(-lookahead, lookback), y_scan, label="Signal")
            plt.axvline(x=0, color="C1", linestyle="--", label="Trigger")
            plt.axhline(
                y=-trigger_threshold, color="k", linestyle="--", label="Threshold"
            )
            plt.axhline(y=trigger_threshold, color="k", linestyle="--")
            plt.xlim((-lookahead, lookback))
            plt.xlabel("Samples")
            plt.ylabel("Response")
            plt.legend()
            plt.show()
            raise RuntimeError(msg)
        else:
            j = triggered[0]
            delays.append(j + start_looking - i)

    print("{title} Delay:")
    for d in delays:
        print(f" {d}")
    delay = int(np.min(delays)) - safety_factor
    print(f"After applying safety factor, final delay for {title} is {delay}")
    return delay

def _plot_delay_v1(delay: int, input_path: str, output_path: str, title: str, _nofail=True):
    print("Plotting the delay for manual inspection...")
    x = wav_to_np(input_path)[:48_000]
    y = wav_to_np(output_path)[:48_000]
    i = np.where(np.abs(x) > 0.5 * np.abs(x).max())[0]  # In case resampled poorly
    if len(i) == 0:
        print("Failed to find the spike in the input file.")
        print(
            "Plotting the input and output; there should be spikes at around the "
            "marked locations."
        )
        expected_spikes = 12_000, 36_000  # For v1 specifically
        fig, axs = plt.subplots(2, 1)
        for ax, curve in zip(axs, (x,y)):
            ax.plot(curve)
            [ax.axvline(x=es,color="C1",linestyle="--") for es in expected_spikes]
        plt.savefig(f'exports/{title}_delay.png')
        plt.show()
        if _nofail:
            raise RuntimeError("Failed to plot delay")
    else:
        i = i[0]
        di = 20
        plt.figure()
        # plt.plot(x[i - di : i + di], ".-", label="Input")
        plt.plot(
            np.arange(-di, di),
            y[i - di + delay : i + di + delay],
            ".-",
            label="Output",
        )
        plt.axvline(x=0, linestyle="--", color="C1")
        plt.legend()
        
        # Save plot to file
        plt.savefig(f'exports/{title}_delay.png')
         
         # Show plot on screen (optional)
         #plt.show() 

with open('list.csv', newline='') as list_file:
    reader = csv.reader(list_file)
    with open('delay.csv', 'w', newline='') as delay_file:
       writer = csv.writer(delay_file)
       for row in reader:
           title=row[0]
           input_path=f'materials/{title}_In.wav'
           output_path=f'materials/{title}_Out.wav'
           delay=_calibrate_delay_v1(input_path,output_path)
           writer.writerow([title,delay])
           
           # Plot and save figure
           _plot_delay_v1(delay,input_path,output_path,title)

#########
#########create data jsons#########
#########
import csv
import json
import os
import sys
print("Creating configuration files for each audio file pair.")
TEMPLATE = {
    "train": {
        "start": None,
        "stop": -432000,
        "ny": 8192
    },
    "validation": {
        "start": -432000,
        "stop": None,
        "ny": None
    },
    "common": {
        "x_path": "materials/*_In.wav",
        "y_path": "materials/*_Out.wav",
        "delay": 0
    }
}

def generate_json_file(path, entry, delay):
    # Make substitutions in template
    template = dict(TEMPLATE)
    template["common"]["x_path"] = template["common"]["x_path"].replace("*", entry)
    template["common"]["y_path"] = template["common"]["y_path"].replace("*", entry)
    template["common"]["delay"] = delay
    
    # Generate JSON file
    filename = f"{entry}.json"
    with open(os.path.join(path, filename), "w") as f:
        json.dump(template, f, indent=4)
    
    print(f"Generated {filename}")

if __name__ == "__main__":
    csv_file = "list.csv"
    delay_file = "delay.csv"
    
    with open(delay_file, 'r') as f:
        delay_reader = csv.reader(f)
        delay_dict = dict(delay_reader)
    
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            entry = row[0]
            delay = float(delay_dict[entry])  # convert to float
            generate_json_file("data/", entry, delay)

#########
#########create model directories#########
#########
import os
import csv

print("Creating an output directory for the results of each model to reside in.")

if __name__ == "__main__":
    # Set the path of the input CSV file
    csv_path = "list.csv"

    # Set the path of the output directory
    output_path = "models"

    # Create the output directory if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Read the input CSV file
    with open(csv_path, "r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            # Get the name of the entry
            entry_name = row[0]

            # Create the directory for the entry
            entry_path = os.path.join(output_path, entry_name)
            os.makedirs(entry_path)

            # Print the path of the created directory and subdirectory
            print(f"Created directory: {entry_path}")