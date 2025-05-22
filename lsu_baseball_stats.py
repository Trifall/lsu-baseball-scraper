# LSU Baseball Stats Scraper
# By Jerren Trifan - https://github.com/Trifall

import json
import logging
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("lsu_baseball_stats.log"), logging.StreamHandler()],
)

# base URL for LSU Baseball Stats
BASE_URL = "https://lsusports.net/bbstats/"

# headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


# fetch the content of a URL and return the BeautifulSoup object
def get_page_content(url):
    try:
        logging.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        # logging.error(f"Error fetching URL {url}: {e}")
        return None


# generate season links based on known URL patterns
def get_season_links():

    season_links = {}
    current_year = datetime.now().year

    # generate URLs for seasons from current year down to 1997
    # format: https://static.lsusports.net/assets/docs/bb/YYstats/teamstat.htm
    for year in range(current_year, 1996, -1):
        short_year = str(year)[-2:]  # get last two digits (e.g., 2025 -> 25)
        url = f"https://static.lsusports.net/assets/docs/bb/{short_year}stats/teamstat.htm"
        season_links[str(year)] = url
        # logging.info(f"Generated season link for {year}: {url}")

    # prior to 1997, the data is in PDF format and not directly parsable

    # generate URLs for seasons from 1996 down to 1949 (or earlier if needed)
    # format: https://static.lsusports.net/assets/docs/bb/pdf/YYstats.pdf
    for year in range(
        1996, 1948, -1
    ):  # last data point is 1949 (inclusive), so 1948 is end of range
        short_year = str(year)[-2:]  # get last two digits (e.g., 1996 -> 96)
        url = f"https://static.lsusports.net/assets/docs/bb/pdf/{short_year}stats.pdf"
        # only add if not already in the dictionary
        if str(year) not in season_links:
            season_links[str(year)] = url
            # logging.info(f"Generated season link for {year}: {url}")

    return season_links


# extract all box score links from a season page
def get_box_score_links(soup, season, url):
    box_score_links = []

    # For PDF seasons (1996 and earlier), just add a single entry with the PDF URL
    if int(season) <= 1996:
        box_score_links.append(
            {
                "date": f"Jan 1, {season}",
                "location": "Baton Rouge, LA",
                "result": "N/A",
                "url": url,
                "format": "PDF",
            }
        )
        logging.info(f"Added PDF link for season {season}: {url}")
        return box_score_links

    # for HTML seasons (1997 and later)
    # find the first table on the page
    table = soup.find("table")
    if not table:
        logging.warning(f"No table found on season page for {season}")
        return box_score_links

    # find all rows in the table body
    rows = table.find_all("tr")

    for row in rows:
        # look for the 'Box score' link in the row
        box_score_link = row.find("a", string="Box score")
        if box_score_link:
            href = box_score_link.get("href")
            if href:
                # get the date, location, and result from the row
                cells = row.find_all("td")
                date = cells[0].text.strip() if len(cells) > 0 else "Unknown Date"
                location = (
                    cells[1].text.strip() if len(cells) > 1 else "Unknown Location"
                )
                result = cells[2].text.strip() if len(cells) > 2 else "Unknown Result"

                # extract the year from the season (last 2 digits)
                year_short = str(season)[-2:]

                # extract the filename from the href
                filename = href.split("/")[-1] if "/" in href else href

                # construct the correct URL format
                full_url = f"https://static.lsusports.net/assets/docs/bb/{year_short}stats/{filename}"

                box_score_links.append(
                    {
                        "date": date,
                        "location": location,
                        "result": result,
                        "url": full_url,
                        "format": "HTML",
                    }
                )

                # logging.info(f"Found box score link: {full_url}")

    return box_score_links


def fetch_lsu_bball_stats():
    # get all season links directly using the URL patterns
    season_links = get_season_links()
    if not season_links:
        logging.error("No season links generated")
        return None

    logging.info(f"Generated {len(season_links)} season links")

    # dictionary to store all box score links by season
    all_box_scores = {}

    # navigate to each season page and extract box score links
    for season, season_url in season_links.items():
        logging.info(f"Processing season: {season}")

        # add a delay to avoid being rate limited
        time.sleep(1)

        # get the season page content
        try:
            season_soup = get_page_content(season_url)
            if not season_soup:
                logging.warning(
                    f"Failed to fetch season page for {season}, URL: {season_url}"
                )
                # for 404 cases, add an empty array with a warning
                all_box_scores[season] = []
                logging.warning(f"No data available for season {season}")
                continue

            # get all box score links for this season
            box_score_links = get_box_score_links(season_soup, season, season_url)

            # store the box score links for this season
            all_box_scores[season] = box_score_links

            logging.info(
                f"Found {len(box_score_links)} box score links for season {season}"
            )
        except Exception as e:
            logging.error(f"Error processing season {season}: {e}")
            # add an empty array for this season
            all_box_scores[season] = []
            continue

    # save the results to a JSON file
    with open("lsu_baseball_box_scores.json", "w") as f:
        json.dump(all_box_scores, f, indent=2)

    logging.info(f"Saved box score links to lsu_baseball_box_scores.json")

    # !! all_box_scores is a dictionary where the key is the season and the value is a list of box score links
    # you can now do whatever scraping / parsing of the box score data you want here

    return all_box_scores


def main():
    logging.info("Starting LSU Baseball stats scraper")
    logging.info(f"Starting URL: {BASE_URL}")

    box_scores = fetch_lsu_bball_stats()

    if box_scores:
        total_links = sum(len(links) for links in box_scores.values())
        logging.info(
            f"Scraping completed. Found {len(box_scores)} seasons with {total_links} total box score links."
        )

        # identify PDF years
        pdf_years = []
        for year, links in box_scores.items():
            if links and any(link.get("format") == "PDF" for link in links):
                pdf_years.append(year)

        # identify years with no data
        no_data_years = [year for year, links in box_scores.items() if not links]

        # log warnings for PDF years
        if pdf_years:
            pdf_years.sort()
            pdf_years_str = ", ".join(pdf_years)
            logging.warning(
                f"Warning: the following years have PDF links, which are not directly parsable: {pdf_years_str}"
            )

        # log warnings for years with no data
        if no_data_years:
            no_data_years.sort()
            no_data_years_str = ", ".join(no_data_years)
            logging.warning(
                f"Warning: the following years have no data found: {no_data_years_str}"
            )
    else:
        logging.error("Scraping failed.")


if __name__ == "__main__":
    main()
