import re

import bs4

REGEX = list(map(re.compile,
                 [
                     "(..):(..)",
                     ".*, (.*?) [(](.*) (..)[)].*",
                     "(....)-(..)-(..)",
                     "(....)-(..)-(..) (..):(..)",
                     "(....)-(..)-(..), (.*)",
                     "Grupė: (.*?)Dalykas: (.*)",
                     "(.+)",
                     ".*(....)-(..)-(..).*<div>(.*)</div>",
                     "(....)-(..)-(..)T(..):(..):(..)"
                 ]))


def open_url(session, url, *args, **kwargs):
    with session.get(url, *args, **kwargs) as r:
        assert r.status_code == 200
        html = r.text
    return html


def post_req(session, url, *args, **kwargs):
    with session.post(url, *args, **kwargs) as r:
        assert r.status_code == 200
        html = r.text
    return html


def menuo1(raw):
    return {
        "sausio": 1,
        "vasario": 2,
        "kovo": 3,
        "balandžio": 4,
        "gegužės": 5,
        "birželio": 6,
        "liepos": 7,
        "rugpjūčio": 8,
        "rugsėjo": 9,
        "spalio": 10,
        "lapkričio": 11,
        "gruodžio": 12
    }[raw]


def menuo2(raw):
    return {
        "sausis": 1,
        "vasaris": 2,
        "kovas": 3,
        "balandis": 4,
        "gegužė": 5,
        "birželis": 6,
        "liepa": 7,
        "rugpjūtis": 8,
        "rugsėjis": 9,
        "spalis": 10,
        "lapkritis": 11,
        "gruodis": 12
    }[raw]


def tipas(raw):
    return {
        "L": "Laboratorinis darbas",
        "K": "Kontrolinis darbas",
        "D": "Diktantas",
        "A": "Atsiskaitymas",
        "S": "Savarankiškas darbas",
        "T": "Testas",
        "PR": "Projektinis darbas",
        "RA": "Rašinys",
        "PD": "Praktinis darbas",
        "TD": "Teorinis darbas"
    }[raw]


def savaites_diena(raw):
    return {
        "Pr": 1,
        "An": 2,
        "Tr": 3,
        "Kt": 4,
        "Pn": 5,
        "Št": 6,
        "Sk": 7
    }[raw]


def savaites_diena2(raw):
    return {
        "pirmadienis": 1,
        "antradienis": 2,
        "trečiadienis": 3,
        "ketvirtadienis": 4,
        "penktadienis": 5,
        "šeštadienis": 6,
        "sekmadienis": 7
    }[raw]


def get_date(junk, metodas):
    kazkokia_data = junk.find("label").text.replace("\n", "").strip()
    groups = REGEX[4].match(kazkokia_data).groups()
    if metodas == 0:
        date = {
            "y": int(groups[0]),
            "m": int(groups[1]),
            "d": int(groups[2]),
            "w": savaites_diena2(groups[3])
        }
    else:
        date = {
            "y": int(groups[0]),
            "m": int(groups[1]),
            "d": int(groups[2]),
            "w": savaites_diena2(groups[3])
        }
    return date


def get_info(junk):
    temp = {"dalykas": junk.find_next("div").text.strip()}
    for i in junk.find_all("label"):
        t, v = i.text.strip(), i.next.next.strip()
        match t:
            case "Pamokos data:":
                groups = REGEX[2].match(v).groups()
                temp["pamokos data"] = {
                    "y": int(groups[0]),
                    "m": int(groups[1]),
                    "d": int(groups[2]),
                    "w": None
                }
            case "Mokytojas(-a):":
                temp["mokytojas"] = v
            case "įvedė:":
                groups = REGEX[3].match(v).groups()
                temp["ivede"] = {
                    "y": int(groups[0]),
                    "m": int(groups[1]),
                    "d": int(groups[2]),
                    "h": int(groups[3]),
                    "min": int(groups[4])
                }
            case "Failai:":
                for a in i.parent.find_all("a"):
                    temp["failai"].append({
                        "pavadinimas": a.text.strip(),
                        "url": f"https://dienynas.tamo.lt{a.get('href')}"
                    })
            case "Atlikimo data:":
                groups = REGEX[2].match(v).groups()
                temp["atlikimo data"] = {
                    "y": int(groups[0]),
                    "m": int(groups[1]),
                    "d": int(groups[2]),
                    "w": None
                }
    return temp


