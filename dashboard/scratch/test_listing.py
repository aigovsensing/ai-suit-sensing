
import os
import sys

def list_data_files():
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found in {os.getcwd()}")
        return []
    files = sorted([f for f in os.listdir(data_dir) if f.endswith(".csv")], reverse=True)
    print(f"Found files: {files}")
    return files

list_data_files()
