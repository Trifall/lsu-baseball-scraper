# LSU Baseball Stats Scraper

A Python script that scrapes and collects LSU baseball statistics from the official LSU Sports website, providing historical data across multiple seasons.

## Features

- Scrapes LSU baseball statistics from 1949 to present
- Collects box score links for all available games
- Handles both HTML and PDF format statistics (PDFs are not directly parsable)
- Organizes data by season for easy analysis
- Logs to both console and file

## Note

This script runs sequentially, but it could be modified to run all of the scraping in parallel. I did not do this because I did not want to overload the LSU Sports website with too many requests and I don't know how many requests they allow or can handle.

## Requirements

- Python 3.6+
- Required packages (see `requirements.txt`)

## Quick Setup with uv

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. Here's how to set up this project with uv:

```bash
# Install uv if you don't have it yet
pip install uv

# Create and activate a virtual environment
uv venv .venv --python=3.12

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate # or .venv/bin/activate.fish
# On Windows:
# .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

## Standard Python Setup

If you prefer to use standard Python tools:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the script with:

```bash
python lsu_baseball_stats.py
```

The script will:

1. Generate links for all available LSU baseball seasons (1949-present)
2. Scrape box score links for each season
3. Save all collected data to `lsu_baseball_box_scores.json`
4. Log the process to both console and `lsu_baseball_stats.log`

## Output

The script generates a JSON file (`lsu_baseball_box_scores.json`) with the following structure:

```json
{
 "2025": [
  {
   "date": "Feb 14, 2025",
   "location": "Baton Rouge, LA",
   "result": "W, 11-3",
   "url": "https://static.lsusports.net/assets/docs/bb/25stats/021425.htm",
   "format": "HTML"
  }
  // More games...
 ]
 // More seasons...
}
```

If a season is not available, the script will log a warning and skip that season and leave an empty array for that season.

If a season has a PDF link, the script will log a warning and only have one entry in the array for that season with the PDF link (and "PDF" in the format field).

## Customization

You can modify the script to:

- Change the delay between requests by modifying the `time.sleep()` value
- Adjust the logging level in the `logging.basicConfig()` settings
- Extend the script to parse individual box scores for more detailed statistics
- Filter for specific seasons or games

## Notes

- Seasons prior to 1997 are available only in PDF format and are not directly parsable
- Some seasons may not have data available on the LSU Sports website (e.g. 1950-1953)

## License

MIT

## Author

Created by Jerren Trifan - <https://github.com/Trifall>
