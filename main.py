from bs4 import BeautifulSoup
import requests
import csv


# TODO: save data to a file with date
# TODO: compare prices of a same listing
# TODO: add search parameters to look into smaller market
# TODO: get exact address from a map
# TODO: pass currency in compose_request() to get proper currency result
# TODO: gather list of districts, categories for search
# TODO: write data in a file


def main():
    offers = get_offer_details(compose_request())
    update_offer_record(offers)


def write_to_csv(offer_string):
    with open('offers.csv', 'a', newline='') as csvfile:
        csv.writer(csvfile).writerow(offer_string)
        csvfile.close()


def verify_offer_exists_in_storage(data_id):
    with open('offers.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for field in row:
                if field == data_id:
                    return True


def update_offer_record(list_of_offers):
    for offer in list_of_offers:
        data_id = offer[0]
        if verify_offer_exists_in_storage(data_id):
            print('Offer is already in storage')
        else:
            write_to_csv(offer)
            print("It's a new offer")


def compose_request():
    city_id = 280
    region_id = 8
    district_id = 79
    district = 0
    number_of_rooms_from = 3
    number_of_rooms_to = 3
    category_id = 13
    currency_usd = "USD"
    currency_eur = "EUR"

    search_request = "https://www.olx.ua/ajax/kharkov/search/list/"
    request_parameters = {'search[city_id]': city_id,
                          'search[category_id]': category_id,
                          'search[region_id]': region_id,
                          'search[district_id]': district_id,
                          'search[dist]': district,
                          'search[filter_float_number_of_rooms:from]': number_of_rooms_from,
                          'search[filter_float_number_of_rooms:to]': number_of_rooms_to,
                          'currency': currency_usd,
                          'page': ''}
    request_timeout = [10]
    url = [search_request, request_parameters, request_timeout]

    return url


def get_offer_details(url_with_params):
    offer_string = []
    # TODO: add cycle for adding pages in request parameters

    page = requests.post(url_with_params[0], url_with_params[1])
    print(page.status_code)
    page = page.text
    soup = BeautifulSoup(page, "html.parser")
    offers = soup.find_all("td", class_="offer")
    # print(offers)
    for offer in offers:
        data_id = offer.table["data-id"]  # Get id of an offer
        offer_title = offer.find("a",
                                 class_="marginright5 link linkWithHash detailsLink").strong.string  # too specific. Should make class more general
        offer_price = offer.find("p", class_="price").strong.string
        link_to_offer = offer.find("a", class_="marginright5 link linkWithHash detailsLink")[
            'href']  # Link to a page with the offer

        offer_string.append([data_id, offer_title, offer_price])

        # break

    return offer_string


main()
