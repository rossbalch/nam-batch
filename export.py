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
        export_dir = os.path.join('exports', t)

        # construct arguments
        e = os.path.join(time_code_dir, time_code, 'lightning_logs', 'version_0', 'checkpoints')
        checkpoint_file = f'checkpoint_epoch_epoch={max_epochs_str}.ckpt'
        c = os.path.join(e, checkpoint_file)
        args = ['config_model.json', c, e]

        # run generate/main.py
        subprocess.run(['python', 'generate/main.py'] + args, shell=True)

        # move model.nam file to exports/
        src_file = os.path.join(e, 'model.nam')
        dst_file = os.path.join(export_dir, 'model.nam')
        os.makedirs(export_dir, exist_ok=True)
        shutil.move(src_file, dst_file)

        # move comparison.png and ESR.png to exports/
        src_dir = os.path.join(time_code_dir, time_code)
        dst_dir = os.path.join(export_dir, time_code)
        os.makedirs(dst_dir, exist_ok=True)
        for file_name in ['comparison.png', 'ESR.png']:
            src_file = os.path.join(src_dir, file_name)
            dst_file = os.path.join(dst_dir, f'{t}_{file_name}')
            shutil.move(src_file, dst_file)
print("NAM, and Validation files generated and available in exports folder.")