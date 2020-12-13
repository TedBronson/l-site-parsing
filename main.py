import logging
import time
from datetime import datetime, timedelta

import Data_storage as ds
import Offer
import config as cfg
import request_composition

logging.basicConfig(level=logging.INFO)


# TODO: implement changing user agent
# TODO: compare prices of a same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: gather list of districts, categories for search
# TODO: save a phone number


def main():
    """ Parse offers according to limitations set in config file and in request
    composition.py and create a list with results """
    for query in ds.get_parsing_queries():
        offers_added = 0

        query_name = query.get("Name")
        category_id = query.get("category_id")

        cfg.category_id = category_id

        logging.info("Parsing offers for query: {}. \n".format(query_name))

        list_of_offers = parse_search_results_pages(
            query.get("city_id"),
            query.get("region_id"),
            query.get("district_id"),
            query.get("distance"),
            query.get("query_term"),
            query.get("category_id"),
        )

        filtered_list_of_offers = filter_out_existing_offers(
            list_of_offers, category_id
        )

        for offer in filtered_list_of_offers:
            time.sleep(4)  # sleep before getting next offer details
            try:
                offer_details = Offer.get_offer_details(offer)
            except (Offer.PageNotValid, AttributeError):
                continue
            update_offer_record(offer_details)
            offers_added += 1

        logging.info("{} added: {}.".format(query_name, offers_added))


def filter_out_existing_offers(list_of_offers, category_id):
    ids_in_db = ds.existing_offer_ids(category_id)

    filtered_list_of_offers = list()
    for offer in list_of_offers:
        try:
            olx_offer_id = int(offer.table["data-id"])  # Get id of an offer
        except TypeError:
            continue
        if olx_offer_id not in ids_in_db:
            filtered_list_of_offers.append(offer)

    return filtered_list_of_offers


def parse_search_results_pages(
    city_id, region_id, district_id, distance, query_term, category_id
):
    """
    This function parses all offers from search pages within given limits
    and creates a list of offers with limited info
    available (price, olx_id, title).
    :param city_id:
    :param region_id:
    :param district_id:
    :param distance:
    :param query_term:
    :param category_id:
    :return:
    """
    list_of_offers = []

    # Don't search for houses on pages above 10, they don't exist.
    if category_id == 1602 & cfg.search_pages_lower_limit > 10:
        return list_of_offers

    search_url = request_composition.compose_request(
        city_id, region_id, district_id, category_id, distance, query_term
    )
    for current_page in range(
        cfg.search_pages_lower_limit, cfg.search_pages_upper_limit
    ):
        time.sleep(2)  # to slow down process for anti-parsing algorithms
        search_url[1]["page"] = current_page
        try:
            offers_set = Offer.get_set_of_offers(
                search_url
            )  # Parses offers from a page
        except Offer.PageNotValid:
            continue
        for offer in offers_set:
            list_of_offers.append(
                offer
            )  # Parses offers from all pages in a range and creates list
    logging.info(
        "Number of offers parsed from search: {}\n".format(len(list_of_offers))
    )
    return list_of_offers


def update_offer_record(list_of_offers):
    """
    Adds offer record if it doesn't exist in data storage
    :param list_of_offers:
    :return:
    """
    for offer in list_of_offers:
        ds.write_to_db(offer)


start_time = datetime.now()
main()
logging.info(
    "--- Process finished in {} ---".format(
        str(timedelta(seconds=(datetime.now() - start_time).seconds))
    )
)
