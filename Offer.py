import datetime
import requests
from bs4 import BeautifulSoup
import re


def get_offer_details(url_with_params):
    """
    Offer parsing, data extraction
    :param url_with_params:
    :return:
    """
    list_of_offers = []
    from Data_storage import verify_offer_exists_in_db

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
        offer_price = offer.find("p", class_="price").strong.string  # TODO: удалить валюту, добавить её в отдельную ячейку
        try:
            offer_price = re.sub(' грн.', '', offer_price)  # TODO: replace it with adding UAH in separate column
            offer_price = re.sub(' ', '', offer_price)
        except Exception:
            pass


        offer_url = offer.find("a", class_="marginright5 link linkWithHash detailsLink").attrs['href']
        offer_main_area = []
        if verify_offer_exists_in_db(data_id):
            offer_details = {}
            pass
        else:
            offer_details = get_details_from_offer_page(offer_url)

        date = datetime.datetime.now().strftime("%Y-%m-%d")
        link_to_offer = offer.find("a", class_="marginright5 link linkWithHash detailsLink")[
            'href']  # Link to a page with the offer
        try:
            offer_main_area = offer_details['Общая площадь']
        except KeyError:
            offer_main_area = ''

        # list_of_offers.append([data_id, date, offer_title, offer_price])
        list_of_offers.append([data_id, offer_price, offer_main_area])

        # break

    return list_of_offers


def get_details_from_offer_page(offer_url):
    page = requests.get(offer_url)
    page = page.text
    soup = BeautifulSoup(page, "html.parser")
    offer_details = {}
    offer_details_table = soup.find("table", attrs={'class': 'details'})
    all_detail_tables = offer_details_table.find_all("table", attrs={'class': 'item'})
    for detail in all_detail_tables:
        detail_value = detail.find("td").strong.string  # add recognition of "Объявление от" field
        try:
            detail_value = re.sub('\s+', '', detail_value)
        except Exception:
            pass
        try:
            detail_value = re.sub('м²', '', detail_value)
        except Exception:
            pass
        detail_name = detail.find("th").string
        offer_details[detail_name] = detail_value

    return offer_details