import datetime
import logging
import re

import dateparser
import requests
from bs4 import BeautifulSoup

from config import category_id
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
    try:
        olx_offer_id = offer.table["data-id"]  # Get id of an offer
    except TypeError:
        logging.info("Invalid element has been parsed as offer")
        return list_of_offer_details
    offer_price = get_price(offer)
    if not verify_offer_exists_in_db(olx_offer_id):
        extended_offer_details(olx_offer_id, list_of_offer_details, offer, offer_price)
        return list_of_offer_details
    # Purpose of this clause is unclear
    # elif (
    #     verify_offer_exists_in_db(olx_offer_id)
    #     and currency == "UAH"
    #     and verify_price_is_primary(offer_price)
    # ):
    #     extended_offer_details(
    #         currency, olx_offer_id, list_of_offer_details, offer, offer_price
    #     )
    #     return list_of_offer_details
    else:
        logging.info("Offer with id {} already exist in DB".format(olx_offer_id))
        return list_of_offer_details


def extended_offer_details(data_id, list_of_offer_details, offer, offer_price):
    offer_title = offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    ).strong.string  # too specific.
    #  Should make class more general
    offer_url = offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    ).attrs["href"]
    offer_details = get_details_from_offer_page(offer_url)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    if category_id == 1600:
        offer_main_area = offer_details.get("Общая площадь")
        number_of_rooms = offer_details.get("Количество комнат")
        floor = offer_details.get("Этаж")
        floors_in_house = offer_details.get("Этажность")
        living_area = offer_details.get("Жилая площадь")
        kitchen_area = offer_details.get("Площадь кухни")
        offer_from = offer_details.get("Объявление от")
        apartment_type = offer_details.get("Тип дома", "Не указано")
        house_type = offer_details.get("Тип стен", "Не указано")
        layout = offer_details.get("Планировка", "Не указано")
        district = offer_details.get("district")
        offer_added_date = offer_details.get("offer_added_date")
        offer_text = offer_details.get("text")
        list_of_offer_details.append(
            [
                data_id,
                offer_price,
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
                offer_url,
                layout,
            ]
        )
    if category_id == 206:
        offer_main_area = offer_details.get("Общая площадь")
        number_of_rooms = offer_details.get("Количество комнат")
        floors_in_house = offer_details.get("Этажность")
        offer_from = offer_details.get("Объявление от")
        house_type = offer_details.get("Тип дома", "Не указано")
        district = offer_details.get("district")
        offer_added_date = offer_details.get("offer_added_date")
        offer_text = offer_details.get("text")
        land_area = offer_details.get("Площадь участка")
        list_of_offer_details.append(
            [
                data_id,
                offer_price,
                offer_main_area,
                number_of_rooms,
                floors_in_house,
                date,
                offer_title,
                offer_from,
                house_type,
                district,
                offer_added_date,
                offer_text,
                offer_url,
                land_area,
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
        detail_name = ""
        detail_value = ""
        detail_name = detail.find("th").string
        if detail_name in [
            "Объявление от",
            "Тип объекта",
            "Тип дома",
            "Тип",
            "Планировка",
            "Тип стен",
        ]:
            try:
                detail_value = detail.find("td").strong.a.get_text(
                    "|", strip=True
                )  # add recognition of "Объявление от" field
            except AttributeError as error:
                print(offer_url)
                print(error)
            offer_details[detail_name] = detail_value
        if detail_name in ["Общая площадь", "Площадь кухни", "Жилая площадь"]:
            try:
                detail_value = detail.find("td").strong.get_text(
                    "|", strip=True
                )  # add recognition of "Объявление от" field
            except AttributeError as error:
                print(offer_url)
                print(error)
            detail_value = re.sub(" м²", "", detail_value)
            detail_value = re.sub(" ", "", detail_value)
            offer_details[detail_name] = float(detail_value)
        if detail_name in ["Площадь участка"]:
            try:
                detail_value = detail.find("td").strong.get_text(
                    "|", strip=True
                )  # add recognition of "Объявление от" field
            except AttributeError as error:
                print(offer_url)
                print(error)
            detail_value = re.sub(" соток", "", detail_value)
            detail_value = re.sub(" ", "", detail_value)
            offer_details[detail_name] = float(detail_value)
        if detail_name in ["Этаж", "Этажность", "Количество комнат"]:
            try:
                detail_value = detail.find("td").strong.get_text(
                    "|", strip=True
                )  # add recognition of "Объявление от" field
            except AttributeError as error:
                print(offer_url)
                print(error)
            offer_details[detail_name] = float(detail_value)
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
        offer_added_date = re.search("\d+ .*,", offer_added_date).group(0)
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


def get_price(offer):
    # TODO: replace with input of a string. Parsing shoould be separated.
    offer_price = offer.find("p", class_="price").strong.string
    try:
        offer_price = re.sub(" грн.|\$|€", "", offer_price)
        offer_price = re.sub(" ", "", offer_price)
    except Exception as detail:
        print(detail)

    return offer_price
