# standard
from datetime import datetime, timedelta

# installed
import os
import aiohttp
import xml.etree.ElementTree as ElTree
from logzero import logger as LOGGER
import json
import requests
# import xml.etree.ElementTree.Element as Element
import asyncio
import predcrash_connect.open_data_gouv.constants as cst
import json
from predcrash_utils.commons import get_asset_root
import re

async def exec_http_request(url: str, params: dict=None, need_api: bool = False) -> str:
    """
    Execute an http request on url, using GET params, and return HTTP response.
    (This function could be used for non-SIX purpose)
    :param url: string: in six module it's always cst.SIX_URL constant
    :param params: dictionary: {"GET_param1_name": "GET_param1_value", "GET_param2_name": "GET_param2_value", ...}
    :param need_token: Must be True if the request needs a token
    :return: string containing response text, SIX should return an XML document.
    """
    if need_api:
        params['API-KEY'] = cst.API_KEY

    async with aiohttp.ClientSession() as session:
        #LOGGER.info([url, params])
        async with session.get(url, params=params) as response:
            res = await response.text()

    # If the request failed because the token was invalid, we go check our token against the one on the server.
    # LOGGER.info(res)
    return res

async def get_all_url_to_download(url_chunk:str):
    json_result = await exec_http_request(cst.API_DATA_GOUV+url_chunk)
    dict_good = json.loads(json_result)
    data_needed = dict_good['resources']
    list_url = []
    for i in data_needed:
        list_url.append(i['extras']['check:url'])
    return list_url

async def download_file(url:str, file_name:str):
    cfg = await get_asset_root()
    directory_file = os.path.join(cfg['download_root'], file_name)
    if not os.path.isfile(directory_file+'.zip'):
        response = requests.get(url)
        assert response.status_code == 200
        # For large files use response.content.read(chunk_size) instead.
        g = response.content
        extension = response.headers['content-type']
        if '/' in extension :
            start_index = extension.find('/')
            extension = extension[start_index+1:]
        with open(f"{directory_file}.{extension}", "wb") as f:
            f.write(g)
    return url

def name_from_url(url:str):
    l = re.findall('net/.+?.zip', url)

    return l[0][4:-4]

async def main():
    list_url = await get_all_url_to_download('/datasets/carte-des-departements-2/')
    timeout = aiohttp.ClientTimeout(total=600)
    for url in list_url:
        try:
            name = name_from_url(url)
            await download_file(url, name)
            LOGGER.info(name)
        except Exception as e:
            LOGGER.info(e)
            LOGGER.info(name)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())