def log_in(session, parser, username, password, check):
    data = dict()
    first_soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/Prisijungimas/Login"), parser)
    for i in first_soup.find_all("input"):
        key = i.get("id")
        if key is None:
            key = i.get("name")
        value = i.get("value")
        if key is not None and value is not None:
            data[key] = value
    data["UserName"] = username
    data["Password"] = password
    if check:
        soup = bs4.BeautifulSoup(post_req(session, "https://dienynas.tamo.lt/?clickMode=True", data=data), parser)
        if "Prisijungimas" in soup.find("title").text:
            raise AssertionError("Incorrect Login Info")
    else:
        post_req(session, "https://dienynas.tamo.lt/?clickMode=True", data=data)


def tvarkarastis(session, parser, savaite):
    url = ("https://dienynas.tamo.lt/TvarkarascioIrasas/MokinioTvarkarastis"
           if savaite is None else f"https://dienynas.tamo.lt/TvarkarascioIrasas/MokinioTvarkarastis?data={savaite}")
    soup = bs4.BeautifulSoup(open_url(session, url), parser)
    data = []
    for i in soup.find_all("table", class_="full_width form-horizontal table table-hover table-responsive"):
        temp = []
        for j in i.find_all("tr")[1:]:
            temper = dict(zip(("numeris", "laikas", "pabaiga", "dalykas", "mokytojas"),
                              map(lambda x: x.text.strip(), j.find_all("td"))))
            try:
                grupes = REGEX[0].match(temper["laikas"]).groups()
            # jei pagavom mitini "Pamoku nera"
            except KeyError:
                continue
            temper["pradzia"] = {
                "h": int(grupes[0]),
                "m": int(grupes[1])
            }
            temper["laikas"] += " - " + temper["pabaiga"]
            grupes = REGEX[0].match(temper["pabaiga"]).groups()
            temper["pabaiga"] = {
                "h": int(grupes[0]),
                "m": int(grupes[1])
            }
            temp.append(temper)
        data.append(temp)
    return data


def dienynas(session, parser, metai, menuo):
    if metai is not None and menuo is not None:
        soup = bs4.BeautifulSoup(post_req(
            session, "https://dienynas.tamo.lt/Pamoka/MokinioDienynasTable", data={
                "metai": str(metai),
                "menuo": str(menuo)
            }), parser)
    else:
        soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/Pamoka/MokinioDienynas"), parser)
    stripped_page = soup.find_all(class_="dienynas")[1]
    day = savaites_diena(stripped_page.find("div").text.strip())

    lankomumai = []
    ivertinimai = []
    for i in stripped_page.find_all("tr")[1:]:
        dalykas = i.find("td").text.replace("\n", "").strip()
        for index, j in enumerate(i.find_all("td")[1:]):
            try:
                groups = REGEX[1].match(j["data-original-title"]).groups()
                ivertinimas = j.text.strip()
                if "\n" in ivertinimas:
                    ivertinimas, lankomumas = ivertinimas.split("\n")
                    lankomumai.append({"dalykas": dalykas,
                                       "tipas": lankomumas,
                                       "data": {
                                           "d": index + 1,
                                           "w": (index + day) % 7 if (index + day) % 7 else 7
                                       }})
                ivertinimai.append({"dalykas": dalykas,
                                    "ivertinimas": ivertinimas,
                                    "tipas": groups[0],
                                    "taisymo data": {
                                        "m": menuo1(groups[1]),
                                        "d": int(groups[2])
                                    },
                                    "data": {
                                        "d": index + 1,
                                        "w": (index + day) % 7 if (index + day) % 7 else 7
                                    }})
            except AttributeError:
                lankomumai.append({"dalykas": dalykas,
                                   "tipas": j.text.strip(),
                                   "data": {
                                       "d": index + 1,
                                       "w": (index + day) % 7 if (index + day) % 7 else 7
                                   }})
            except KeyError:
                pass
    return {"ivertinimai": ivertinimai, "lankomumas": lankomumai}


