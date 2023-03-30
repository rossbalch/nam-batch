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

#########
#########run the model training#########
#########
import csv
import os
import subprocess
import sys

print("Begin queue of training.")

if __name__ == "__main__":
    csv_file = 'list.csv'
    command_template = ["python", "main.py", "data/{}.json", "config_model.json", "config_learning.json", "models/{}/", "--no-show"]

    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            entry = row[0]
            print(f"Now training model {entry}")
            command = command_template[:]
            command[2] = command[2].format(entry)
            command[5] = command[5].format(entry)
            subprocess.run(command)
    
    print("Finished training all inputs")