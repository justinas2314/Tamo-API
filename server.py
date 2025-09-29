import time
import secrets
import string
import flask

from TamoAPI import TamoSession


app = flask.Flask(__name__)

ALPHABET = string.ascii_letters + string.digits
ONLINE_ACCOUNTS = dict()  # token: {last timestamp: last timestamp, session: session}
DOCS = {
    "log_in": {
        "request fields": {
            "username": "str username to log into your Tamo account",
            "password": "str password to log into your Tamo account"
        }, "response fields": None
    },
    "tvarkarastis": {
        "request fields": {
            "savaite": "str or null yyyy-mm-dd"
        }, "response fields": {
            "numeris": "str Nulinė/Pirma/Antra... ",
            "laikas": "str hh:mm - hh:mm",
            "dalykas": "str Fizika/Muzika...",
            "mokytojas": "str Vardenis Paverdenis",
            "pradzia": {
                "h": "int hours",
                "m": "int minutes"
            },
            "pabaiga": {
                "h": "int hours",
                "m": "int minutes"
            }
        }
    },
    "dienynas": {
        "request fields": {
            "metai": "int or null",
            "menuo": "int or null",
        }, "response fields": {
            "ivertinimai": {
                "dalykas": "str Matematika/Dorinis ugdymas (etika)/...",
                "ivertinimas": "str 10/9/įsk./...",
                "tipas": "str Klasės darbas/Kontrolinis darbas/...",
                "taisymo data": {
                    "m": "int month",
                    "d": "int day"
                }, "data": {
                    "d": "int day",
                    "w": "int weekday"
                }
            },
            "lankomumas": {
                "dalykas": "str Matematika/Dorinis ugdymas (etika)/...",
                "tipas": "str n/p",
                "data": {
                    "d": "int day",
                    "w": "int weekday"
                }

            }
        }
    },
    "pamokos": {
        "request fields": {
            "metai": "int or null",
            "menuo": "int or null",
            "mmid": "int or null",
        }, "response fields": {
            "dalykas": "str Fizika/Matematika/...",
            "mokytojas": "str Vardenis Paverdenis",
            "data": {
                "m": "int month",
                "d": "int day",
                "w": "int weekday"
            },
            "ivertinimas": "str or null",
            "tema": "str or null",
            "klases darbas": "str or null",
            "namu darbas": "str or null"
        }
    },
    "namu_darbai": {
        "request fields": {
            "nuo data": "str or null yyyy-mm-dd",
            "iki data": "str or null yyyy-mm-dd",
            "dalyko id": "int or null 0 is the default and does not filter anything",
            "datos metodas": "int 0 or 1 (0 sorts by due date, and is the default. 1 sorts by lesson date) when 0 w "
                             "in pamokos data will be null, when 1 w in atlikimo data will be null"
        }, "response fields": {
            "failai": [{
                "pavadinimas": "str",
                "url": "str self.session.get() to open it"
            }],
            "pamokos data": {
                "y": "int year",
                "m": "int month",
                "d": "int day",
                "w": "int or null weekday"
            }, "ivede": {
                "y": "int year",
                "m": "int month",
                "d": "int day",
                "h": "int hours",
                "min": "int minutes"
            }, "namu darbas": "str",
            "atlikimo data": {
                "y": "int year",
                "m": "int month",
                "d": "int day",
                "w": "int or null weekday"
            }
        }
    },
    "atsiskaitomieji_darbai": {
        "request fields": {
            "metai": "int or null",
            "menuo": "int or null",
            "mmid": "int or null"
        }, "response fields": {
            "dalykas": "str Fizika/Muzika/...",
            "grupe": "str 2c/2C programavimas/...",
            "tipai": [],
            "pilni tipai": [],
            "data": {
                "d": "int day"
            }
        }
    },
    "pastabos": {
        "request fields": None,
        "response fields": {
            "tipas": "str Komentaras/...",
            "tekstas": "str",
            "dalykas": "str Istorija/Fizika/...",
            "mokytojas": "str Vardenis Pavardenis/...",
            "pamokos data": {
                "y": "int year",
                "m": "int month",
                "d": "int day"
            }, "irasymo data": {
                "y": "int year",
                "m": "int month",
                "d": "int day",
                "h": "int hours",
                "min": "int minutes"
            }
        }
    },
    "pusmeciai": {
        "request fields": {
            "pusmecio id": "str or null; randamas url https://dienynas.tamo.lt/PeriodoVertinimas/MokinioVertinimai/X"
        }, "response fields": {
            "vidurkis": {
                "pazymiu": "float or null",
                "vidurkiu": "float or null",
                "isvestu pazymiu": "float or null"
            },
            "dalykai": [
                {
                    "dalykas": "str Biologija/Fizika/...",
                    "mokytojai": [],
                    "pazymiai": [
                        {
                            "ivertinimas": "str 10/9/įsk./...",
                            "data": {
                                "y": "int year",
                                "m": "int month",
                                "d": "int day"
                            },
                            "tipas": "str Kontrolinis darbas/Testas/..."
                        }
                    ]
                }
            ],

        }
    },
    "pranesimai": {
        "request fields": {
            "puslapis": "int or null",
            "id": "str or null output from /pranesimai\nif this is null 2 extra requests will be made"
        },
        "response fields": {
            "id": "str this can be passed to /pranesimai or /pranesimas to make 1 instead of 3 requests",
            "pranesimai": [
                {
                    "tema": "str",
                    "data": {
                        "y": "int year",
                        "m": "int month",
                        "d": "int day",
                        "h": "int hours",
                        "min": "int minutes",
                        "s": "int seconds"
                    },
                    "siuntejas": "str",
                    "siuntejo tipas": "str Mokinys/Mokyklos vadovybė/...",
                    "turi prisegtu files": "bool",
                    "id": "int this can be passed to /pranesimas",
                    "perskaitymo data (can be null)": {
                        "y": "int year",
                        "m": "int month",
                        "d": "int day",
                        "h": "int hours",
                        "min": "int minutes",
                        "s": "int seconds"
                    }
                }
            ]
        }
    },
    "pranesimas": {
        "request fields": {
            "pranesimo id": "int output from /pranesimai",
            "id": "str or null output from /pranesimai\nif this is null 2 extra requests will be made"
        },
        "response fields": {
            "html tekstas": "str",
            "tekstas": "str",
            "prisegti files": [
                {
                    "pavadinimas": "str",
                    "id": "str this can be passed to /file_url"
                }
            ]
        }
    },
    "file_url": {
        "request fields": {
            "file id": "str output from /pranesimas"
        },
        "response fields": {
            "url": "str"
        }
    },
    "proxy": {
        "request fields": {
            "args": "[Any] args to pass to session.get/session.post/...",
            "kwargs": "{key: value} to pass to session.get/session.post/..."
        },
        "response fields": {}
    }
}


