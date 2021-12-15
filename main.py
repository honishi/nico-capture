#!/usr/bin/env python

import configparser
import datetime
import json
import os
import time
import uuid

from bs4 import BeautifulSoup
import requests
import tweepy

LIVE_BASE_URL = "https://live.nicovideo.jp/watch/"
IMAGE_FETCH_INTERVAL_SEC = 3


class Community:
    def __init__(self, community, consumer_key, consumer_secret, token, token_secret):
        self.community = community
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret


class NicoCapture:
    def __init__(self):
        self.communities = self.read_communities()
        pass

    def start(self):
        # print(self.communities)
        for community in self.communities:
            print(f"*** {datetime.datetime.now()}")
            print(f"{community.community}")
            filenames = []
            max_image_count = 4
            for count in range(max_image_count):
                if count > 0:
                    print(f"sleeping... {count}/{max_image_count - 1}")
                    time.sleep(IMAGE_FETCH_INTERVAL_SEC)
                image_url = NicoCapture.fetch_live_thumbnail(community.community)
                if image_url is None:
                    break
                filename = NicoCapture.save_image(image_url)
                filenames.append(filename)
                print(f"fetched: {filename}")
            if len(filenames) == 0:
                print("no images fetched.")
                break
            api = NicoCapture.tweepy_api(community)
            NicoCapture.tweet_images(api, filenames)
            NicoCapture.remove_files(filenames)

    @staticmethod
    def read_communities():
        config = configparser.ConfigParser()
        config.read('settings.ini')
        communities = []
        for community in config.sections():
            communities.append(
                Community(
                    community,
                    config.get(community, "consumer_key"),
                    config.get(community, "consumer_secret"),
                    config.get(community, "token"),
                    config.get(community, "token_secret")
                )
            )
        return communities

    @staticmethod
    def fetch_live_thumbnail(community):
        response = requests.get(LIVE_BASE_URL + community)
        soup = BeautifulSoup(response.text, 'html.parser')

        script_embedded_data = soup.select_one("script[id=\"embedded-data\"]")
        if script_embedded_data is None:
            return None
        data_props = script_embedded_data["data-props"]
        if data_props is None:
            return None
        data_props_json = json.loads(data_props)
        program_status = data_props_json["program"]["status"]
        # print(program_status)
        if program_status != "ON_AIR":
            return None
        meta_image = soup.select_one("meta[property=\"og:image\"]")
        if meta_image is None:
            return None
        return meta_image["content"]

    @staticmethod
    def save_image(url):
        filename = str(uuid.uuid1())[:8] + ".jpg"
        response = requests.get(url)
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
        return filename

    @staticmethod
    def tweet_images(api, filenames):
        media_ids = []
        for filename in filenames:
            response = api.media_upload(filename)
            print(response)
            media_ids.append(response.media_id_string)
        api.update_status("", media_ids=media_ids)

    @staticmethod
    def tweepy_api(community):
        auth = tweepy.OAuthHandler(community.consumer_key, community.consumer_secret)
        auth.set_access_token(community.token, community.token_secret)
        return tweepy.API(auth)

    @staticmethod
    def remove_files(filenames):
        for filename in filenames:
            os.remove(filename)


nico_capture = NicoCapture()
nico_capture.start()
