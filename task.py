from la_news import LATimes
from src.config import LATimesConfig
from src.common import get_workitems


def task() -> None:
    """Runs the whole news fetching process.
    """
    try:
        workitems = get_workitems()
        news_obj = LATimes(workitems)
        news_obj.make_dir()
        news_obj.open_browser()
        news_obj.phrase_search()
        news_obj.get_starting_date()

        news_obj.sort_by()
        if news_obj.is_search_provided():
            news_obj.select_topics(news_obj.topic)

        loaded = news_obj.load_news()
        if loaded:
            news_obj.get_text()

    except Exception as e:
        news_obj.browser.screenshot(filename=LATimesConfig.error_screenshot)
        raise e
    

if __name__ == '__main__':
    task()
