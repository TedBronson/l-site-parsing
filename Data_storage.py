import sqlite3


def write_to_db(offer_string):
    """
    Appends a new line to a file. No verification and it doesn't update old records
    :param offer_string:
    :return:
    """
    try:
        x = offer_string
        conn = sqlite3.connect("D:\Projects\l-site-parsing\offers.db")
        c = conn.cursor()
        c.execute('INSERT INTO offers values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', x)
        conn.commit()
        conn.close()
        print("Offer has been added")
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
        conn = sqlite3.connect("D:\Projects\l-site-parsing\offers.db")
        c = conn.cursor()
        if c.execute('select count(1) from offers where olx_id = (?)', (data_id,)).fetchone() == (1,):
            conn.commit()
            conn.close()
            print("This offer already exists in db")
            verify_offer_exists_in_db.counter += 1
            print("Количество проверок существования записей в базе: ", verify_offer_exists_in_db.counter)
            return True
        else:
            conn.commit()
            conn.close()
            return False
    except Exception as detail:
        print(detail)

verify_offer_exists_in_db.counter = 0