import csv

import Offer
import request_composition


# TODO: compare prices of a same listing
# TODO: write all three prices for same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: gather list of districts, categories for search
# TODO: separate data storage in separate function


def main():
    request_all_currencies([''])  # , 'USD', 'EUR'])


def request_all_currencies(currencies_list):
    for currency in currencies_list:
        post_request_offers = request_composition.compose_request(currency) # Creates URL request with city, category and other params
        offers = Offer.get_offer_details(post_request_offers) # Parses offers from a page
        update_offer_record(offers)  # Updates or creates a record in data storage


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
    except Exception as detail:
        print(detail)


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
    except Exception as detail:
        print(detail)


def verify_price_is_primary(offer):
    """
    Verifyes what currency is primary for particular offer. Does it by checking that last two digits are '00'.
    :param offer:
    :return:
    """
    offer_price_string = offer[1]  # TODO: Change from index to a name
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
        else:  # elif verify_price_is_primary(offer):
            write_to_csv(offer)
            print('New offer has been added')


main()