def pamokos(session, parser, metai, menesis, mmid):
    if mmid is not None:
        url = f"https://dienynas.tamo.lt/Pamoka/MokinioPamokuPartial?moksloMetuMenesiaiId={mmid}&krautiVisaMenesi=True"
    elif metai is not None and menesis is not None:
        mmid = (metai - 2014) * 12 + menesis + 5
        url = f"https://dienynas.tamo.lt/Pamoka/MokinioPamokuPartial?moksloMetuMenesiaiId={mmid}&krautiVisaMenesi=True"
    else:
        # have to make an extra request if metai and menesis are not specified
        soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/Pamoka/Sarasas"), parser)
        for i in reversed(soup.find_all("a")):
            if "Daugiau" in i.text:
                url = "https://dienynas.tamo.lt" + i["href"]
                break
    soup = bs4.BeautifulSoup(post_req(session, url), parser)
    data = []
    for i in soup.find_all(class_="row", recursive=False):
        raw_menuo, raw_diena, raw_sav = i.find_all(class_="f-header")[1:4]
        for j in i.find_all("div", recursive=False)[1].find_all(class_="row", recursive=False):
            div = j.find("div", recursive=False)
            dalykas = div.find(class_="f-header").text
            mokytojas = div.find("label").next.next.strip()
            temp = {
                "dalykas": dalykas,
                "mokytojas": mokytojas,
                "data": {
                    "m": menuo2(raw_menuo.text.strip()),
                    "d": int(raw_diena.text),
                    "w": savaites_diena(raw_sav.text.strip())
                },
                "ivertinimas": None,
                "tema": None,
                "klases darbas": None,
                "namu darbas": None
            }
            for k in div.find_all("label")[1:]:
                string = k.text.strip()
                if string == "Įvertinimas:":
                    string = "pazymys"
                elif string == "Tema:":
                    string = "tema"
                elif string == "Namų darbas:":
                    string = "namu darbas"
                elif string == "Klasės darbas:":
                    string = "klases darbas"
                temp[string] = k.findNext("div").text.strip()
            data.append(temp)
    return data


def namu_darbai(session, parser, nuo_data, iki_data, dalyko_id, metodas):
    if nuo_data is None or iki_data is None:
        soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/Darbai/NamuDarbai"), parser)
    else:
        soup = bs4.BeautifulSoup(post_req(session, "https://dienynas.tamo.lt/Darbai/NamuDarbai",
                                          data={
                                              "DateFilterMode": metodas,
                                              "DataNuo": nuo_data,
                                              "DataIki": iki_data,
                                              "DalykoId": str(dalyko_id)}), parser)
    data = []
    soup = soup.find("div", class_="namu_darbai_content")
    for i in soup.find_all("div"):
        try:
            classes = i["class"]
        except KeyError:
            continue
        if "col-md-10" in classes:
            current_date = get_date(i, 0)
        elif "col-md-13" in classes:
            temp = get_info(i)
            if len(temp) == 1 and len(temp["dalykas"]) > 0:
                entry = {"namu darbas": temp["dalykas"]}
                entry |= current_info
                entry["atlikimo data" if metodas == 0 else "pamokos data"] = current_date
                data.append(entry)
            else:
                current_info = temp
    return data


def atsiskaitomieji_darbai(session, parser, metai, menesis, mmid):
    if mmid is not None:
        soup = bs4.BeautifulSoup(
            open_url(session,
                     f"https://dienynas.tamo.lt/Darbai/Atsiskaitymai?MoksloMetuMenesioId={mmid}"), parser)
    elif metai is not None and menesis is not None:
        soup = bs4.BeautifulSoup(
            open_url(session,
                     f"https://dienynas.tamo.lt/Darbai/Atsiskaitymai"
                     # atrodo jie sita formule pakeicia kasmet wtf plz visi naudokit mmid
                     f"?MoksloMetuMenesioId={(metai - 2014) * 12 + menesis + 5}"), parser)
    else:
        soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/Darbai/Atsiskaitymai"), parser)
    data = []
    for i in soup.find_all("tr")[1:]:
        groups = REGEX[5].match(i.find("td").text.replace("\n", "").strip()).groups()
        for index, j in enumerate(i.find_all("td")[1:]):
            t = REGEX[6].findall(j.text.strip())
            if len(t):
                data.append({"dalykas": groups[1],
                             "grupe": groups[0],
                             "tipai": t,
                             "pilni tipai": list(map(tipas, t)),
                             "data": {
                                 "d": index + 1,
                             }})
    return data


