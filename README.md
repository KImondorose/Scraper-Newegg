# Newegg GPU Scraper (Selenium + Excel)

This project is a Python-based web scraper that collects GPU product data from [Newegg.com](https://www.newegg.com) using **Selenium**. It extracts product title, price, shipping info, and product link across multiple pages, and saves them to a clean Excel file.

---

## Features

- Scrapes GPU listings from Newegg
- Supports scraping multiple result pages
- Saves data to `newegg_gpus.xlsx`
- Logs how many items were skipped due to missing info
- Uses Selenium to handle JavaScript-rendered content

---

## What It Extracts

Each product includes:

- **Title** (product name)
- **Price** (or `"N/A"` if missing)
- **Shipping cost** (or `"N/A"` if missing)
- **Product link**

---

## Setup Instructions

### 1. Clone this repository

`git clone https://github.com/your-username/newegg-gpu-scraper.git`
`cd newegg-gpu-scraper`

### 2. Install required packages
`pip install selenium pandas openpyxl webdriver-manager`
Alternatively, run, `pip install -r requirements.txt` after adding the `requirements.txt` file to your project folder.

## How to Use
Run the scraper:
`python newegg.py`

By default, it will:
- Scrape the **first 3 pages** of Newegg graphics cards listings
- Save the results to newegg_gpus.xlsx
- Print a summary to the terminal

## Output
You’ll find a file named:
`newegg_gpus.xlsx`

It will contain all scraped results in Excel format.

## Example Output
`Scraping page 1: https://www.newegg.com/p/pl?d=graphics+card&page=1`
`Found 44 item blocks on page 1`
`Saved 39 items to newegg_gpus.xlsx`
`Skipped 5 items due to missing or malformed data.`

## Customize Pages to Scrape
Inside `newegg.py`, you can modify this line to control how many pages to scrape:

`gpus, skipped = scrape_multiple_pages_newegg_gpus(max_pages=3)`

Change `max_pages=3` to however many pages you want to collect.

## Notes
- Close `newegg_gpus.xlsx` before running the script again or it may cause a permission error.

- Some products may be skipped if they don’t have title or link (e.g., ads, empty blocks).

- If Newegg changes its website layout or class names, the script will need to be updated.

## Author
Made with ❤️ by **Rose Kimondo**


