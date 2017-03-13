from bs4 import BeautifulSoup
import requests


# TODO: save data to a file with date
# TODO: compare prices of a same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: pass currency in compose_request() to get proper currency result
# TODO: gather list of districts, categories for search
# TODO: write data in a file

def main():
    # get_offer_details("https://www.olx.ua/nedvizhimost/prodazha-kvartir/kharkov/?search[filter_float_number_of_rooms:from]=3&search[filter_float_number_of_rooms:to]=3&search[district_id]=79")
    get_offer_details(compose_request())


def compose_request():
    city_id = 280
    region_id = 8
    district_id = 79
    district = 0
    number_of_rooms_from = 3
    number_of_rooms_to = 3
    category_id = 13
    currency_USD = "USD"
    currency_EUR = "EUR"

    search_request = "https://www.olx.ua/ajax/kharkov/search/list/"
    request_parameters = {'search[city_id]': city_id,
                          'search[category_id]': category_id,
                          'search[region_id]': region_id,
                          'search[district_id]': district_id,
                          'search[dist]': district,
                          'search[filter_float_number_of_rooms:from]': number_of_rooms_from,
                          'search[filter_float_number_of_rooms:to]': number_of_rooms_to,
                          'currency': currency_USD,
                          'page': 3}
    request_timeout = [10]
    url = [search_request, request_parameters, request_timeout]

    return url


def get_offer_details(url_with_params):
    page = requests.post(url_with_params[0], url_with_params[1])
    print(page.status_code)
    page = page.text
    soup = BeautifulSoup(page)
    offers = soup.find_all("td", class_="offer")
    # print(offers)
    for offer in offers:
        data_id = offer.table["data-id"]  # Get id of an offer
        offer_title = offer.find("a",
                                 class_="marginright5 link linkWithHash detailsLink").strong.string  # too specific. Should make class more general
        offer_price = offer.find("p", class_="price").strong.string
        link_to_offer = offer.find("a", class_="marginright5 link linkWithHash detailsLink")[
            'href']  # Link to a page with the offer

        print(data_id)
        print(offer_title)
        print(offer_price)
        print(link_to_offer)
        print("--------------------")

        break


main()
