import time

import psycopg

from issuance import process


if __name__ == "__main__":
    while True:
        try:
            process()
        except psycopg.Error:
            print("Local database unavailable", flush=True)
        time.sleep(3)
