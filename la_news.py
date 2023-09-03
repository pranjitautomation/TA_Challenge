import os
import re
import string
import shutil
from datetime import datetime, timedelta

from dateutil import parser
from retry import retry
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from SeleniumLibrary.errors import ElementNotFound
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        StaleElementReferenceException,
                                        WebDriverException)

from src.common import logfile, make_excel
from src.config import LATimesConfig


class LATimes():
    def __init__(self, work_items) -> None:
        self.browser = Selenium()
        self.http = HTTP()

        self.phrase = work_items["phrase"]
        self.topic = work_items["section"]
        self.month_no = work_items["months"]

        self.excel_file = LATimesConfig.excel_file
        self.image_folder = LATimesConfig.image_folder
        self.logging = logfile()

    def make_dir(self) -> None:
        "Creates a directory if not present."
        os.makedirs(self.image_folder, exist_ok=True)

    def open_browser(self) -> None:
        """Opens the browser.
        """
        self.logging.info('Initialization of the process.')
        self.browser.open_available_browser('https://www.latimes.com')
        self.browser.maximize_browser_window()
        self.browser.wait_until_element_is_visible('//button[@data-element="search-button"]')
        self.browser.click_element('//button[@data-element="search-button"]')

    def phrase_search(self) -> None:
        """Searches for the phrase for getting news.
        """
        self.logging.info('Searching the Phrase.')
        self.browser.input_text_when_element_is_visible('//input[@data-element="search-form-input"]', self.phrase)
        self.browser.click_element_when_visible('//button[@data-element="search-submit-button"]')
    
    def is_search_provided(self) -> bool:
        """Checks whether search phrase is provided or not.
        Returns:
            bool: Returns true if search phrase is properly provided; otherwise, returns false
        """
        self.logging.info('Checking whether the search phrase is provided or not.')
        search_provided = True

        if type(self.topic) == list:
            if len(self.topic) == 0:
                search_provided = False
            else:
                for x in self.topic:
                    if len(x.strip()) == 0:
                        self.topic.remove(x)
                        if len(self.topic) == 0:
                            search_provided = False

        if type(self.topic) == str:
            if ',' in self.topic:
                self.topic = self.topic.split(',')
                if len(self.topic) == 0:
                    search_provided = False
                else:
                    for x in self.topic:
                        if len(x.strip()) == 0:
                            self.topic.remove(x)
                            if len(self.topic) == 0:
                                search_provided = False
        
        if not search_provided:
            self.logging.info('Search phrase is not properly provided.')
                   
        return search_provided    
         
    def sort_by(self) -> None:
        """Sort the news by the latest date.
        """
        self.logging.info('Sorting the news by newest.')
        self.browser.wait_until_element_is_visible('//select[@class="select-input"]',15)
        self.browser.click_element('//select[@class="select-input"]')
        self.browser.select_from_list_by_label('//select[@class="select-input"]', 'Newest')

    def select_topics(self, topic: list) -> None:
        """Selects the provided topics from the list of topics.
        Args:
           topic : List of the required topics.
        """
        self.logging.info('Beginning the process of selecting topics.')

        topic_click = True
        for top in topic:
            top = top.strip().title()
            try:
                self.browser.wait_until_element_is_visible('//p[text()="Topics"]', 60)
                try:
                    self.browser.wait_until_element_is_enabled(f'//span[text()="{top}"]', 10)
                except AssertionError:
                    pass
                
                if self.browser.is_element_enabled(f'//span[text()="{top}"]'):
                    self.browser.scroll_element_into_view(f'//span[text()="{top}"]')
                    self.browser.click_element(f'//span[text()="{top}"]//preceding-sibling::input')
                    
                    try:
                        self.browser.wait_until_element_is_visible('//div[@class="search-results-module-no-results"]', 3)
                    except AssertionError:
                        pass
                
                else:
                    topic_click = False
                    self.logging.info(f'{top} topic may not be present in the list of topics or may not be properly enabled at this moment.')
                    
            except (AssertionError, StaleElementReferenceException, ElementNotInteractableException):
                self.logging.info(f'{top} topic is not properly clicked.')
                topic_click = False

        if topic_click:
            self.logging.info('Topics are properly clicked.')

    def get_starting_date(self) -> datetime:
        """Finds the starting date from which news should be fetched.
        Returns:
            datetime: Returns the starting date.
        """

        today = datetime.today()
        if int(self.month_no) == 1 or int(self.month_no) == 0:
            target_date = today.replace(day=1) - timedelta(days=1)
        
        elif int(self.month_no) > 1:
            target_date = today.replace(day=1)

            years_to_subtract = self.month_no // 12
            months_to_subtract = self.month_no % 12

            new_year = target_date.year - years_to_subtract
            new_month = target_date.month - months_to_subtract+1

            if new_month <= 0:
                new_year -= 1
                new_month += 12

            target_date = datetime(new_year, new_month, target_date.day)
            
        target_date = target_date.replace(day=1)
        target_date = datetime.combine(target_date, datetime.min.time())
        self.logging.info(f'Fetching news articles from the date {target_date}.')
        return target_date
    
    def convert_to_datetime(self, date_str: str) -> datetime:
        """Converts any date string to datetime format.
        Args:
           date_str : The date string which needs to be converted in datetime format.
        Returns:
            datetime: Returns the date in datetime format.
        """
        if ('h ago' in date_str.lower()
                or 'minutes ago' in date_str.lower()
                or 'm ago' in date_str.lower()
                or 'hour ago' in date_str.lower()
                or 'hours ago' in date_str.lower()):
                
            dt = datetime.today()
            return dt

        else:
            try:
                dt = parser.parse(date_str)
                return dt
            except ValueError:
                raise ValueError("Unrecognized date format")

    def load_news(self) -> None:
        """Checks whether the news are properly loaded or not.
        """
        loaded = False
        try:
            self.browser.wait_until_element_is_visible('//div[@class="search-results-module-no-results"]', 5)
        except AssertionError:
            pass

        if self.browser.is_element_visible('//div[@class="search-results-module-no-results"]'):
            self.logging.info('There is no result for the search phrase.')
        else:
            try:
                self.browser.wait_until_element_is_visible('//div[@class="search-results-module-count"]', 15)
                self.logging.info("News are properly loaded.")
                loaded = True
            except AssertionError:
                self.logging.info('News are not properly loaded')
        
        return loaded
    
    def get_text(self) -> None:
        """Fetches all the required texts from the news article.
        """
        
        self.logging.info("Initialization of the process of fetching text.")
        start_date = self.get_starting_date()
        date_list = []
        title_list = []
        description_list = []
        img_src_list = []
        count_phrase_list = []
        money_present_list = []

        while True:
            date_elements = self.browser.get_webelements('//p[@class="promo-timestamp"]')
            last_date_text = self.browser.get_text(date_elements[-1])
            last_on_date = self.convert_to_datetime(last_date_text)

            for i in range (1, len(date_elements)+1):
                date_text = self.browser.get_text(f'(//p[@class="promo-timestamp"]){[i]}')
                on_date = self.convert_to_datetime(date_text)

                if on_date >= start_date:
                    try:
                        title_text = self.browser.get_text(f'(//h3[@class="promo-title"]){[i]}')
                    except ElementNotFound:
                        title_text = ''
                    
                    try:
                        description_text = self.browser.get_text(f'(//p[@class="promo-description"]){[i]}')
                    except ElementNotFound:
                        description_text = ''
                    
                    try:
                        img_src = self.browser.get_element_attribute(f'(//img[@class="image"]){[i]}', 'src')
                    except ElementNotFound:
                        img_src = ''
                    
                    count_in_title = self.count_phrase(title_text)
                    count_in_des = self.count_phrase(description_text)
                    count_ele = f'Title:{count_in_title}; Description{count_in_des}'

                    money_in_title = self.match_money(title_text)
                    money_in_des = self.match_money(description_text)
                    
                    if money_in_title or money_in_des:
                        money_present = True
                    else:
                        money_present = False
                    
                    if len(img_src)>0:   
                        ele_no = len(date_list) + 1
                        image_filename = f'image {ele_no}.png'
                        image_filepath = os.path.join(self.image_folder, image_filename)
                        self.download_image(img_src, image_filepath)
                    else:
                        image_filename = ''

                    date_list.append(date_text)
                    title_list.append(title_text)
                    description_list.append(description_text)
                    img_src_list.append(image_filename)
                    count_phrase_list.append(count_ele)
                    money_present_list.append(money_present)
                        
            if last_on_date >= start_date:
                try:
                    self.next_page()
                except (AssertionError, ElementClickInterceptedException):
                    self.logging.info('The process of news fetching is completed.')
                    break

            else:
                break
        shutil.make_archive(self.image_folder, 'zip', self.image_folder)
        shutil.rmtree(self.image_folder)

        excel_data = {
            'Title' : title_list,
            'Date' : date_list,
            'Description' : description_list,
            'Image Filename' : img_src_list,
            'Count of Phrases': count_phrase_list,
            'Money Present': money_present_list
        }    
        self.logging.info('Initializing the Excel creation process.')
        make_excel(excel_data)
        self.logging.info('Excel creation is completed.')
        
        self.logging.info('Full process is completed.')
        
    @retry((AssertionError, ElementClickInterceptedException, WebDriverException), 2, 3)
    def next_page(self) -> None:
        """Clicks for the next page.
        """
        self.browser.scroll_element_into_view('//div[@class="search-results-module-next-page"]')  
        page = self.browser.get_text('//div[@class="search-results-module-page-counts"]')
        page_list = page.split('of')
        page_no = int(page_list[0].strip().replace(',', ''))
        new_page = f'{page_no+1} of{page_list[-1]} '
        
        self.browser.click_element('//div[@class="search-results-module-next-page"]')
        self.browser.wait_until_element_is_enabled(f'//div[text()="{new_page}"]', 10)

    def match_money(self, text: str) -> bool:
        """Checks if there is any money amount present in the input string.
        Args:
           text : The text in which the presence of a money string needs to be checked.
        Returns:
            bool: Returns true if money is present; otherwise, returns false.
        """
        match_exp = r'(?:\$\d+(?:,\d{3})*(?:\.\d+)?)|(?:\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:dollars|USD)\b'
        money_present = re.findall(match_exp, text)
        
        if len(money_present)>0:
            return True
        else:
            return False
        
    def count_phrase(self, input_str: str) -> int:
        """Counts the number of times the search phrase appears in the input string.
        Args:
           input_str : The string from which the search phrase needs to be counted.
        Returns:
            int: Returns the count of search phrase in the input string.
        """
        translator = str.maketrans('', '', string.punctuation)
        clean_phrase = input_str.translate(translator).lower()
        no_of_phrase = clean_phrase.count(self.phrase.lower())
        
        return no_of_phrase

    def download_image(self, image_src: str, filename: str) -> None:
        """Downloads the image from the given url.
        Args:
           image_src : Url of the image.
           filename : Name of the file where the image has been saved.
        """
        self.http.download(image_src, filename)
    