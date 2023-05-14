# Tamo-API
Tamo.lt scraper that acts as an unofficial API  
## Perspėjimai
Norint naudoti API reikia duoti script/server savo prisijungimo duomenis, o tai įprastai yra bloga idėja, tai prašau įsitikinti, kad šis API nieko blogo nedarys.  
Tamo priverčia po tam tikro laiko tarpo atsijungti, šis API to neatpažins, todėl reikės pasinaudot smegenim ir kas 30-60 min susikurti naują login session.  
Šis API nėra oficialus, jei tamo.lt nuspręstų pakeisti savo puslapį, tai šis API nustotų veikti iki kol aš jį atnaujinčiau, todėl šis API neturėtų būti naudojamas labai rimtuose projektuose.  
Šis API pagrinde daro tą patį, ką darytų žmogus naršyklėje tik greičiau ir efektyviau. Jeigu Tamo atpažintų, kad tai nėra naršyklė, o web scraper, tai kaltininko paskyra galėtų sulaukti **ban**. Testuojant šį API savo paskyroje, ban negavau, tai bent kol kas nemanau, kad Tamo tai tikrina, tačiau tas galėtų pasikeisti bet kurią akimirką. Kad būtų mažesnė tikimybė gauti ban tarp requests reiktų padaryti kelių sekundžių pauzę.
## Kaip naudotis?
Kaip API naudojimosi pavyzdį galima paskaityti `server.py`  
Susiinstaliuoti [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) ir, priklausomai nuo pasirinktos versijos, arba [requests](https://pypi.org/project/requests/), arba [aiohttp](https://pypi.org/project/aiohttp/).  
`main.py` turėtu būti importuojamas norint naudoti šį API python script.  
`server.py` turėtu būti naudojamas norint turėti serveri (turbut `http://127.0.0.1:5000/`), kuriuo galima naudotis ir su kitomis programavimo kalbomis. Reikia turėti [flask](https://pypi.org/project/Flask/).  
`scraper.py` neturėtu būti importuojamas, tai duobė į kurią aš sumečiau visą script logiką. Vietoj `scraper.py` reiktų naudoti `main.py`, nes `main.py` yra wrapper aplink `scraper.py`.  
`async` folder yra `main.py` ir `scraper.py` asinchroninės versijos, kurios veikia beveik visiškai taip pat.   
Kaip naudotis `main.py` galima sužinoti atsidarius `main.py`, o `server.py` atsidarius serverio link (turbut `http://127.0.0.1:5000/`). `main.py`, kaip ir `server.py`, grąžina dict ir list populiuotus primityviais tipais, visos funkcijos (jų priimami ir grąžinami parametrai) yra tokios pačios.  
## Ką galima su šitu API padaryti?
Šis API atlieka funkcijas, kurias gali atlikti bet kuris mokinys (neturiu nei premium mokinio, nei mokytojo paskyros, tai nežinau kaip tai veiktų).  
Šis API negali padaryti 100% to ką gali padaryti tamo.lt svetainė, tačiau gali padaryti pakankamai, kad būtų naudingas tikrinant pažymius/vidurkius/pastabas/pranešimus ir pan.  
Šis API gali nuscrapinti šiuos tamo.lt puslapius:
* Tvarkaraštis (tvarkarastis)
* Dienynas (dienynas)
* Pamokos (pamokos)
* Namų darbai (namu_darbai)
* Atsiskaitomieji darbai (atsiskaitomieji_darbai)
* Pagyrimai/ Pastabos (pastabos)
* Trimestrai / Pusmečiai (pusmeciai)  

Šis API taip pat gali perskaityti gautus pranešimus (pranesimai, pranesimas, file_url).

### Pavyzdžiai
Į server.py galima žiūrėti kaip į šio API pritaikymo pavyzdį. Trumpesni ir paprastesni pavyzdžiai yra čia:
##### Synchroninis
```python
import pprint
from TamoAPI import TamoSession

# timeout - automatiškai viduje callins time.sleep(self.timeout) prieš kiekvieną request,
# todėl jums netyčia įvėlus bug'ą mažesnė tikimybė, kad tamo serveriai gaus 200 req/s, o jūs laikiną ip ban'ą
with TamoSession(USERNAME, PASSWORD, timeout=1) as session:
    print('Namu darbai:')
    for namu_darbo_irasas in session.namu_darbai():
        del namu_darbo_irasas['mokytojas']
        pprint.pprint(namu_darbo_irasas)

    print('Namu darbai pagal data:')
    for namu_darbo_irasas in session.namu_darbai('2023-01-01', '2023-01-31'):
        del namu_darbo_irasas['mokytojas']
        pprint.pprint(namu_darbo_irasas)

    pusmeciu_duomenys = session.pusmeciai(1)

    print('Vidurkis:')
    pprint.pprint(pusmeciu_duomenys['vidurkis'])

    print('Kiekvieno dalyko vidurkiai:')
    for dalykas in pusmeciu_duomenys['dalykai']:
        del dalykas['mokytojai']
        del dalykas['pazymiai']
        pprint.pprint(dalykas)

```
##### Asynchroninis
```python
import pprint
import asyncio
from TamoAPI.asyn import TamoSession


async def main():
    async with TamoSession(USERNAME, PASSWORD, timeout=1) as session:
        print('Namu darbai:')
        for namu_darbo_irasas in await session.namu_darbai():
            del namu_darbo_irasas['mokytojas']
            pprint.pprint(namu_darbo_irasas)

        print('Namu darbai pagal data:')
        for namu_darbo_irasas in await session.namu_darbai('2023-01-01', '2023-01-31'):
            del namu_darbo_irasas['mokytojas']
            pprint.pprint(namu_darbo_irasas)

        pusmeciu_duomenys = await session.pusmeciai(1)

        print('Vidurkis:')
        pprint.pprint(pusmeciu_duomenys['vidurkis'])

        print('Kiekvieno dalyko vidurkiai:')
        for dalykas in pusmeciu_duomenys['dalykai']:
            del dalykas['mokytojai']
            del dalykas['pazymiai']
            pprint.pprint(dalykas)

asyncio.run(main())
```
##### Galimas rezultatas
```
Namu darbai:
{'atlikimo data': {'d': 15, 'm': 5, 'w': 1, 'y': 2023},
 'dalykas': 'Užsienio kalba (anglų)',
 'failai': [],
 'ivede': {'d': 8, 'h': 12, 'm': 5, 'min': 41, 'y': 2023},
 'namu darbas': 'To do exams',
 'pamokos data': {'d': 8, 'm': 5, 'w': None, 'y': 2023}}
{'atlikimo data': {'d': 15, 'm': 5, 'w': 1, 'y': 2023},
 'dalykas': 'Užsienio kalba (anglų)',
 'failai': [],
 'ivede': {'d': 8, 'h': 12, 'm': 5, 'min': 41, 'y': 2023},
 'namu darbas': 'To do exams',
 'pamokos data': {'d': 8, 'm': 5, 'w': None, 'y': 2023}}
Namu darbai pagal data:
{'atlikimo data': {'d': 17, 'm': 1, 'w': 2, 'y': 2023},
 'dalykas': 'Užsienio kalba (anglų)',
 'failai': [],
 'ivede': {'d': 16, 'h': 14, 'm': 1, 'min': 52, 'y': 2023},
 'namu darbas': 'To finish reading the given texts.',
 'pamokos data': {'d': 16, 'm': 1, 'w': None, 'y': 2023}}
{'atlikimo data': {'d': 18, 'm': 1, 'w': 3, 'y': 2023},
 'dalykas': 'Užsienio kalba (vokiečių)',
 'failai': [],
 'ivede': {'d': 16, 'h': 21, 'm': 1, 'min': 3, 'y': 2023},
 'namu darbas': 'Technisierung. Hörverstehen',
 'pamokos data': {'d': 16, 'm': 1, 'w': None, 'y': 2023}}
{'atlikimo data': {'d': 23, 'm': 1, 'w': 1, 'y': 2023},
 'dalykas': 'Užsienio kalba (anglų)',
 'failai': [],
 'ivede': {'d': 17, 'h': 16, 'm': 1, 'min': 38, 'y': 2023},
 'namu darbas': 'To read 3 texts.',
 'pamokos data': {'d': 17, 'm': 1, 'w': None, 'y': 2023}}
{'atlikimo data': {'d': 25, 'm': 1, 'w': 3, 'y': 2023},
 'dalykas': 'Užsienio kalba (vokiečių)',
 'failai': [],
 'ivede': {'d': 24, 'h': 7, 'm': 1, 'min': 28, 'y': 2023},
 'namu darbas': 'Übungen beenden und Vokabeln in Sätzen lernen',
 'pamokos data': {'d': 23, 'm': 1, 'w': None, 'y': 2023}}
Vidurkis:
{'isvestu pazymiu': 8.86, 'pazymiu': 8.65, 'vidurkiu': None}
Kiekvieno dalyko vidurkiai:
{'dalykas': 'Dorinis ugdymas (etika)', 'isvesta': 'įsk.', 'vidurkis': None}
{'dalykas': 'Fizika', 'isvesta': '7', 'vidurkis': '7.17'}
{'dalykas': 'Fizinis ugdymas', 'isvesta': 'įsk.', 'vidurkis': None}
{'dalykas': 'Informacinės technologijos', 'isvesta': '10', 'vidurkis': '9.6'}
{'dalykas': 'Istorija', 'isvesta': '9', 'vidurkis': '8.67'}
{'dalykas': 'Istorijos modulis', 'isvesta': None, 'vidurkis': None}
{'dalykas': 'Lietuvių kalba ir literatūra', 'isvesta': '8', 'vidurkis': '7.5'}
{'dalykas': 'Matematika', 'isvesta': '8', 'vidurkis': '8.29'}
{'dalykas': 'Menų pažinimas', 'isvesta': 'įsk.', 'vidurkis': None}
{'dalykas': 'Muzika', 'isvesta': None, 'vidurkis': None}
{'dalykas': 'Užsienio kalba (anglų)', 'isvesta': '10', 'vidurkis': '9.67'}
{'dalykas': 'Užsienio kalba (vokiečių)', 'isvesta': '10', 'vidurkis': '9.75'}
```
