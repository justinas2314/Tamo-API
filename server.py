import time
import flask

from main import TamoSession


app = flask.Flask(__name__)

ONLINE_ACCOUNTS = dict()  # (username, password): {last timestamp: timestamp, session: session)
FAILED_LOGINS = dict()  # ip: {last timestamp: timestamp, count: count}
DOCS = {
    "log_in": {
        "request fields": {
            "username": "str username to log into your Tamo account, you will have to send this everywhere else",
            "password": "str password to log into your Tamo account, you will have to send this everywhere else"
        }, "response fields": None
    },
    "tvarkarastis": {
        "request fields": {
            "savaite": "str or null optionally specify which week to look at for example '2020-09-14'"
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
        }
    },
    "pamokos": {
        "request fields": {
            "metai": "int or null",
            "menuo": "int or null"
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
            "dalyko id": "int or null 0 is the default and does not filter anything"
        }, "response fields": {
            "pamokos data": {
                "y": "int year",
                "m": "int month",
                "d": "int day"
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
                "w": "int weekday"
            }
        }
    },
    "atsiskaitomieji_darbai": {
        "request fields": {
            "metai": "int",
            "menuo": "int"
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
            "pusmecio id": "str or null 0=metinis;1=pirmas pusmetis;2=antras pusmetis"
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
    }
}

def get_user(key):
    if not all(key):
        return flask.abort(400, "'username' or 'password' is not specified")
    elif key not in ONLINE_ACCOUNTS:
        return flask.abort(403, "Not registered")
    else:
        output = ONLINE_ACCOUNTS[key]
        ctime = time.time()
        if ctime - output["last timestamp"] < 1:
            return flask.abort(429, "Too many requests")
        else:
            ONLINE_ACCOUNTS[key]["last timestamp"] = ctime
            return output["session"]


def clean_up(ctime):
    global ONLINE_ACCOUNTS, FAILED_LOGINS
    data = dict()
    for i, j in ONLINE_ACCOUNTS.items():
        if ctime - j["last timestamp"] < 1800:  # 30 mins time limit
            data[i] = j
        else:
            j["session"].close()
    ONLINE_ACCOUNTS = data
    data = dict()
    for i, j in FAILED_LOGINS.items():
        if ctime - j["last timestamp"] < 86400:  # ban lasts for 24h
            data[i] = j
    FAILED_LOGINS = data



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
    <p>"/log_in" session ištrinamas po 30 minučių</p>
    <p>Vienas account gali daryti tik 1 request per sekundę, jei serveris pastebės, kad tarp dviejų requests
      buvo mažiau negu sekundės laiko tarpas, tai mes error.</p>
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
    </ul>
</body>
</html>
"""



@app.route('/log_in', methods=["post", "get"])
def log_in():
    ip = flask.request.remote_addr
    ctime = time.time()
    clean_up(ctime)
    if ip in FAILED_LOGINS and FAILED_LOGINS[ip]["counter"] > 10:
        FAILED_LOGINS[ip]["last timestamp"] = ctime
        return flask.abort(429, "This ip is banned for 24h\nToo many incorrect logins")
    if flask.request.method == "GET":
        return DOCS["log_in"]
    data = flask.request.get_json()
    if data is None:
        return flask.abort(400, "No json payload")
    username = data.get("username")
    password = data.get("password")
    if (username, password) in ONLINE_ACCOUNTS:
        flask.abort(403, "Already Registered with this username and password")
    if not all((username, password)):
        flask.abort(400, "'username' or 'password' is not specified")
    else:
        try:
            ONLINE_ACCOUNTS[(username, password)] = {
                "last timestamp": ctime,
                "session": TamoSession(username, password)
            }
        except AssertionError:
            try:
                FAILED_LOGINS[ip]["last timestamp"] = ctime
                FAILED_LOGINS[ip]["counter"] += 1
            except KeyError:
                FAILED_LOGINS[ip] = {
                    "last timestamp": ctime,
                    "counter": 1
                }
            return flask.abort(401, "Incorrect Username/Password")
        resp = flask.make_response()
        resp.set_cookie("username", username)
        resp.set_cookie("password", password)
        return resp  # success


@app.route("/tvarkarastis", methods=["post", "get"])
def tvarkarastis():
    if flask.request.method == "GET":
        return DOCS["tvarkarastis"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))
    savaite = flask.request.get_json().get("savaite")
    return flask.jsonify(user.tvarkarastis(savaite))


@app.route("/dienynas", methods=["post", "get"])
def dienynas():
    if flask.request.method == "GET":
        return DOCS["dienynas"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))
    json = flask.request.get_json()
    metai = json.get("metai")
    menuo = json.get("menuo")
    return flask.jsonify(user.dienynas(metai, menuo))


@app.route("/pamokos", methods=["post", "get"])
def pamokos():
    if flask.request.method == "GET":
        return DOCS["pamokos"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))
    json = flask.request.get_json()
    metai = json.get("metai")
    menuo = json.get("menuo")
    return flask.jsonify(user.pamokos(metai, menuo))


@app.route("/namu_darbai", methods=["post", "get"])
def namu_darbai():
    if flask.request.method == "GET":
        return DOCS["namu_darbai"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))
    json = flask.request.get_json()
    nuo_data = json.get("nuo data")
    iki_data = json.get("iki data")
    dalyko_id = json.get("dalyko id", 0)
    return flask.jsonify(user.namu_darbai(nuo_data, iki_data, dalyko_id))


@app.route("/atsiskaitomieji_darbai", methods=["post", "get"])
def atsiskaitomieji_darbai():
    if flask.request.method == "GET":
        return DOCS["atsiskaitomieji_darbai"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))
    json = flask.request.get_json()
    metai = json.get("metai")
    menuo = json.get("menuo")
    return flask.jsonify(user.atsiskaitomieji_darbai(metai, menuo))


@app.route("/pastabos", methods=["post", "get"])
def pastabos():
    if flask.request.method == "GET":
        return DOCS["pastabos"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))
    return flask.jsonify(user.pastabos())


@app.route("/pusmeciai", methods=["post", "get"])
def pusmeciai():
    if flask.request.method == "GET":
        return DOCS["pusmeciai"]
    data = flask.request.cookies
    if data is None:
        return flask.abort(400, "No json payload")
    user = get_user((data.get("username"), data.get("password")))

    pusmecio_id = flask.request.get_json().get("pusmecio id")
    return flask.jsonify(user.pusmeciai(pusmecio_id))


app.run()
