import requests
import datetime
import json

import re

file = open("authToken.txt", "r")
authToken = file.read()
file = open("calendrier_scolaire_url.txt", "r")
calendrier_scolaire_url = file.read()
file = open("activite_calendrier_url.txt", "r")
activite_calendrier_url = file.read()
try:
    m =re.search('donneesAnnuelles/(.+?)activitescalendrier?', activite_calendrier_url).group(1)
    print(m)
    codes = m.split("/")
    numero_ecole = codes[0]
    numero_eleve = codes[1]
except AttributeError:
    # AAA, ZZZ not found in the original string
    found = 'dsadwdas' # apply your error handling


headers = {
    'Authorization': 'Bearer ' + authToken,
}
response = requests.get(
    calendrier_scolaire_url,
    headers=headers,
)
data = response.json()

datedebut = data['anneeScolaire']['dateDebut']
datefin = data['anneeScolaire']['dateFin']
start_date = datetime.datetime.strptime(datedebut, "%Y-%m-%d")
one_day = datetime.timedelta(days=1)
while start_date.weekday() > 4:
    start_date = start_date - one_day
end_date = datetime.datetime.strptime(datefin, "%Y-%m-%d")
seven_day = datetime.timedelta(days=7)
six_days = datetime.timedelta(days=6)
while start_date <= end_date:
    format_string = '%Y-%m-%d'
    datesum = start_date + six_days
    date1 = start_date.strftime(format_string)
    date2 = datesum.strftime(format_string)

    url = 'https://apiaffairesmp.mozaikportail.ca/api/organisationScolaire/donneesAnnuelles/' + numero_ecole + '/' + numero_eleve + '/activitescalendrier?dateDebut=' + date1 + '&dateFin=' + date2
    responsehoraire = requests.get(
        url,
        headers=headers,
    )
    urlfinal = json.dumps(responsehoraire.json())
    print(urlfinal)
    start_date = start_date + six_days
