import bs4
import requests

import scraper


class TamoSession:
    def __init__(self, username: str, password: str, *, parser: str = "html.parser", check_incorrect_login: bool = True):
        self._parser = parser
        self._session = requests.Session()
        scraper.log_in(self._session, parser, username, password, check_incorrect_login)

    def tvarkarastis(self, savaite: str = None):
        """
        :param savaite: savaites pradzia formatu "YYYY-MM-DD"
        :return: [
                    {
                        "numeris": str,
                        "laikas": str,
                        "pavadinimas": str,
                        "mokytoja": str,
                        "pradzia": {
                            "h": int,
                            "n": int
                        },
                        "pabaiga": {
                            "h": int,
                            "m": int
                        }
                    }, ...
                ]
        """
        return scraper.tvarkarastis(self._session, self._parser, savaite)

    def dienynas(self, metai: int = None, menuo: int = None):
        """
        :return: [
                    {
                        "dalykas": str,
                        "pazymys": str,
                        "tipas": str,
                        "taisymo data": {
                            "m": int,
                            "d": int
                        },
                        "d": int,
                        "w": int
                    }, ...
                ]
        """
        return scraper.dienynas(self._session, self._parser, metai, menuo)

    def pamokos(self, metai: int = None, menuo: int = None):
        """
        :return: [
                    {
                        "dalykas": str,
                        "mokytojas": str,
                        "data": {
                            "m": int,
                            "d": int,
                            "w": int
                        },
                        "ivertinimas": str or None,
                        "tema": str or None,
                        "klases darbas": str or None,
                        "namu darbas": str or None
                    }, ...
                ]
        """
        return scraper.pamokos(self._session, self._parser, metai, menuo)

    def namu_darbai(self, nuo_data: str = None, iki_data: str = None, dalyko_id: int = 0):
        """

        :param nuo_data: formatas "YYYY-MM-DD"
        :param iki_data: formatas "YYYY-MM-DD"
        :param dalyko_id: 0 kad nefiltruotu, kiti skaiciai filterins, ne tas skaicius yra undefined behaviour
        :return: [
                    {
                        "pamokos data": {
                        "y": int,
                        "m": int,
                        "d": int
                        },
                        "ivede": {
                            "y": int,
                            "m": int,
                            "d": int,
                            "h": int,
                            "min": int
                        },
                        "namu darbas": "str",
                        "atlikimo data": {
                            "y": int,
                            "m": int,
                            "d": int,
                            "w": int
                        }
                    }, ...
                ]
        """
        return scraper.namu_darbai(self._session, self._parser, nuo_data, iki_data, dalyko_id)

    def atsiskaitomieji_darbai(self, metai: int = None, menuo: int = None):
        """
        :return: [
                    {
                        "response fields": {
                        "dalykas": str,
                        "grupe": str
                        "tipai": [str],
                        "pilni tipai": [str],
                        "data": {
                            "d": int
                        }
                    }, ...
                ]
        """
        return scraper.atsiskaitomieji_darbai(self._session, self._parser, metai, menuo)

    def pastabos(self):
        """
        :return: [
                    {
                        "tipas": str,
                        "tekstas": str,
                        "dalykas": str,
                        "mokytojas": str,
                        "pamokos data": {
                            "y": int,
                            "m": int,
                            "d": int
                        },
                        "irasymo diena": {
                            "y": int,
                            "m": int,
                            "d": int,
                            "h": int,
                            "min": int
                        }
                    }, ...
                ]
        """
        return scraper.pastabos(self._session, self._parser)

    def pusmeciai(self, pusmecio_id: int = None):
        """
        :param pusmecio_id: 0 -> metinis; 1 -> pirmas pusmetis; 2-> antras pusmetis;
        :return: {
                    "vidurkis": {
                        "pazymiu": float or None,
                        "vidurkiu": float or None,
                        "isvestu pazymiu": float or None
                    },
                    "dalykai": [
                        {
                            "dalykas": str,
                            "mokytojai: [str],
                            "pazymiai": [
                                {
                                    "ivertinimas": str,
                                    "data": {
                                        "y": int,
                                        "m": int,
                                        "d": int
                                    },
                                    "tipas": str
                                }
                            ],
                            "vidurkis": str or None,
                            "isvesta": str or None
                        }
                    ]
                }
        """
        return scraper.pusmeciai(self._session, self._parser, pusmecio_id)

    def close(self):
        self._session.close()
