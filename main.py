#!/usr/bin/env python

import configparser


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
            print(community.consumer_key)
            print(community.token)

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


nico_capture = NicoCapture()
nico_capture.start()