def get_token():
    while True:
        token = ''.join(secrets.choice(ALPHABET) for _ in range(256))
        # is viso yra tiek variantu:
        # 711659926691456588820198688981513283237719214167524272940980007340737850071505550367426050190853744948955339987662427844810850852717191846883823768674280839119270574786535774460628640384757837267418932039347078114901615267344319690975277428929737916031623809028545597238524149983532303848529517503894555603085813572927495336324076794731576794044444062823255544802787912646756996122962654809395519130134923611540639384237080197541181260772381917961683956924416
        if token not in ONLINE_ACCOUNTS:
            return token


def get_user(key):
    try:
        return ONLINE_ACCOUNTS[key]["session"]
    except KeyError:
        return flask.abort(404, "User not found")


def clean_up(ctime):
    global ONLINE_ACCOUNTS
    data = dict()
    for i, j in ONLINE_ACCOUNTS.items():
        if ctime - j["last timestamp"] < 2400:  # 40 mins time limit
            data[i] = j
        else:
            j["session"].close()
    ONLINE_ACCOUNTS = data


@app.route("/", methods=["get"])
def docs():
    return """

<!DOCTYPE html>
<html>
<head>
    <title>Tamo API</title>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
</head>
<body>
    <p>Dokumentacija parašyta kiekviename puslapyje.
       Norint perskaityti dokumentacija reikia padaryti "get" request, o norint naudotis API - "post".</p>
    <p>Prieš naudojantis API reikia atidaryti Tamo Session "/log_in"</p>
    <p>"/log_in" session ištrinamas po 40 minučių</p>
    <p><b>Galimi naudoti puslapiai:</b></p>
    <ul>
      <li>/log_in</li>
      <li>/tvarkarastis</li>
      <li>/dienynas</li>
      <li>/pamokos</li>
      <li>/namu_darbai</li>
      <li>/atsiskaitomieji_darbai</li>
      <li>/pastabos</li>
      <li>/pusmeciai</li>
      <li>/pranesimai</li>
      <li>/pranesimas</li>
      <li>/file_url</li>
      <li>/proxy</li>
    </ul>
</body>
</html>
"""


@app.route('/log_in', methods=["post", "get"])
def log_in():
    ctime = time.time()
    clean_up(ctime)
    if flask.request.method == "GET":
        return DOCS["log_in"]
    data = flask.request.get_json(silent=True)
    if data is None:
        return flask.abort(400, "No json payload")
    username = data.get("username")
    password = data.get("password")
    if not all((username, password)):
        return flask.abort(400, "'username' or 'password' is not specified")
    token = get_token()
    try:
        ONLINE_ACCOUNTS[token] = {
            "last timestamp": ctime,
            "session": TamoSession(username, password)
        }
    except AssertionError:
        return flask.abort(401, "Incorrect Username/Password")
    resp = flask.make_response()
    resp.set_cookie("token", token)
    return resp


