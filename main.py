import Offer
import config as cfg
import request_composition
from Data_storage import write_to_db


# TODO: compare prices of a same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: gather list of districts, categories for search


def main():
    list_of_offers = parse_offers()
    print("Number of offers parsed from search: ", len(list_of_offers))
    for offer in list_of_offers:
        update_offer_record(Offer.get_offer_details(offer))
        print("-----")


def parse_offers():
    list_of_offers = []
    currencies_list = cfg.currencies_list
    for currency in currencies_list:
        post_request_offers = request_composition.compose_request(currency) # Creates URL request with city, category and other params
        for current_page in range(cfg.search_pages_lower_limit, cfg.search_pages_upper_limit):
            post_request_offers[1]['page'] = current_page
            page_list_of_offers = Offer.get_list_of_offers(post_request_offers)  # Parses offers from all pages in a range
            for offer in page_list_of_offers:
                list_of_offers.append(offer)  # Parses offers from all pages in a range
        """
        This will only search one random page. This is for debugging/testing/developing purposes.
        """
        # post_request_offers[1]['page'] = random.randrange(cfg.search_pages_lower_limit, cfg.search_pages_upper_limit)
        # print("Search page # is: ", post_request_offers[1]['page'])
        # page_list_of_offers = Offer.get_list_of_offers(post_request_offers)  # Parses offers from all pages in a range
        # for offer in page_list_of_offers:
        #     list_of_offers.append(offer)  # Parses offers from all pages in a range
    return list_of_offers


def update_offer_record(list_of_offers):
    """
    Adds offer record if it doesn't exist in data storage
    :param list_of_offers:
    :return:
    """

    for offer in list_of_offers:
        write_to_db(offer)
        update_offer_record.counter += 1
        print(update_offer_record.counter)


update_offer_record.counter = 0


main()
