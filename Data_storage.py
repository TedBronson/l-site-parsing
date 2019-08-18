import logging
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
        offer_olx_id = offer_string[0]
        conn = sqlite3.connect(config.db_file_path)
        c = conn.cursor()
        if not verify_offer_exists_in_db(offer_olx_id):
            c.execute(
                "INSERT INTO offers values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                offer_string,
            )
            logging.info(
                "Added new offer with id: {}. Price: {} {}".format(
                    offer_string[0], offer_string[1], offer_string[2]
                )
            )
        else:
            c.execute(
                "UPDATE offers SET price = ?, currency = ? WHERE olx_id == ?",
                (offer_string[1], offer_string[2], offer_string[0]),
            )
            # TODO: Show previous price too
            logging.info(
                "updated offer with id: {}. Price: {} {}".format(
                    offer_string[0], offer_string[1], offer_string[2]
                )
            )
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
        if c.execute(
            "select count(1) from offers where olx_id = (?)", (data_id,)
        ).fetchone() == (1,):
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False
    except Exception as detail:
        print(detail)
