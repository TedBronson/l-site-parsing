cities = {"Kharkiv": 280,
          "Kyiv": 268}

districts = {"Индустриальный": 79}

regions = {"Харьковская область": 8}

def compose_request(currency):
    """
    Creates a request to get a list of offers for parsing
    :param currency: string. is empty for Hryvnya
    :return:
    """
    city_id = 280
    region_id = 8
    district_id = ''
    distance = 0  # Search distance from a point
    number_of_rooms_from = 1
    number_of_rooms_to = 1
    category_id = 13  # Продажа квартир

    search_request = "https://www.olx.ua/ajax/kharkov/search/list/"
    request_parameters = {'search[city_id]': city_id,
                          'search[category_id]': category_id,
                          'search[region_id]': region_id,
                          'search[district_id]': district_id,
                          'search[dist]': distance,
                          'search[filter_float_number_of_rooms:from]': number_of_rooms_from,
                          'search[filter_float_number_of_rooms:to]': number_of_rooms_to,
                          'currency': currency,
                          'page': ''}
    request_timeout = [10]
    url = [search_request, request_parameters, request_timeout]


    return url