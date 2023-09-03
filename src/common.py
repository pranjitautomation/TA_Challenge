import logging

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
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
        
def get_workitems() -> dict:
    """
    Gets the inputs for the whole process.
    """
    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()
    
    return work_item