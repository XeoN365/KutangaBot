import json
import os


class CardAgainstHumanity:
    def __init__(self):
        self.data = self._load_file(os.path.join(os.getcwd(), "data\\cards.json"))
        self.packs = self._load_packs()

    def _load_file(self, filename: str) -> dict:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        return data

    def _load_packs(self) -> list:
        packs = []
        for pack in self.data:
            packs.append(pack["name"])
        return packs

    def get_packs(self) -> list:
        return self.packs

    def _get_white_cards(self, pack_name: str) -> list:
        get_pack = [pack for pack in self.data if pack["name"] == pack_name]
        if get_pack:
            raw_white = get_pack[0]["white"]
            white = [card["text"] for card in raw_white]
            return white
        else:
            return []

    def _get_black_cards(self, pack_name: str) -> list:
        get_pack = [pack for pack in self.data if pack["name"] == pack_name]
        if get_pack:
            raw_black = get_pack[0]["black"]
            black = [card["text"] for card in raw_black]
            return black
        else:
            return []

    def get_cards(self, pack_name: str) -> list:
        white_cards = self._get_white_cards(pack_name)
        black_cards = self._get_black_cards(pack_name)
        return {"white": white_cards, "black": black_cards}