def pastabos(session, parser):
    soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/Pastabos/Mokiniams"), parser)
    data = []
    names = ["tipas", "tekstas", "dalykas", "mokytojas"]
    for i in soup.find(class_="records").find_all(class_="row"):
        temp = dict()
        index = 0
        divs = i.find_all("div", recursive=False)[1:]
        if not len(divs):
            continue
        for j in divs[:2]:
            for k in j.find_all("div"):
                temp[names[index]] = k.text.strip()
                index += 1
        first_date, second_date = divs[2].find_all("div")
        first_group = REGEX[2].match(first_date.text.strip()).groups()
        temp["pamokos data"] = {
            "y": int(first_group[0]),
            "m": int(first_group[1]),
            "d": int(first_group[2])
        }
        second_group = REGEX[3].match(second_date.text.strip()).groups()
        temp["irasymo data"] = {
            "y": int(second_group[0]),
            "m": int(second_group[1]),
            "d": int(second_group[2]),
            "h": int(second_group[3]),
            "min": int(second_group[4])
        }
        data.append(temp)
    return data


def pusmeciai0(session, parser):
    soup = bs4.BeautifulSoup(open_url(session, "https://dienynas.tamo.lt/PeriodoVertinimas/MokinioVertinimai/0"),
                             parser)
    data = {}
    rows = soup.find("table", class_="c_main_table wrap_text c_block").find_all("tr")[2:]
    _, pazymiu, vidurkiu, pagr_isvestu, pap_isvestu = rows[-1].find_all("td")
    isvestu_text = max(pagr_isvestu.text.strip(), pap_isvestu.text.strip(), key=len)
    data["vidurkis"] = dict()
    try:
        data["vidurkis"]["pazymiu"] = float(pazymiu.text.strip().replace(",", "."))
    except ValueError:
        data["vidurkis"]["pazymiu"] = None
    try:
        data["vidurkis"]["vidurkiu"] = float(vidurkiu.text.strip().replace(",", "."))
    except ValueError:
        data["vidurkis"]["vidurkiu"] = None
    try:
        data["vidurkis"]["isvestu pazymiu"] = float(isvestu_text.replace(",", "."))
    except ValueError:
        data["vidurkis"]["isvestu pazymiu"] = None
    dalykai = []
    for i in rows[:-1]:
        tds = i.find_all("td")
        dalykas, *mokytojai = tds[0].find_all("div")
        pirmas = tds[1].text.strip().replace(",", ".")
        antras = tds[2].text.strip().replace(",", ".")
        metinis = tds[3].text.strip().replace(",", ".")
        if len(pirmas) == 0:
            pirmas = None
        if len(antras) == 0:
            antras = None
        if len(metinis) == 0:
            metinis = None
        temp = {
            "dalykas": dalykas.text.strip(),
            "mokytojai": list(map(lambda x: x.text.strip(), mokytojai)),
            "pirmo pusmecio pazymys": pirmas,
            "antro pusmecio pazymys": antras,
            "metinis pazymys": metinis
        }
        dalykai.append(temp)
    data["dalykai"] = dalykai
    return data


def pusmeciai(session, parser, pusmecio_id):
    if pusmecio_id == 0:
        return pusmeciai0(session, parser)
    if pusmecio_id is None:
        soup = bs4.BeautifulSoup(
            open_url(session, "https://dienynas.tamo.lt/PeriodoVertinimas/MokinioVertinimai"), parser)
    else:
        soup = bs4.BeautifulSoup(
            open_url(session, f"https://dienynas.tamo.lt/PeriodoVertinimas/MokinioVertinimai/{pusmecio_id}"), parser)
    data = dict()
    rows = soup.find(id="c_main").find("table").find_all("tr")[1:]
    _, pazymiu, vidurkiu, isvestu, *_ = rows[-1].find_all("td")
    data["vidurkis"] = dict()
    try:
        data["vidurkis"]["pazymiu"] = float(pazymiu.text.strip().replace(",", "."))
    except ValueError:
        data["vidurkis"]["pazymiu"] = None
    try:
        data["vidurkis"]["vidurkiu"] = float(vidurkiu.text.strip().replace(",", "."))
    except ValueError:
        data["vidurkis"]["vidurkiu"] = None
    try:
        data["vidurkis"]["isvestu pazymiu"] = float(isvestu.text.strip().replace(",", "."))
    except ValueError:
        data["vidurkis"]["isvestu pazymiu"] = None
    dalykai = []
    for i in rows[:-1]:
        tds = i.find_all("td")
        dalykas, *mokytojai = tds[0].find_all("div")
        pazymiai = []
        for j in tds[1].find_all("div"):
            groups = REGEX[7].match(j.get("data-original-title")).groups()
            pazymiai.append({
                "ivertinimas": j.text.strip(),
                "data": {
                    "y": int(groups[0]),
                    "m": int(groups[1]),
                    "d": int(groups[2])
                },
                "tipas": groups[3]
            })
        vidurkis = tds[2].text.strip().replace(",", ".")
        isvesta = tds[3].text.strip().replace(",", ".")
        if len(vidurkis) == 0:
            vidurkis = None
        if len(isvesta) == 0:
            isvesta = None
        temp = {
            "dalykas": dalykas.text.strip(),
            "mokytojai": list(map(lambda x: x.text.strip(), mokytojai)),
            "pazymiai": pazymiai,
            "vidurkis": vidurkis,
            "isvesta": isvesta
        }
        dalykai.append(temp)
    data["dalykai"] = dalykai
    return data


