#########
#########create nam and validation files and move them to exports #########
#########

import csv
import os
import json
import subprocess
import shutil

# read config_learning.json to get max_epochs
with open('config_learning.json') as f:
    config_learning = json.load(f)
max_epochs = config_learning['trainer']['max_epochs'] - 1
max_epochs_str = f'{max_epochs:04d}'

# read list.csv and process each item
with open('list.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        t = row[0]

        # get time code
        time_code_dir = os.path.join('models', t)
        time_code = sorted(os.listdir(time_code_dir))[-1]

        # construct arguments
        e = os.path.join(time_code_dir, time_code, 'lightning_logs', 'version_0', 'checkpoints')
        checkpoint_file = f'checkpoint_epoch_epoch={max_epochs_str}.ckpt'
        c = os.path.join(e, checkpoint_file)
        args = ['config_model.json', c, e]

        # run generate/main.py
        subprocess.run(['python', 'bin/export/main.py'] + args, shell=True)

        # move model.nam file to exports/
        src_file = os.path.join(e, 'model.nam')
        dst_file = os.path.join('exports', f'{t}.nam')
        shutil.move(src_file, dst_file)

        # move comparison.png and ESR.png to exports/
        src_dir = os.path.join(time_code_dir, time_code)
        for file_name in ['comparison.png', 'ESR.png']:
            src_file = os.path.join(src_dir, file_name)
            dst_file = os.path.join('exports', f'{t}_{file_name}')
            shutil.move(src_file, dst_file)

print("NAM, and Validation files generated and available in exports folder.")

#########
#########cleanup unneccessary data#########
#########

import os
import shutil

print("Cleaning up the directory structure.")

folders = ["data", "models", "materials"]
for folder_name in folders:
    if os.path.exists(folder_name):
        if folder_name == "materials":
            for file_name in os.listdir(folder_name):
                file_path = os.path.join(folder_name, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            print(f"Deleted all files in '{folder_name}'")
        else:
            shutil.rmtree(folder_name)
            print(f"Deleted folder '{folder_name}'")
    else:
        print(f"Folder '{folder_name}' not found")

file_names = ["list.csv", "delay.csv"]
for file_name in file_names:
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"Deleted file '{file_name}'")
    else:
        print(f"File '{file_name}' not found")

#########
#########finishing message#########
#########

print("All done! Have fun with your new models! Please Share. Script by Cosmic Crucible Studio.")