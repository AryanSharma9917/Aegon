import re
import sys
import webbrowser

import inflect
import requests
import wolframalpha
import yaml
from geopy.distance import geodesic

from executors.word_match import word_match
from modules.audio import listener, speaker
from modules.conditions import keywords
from modules.exceptions import EgressErrors
from modules.logger.custom_logger import logger
from modules.models import models


def alpha(text: str) -> bool:
    """Uses wolfram alpha API to fetch results for uncategorized phrases heard.

    Args:
        text: Takes the voice recognized statement as argument.

    Notes:
        Handles broad ``Exception`` clause raised when Full Results API did not find an input parameter while parsing.

    Returns:
        bool:
        Boolean True if wolfram alpha API is unable to fetch consumable results.

    References:
        `Error 1000 <https://products.wolframalpha.com/show-steps-api/documentation/#:~:text=(Error%201000)>`__
    """
    if not models.env.wolfram_api_key:
        return False
    alpha_client = wolframalpha.Client(app_id=models.env.wolfram_api_key)
    try:
        res = alpha_client.query(text)
    except Exception:  # noqa
        return False
    if res['@success'] == 'false':
        return False
    else:
        try:
            response = next(res.results).text.splitlines()[0]
            response = re.sub(r'(([0-9]+) \|)', '', response).replace(' |', ':').strip()
            if response == '(no data available)':
                return False
            speaker.speak(text=response)
            return True
        except (StopIteration, AttributeError):
            return False


def google_maps(query: str) -> bool:
    """Uses google's places api to get places nearby or any particular destination.

    This function is triggered when the words in user's statement doesn't match with any predefined functions.

    Args:
        query: Takes the voice recognized statement as argument.

    Returns:
        bool:
        Boolean True if Google's maps API is unable to fetch consumable results.
    """
    if not models.env.maps_api:
        return False

    maps_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    try:
        response = requests.get(maps_url + 'query=' + query + '&key=' + models.env.maps_api)
    except EgressErrors as error:
        logger.error(error)
        return False
    collection = response.json()['results']
    required = []
    for element in range(len(collection)):
        try:
            required.append({
                "Name": collection[element]['name'],
                "Rating": collection[element]['rating'],
                "Location": collection[element]['geometry']['location'],
                "Address": re.search('(.*)Rd|(.*)Ave|(.*)St |(.*)St,|(.*)Blvd|(.*)Ct',
                                     collection[element]['formatted_address']).group().replace(',', '')
            })
        except (AttributeError, KeyError):
            pass
    if required:
        required = sorted(required, key=lambda sort: sort['Rating'], reverse=True)
    else:
        return False

    try:
        with open(models.fileio.location) as file:
            current_location = yaml.load(stream=file, Loader=yaml.FullLoader)
    except yaml.YAMLError as error:
        logger.error(error)
        return False

    results = len(required)
    speaker.speak(text=f"I found {results} results {models.env.title}!") if results != 1 else None
    start = current_location['latitude'], current_location['longitude']
    n = 0
    for item in required:
        item['Address'] = item['Address'].replace(' N ', ' North ').replace(' S ', ' South ').replace(' E ', ' East ') \
            .replace(' W ', ' West ').replace(' Rd', ' Road').replace(' St', ' Street').replace(' Ave', ' Avenue') \
            .replace(' Blvd', ' Boulevard').replace(' Ct', ' Court')
        latitude, longitude = item['Location']['lat'], item['Location']['lng']
        end = f"{latitude},{longitude}"
        far = round(geodesic(start, end).miles)
        miles = f'{far} miles' if far > 1 else f'{far} mile'
        n += 1
        if results == 1:
            option = 'only option I found is'
            next_val = f"Do you want to head there {models.env.title}?"
        elif n <= 2:
            option = f'{inflect.engine().ordinal(n)} option is'
            next_val = f"Do you want to head there {models.env.title}?"
        elif n <= 5:
            option = 'next option would be'
            next_val = "Would you like to try that?"
        else:
            option = 'other'
            next_val = 'How about that?'
        speaker.speak(text=f"The {option}, {item['Name']}, with {item['Rating']} rating, "
                           f"on{''.join([j for j in item['Address'] if not j.isdigit()])}, which is approximately "
                           f"{miles} away. {next_val}", run=True)
        sys.stdout.write(f"\r{item['Name']} -- {item['Rating']} -- "
                         f"{''.join([j for j in item['Address'] if not j.isdigit()])}")
        if converted := listener.listen():
            if 'exit' in converted or 'quit' in converted or 'Xzibit' in converted:
                break
            elif word_match(phrase=converted.lower(), match_list=keywords.keywords.ok):
                maps_url = f'https://www.google.com/maps/dir/{start}/{end}/'
                webbrowser.open(url=maps_url)
                speaker.speak(text=f"Directions on your screen {models.env.title}!")
                return True
            elif results == 1:
                return True
            elif n == results:
                speaker.speak(text=f"I've run out of options {models.env.title}!")
                return True
            else:
                continue
        else:
            return True