def pranesimai(session, page, identification):
    # 2 more requests if identification is None
    if identification is None:
        open_url(session, "https://dienynas.tamo.lt/GoTo/Bendrauk")
        with session.get("https://api.tamo.lt/messaging/core/roles",
                         headers={"Accept": "application/json"}) as r:
            assert r.status_code == 200
            identification = r.json()["items"][0]["id"]
    with session.get(f"https://api.tamo.lt/messaging/messages/received?orderDescending=true&searchTerm=&page={page}",
                     headers={"Accept": "application/json", "x-selected-role": identification}) as r:
        assert r.status_code == 200
        raw_data = r.json()
    data = []
    for i in raw_data["items"]:
        first_groups = REGEX[8].match(i["date"]).groups()
        temp = {
            "tema": i["subject"],
            "data": {
                "y": int(first_groups[0]),
                "m": int(first_groups[1]),
                "d": int(first_groups[2]),
                "h": int(first_groups[3]),
                "min": int(first_groups[4]),
                "s": int(first_groups[5])
            },
            "siuntejas": i["senderPerson"],
            "siuntejo tipas": i["senderPersonTitle"],
            "turi prisegtu files": i["hasAttachments"],
            "id": i["id"]
        }
        try:
            second_groups = REGEX[8].match(i["readDate"]).groups()
        except KeyError:
            temp["perskaitymo data"] = None
        else:
            temp["perskaitymo data"] = {
                "y": int(second_groups[0]),
                "m": int(second_groups[1]),
                "d": int(second_groups[2]),
                "h": int(second_groups[3]),
                "min": int(second_groups[4]),
                "s": int(second_groups[5])
            }
        data.append(temp)
    return {"id": identification, "pranesimai": data}


def pranesimas(session, message_id, identification):
    if identification is None:
        open_url(session, "https://dienynas.tamo.lt/GoTo/Bendrauk")
        with session.get("https://api.tamo.lt/messaging/core/roles",
                         headers={"Accept": "application/json"}) as r:
            assert r.status_code == 200
            identification = r.json()["items"][0]["id"]
    with session.get(f"https://api.tamo.lt/messaging/messages/received/{message_id}",
                     headers={"Accept": "application/json", "x-selected-role": identification}) as r:
        assert r.status_code == 200
        raw_data = r.json()
    try:
        data = {
            "html tekstas": raw_data["item"]["body"],
            "tekstas": raw_data["item"]["bodyPlain"]
        }
    except KeyError:
        raise FileNotFoundError  # incorrect message_id
    attachments = []
    for i in raw_data["attachments"]:
        attachments.append({
            "pavadinimas": i["name"],
            "id": i["sid"]
        })
    data["prisegti files"] = attachments
    return data


def file_url(session, file_id):
    with session.post("https://api.tamo.lt/files/filedownloadurl",
                      headers={"Content-Type": "application/json"},
                      json={"fileSid": file_id}) as r:
        if r.status_code == 404:
            raise FileNotFoundError
        assert r.status_code == 200
        return r.json()


def proxy(session, method="get", *args, **kwargs):
    with getattr(session, method)(*args, **kwargs) as r:
        return r.content
