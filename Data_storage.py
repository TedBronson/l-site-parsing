import sqlite3
from config import db_file_path


def write_to_db(offer_string):
    """
    Appends a new line to a file. No verification and it doesn't update old records.
    category_id for houses and apartments is hardcoded, so saving other categories would require code adjustments.
    :param offer_string:
    :return:
    """
    from config import category_id
    try:
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        if category_id == 1600:
            c.execute(
                "INSERT INTO offers values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                offer_string,
            )
        elif category_id == 1602:
            c.execute(
                "INSERT INTO houses values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                offer_string,
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def existing_offer_ids(category_id):
    """Returns ids of all offers of specified category currently in DB."""
    conn = sqlite3.connect(db_file_path)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    if category_id == 1600:
        ids_in_db = c.execute("select olx_id from offers").fetchall()
    if category_id == 1602:
        ids_in_db = c.execute("select olx_id from houses").fetchall()
    # TODO: this common query needs to be verified
    # ids_in_db = c.execute("select olx_id from offers union select olx_id from houses").fetchall()
    conn.close()
    return ids_in_db


def get_parsing_queries():
    """
    Read search queries from DB.

    Function to read and return active queries that should be used to get data about offers with all parameters.
    :return: list of dictionaries. Where each dictionary is a parsing query
    """
    conn = sqlite3.connect(db_file_path)
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

