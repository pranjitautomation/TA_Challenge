# Task Details: 
    https://thoughtfulautomation.notion.site/RPA-Challenge-Fresh-news-2-0-37e2db5f88cb48d5ab1c972973226eb4

# News Fetching Bot


# Overview
    The News Fetching Bot is designed to accept work items that specify a search phrase, news section, and a number of months. It fetches news articles based on the provided criteria.


# Usage
    To utilize this bot effectively, you can input work items in the following format:

{
    "phrase": "Your_Search_Phrase",
    "section": "Desired_Section",
    "months": "Time_Period"
}


# Example Work Item:

{
    "phrase": "machines",
    "section": ["opinion", "industry"],
    "months": "3"
}


# Outputs
    The bot generates two essential outputs:

    Excel File: An Excel file containing detailed information about the fetched news articles.

    Zip Folder: A compressed folder containing all the images associated with the retrieved news articles.
