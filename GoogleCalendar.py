from __future__ import print_function
import datetime
import os.path
import json
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from googleapiclient.http import BatchHttpRequest
SCOPES = ['https://www.googleapis.com/auth/calendar']
def main():
    creds = None
    file = open("authToken.txt", "r")
    authToken = file.read()
    headers = {
        'Authorization': 'Bearer ' + authToken,
    }
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        calendarid = ""
        service = build('calendar', 'v3', credentials=creds)
        batch = service.new_batch_http_request()
        calendar_dict = service.calendarList().list().execute()
        #Cherche si calendrier scolaire existe déja
        calendar_str = str(calendar_dict).lower()
        print(calendar_str)
        if calendar_str.find("birthdays") != -1:
            for items in calendar_dict["items"]:
                stringnotcasesensitive = str(items["summary"]).lower()
                index = stringnotcasesensitive.find("school")
                if index != -1:
                    calendarid = items["id"]
                    print(calendarid)
        # else:
        #     print("No calendar for school found! Creating one...")
        #     calendar = {
        #         'summary': 'School',
        #         'timeZone': 'America/New_York'
        #     }
        #     created_calendar = service.calendars().insert(body=calendar).execute()
        #     calendarid = created_calendar['id']



        url = 'https://apiaffairesmp.mozaikportail.ca/api/organisationScolaire/calendrierScolaire/784025/1?dateDebut=2023-09-10&dateFin=2023-09-16'
        response = requests.get(
                  url,
                  headers=headers,
             )
        print(response.json())
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
        response = requests.get(
            calendrier_scolaire_url,
            headers=headers,
        )
        data = response.json()

        datedebut = data['anneeScolaire']['dateDebut']
        datefin = data['anneeScolaire']['dateFin']
        start_date = datetime.datetime.strptime(datedebut, "%Y-%m-%d").strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(datefin, "%Y-%m-%d").strftime('%Y-%m-%d')
        url = 'https://apiaffairesmp.mozaikportail.ca/api/organisationScolaire/donneesAnnuelles/' + numero_ecole + '/' + numero_eleve + '/activitescalendrier?dateDebut=' + start_date + '&dateFin=' + end_date
        responsehoraire = requests.get(
                url,
                headers=headers,
        )

        donneeshoraire = json.dumps(responsehoraire.json())
        # print(donneeshoraire)
        # TODO - Optimiser performance en envoyant en batch, avec liste ou dict
        # TODO - Site Web
        # TODO - Transformer code MozaikGet.java en javascript pour site web
        # TODO - New Relic
        # TODO - Ajouter Parametres
        # TODO - Ajouter couleur calendrier
        #Créer événement
        data = donneeshoraire
        res = json.loads(data)
        # donneeshoraire et res = json de horaire de mozaik
        # For each events in donneeshoraire, loop to find if contain event at the same time
        # loop a travers horaire de mozaik
        for i in range(len(res)):
            # print(res[i]['dateDebut'])
            if res[i]['locaux']:
                event = {
                            'summary': res[i]['description'],
                            'location': res[i]['locaux'],
                            'description': res[i]['intervenants'][0]['prenom'] + ' ' + res[i]['intervenants'][0]['nom'],
                            'start': {
                                'dateTime': res[i]['dateDebut'] + 'T' + res[i]['heureDebut'] + ':00',
                                'timeZone': 'America/New_York',
                            },
                            'end': {
                                'dateTime': res[i]['dateFin'] + 'T' + res[i]['heureFin'] + ':00',
                                'timeZone': 'America/New_York',
                            },
                            'reminders': {
                                'useDefault': False,
                                'overrides': [
                                    {'method': 'popup', 'minutes': 10},
                                ],
                            },
                        }
            else:
                event = {
                            'summary': res[i]['description'],
                            'description': res[i]['intervenants'][0]['prenom'] + ' ' + res[i]['intervenants'][0]['nom'],
                            'start': {
                                'dateTime': res[i]['dateDebut'] + 'T' + res[i]['heureDebut'] + ':00',
                                'timeZone': 'America/New_York',
                            },
                            'end': {
                                'dateTime': res[i]['dateFin'] + 'T' + res[i]['heureFin'] + ':00',
                                'timeZone': 'America/New_York',
                            },
                            'reminders': {
                                'useDefault': False,
                                'overrides': [
                                    {'method': 'popup', 'minutes': 10},
                                ],
                            },
                        }
            batch.add(service.events().insert(calendarId=calendarid, body=event))
        batch.execute()
    except HttpError as error:
        print('An error occurred: %s' % error)






if __name__ == '__main__':
    main()