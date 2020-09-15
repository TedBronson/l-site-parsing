import datetime
import logging
import re

import dateparser
import requests as r
from bs4 import BeautifulSoup


class PageNotValid(Exception):
    """Raised when offer detail page returns redirect, page not found or any code other than 200."""
    pass


def get_set_of_offers(url_with_params):
    """
    Find separate offers on a page with search results.

    Offer parsing, data extraction
    :param url_with_params:
    :return:
    """
    search_results_page = r.post(url_with_params[0], url_with_params[1], allow_redirects=False)
    if search_results_page.status_code != 200:
        logging.info("Search request resulted in code: {}".format(search_results_page.status_code))
        raise PageNotValid
    page_text = search_results_page.text
    soup = BeautifulSoup(page_text, "html.parser")
    offers = soup.find_all("td", class_="offer")

    return offers


def get_offer_details(offer):
    """
    Get offer details from individual page if offer doesn't exist in DB.

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
    try:
        extended_offer_details(olx_offer_id, list_of_offer_details, offer, offer_price)
    except (PageNotValid, AttributeError):
        raise
    return list_of_offer_details


def extended_offer_details(data_id, list_of_offer_details, offer, offer_price):
    """
    Parse individual offer page and save relevant data as dictionary.

    This function opens link to an individual offer, parses fields on the page and populates list_of_offer_details
    :param data_id: olx_id
    :param list_of_offer_details: empty list
    :param offer: individual offer parsed from search page
    :param offer_price:
    :return: dictionary
    """
    from config import category_id

    offer_title = offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    ).strong.string  # too specific.
    #  Should make class more general
    offer_url = re.findall("(.+html)", offer.find(
        "a", class_="marginright5 link linkWithHash detailsLink"
    ).attrs["href"])[0]
    try:
        offer_details = get_details_from_offer_page(offer_url)
    except (PageNotValid, AttributeError):
        print("Couldn't get details from offer page")
        raise
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
        print("Saved '{}' offer details".format(offer_title))
    if category_id == 1602:
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
        print("Saved '{}' offer details".format(offer_title))


def get_details_from_offer_page(offer_url):
    """
    TODO: Add verification that page with search exists.
    :param offer_url:
    :return:
    """
    offer_details = {}

    page = r.get(offer_url, allow_redirects=False)
    if page.status_code != 200:
        raise PageNotValid
    page_text = page.text
    soup = BeautifulSoup(page_text, "html.parser")
    offer_details_table = soup.find("ul", attrs={"class": "offer-details"})
    try:
        all_detail_tables = offer_details_table.find_all("li", attrs={"class": "offer-details__item"})
    except AttributeError as details:
        print(details)
        raise
    for detail in all_detail_tables:
        detail_name = ""
        detail_value = ""
        detail_name = detail.find("span", attrs={"class": "offer-details__name"}).string
        if detail_name in [
            "Объявление от",
            "Тип объекта",
            "Тип дома",
            "Тип",
            "Планировка",
            "Тип стен",
        ]:
            try:
                detail_value = detail.find("strong").get_text(
                    "|", strip=True
                )  # add recognition of "Объявление от" field
            except AttributeError as error:
                print(offer_url)
                print(error)
            offer_details[detail_name] = detail_value
        if detail_name in ["Общая площадь", "Площадь кухни", "Жилая площадь"]:
            try:
                detail_value = detail.find("strong").get_text(
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
                detail_value = detail.find("strong").get_text(
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
                detail_value = detail.find("strong").get_text(
                    "|", strip=True
                )  # add recognition of "Объявление от" field
            except AttributeError as error:
                print(offer_url)
                print(error)
            offer_details[detail_name] = float(detail_value)
    # Get district name
    district = soup.find("address").p.get_text()
    try:
        district = re.sub(
            "Харьков, Харьковская область, ", "", district
        )  # Hardcode for Харьков, Харьковская область only
    except Exception as detail:
        print(detail)
    offer_details["district"] = district
    # Get offer added date and format it
    try:
        offer_added_date = soup.find(string=re.compile(".*Добавлено: в.*"))
        offer_added_date = re.search("\d{1,2}\D*\d{4}", offer_added_date).group(0)
        offer_added_date = dateparser.parse(
            offer_added_date, date_formats=["%d %B %Y"], languages=["ru"]
        ).strftime("%Y-%m-%d")
        offer_details["offer_added_date"] = offer_added_date
    except Exception as detail:
        print("Couldn't save 'offer added date' because of Exception: {}".format(detail))
    try:
        offer_details["text"] = soup.find("div", attrs={"id": "textContent"}).get_text(
            "|", strip=True
        )
    except Exception as detail:
        print(detail)

    return offer_details


def get_price(offer):
    """
    Get price value from field in offer html.

    Function takes offer with short information and returns int with offer price.
    :param offer: offer parsed from search page.
    :return: int with price.
    """
    offer_price = offer.find("p", class_="price").strong.string
    try:
        offer_price = re.sub(" грн.|\$|€", "", offer_price)
        offer_price = re.sub(" ", "", offer_price)
    except Exception as detail:
        print(detail)

    return offer_price
