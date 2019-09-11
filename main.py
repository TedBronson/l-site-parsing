import logging
import time

import Offer
import config as cfg
import request_composition
from Data_storage import write_to_db

logging.basicConfig(level=logging.INFO)


# TODO: compare prices of a same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: gather list of districts, categories for search
# TODO: save a phone number


def main():
    # Parse offers according to limitations set in config file and in request composition.py and create a list with results
    global offers_added
    global offers_skipped
    offers_added = 0
    offers_skipped = 0

    list_of_offers = parse_offers()
    logging.info("Number of offers parsed from search: {}".format(len(list_of_offers)))

    for offer in list_of_offers:
        offer_details = Offer.get_offer_details(offer)
        if offer_details:
            update_offer_record(offer_details)
            offers_added += 1
        else:
            offers_skipped += 1


def parse_offers():
    list_of_offers = []
    currencies_list = cfg.currencies_list
    for currency in currencies_list:
        # Creates URL request with city, category and other params
        post_request_offers = request_composition.compose_request(currency)
        for current_page in range(
            cfg.search_pages_lower_limit, cfg.search_pages_upper_limit
        ):
            post_request_offers[1]["page"] = current_page
            page_list_of_offers = Offer.get_list_of_offers(
                post_request_offers
            )  # Parses offers from a page
            for offer in page_list_of_offers:
                list_of_offers.append(offer)  # Parses offers from all pages in a range and creates list
    return list_of_offers


def update_offer_record(list_of_offers):
    """
    Adds offer record if it doesn't exist in data storage
    :param list_of_offers:
    :return:
    """

    for offer in list_of_offers:
        write_to_db(offer)


start_time = time.time()
main()
logging.info("Offers added: {}. Offers skipped: {}.".format(offers_added, offers_skipped))
logging.info("--- Process finished in {} seconds ---".format(time.time() - start_time))
