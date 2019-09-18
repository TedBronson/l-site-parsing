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
            if config.category_id == 1600:
                c.execute(
                    "INSERT INTO offers values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    offer_string,
                )
                logging.info(
                    "Added new apartment with id: {}. Price: {} {}".format(
                        offer_string[0], offer_string[1], offer_string[2]
                    )
                )
            elif config.category_id == 206:
                c.execute(
                    "INSERT INTO houses values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    offer_string,
                )
                logging.info(
                    "Added new house with id: {}. Price: {} {}".format(
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
        ).fetchone() == (1,) or c.execute(
            "select count(1) from houses where olx_id = (?)", (data_id,)
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


def get_parsing_queries():
    """
    Function to read and return active queries that should be used to get data about offers with all parameters.
    :return: list of dictionaries. Where each dictionary is a parsing query
    """
    conn = sqlite3.connect(config.db_file_path)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM parsing_queries where query_enabled=TRUE")
    parsing_queries = c.fetchall()

    conn.commit()
    conn.close()

    return parsing_queries


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

