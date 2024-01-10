from __future__ import print_function
import datetime
import os.path
import json
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from tqdm import tqdm
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
            os.system('cls')
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        calendarid = ""
        service = build('calendar', 'v3', credentials=creds)
        batch = service.new_batch_http_request()
        calendar_dict = service.calendarList().list().execute()
        print("Bienvenue, maintenant vous devrez choisir dans quelle calendrier vous voulez importer votre calendrier Mozaik ou vous pouvez en créer un nouveau. Pour ce faire, veuillez entrer le chiffre à la gauche du calendrier sélectionné ou de l'option de la création d'un nouveau calendrier")
        print("Voici vos calendriers dans Google Calendar:")
        i = 1
        for items in calendar_dict["items"]:
            print(str(i) + ":" + items["summary"])
            i = i+1
        print(str(i) + ":Créer un nouveau calendrier")
        choix = int(input("Veuillez choisir votre option : ")) - 1
        if choix == i-1:
            nom_nouveau_calendrier = input("Comment voulez-vous nommer votre nouveau calendrier? : ")
            print("Calendrier en création...")
            calendar = {
                    'summary': nom_nouveau_calendrier,
                    'timeZone': 'America/New_York'
                }
            created_calendar = service.calendars().insert(body=calendar).execute()
            calendarid = created_calendar['id']
        else:
            calendarid = calendar_dict["items"][choix]['id']

        file = open("authToken.txt", "r")
        authToken = file.read()
        file = open("calendrier_scolaire_url.txt", "r")
        calendrier_scolaire_url = file.read()
        file = open("activite_calendrier_url.txt", "r")
        activite_calendrier_url = file.read()
        try:
            m =re.search('donneesAnnuelles/(.+?)activitescalendrier?', activite_calendrier_url).group(1)
            codes = m.split("/")
            numero_ecole = codes[0]
            numero_eleve = codes[1]
        except AttributeError:
            found = 'dsadwdas'
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
        # Créer événement
        data = donneeshoraire
        res = json.loads(data)
        f = open("donnees.txt", "x")
        f.write(data)
        f.close()
        # donneeshoraire et res = json de horaire de mozaik
        # For each events in donneeshoraire, loop to find if contain event at the same time
        # loop a travers horaire de mozaik
        for i in tqdm(range(len(res)), colour="white"):
            try:
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
            except KeyError as e:
                if res[i]['locaux']:
                    event = {

                        'summary': res[i]['description'] + ' Gr:' + res[i]['matieresGroupes'][0]['codeGroupe'],
                        'description' :res[i]['codeActivite'],
                        'location': res[i]['locaux'],
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

                        'summary': res[i]['description'] + ' Gr:' + res[i]['matieresGroupes'][0]['codeGroupe'],
                        'description' :res[i]['codeActivite'],
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
        print("Insertion du calendrier...")
        print("Veuillez patienter, ceci peut prendre quelques minutes")
        print("L'application fermera lorsque l'importation aura fini!")
        batch.execute()

    except HttpError as error:
        print('An error occurred: %s' % error)






if __name__ == '__main__':
    main()