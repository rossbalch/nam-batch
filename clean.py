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
