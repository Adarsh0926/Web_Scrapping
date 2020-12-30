#Project 2: Web Scrapper using BeautifulSoup and Requests
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas
import argparse
import connect

parser = argparse.ArgumentParser()
parser.add_argument("--page_num_max", help="Enter the number to pages to parse", type=int)
parser.add_argument("--dbname", help="Enter the umber of pages to parse", type=int)
args = parser.parse_args()

oyo_url = "https://www.oyorooms.com/hotels-in-dehradun//?page="
page_num_MAX = args.page_num_max
scraped_info_list = []
connect.connect(args.dbname)

for page_num in range(1, page_num_MAX):
    req = Request(oyo_url + str(page_num), headers={"User-Agent": "Mozilla/5.0"})

    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, "html.parser")

    all_hotels = soup.find_all("div", {"class": "hotelCardListing"})
    

    for hotel in all_hotels:
        hotel_dict = {}
        hotel_dict["Name"] = hotel.find("h3", {"class": "listingHotelDescription__hotelName"}).text
        hotel_dict["Address"] = hotel.find("span", {"itemprop": "streetAddress"}).text
        hotel_dict["Price"] = hotel.find("span", {"class": "listingPrice__finalPrice"}).text
        #try ... except
        try:
            hotel_dict["Rating"] = hotel.find("span", {"class": "hotelRating__ratingSummary"}).text
        except AttributeError:
            hotel_dict["Rating"] = None

        parent_amenities_element = hotel.find("div", {"class": "amenityWrapper"})

        amenities_list = []
        for amenity in parent_amenities_element.find_all("div", {"class": "amenityWrapper__amenity"}):
            amenities_list.append(amenity.find("span", {"class": "d-body-sm"}).text.strip())

            hotel_dict["Amenities"] = ', '.join(amenities_list[:-1])

            scraped_info_list.append(hotel_dict)
            connect.insert_into_table(args.dbname, tuple(hotel_dict.values()))
        
        #print(hotel_name, hotel_address, hotel_price, hotel_rating, amenities_list)

dataFrame = pandas.DataFrame(scraped_info_list)
print("Creating csv file...")
dataFrame.to_csv("Oyo.csv")
print("File Creation Successful")
connect.get_hotel_info(args.dbname)