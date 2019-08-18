import logging

import requests
from bs4 import BeautifulSoup
import re
import datetime
import dateparser
import sys
from Data_storage import verify_offer_exists_in_db


def get_list_of_offers(url_with_params):
    """
    Offer parsing, data extraction
    :param url_with_params:
    :return:
    """
    page = requests.post(url_with_params[0], url_with_params[1])
    logging.info("Search request resulted in code: {}".format(page.status_code))
    page = page.text
    soup = BeautifulSoup(page, "html.parser")
    offers = soup.find_all("td", class_="offer")

    return offers


def get_offer_details(offer):
    """

    :param offer: BeatifulSoup object. Has string 'text' attribute that contains text of an offer.
    :return:
    """
    list_of_offer_details = []
    data_id = offer.table["data-id"]  # Get id of an offer
    price_currency_tuple = split_price_currency(offer)
    offer_price = price_currency_tuple[0]
    currency = price_currency_tuple[1]
    if not verify_offer_exists_in_db(olx_offer_id):
        extended_offer_details(
            currency, olx_offer_id, list_of_offer_details, offer, offer_price
        )
        return list_of_offer_details
    elif (
        verify_offer_exists_in_db(olx_offer_id)
        and currency == "UAH"
        and verify_price_is_primary(offer_price)
    ):
        extended_offer_details(
            currency, olx_offer_id, list_of_offer_details, offer, offer_price
        )
        return list_of_offer_details
    else:
        return list_of_offer_details


def extended_offer_details(
    currency, data_id, list_of_offer_details, offer, offer_price
):
    offer_title = offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    ).strong.string  # too specific.
    #  Should make class more general
    offer_url = offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    ).attrs["href"]
    offer_main_area = []
    offer_details = get_details_from_offer_page(offer_url)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    link_to_offer = offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    )[
        "href"
    ]  # Link to a page with the offer
    try:
        offer_main_area = offer_details["Общая площадь"]
    except KeyError:
        offer_main_area = ""
    try:
        number_of_rooms = offer_details["Количество комнат"]
    except KeyError:
        number_of_rooms = ""
    try:
        floor = offer_details["Этаж"]
    except KeyError:
        floor = ""
    try:
        floors_in_house = offer_details["Этажность дома"]
    except KeyError:
        floors_in_house = ""
    try:
        living_area = offer_details["Жилая площадь"]
    except KeyError:
        living_area = ""
    try:
        kitchen_area = offer_details["Площадь кухни"]
    except KeyError:
        kitchen_area = ""
    try:
        offer_from = offer_details["Объявление от"]
    except KeyError:
        offer_from = ""
    try:
        apartment_type = offer_details["Тип квартиры"]
    except KeyError:
        apartment_type = ""
    try:
        house_type = offer_details["Тип"]
    except KeyError:
        house_type = ""
    try:
        district = offer_details["district"]
    except KeyError:
        district = ""
    try:
        offer_added_date = offer_details["offer_added_date"]
    except KeyError:
        offer_added_date = ""
    try:
        offer_text = offer_details["text"]
    except KeyError:
        offer_text = ""
    list_of_offer_details.append(
        [
            data_id,
            offer_price,
            currency,
            offer_main_area,
            number_of_rooms,
            floor,
            floors_in_house,
            date,
            offer_title,
            living_area,
            kitchen_area,
            offer_from,
            apartment_type,
            house_type,
            district,
            offer_added_date,
            offer_text,
        ]
    )


def get_details_from_offer_page(offer_url):
    """
    TODO: Add verification that page with search exists.
    :param offer_url:
    :return:
    """
    page = requests.get(offer_url)
    page = page.text
    soup = BeautifulSoup(page, "html.parser")
    offer_details = {}
    # try:
    offer_details_table = soup.find("table", attrs={"class": "details"})
    # except NotImplementedError
    all_detail_tables = offer_details_table.find_all("table", attrs={"class": "item"})
    for detail in all_detail_tables:
        detail_name = detail.find("th").string
        if detail_name in ["Объявление от", "Тип квартиры", "Тип"]:
            detail_value = detail.find("td").strong.a.get_text(
                "|", strip=True
            )  # add recognition of "Объявление от" field
            offer_details[detail_name] = detail_value
        else:
            detail_value = detail.find("td").strong.get_text(
                "|", strip=True
            )  # add recognition of "Объявление от" field
            try:
                detail_value = re.sub("м²", "", detail_value)
            except Exception:
                pass
            offer_details[detail_name] = detail_value
    titlebox_details = soup.find("div", attrs={"class": "offer-titlebox__details"})
    # Get district name
    district = titlebox_details.a.strong.string
    try:
        district = re.sub(
            "Харьков, Харьковская область, ", "", district
        )  # Hardcode for Харьков, Харьковская область only
    except Exception as detail:
        print(detail)
    offer_details["district"] = district
    # Get offer added date and format it
    offer_added_date = titlebox_details.em.get_text()
    try:
        offer_added_date = re.search("\d+ .*[7|8|9],", offer_added_date).group(
            0
        )  # This will work for 2017 and 2018 #TODO: this is stupid, should not depend on year last digit
        offer_added_date = re.sub(",", "", offer_added_date)
    except Exception as detail:
        print(detail)
    offer_added_date = dateparser.parse(
        offer_added_date, date_formats=["%d %B %Y"], languages=["ru"]
    ).strftime("%Y-%m-%d")
    offer_details["offer_added_date"] = offer_added_date
    offer_details["text"] = soup.find("div", attrs={"id": "textContent"}).get_text(
        "|", strip=True
    )

    return offer_details


def verify_price_is_primary(offer_price):
    """
    Verifyes what currency is primary for particular offer. Does it by checking that last two digits are '00'.
    :param offer_price:
    :return:
    """
    if abs(int(offer_price)) % 100 == 00:
        return True


def split_price_currency(offer):
    #TODO: replace with input of a string. Parsing shoould be separated.
    offer_price = offer.find("p", class_="price").strong.string
    if re.search(" грн.", offer_price):
        currency = "UAH"
    elif re.search("$", offer_price):
        currency = "USD"
    elif re.search("€", offer_price):
        currency = "EUR"
    else:
        currency = "Unknown"
    try:
        offer_price = re.sub(" грн.|\$|€", "", offer_price)
        offer_price = re.sub(" ", "", offer_price)
    except Exception as detail:
        print(detail)

    return offer_price, currency
