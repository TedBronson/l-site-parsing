import sqlite3
import config

# TODO: move db file path into config

def write_to_db(offer_string):
    """
    Appends a new line to a file. No verification and it doesn't update old records
    :param offer_string:
    :return:
    """
    try:
        x = offer_string
        conn = sqlite3.connect(config.db_file_path)
        c = conn.cursor()
        c.execute('INSERT INTO offers values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', x)
        conn.commit()
        conn.close()
    except Exception as detail:
        print(detail)


def verify_offer_exists_in_db(data_id):
    """
    Verifyes that offer with same data_id already exists in storage. Need to add more variables for verification
    to allow multiple entries of same offer with different prices.
    :param data_id:
    :return:
    """
    try:
        conn = sqlite3.connect(config.db_file_path)
        c = conn.cursor()
        if c.execute('select count(1) from offers where olx_id = (?)', (data_id,)).fetchone() == (1,):
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False
    except Exception as detail:
        print(detail)


def write_offer_price(offer_id, price, currency):
    """
    Verifyes that offer with same data_id already exists in storage. Need to add more variables for verification
    to allow multiple entries of same offer with different prices.
    :param data_id:
    :return:
    """
    try:
        x = [offer_id, price]
        conn = sqlite3.connect(config.db_file_path)
        c = conn.cursor()
        if currency == 'UAH':
            c.execute('INSERT INTO offer_prices values(?, ?, NULL)', x)
        elif currency == 'USD':
            c.execute('INSERT INTO offer_prices values(?, NULL, ?)', x)
        conn.commit()
        conn.close()
    except Exception as detail:
        print(detail)