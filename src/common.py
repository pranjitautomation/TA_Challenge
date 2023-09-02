import logging
import os

from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems

from src.config import LATimesConfig


def make_excel(data: dict) -> None:
    """Makes the excel file.
    Args:
        data : Data for excel file.
    """
    files = Files()
    excel_file = LATimesConfig.excel_file

    files.create_workbook()
    files.create_worksheet(name="Sheet1", content=data, header=True)
    files.remove_worksheet('Sheet')
    files.save_workbook(excel_file)
    
def logfile() -> None:
    """Creates the log file.
    """
    dir_path = LATimesConfig.image_folder
    os.makedirs(dir_path, exist_ok=True)

    logging.basicConfig(
    filename=LATimesConfig.logs_path,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
    )
    return logging

def filter_log() -> None:
    """Filters the log file and deletes the unnecessary auto generated logs produced by Robocorp.
    """
    file_path = LATimesConfig.logs_path
    texts_to_remove = ["WDM - INFO", "RobotFramework - INFO", "RPA.HTTP - INFO", 'Chrome', 'Firefox', 'ChromiumEdge']

    with open(file_path, 'r') as file:
        lines = [line for line in file if all(text not in line for text in texts_to_remove)]

    with open(file_path, 'w') as file:
        file.writelines(lines)
        
def get_workitems() -> dict:
    """
    Gets the inputs for the whole process.
    """
    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()
    
    return work_item