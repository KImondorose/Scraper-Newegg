from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


def scrape_multiple_pages_newegg_gpus(max_pages=3):
    """
    Scrapes multiple pages of GPU listings from Newegg.com.

    Args:
        max_pages (int): Number of pages to scrape.

    Returns:
        tuple: A list of dictionaries containing GPU data and 
               the total number of skipped items.
    """
    # Set Chrome options (maximized browser window)
    options = Options()
    options.add_argument("--start-maximized")

    # Automatically install and launch ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_gpu_data = [] # Store all scraped GPU items
    total_skipped = 0 # Counter for skipped items


    # Loop through each page
    for page in range(1, max_pages + 1):
        url = f"https://www.newegg.com/p/pl?d=graphics+card&page={page}"
        print(f"Scraping page {page}: {url}")
        driver.get(url) # Load page in the browser

        try:
            # Wait until product cards are present on the page
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "item-cell"))
            )
        except:
            # If items do not load in time, skip the page
            print(f"Timeout loading page {page}")
            continue

        # Find all product blocks on the page
        gpu_cards = driver.find_elements(By.CLASS_NAME, "item-cell")
        print(f"Found {len(gpu_cards)} item blocks on page {page}")

        # Loop through each GPU card and extract data
        for idx, card in enumerate(gpu_cards, start=1):
            try:
                # Get product title and link
                title_elem = card.find_element(By.CLASS_NAME, "item-title")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href")

                # Try to get the price (N/A if not found)
                try:
                    price_elem = card.find_element(By.CLASS_NAME, "price-current")
                    price = price_elem.text.strip()
                except:
                    price = "N/A"

                # Try to get the shipping info (N/A if not found)
                try:
                    shipping_elem = card.find_element(By.CLASS_NAME, "price-ship")
                    shipping = shipping_elem.text.strip()
                except:
                    shipping = "N/A"

                # Store data in a dictionary
                gpu_info = {
                    'Title': title,
                    'Price': price,
                    'Shipping': shipping,
                    'Link': link
                }
                all_gpu_data.append(gpu_info) # Add to list

            except Exception as e:
                # If anything fails, skip this item
                total_skipped += 1
                print(f"Skipped item {idx} on page {page}: {e}")
                continue

    driver.quit() # Close the browser
    return all_gpu_data, total_skipped # Return data and skipped count



def save_to_excel(gpu_list, filename="newegg_gpus.xlsx"):
    """
    Saves the list of GPU dictionaries to an Excel file.

    Args:
        gpu_list (list): List of GPU dictionaries.
        filename (str): Name of the output Excel file.
    """
    df = pd.DataFrame(gpu_list) # Convert list to dataframe
    df.to_excel(filename, index=False) # Save to Excel
    print(f"Saved {len(gpu_list)} items to {filename}")


# Entry point
if __name__ == "__main__":
    # Start scraping
    gpus, skipped = scrape_multiple_pages_newegg_gpus(max_pages=3)

    if not gpus:
        print("No GPUs found.")
    else:
        save_to_excel(gpus) # Save the results
        print(f"Saved {len(gpus)} items.")
    
    # Show skipped item count
    print(f"Skipped {skipped} items due to missing or malformed data.")