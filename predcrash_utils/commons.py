# coding: utf-8
"""
.. module:: albator_utils.commons
Commons functions to help with the Api runtime
"""

__author__ = "Sarfraz Kapasi"

# standard
import os
import logzero
from typing import Dict
import json
import asyncio
import pathlib
from pprint import pprint
import zipfile
# installed
import uvloop
import aioredis
from raven import Client
from dotenv import load_dotenv, find_dotenv
import aiofiles
# custom
from predcrash_utils import constants as cst

# Globals
###############################################################################

LOGGER = logzero.logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
LOOP = asyncio.get_event_loop()


# Functions and Classes
###############################################################################

# def raise_error_sentry(exception: Exception):
#     if SENTRY_LOG_ACTIVATED is True:
#         SENTRY.captureException()
#         LOGGER.info("Error reported to sentry.io!")
#     elif not AppErrorException.raising:
#         LOGGER.warning("Report to sentry.io deactivated!")

def get_redis_url() -> str:
    """
    .. function:: get_redis_url()
      :returns: Redis server's url
    """
    load_dotenv(find_dotenv())
    ret = "redis://localhost"
    if cst.REDIS_URL in os.environ:
        ret = os.environ[cst.REDIS_URL]
    return ret
    # return "redis://localhost:63790"


def get_pg_dsn() -> str:
    """
    .. function:: get_pg_dsn()
    """
    load_dotenv(find_dotenv())
    # ret = "dbname=postgres user=postgres host=127.0.0.1 port=54320"
    ret = "dbname=albator user=albator password=albatorpwd host=localhost port=54320"
    # if cst.PG_DSN in os.environ:
    #     ret = os.environ[cst.PG_DSN]
    return ret


async def store_configuration(cfg: Dict[str, str]) -> None:
    """
    .. function:: store_configuration(cfg)
      :param cfg: Dictionary containing the Api configuration
    Store the configuration dict into redis cache
    """
    conn = None
    try:
        redis_conn = get_redis_url()
        pprint("Connection to redis --> " + redis_conn)
        conn = await aioredis.create_connection(redis_conn, loop=asyncio.get_event_loop())
        await conn.execute(cst.SET, cst.API_CONFIGURATION, json.dumps(cfg))
    except Exception as e:
        LOGGER.error("Could not store configuration in Redis")
        raise e
    finally:
        if conn is not None:
            conn.close()
            await conn.wait_closed()


async def get_configuration() -> Dict[str, str]:
    """
    .. function:: get_configuration()
      :rtype: Dict[str, str]
      :returns: The configuration stored earlier
    Gets the configuration from memory store
    """
    ret = {}
    conn = None
    try:
        redis_conn = get_redis_url()
        pprint("Connection to redis --> " + redis_conn)
        conn = await aioredis.create_connection(redis_conn, loop=asyncio.get_event_loop())
        fin = await conn.execute(cst.GET, cst.API_CONFIGURATION)
        # LOGGER.info(fin)
        ret = json.loads(fin)
    except Exception as e:
        LOGGER.error("Could not retrieve the stored configuration in Redis")
        raise e
    finally:
        if conn is not None:
            conn.close()
            await conn.wait_closed()
    # LOGGER.info(ret)
    return ret


async def get_file_content(cfg, name):
    contents = {}
    if cst.CSV_ROOT in cfg:
        root_folder = cfg.get(cst.CSV_ROOT)
        csv_file = f"{root_folder}/{name}.csv"
        if os.path.isfile(csv_file):
            return csv_file
    if cst.SQL_ROOT in cfg:
        root_folder = cfg.get(cst.SQL_ROOT)
        sql_file = f"{root_folder}/{name}.sql"
        if os.path.isfile(sql_file):
            async with aiofiles.open(sql_file) as f:
                contents = await f.read()
        else:
            LOGGER.error("File named %s does not exist", name)
    if name == "allocation_swisslife":
        return cfg['allocations']
    else:
        LOGGER.error("sql_root is not defined in configuration")
    return contents


async def get_key(needed_key: str) -> str:
    """
    .. function:: get_key(needed_key)
      :param needed_key: key that is the purpose of this search
      :rtype: str
      :returns: the string corresponding to the key specified
    Gets the specified key from memory store
    """
    ret = None
    conn = None
    try:
        redis_conn = get_redis_url()
        conn = await aioredis.create_connection(redis_conn, loop=asyncio.get_event_loop())
        ret = await conn.execute(cst.GET, needed_key)
        # LOGGER.info(ret)
    except Exception as e:
        LOGGER.error("Could not retrieve the specified key in Redis")
        raise e
    finally:
        if conn is not None:
            conn.close()
            await conn.wait_closed()
    return ret


async def store_key(key: str, value: str) -> None:
    """
    .. function:: store_key(key, value)
      :param key: The key as to who own the value
      :param value: The litteral value to store
    Store the value as specified key into redis cache
    """
    conn = None
    try:
        redis_conn = get_redis_url()
        conn = await aioredis.create_connection(redis_conn, loop=asyncio.get_event_loop())
        await conn.execute(cst.SET, key, value)
    except Exception as e:
        LOGGER.error("Could not store key in Redis")
        raise e
    finally:
        if conn is not None:
            conn.close()
            await conn.wait_closed()


async def get_asset_root() -> Dict[str, str]:
    """
    :return: the different assets paths to get sql and csv directories
    :rtype: dictionnary
    """
    dir = pathlib.Path(__file__).parent.parent
    dir = os.getenv('ASSET_DIRECTORY', dir)
    csv_root = str(pathlib.PurePath(dir, 'PredCrashData'))
    dict_cfg = {}
    dict_cfg["csv_root"] = csv_root

    return dict_cfg


def get_sentry_dsn(default_url: str = 'DEFAULT'):
    load_dotenv(find_dotenv())
    sentry_activated = os.getenv(cst.SENTRY_ACTIVATED, 'DEFAULT')
    return [os.getenv(cst.SENTRY_DSN, default_url), sentry_activated]


async def handle_error(user_context: dict = None, sentry_dsn: str = 'default'):
    """
    return an error with an additional context for the sentry
    :param sentry_dsn: url of the sentry
    :type sentry_dsn: str
    :param user_context: dict of the additional info
    :type user_context: dict
    :return: send error
    :rtype: send error
    """
    cfg = get_sentry_dsn()
    if sentry_dsn == 'default':
        sentry_dsn = cfg[0]
    if int(cfg[1]) == 1:
        client = Client(sentry_dsn)
        client.user_context(user_context)
        client.captureException()
    else:
        return False


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    f = loop.run_until_complete(get_asset_root())
    LOGGER.info(f)
    g = loop.run_until_complete(get_file_content(f, 'reset'))

    # LOGGER.info(g)
    #
