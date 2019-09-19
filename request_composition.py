

def compose_request(
    city_id,
    region_id,
    district_id,
    category_id,
    distance=0,
    query_term="",
    number_of_rooms_from=1,
    number_of_rooms_to=5,
    currency="USD",
):
    """
    Creates a request to get a list of offers for parsing
    :param city_id: cities = {"Kharkiv": 280, "Kyiv": 268}
    :param region_id: regions = {"Харьковская область": 8}
    :param district_id:
    :param category_id:
    :param distance:
    :param query_term: Search term as text. Short and concise.
    :param number_of_rooms_from:
    :param number_of_rooms_to:
    :param currency: Three-character currency code. Empty string "" for UAH.
    :return:
    """
    search_request = "https://www.olx.ua/ajax/kharkov/search/list/"
    request_parameters = {
        "q": query_term,
        "search[city_id]": city_id,
        "search[category_id]": category_id,
        "search[region_id]": region_id,
        "search[district_id]": district_id,
        "search[dist]": distance,
        "search[filter_float_number_of_rooms:from]": number_of_rooms_from,
        "search[filter_float_number_of_rooms:to]": number_of_rooms_to,
        "currency": currency,
        "page": "",
    }
    request_timeout = [10]
    url = [search_request, request_parameters, request_timeout]

    return url
