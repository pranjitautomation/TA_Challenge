import os
from dataclasses import dataclass


@dataclass
class LATimesConfig:
    output_folder = os.path.join(os.getcwd(), 'output')
    excel_file = os.path.join(output_folder, 'news.xlsx')
    image_folder = os.path.join(output_folder, 'images')
    
    LOG_FILE=f"logfile.txt"
    logs_path=os.path.join(output_folder,LOG_FILE)