@app.route("/tvarkarastis", methods=["post", "get"])
def tvarkarastis():
    if flask.request.method == "GET":
        return DOCS["tvarkarastis"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    try:
        savaite = flask.request.get_json(silent=True).get("savaite")
    except AttributeError:
        savaite = None
    return flask.jsonify(user.tvarkarastis(savaite))


@app.route("/dienynas", methods=["post", "get"])
def dienynas():
    if flask.request.method == "GET":
        return DOCS["dienynas"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is not None:
        metai = json.get("metai")
        menuo = json.get("menuo")
    else:
        metai = menuo = None
    return flask.jsonify(user.dienynas(metai, menuo))


@app.route("/pamokos", methods=["post", "get"])
def pamokos():
    if flask.request.method == "GET":
        return DOCS["pamokos"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is not None:
        metai = json.get("metai")
        menuo = json.get("menuo")
        mmid = json.get("mmid")
    else:
        metai = menuo = mmid = None
    return flask.jsonify(user.pamokos(metai, menuo, mmid))


@app.route("/namu_darbai", methods=["post", "get"])
def namu_darbai():
    if flask.request.method == "GET":
        return DOCS["namu_darbai"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is not None:
        nuo_data = json.get("nuo data")
        iki_data = json.get("iki data")
        dalyko_id = json.get("dalyko id", 0)
        datos_metodas = json.get("datos metodas", 0)
    else:
        nuo_data = iki_data = dalyko_id = datos_metodas = None
    return flask.jsonify(user.namu_darbai(nuo_data, iki_data, dalyko_id, datos_metodas))


@app.route("/atsiskaitomieji_darbai", methods=["post", "get"])
def atsiskaitomieji_darbai():
    if flask.request.method == "GET":
        return DOCS["atsiskaitomieji_darbai"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is not None:
        metai = json.get("metai")
        menuo = json.get("menuo")
        mmid = json.get("mmid")
    else:
        metai = menuo = mmid = None
    return flask.jsonify(user.atsiskaitomieji_darbai(metai, menuo, mmid))


@app.route("/pastabos", methods=["post", "get"])
def pastabos():
    if flask.request.method == "GET":
        return DOCS["pastabos"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    return flask.jsonify(user.pastabos())


@app.route("/pusmeciai", methods=["post", "get"])
def pusmeciai():
    if flask.request.method == "GET":
        return DOCS["pusmeciai"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is not None:
        pusmecio_id = json.get("pusmecio id")
    else:
        pusmecio_id = None
    return flask.jsonify(user.pusmeciai(pusmecio_id))


@app.route("/pranesimai", methods=["post", "get"])
def pranesimai():
    if flask.request.method == "GET":
        return DOCS["pranesimai"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is not None:
        puslapis = json.get("puslapis", 1)
        token = json.get("id")
    else:
        token = None
        puslapis = 1
    return flask.jsonify(user.pranesimai(puslapis, token))


@app.route("/pranesimas", methods=["post", "get"])
def pranesimas():
    if flask.request.method == "GET":
        return DOCS["pranesimas"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is None:
        return flask.abort(400, "No json payload")
    try:
        pranesimo_id = json["pranesimo id"]
    except KeyError:
        return flask.abort(400, "'pranesimo id' is not specified")
    token = json.get("id")
    try:
        return flask.jsonify(user.pranesimas(pranesimo_id, token))
    except FileNotFoundError:
        return flask.abort(404, "Incorrect 'pranesimo id'")


@app.route("/file_url", methods=["post", "get"])
def file_url():
    if flask.request.method == "GET":
        return DOCS["file_url"]
    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is None:
        return flask.abort(400, "No json payload")
    try:
        file_id = json["file id"]
    except KeyError:
        return flask.abort(400, "'file id' is not specified")
    try:
        return flask.jsonify(user.file_url(file_id))
    except FileNotFoundError:
        return flask.abort(404, "Incorrect 'file id'")


@app.route("/proxy", methods=["get", "post"])
def proxy():
    if flask.request.method == "GET":
        return DOCS["proxy"]

    data = flask.request.cookies
    user = get_user(data.get("token"))
    json = flask.request.get_json(silent=True)
    if json is None:
        return flask.abort(400, "No json payload")
    args = json.get("args", [])
    kwargs = json.get("kwargs", dict())
    try:
        return user.proxy(*args, **kwargs)
    except FileNotFoundError:
        return flask.abort(400, "Something went wrong possibly with the json payload")


app.run()
