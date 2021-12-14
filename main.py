#!/usr/bin/env python

import configparser
import json

import requests
from bs4 import BeautifulSoup

LIVE_BASE_URL = "https://live.nicovideo.jp/watch/"


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
        print(self.communities)
        for community in self.communities:
            print(community.community)
            print(self.fetch_live_thumbnail(community.community))

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
        print(program_status)

        meta_image = soup.select_one("meta[property=\"og:image\"]")
        if meta_image is None:
            return None
        return meta_image["content"]


nico_capture = NicoCapture()
nico_capture.start()
