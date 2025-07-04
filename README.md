# Newegg Graphics Card Scraper (Selenium + Excel)

Collects GPU listings (title, price, shipping, product link, thumbnail) from **Newegg.com**, works around anti-bot measures, and saves the data to **`newegg_gpus.xlsx`**—optionally embedding the product thumbnails directly in the workbook.

---

## Key Features

| Category        | What it does                                                                                      |
|-----------------|-------------------------------------------------------------------------------------------------|
| **Anti-blocking** | • Rotates proxies per page<br>• Spoofs a modern Chrome user-agent<br>• Masks Selenium automation flag (`navigator.webdriver`)<br>• Launches a **fresh browser for every page** to reset cookies/TLS fingerprints<br>• Adds random delays between requests |
| **Data captured**  | Title · Price · Shipping · Product URL · **Thumbnail URL**                                      |
| **Excel export**   | Two modes:<br>**① URL-only** (lightweight)<br>**② Embedded thumbnails** via *xlsxwriter*      |
| **Self-contained** | Installs the right ChromeDriver on first run (`webdriver-manager`)                              |

---

## 🔧 How Anti-Blocking Works

| Tactic               | Code Location                         | Benefit                                                                                 |
|----------------------|-------------------------------------|-----------------------------------------------------------------------------------------|
| **Proxy rotation**   | `proxy_pool = itertools.cycle(...)` + `build_options(proxy)` | Each request shows up from a new IP, so rate limits reset.                              |
| **Realistic UA string** | `--user-agent="Mozilla/5.0 … Chrome/126"`               | Removes the default Selenium fingerprint.                                              |
| **Automation masking** | `--disable-blink-features=AutomationControlled`          | Hides `navigator.webdriver`.                                                           |
| **Headless-new mode** | `--headless=new`                                            | Modern headless Chrome renders like full Chrome (no “headless” tell-tales).            |
| **Fresh driver per page** | New `webdriver.Chrome()` inside `for page ...` loop      | Drops cookies + TLS fingerprint between pages.                                         |
| **Random sleep**     | `time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))`           | Mimics human pacing, avoids burst detection.                                           |

---

## How Images Are Stored

1. **Thumbnail URL** collected from either `src` or `data-src` attributes.  
2. URL saved in the `Image_URL` field for every product.  
3. **If `EMBED_IMAGES = False`**  
   *The Excel column simply contains the URL text.*  
4. **If `EMBED_IMAGES = True`**  
   *The script downloads each thumbnail and uses `xlsxwriter`*  
   ```python
   ws.insert_image(row, 4, img_url, {
       "image_data": io.BytesIO(resp.content),
       "x_scale": 0.5, "y_scale": 0.5
   })
- This embeds a 50%-scaled image directly in the cell; on errors it falls back to writing the URL.

## Quick Start
### 1. Install dependencies
pip install selenium webdriver-manager pandas requests xlsxwriter

### 2. (Optional) create proxies.txt
####    One proxy per line:   user:pass@host:port   or   host:port
echo 123.45.67.89:8080 > proxies.txt

### 3. Run the scraper
python newegg_gpu_scraper.py

### Configuration Flags
- MAX_PAGES: How many pages to scrape
- EMBED_IMAGES: True → thumbnails in Excel, False → URL only.
- HEADLESS:	True - Run Chrome without a GUI.
- MIN_DELAY, MAX_DELAY- Random sleep range (seconds) between page fetches.
- PROXY_FILE: "proxies.txt"- File path containing proxy list.
- EXCEL_FILE: "newegg_gpus.xlsx"- Output workbook name.


## Author
Made with ❤️ by **Rose Kimondo**