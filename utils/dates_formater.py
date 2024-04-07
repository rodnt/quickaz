import os
import datetime
from utils.colors import color_good, color_bad
import sys

def create_directory_with_timestamp(base_dir_name):
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d_%H-%M")
    new_dir_name = f"{base_dir_name}_{date_time_str}"
    try:
        os.mkdir(new_dir_name)
        print(color_good(f">> New Directory {new_dir_name} created."))
    except Exception as e:
        print(color_bad(f"Failed to create {new_dir_name}. Error: {str(e)}"))
        sys.exit(1)