import Offer
import request_composition
import config as cfg
# TODO: compare prices of a same listing
# TODO: write all three prices for same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: gather list of districts, categories for search
# TODO: separate data storage in separate function
from Data_storage import write_to_csv, verify_offer_exists_in_storage


def main():
    parse_offers()


def parse_offers():
    currencies_list = cfg.currencies_list
    for currency in currencies_list:
        post_request_offers = request_composition.compose_request(currency) # Creates URL request with city, category and other params
        for current_page in range(cfg.limit_search_pages):
            post_request_offers[1]['page'] = current_page
            offers = Offer.get_offer_details(post_request_offers) # Parses offers from all pages in a range
            update_offer_record(offers)  # Updates or creates a record in data storage


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
            print(data_id)
        else:  # elif verify_price_is_primary(offer):
            write_to_csv(offer)


main()
