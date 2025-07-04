import random, time, itertools, io, requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# ---------- CONFIG ---------- #
MAX_PAGES       = 20  # Number of pages to scrape from Newegg
EMBED_IMAGES    = False           # True will Save image also. False is saving the URLs only
HEADLESS        = True     # Run Chrome in headless mode (no GUI)
MIN_DELAY, MAX_DELAY = 2, 5   # Random delay range between page requests (seconds)
PROXY_FILE      = "proxies.txt"  # File containing list of proxies to rotate through
EXCEL_FILE      = "newegg_gpus.xlsx"   # Output Excel file name
# ----------------------------- #

# Create an infinite cycle of proxies (or [None] if no proxy file exists)
proxy_pool = itertools.cycle(
    [None] if not Path(PROXY_FILE).exists() else
    [p.strip() for p in open(PROXY_FILE) if p.strip()]
)

def build_options(proxy=None) -> Options:
    """
    Configure and return Selenium Chrome options.

    Args:
        proxy (str or None): Optional proxy string to route browser traffic.

    Returns:
        Options: Configured Chrome Options object.
    """
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")  # Use headless mode if configured
    opts.add_argument("--disable-blink-features=AutomationControlled")  # Mask automation fingerprint
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/126.0.0.0 Safari/537.36")  # Realistic browser user-agent
    if proxy:
        opts.add_argument(f"--proxy-server=http://{proxy}")  # Set proxy if provided
    return opts

def scrape_newegg_gpus(max_pages=MAX_PAGES):
    """
    Scrape GPU listings from Newegg.com across multiple pages.

    Args:
        max_pages (int): Number of pagination pages to scrape.

    Returns:
        list: A list of dictionaries with GPU data.
    """
    all_gpu_data, total_skipped = [], 0 # Store all GPU data and skipped item count

    # Loop over the desired number of pages
    for page in range(1, max_pages + 1):
        proxy = next(proxy_pool) # Get the next proxy in the pool
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=build_options(proxy),
        )
        try:
            url = f"https://www.newegg.com/p/pl?d=graphics+card&page={page}"
            driver.get(url)
            # Wait for product cards to be present
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "item-cell"))
            )
            cards = driver.find_elements(By.CLASS_NAME, "item-cell") # Find all product blocks
            for card in cards:
                try:
                    # Extract product title and link
                    title_elem   = card.find_element(By.CLASS_NAME, "item-title")
                    img_elem     = card.find_element(By.CSS_SELECTOR, ".item-img img")

                    # Extract product image URL (some thumbnails are lazy‑loaded in data-src)
                    img_url = (img_elem.get_attribute("src")
                               or img_elem.get_attribute("data-src") or "").strip()

                    # Extract price and shipping info if available
                    price_elem   = card.find_elements(By.CLASS_NAME, "price-current")
                    ship_elem    = card.find_elements(By.CLASS_NAME, "price-ship")

                    # Append product details to the list
                    all_gpu_data.append({
                        "Title"   : title_elem.text.strip(),
                        "Price"   : price_elem[0].text.strip() if price_elem else "N/A",
                        "Shipping": ship_elem[0].text.strip() if ship_elem else "N/A",
                        "Link"    : title_elem.get_attribute("href"),
                        "Image_URL": img_url,
                    })
                except Exception:
                    total_skipped += 1 # Always close the browser session
                    continue
        finally:
            driver.quit()
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY)) # Sleep to avoid rate limit

    print(f"Skipped {total_skipped} items.")
    return all_gpu_data

def save_to_excel(data, fname=EXCEL_FILE, embed_images=EMBED_IMAGES):
    """
    Save GPU data to an Excel file. Optionally embed image thumbnails.

    Args:
        data (list): List of GPU data dictionaries.
        fname (str): Output Excel file name.
        embed_images (bool): If True, embed thumbnail images; else just add URL.
    """
    if not embed_images:
        # Simple URL‑only version
        pd.DataFrame(data).to_excel(fname, index=False)
        print(f"Saved {len(data)} rows → {fname}")
        return

    # ----- embed thumbnails with XlsxWriter ----- #
    import xlsxwriter

    wb = xlsxwriter.Workbook(fname)
    ws = wb.add_worksheet("GPUs")

    headers = ["Title", "Price", "Shipping", "Link", "Image"]
    # write headers
    for col, h in enumerate(headers):
        ws.write(0, col, h)

    row = 1
    for d in data:
        ws.write(row, 0, d["Title"])
        ws.write(row, 1, d["Price"])
        ws.write(row, 2, d["Shipping"])
        ws.write_url(row, 3, d["Link"], string="Product link")

        # download & insert image (resize to cell height)
        img_url = d["Image_URL"]
        if img_url:
            try:
                resp = requests.get(img_url, timeout=10)
                if resp.ok:
                    image_data = io.BytesIO(resp.content)
                    ws.insert_image(row, 4, img_url, {
                        "image_data": image_data,
                        "x_scale": 0.5, "y_scale": 0.5,  # tweak thumbnail size
                        "object_position": 1,  # move with cells
                    })
            except Exception:
                ws.write(row, 4, img_url)  # fallback: just write URL
        else:
            ws.write(row, 4, "N/A")
        row += 1

    wb.close()
    print(f"Saved {len(data)} rows with thumbnails → {fname}")

if __name__ == "__main__":
    # Main Execution Block
    gpus = scrape_newegg_gpus() # Scrape GPU date
    save_to_excel(gpus) # Save results to Excel 
