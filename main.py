import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import time


def accept_cookies(driver_cookies):
    try:
        # Wait for the cookie consent button to appear and click it
        cookie_button = WebDriverWait(driver_cookies, 10).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "c24-cookie-consent-functional"))
        )
        cookie_button.click()
        print("Accepted cookies")
    except Exception as e:
        print("Cookie consent button not found or already accepted")


# WebDriver for Chrome setup
driver = webdriver.Chrome()

# Base URL of the page you want to scrape (with a placeholder for the page number)
base_url = "https://urlaub.check24.de/suche/hotel?adult=2&airport=VIE&areaId=1079&areaSort=topregion&cateringList=allinclusive%2CallinclusivePlus&days=1w&departureDate=2024-12-01&directFlight=1&ds=r&extendedSearch=1&hotelCategoryList=4%2C5&offerSort=default&page={}&pageArea=package&rating=8&returnDate=2025-01-31&roomAllocation=A-A&roomCount=1&sorting=price&transfer=transfer&transportType=flight"

all_hotel_data = []

# Initialize the page number
current_page = 1

# Start scraping
while True:
    print(f"Scraping page {current_page}...")
    url = base_url.format(current_page)  # Update the URL with the current page number
    driver.get(url)

    time.sleep(3)  # Wait for the page to load

    # Accept cookies if necessary
    accept_cookies(driver)

    # Wait until at least one hotel element is present in the DOM
    try:
        WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.ID, 'legend-box'))
        )

        # Scroll to the bottom of the page to load all content
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollBy(0, 2000);")  # Scroll down by 2000 pixels
            time.sleep(0.5)  # Wait for content to load

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # Check if we have reached the bottom of the page
                break
            last_height = new_height

        # Get the HTML content of the page
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Max page index
        pagination_div = soup.find("div", class_='_Pagination_177if_88')
        if pagination_div:
            total_results_text = pagination_div.find("div").text.strip()
            total_results = int(total_results_text.split("insgesamt ")[1])
            maxIndex = math.ceil(total_results / 25)  # Calculate maxIndex based on total results
            print(f"Total results: {total_results}, Max pages: {maxIndex}")
        else:
            print("Pagination div not found.")
            break  # Exit if no pagination found

        # Find all hotel listings on the current page
        all_hotels = soup.find_all("div", class_='_Item_6cmnh_113')
        print(f"Found {len(all_hotels)} hotels on page {current_page}")

        for hotel in all_hotels:
            # Extract hotel information
            name_tag = hotel.find("a", class_='_Title_1kztl_88 _Title_13ut3_111')
            name = name_tag.text.strip() if name_tag else 'N/A'
            href = name_tag['href'] if name_tag else 'N/A'
            rating_tag = hotel.find("div", class_='_Value_apzia_99 _RatingValue_13ut3_135')
            rating = rating_tag.text.strip() if rating_tag else 'N/A'
            rating_count_tag = hotel.find("span", class_='_Count_apzia_144')
            rating_count = rating_count_tag.text.strip() if rating_count_tag else 'N/A'
            price_tag = hotel.find('span', class_='_Price_15k1c_88 _TotalPrice_1m5yd_133')
            price = price_tag.text.strip() if price_tag else 'N/A'
            discount_tag = hotel.find('div', class_='_Discount_1m5yd_146')
            discount = discount_tag.text.strip() if discount_tag else 'No discount'
            location_tag = hotel.find("div", class_='_Location_14isu_89')
            location = location_tag.text.strip() if location_tag else 'N/A'
            image_tag = hotel.find("div", class_='swiper-slide swiper-slide-visible swiper-slide-fully-visible swiper-slide-active _Slide_1n1xx_88 _Slide_1jbnc_100')
            img_url = 'No image found'
            if image_tag:
                image = image_tag.find('img')
                img_url = image['src'] if image else 'No image found'

            # Collect the extracted information into a dictionary
            hotel_data = {
                'Name': name,
                'Rating': rating,
                'Rating Count': rating_count,
                'Price': price,
                'Discount': discount,
                'Location': location,
                'Image': img_url,
                'Link': href,
            }
            all_hotel_data.append(hotel_data)

            # Optionally, print the extracted information
            print(f'Name: {name}')
            print(f'Rating: {rating}')
            print(f'Rating count: {rating_count}')
            print(f'Price: {price}')
            print(f'Discount: {discount}')
            print(f'Location: {location}')
            print(f'Image: {img_url}')
            print(f'Link: {href}')
            print('---')

        # Break the loop if the current page exceeds maxIndex
        if current_page >= maxIndex:
            break

        # Increment the page number
        current_page += 1

    except Exception as e:
        print(f"Error occurred while scraping page {current_page}: {e}")
        break  # Exit loop on error

# Close the WebDriver
driver.quit()

# Optionally, you can save the collected data to a file or process it further
