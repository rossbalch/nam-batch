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