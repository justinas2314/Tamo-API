import aiohttp
import scraper


class TamoSession:
    """
    Tamo paskyra atjungia po tam tikro laiko tarpo ir šis API nežino kada tai įvyks, tai jeigu
    kažkas nesigauna galima bandyti per naują prisijungti su nauju TamoSession()
    """
    @classmethod
    async def create(cls, username: str, password: str, *, parser: str = "html.parser", check_incorrect_login: bool = True):
        tamo_session = TamoSession()
        tamo_session._parser = parser
        tamo_session.session = aiohttp.ClientSession()
        await scraper.log_in(tamo_session.session, parser, username, password, check_incorrect_login)
        return tamo_session

    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    async def __aenter__(self):
        self._instance = await self.create(*self.__args, **self.__kwargs)
        return self._instance

    async def __aexit__(self, *_):
        await self._instance.close()

    async def tvarkarastis(self, savaite: str = None):
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
        return await scraper.tvarkarastis(self.session, self._parser, savaite)

    async def dienynas(self, metai: int = None, menuo: int = None):
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
        return await scraper.dienynas(self.session, self._parser, metai, menuo)

    async def pamokos(self, metai: int = None, menuo: int = None):
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
        return await scraper.pamokos(self.session, self._parser, metai, menuo)

    async def namu_darbai(self, nuo_data: str = None, iki_data: str = None, dalyko_id: int = 0):
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
        return await scraper.namu_darbai(self.session, self._parser, nuo_data, iki_data, dalyko_id)

    async def atsiskaitomieji_darbai(self, metai: int = None, menuo: int = None):
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
        return await scraper.atsiskaitomieji_darbai(self.session, self._parser, metai, menuo)

    async def pastabos(self):
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
        return await scraper.pastabos(self.session, self._parser)

    async def pusmeciai(self, pusmecio_id: int = None):
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
                        }, ...
                    ]
                }
        """
        return await scraper.pusmeciai(self.session, self._parser, pusmecio_id)

    async def pranesimai(self, puslapis: int = 1, identification: str = None):
        """
        :param identification: str tokenas, kuri reiktu issaugoti jeigu norima
            naudotis pranesimai ar pranesimas antra karta
        :return: {
                    "id": str,  # identification parametras
                    "pranesimai": [
                        {
                            "tema": str,
                            "data": {
                                "y": int,
                                "m": int,
                                "d": int,
                                "h": int,
                                "min": int,
                                "s": int
                            },
                            "siuntejas": str,
                            "siuntejo tipas": str,
                            "turi prisegtu files": bool,
                            "id": int,  # parametras funkcijai pranesimas()
                            "perskaitymo data": None or {
                                "y": int,
                                "m": int,
                                "d": int,
                                "h": int,
                                "min": int,
                                "s": int
                            }
                        }, ...
                    ]
                }
        """
        return await scraper.pranesimai(self.session, puslapis, identification)

    async def pranesimas(self, pranesimo_id: int, identification: str = None):
        """
        :param message_id: int gaunamas funkcijoje pranesimai()
        :param identification: str tokenas gaunamas funkcijoje pranesimai(), jeigu None bus gautas naujas
        :return: {
                    "html tekstas": str,
                    "tekstas": str,
                    "prisegti files": [
                        {
                            "pavadinimas": str,
                            "id": str  # parametras funkcijai file_url()
                        }, ...
                    ]
                }
        """
        return await scraper.pranesimas(self.session, pranesimo_id, identification)

    async def file_url(self, file_id: str):
        """
        :param file_id: gaunamas funkcijoj pranesimas()
        :return: {
                    "url": str  # url parsisiusti file
                }
        """
        return await scraper.file_url(self.session, file_id)

    async def proxy(self, method="get", *args, **kwargs):
        """
        Can be used to download files from namu_darbai()
        :param method: get, post, patch, ...
        :return: content from a request
        """
        return await scraper.proxy(self.session, method.lower(), *args, **kwargs)

    async def close(self):
        await self.session.close()
