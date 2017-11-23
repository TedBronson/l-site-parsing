from bs4 import BeautifulSoup
import requests
import csv


# TODO: save data to a file with date
# TODO: compare prices of a same listing
# TODO: write all three prices for same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: pass currency in compose_request() to get proper currency result
# TODO: gather list of districts, categories for search
# TODO: separate data storage in separate function


def main():
    request_all_currencies(['', 'USD', 'EUR'])


def request_all_currencies(currencies_list):
    for currency in currencies_list:
        post_request_offers = compose_request(currency) # Creates URL request with city, category and other params
        offers = get_offer_details(post_request_offers) # Parses offers from a page
        update_offer_record(offers) # Updates or creates a record in data storage


def write_to_csv(offer_string):
    """
    Appends a new line to a file. No verification and it doesn't update old records
    :param offer_string:
    :return:
    """
    csv_file_location = 'offers.csv'
    try:
        with open(csv_file_location, 'a', newline='') as csvfile:
            csv.writer(csvfile).writerow(offer_string)
            csvfile.close()
    except Exception:
        print("This file doesn't exist")


def verify_offer_exists_in_storage(data_id):
    """
    Verifyes that offer with same data_id already exists in storage. Need to add more variables for verification
    to allow multiple entries of same offer with different prices.
    :param data_id:
    :return:
    """
    try:
        with open('offers.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for field in row:
                    if field == data_id:
                        return True
    except Exception:
        print("File offers.csv doesn't exist")


def verify_price_is_primary(offer):
    """
    Verifyes what currency is primary for particular offer. Does it by checking that last two digits are '00'.
    :param offer:
    :return:
    """
    offer_price_string = offer[2]
    offer_price = [int(s) for s in offer_price_string.split() if s.isdigit()]
    offer_price = int(''.join(map(str, offer_price)))
    if abs(offer_price) % 100 == 00:
        return True


def update_offer_record(list_of_offers):
    """
    Adds offer record if it doesn't exist in data storage
    :param list_of_offers:
    :return:
    """
    for offer in list_of_offers:
        data_id = offer[0]
        if verify_offer_exists_in_storage(data_id):
            print('Offer is already in storage')
        elif verify_price_is_primary(offer):
            write_to_csv(offer)
            print('New offer has been added')


def compose_request(currency):
    """
    Creates a request to get a list of offers for parsing
    :param currency: string. is empty for Hryvnya
    :return:
    """
    city_id = 280  # Харьков
    region_id = 8  # Харьковская область
    district_id = 79  # Индустриальный
    distance = 0  # Search distance from a point
    number_of_rooms_from = 3
    number_of_rooms_to = 3
    category_id = 13  # Продажа квартир

    search_request = "https://www.olx.ua/ajax/kharkov/search/list/"
    request_parameters = {'search[city_id]': city_id,
                          'search[category_id]': category_id,
                          'search[region_id]': region_id,
                          'search[district_id]': district_id,
                          'search[dist]': distance,
                          'search[filter_float_number_of_rooms:from]': number_of_rooms_from,
                          'search[filter_float_number_of_rooms:to]': number_of_rooms_to,
                          'currency': currency,
                          'page': ''}
    request_timeout = [10]
    url = [search_request, request_parameters, request_timeout]


    return url


def get_offer_details(url_with_params):
    """
    Offer parsing, data extraction
    :param url_with_params:
    :return:
    """
    list_of_offers = []
    for current_page in range(2): # Sets number of pages to scan. Should be variable based on returned pages
        #  for production
        url_with_params[1]['page'] = current_page

        page = requests.post(url_with_params[0], url_with_params[1])
        print(page.status_code)
        page = page.text
        soup = BeautifulSoup(page, "html.parser")
        offers = soup.find_all("td", class_="offer")
        # print(offers)
        for offer in offers:
            data_id = offer.table["data-id"]  # Get id of an offer
            offer_title = offer.find("a",
                                     class_="marginright5 link linkWithHash detailsLink").strong.string  # too specific.
            #  Should make class more general
            offer_price = offer.find("p", class_="price").strong.string
            link_to_offer = offer.find("a", class_="marginright5 link linkWithHash detailsLink")[
                'href']  # Link to a page with the offer

            list_of_offers.append([data_id, offer_title, offer_price])

            # break

    return list_of_offers


main()
