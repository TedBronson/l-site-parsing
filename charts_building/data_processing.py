import sqlite3
import pandas as pd
import numpy as np


def _read_db_data(offer_type, db_link):
    """
    This function reads data from Sqlite DB and writes it into Pandas dataframe.

    :param offer_type: Accepts two options: 'houses' and 'apartments'
    :param db_link: address of the file with local database
    :return: Pandas DataFrame
    """
    conn = sqlite3.connect(db_link)

    if offer_type == "houses":
        data = pd.read_sql("SELECT * FROM houses", conn, index_col="olx_id")
    if offer_type == "apartments":
        data = pd.read_sql("SELECT * FROM offers", conn, index_col="olx_id")

    conn.close()

    return data


def _data_cleanup(data, offer_type):
    """
    This function applies rules to exlude offers that have invalid data, data that doesn't make sense.

    :param data: Pandas DataFrame
    :param offer_type: Accepts two options: 'houses' and 'apartments'
    :return: Pandas DataFrame.
    """
    if offer_type == "houses":
        data["total_area"].replace("", np.nan, inplace=True)
        data["price"].replace("", np.nan, inplace=True)
        data["floors_in_house"].replace("", np.nan, inplace=True)

        data = data[
            (
                data["district"].isin(
                    [
                        "Шевченковский",
                        "Киевский",
                        "Фрунзенский",
                        "Холодногорский",
                        "Московский",
                        "Червонозаводской",
                        "Октябрьский",
                        "Индустриальный ",
                        "Коминтерновский",
                    ]
                )
            )
        ]
        data = data[(data["total_area"] > 10)]
        data = data[(data["price"] > 5000)]
        data = data[(data["floors_in_house"] < 5)]
    if offer_type == "apartments":
        data["total_area"].replace("", np.nan, inplace=True)
        data["living_area"].replace("", np.nan, inplace=True)
        data["kitchen_area"].replace("", np.nan, inplace=True)
        data["rooms"].replace("", np.nan, inplace=True)
        data["floor"].replace("", np.nan, inplace=True)
        data["floors_in_house"].replace("", np.nan, inplace=True)

        data["offer_added_date"] = data.offer_added_date.astype("datetime64")
        data["rooms"] = data.rooms.astype("float")
        data["floor"] = data.floor.astype("float")
        data["floors_in_house"] = data.floors_in_house.astype("float")
        data["total_area"] = data.total_area.astype("float")
        data["price"] = data.price.astype("float")
        data["kitchen_area"] = data.kitchen_area.astype("float")  # some data is in string type and it causes errors

        data = data[
            (
                data["district"].isin(
                    [
                        "Шевченковский",
                        "Киевский",
                        "Фрунзенский",
                        "Холодногорский",
                        "Московский",
                        "Червонозаводской",
                        "Октябрьский",
                        "Индустриальный ",
                        "Коминтерновский",
                    ]
                )
            )
        ]
        data = data[(data["total_area"] > data["kitchen_area"])]
        data = data[(data["total_area"] > 10)]
        data = data[(data["price"] > 5000)]
        data = data[(data["floor"] < 31)]
        data = data[(data["floors_in_house"] < 31)]

    return data


def read_data(offer_type, db_link):
    """
    Function that reads data from DB and removes entries with wrong data.
    :param offer_type: Accepts two options: 'houses' and 'apartments'
    :param db_link: address of the file with local database
    :return: Pandas DataFrame.
    """
    data = _read_db_data(offer_type, db_link)
    data = _data_cleanup(data, offer_type)

    return data

