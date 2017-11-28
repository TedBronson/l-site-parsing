import csv


def write_to_csv(offer_string):
    """
    Appends a new line to a file. No verification and it doesn't update old records
    :param offer_string:
    :return:
    """
    csv_file_location = 'offers.csv'
    try:
        with open(csv_file_location, 'a', newline='') as csvfile:
            csv.writer(csvfile).writerow(offer_string)
            csvfile.close()
            print('New offer has been added')
    except Exception as detail:
        print(detail)


def verify_offer_exists_in_storage(data_id):
    """
    Verifyes that offer with same data_id already exists in storage. Need to add more variables for verification
    to allow multiple entries of same offer with different prices.
    :param data_id:
    :return:
    """
    try:
        with open('offers.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for field in row:
                    if field == data_id:
                        return True
    except Exception as detail:
        print(detail)