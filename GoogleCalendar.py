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
        service = build('calendar', 'v3', credentials=creds)
        calendar_dict = service.calendarList().list().execute()
        calendar_string = str(calendar_dict).lower()

    #Cherche si calendrier scolaire existe déja
        if ("école" or "ecole" or "school") in calendar_string:
            for items in calendar_dict["items"]:
                stringnotcasesensitive = str(items["summary"]).lower()
                if ("école" or "ecole" or "school") in stringnotcasesensitive:
                    calendarid = items["id"]
                    print(calendarid)


        else:
            print("No calendar for school found! Creating one...")
            calendar = {
                'summary': 'School',
                'timeZone': 'America/New_York'
            }
            created_calendar = service.calendars().insert(body=calendar).execute()
            calendarid = created_calendar['id']



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
        start_date = datetime.datetime.strptime(datedebut, "%Y-%m-%d")
        one_day = datetime.timedelta(days=1)
        while start_date.weekday() > 4:
            start_date = start_date - one_day
        end_date = datetime.datetime.strptime(datefin, "%Y-%m-%d")
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
            donneeshoraire = json.dumps(responsehoraire.json())
            print(donneeshoraire)
            start_date = start_date + six_days
            # TODO - Ajouter Github Control Version en private
            # TODO - BUG Quelques evenement en doublon
            # TODO - Site Web
            # TODO - Transformer code MozaikGet.java en javascript pour site web
            # TODO - Ajouter Parametres
            # TODO - Ajouter couleur calendrier
            #Créer événement
            data = donneeshoraire
            res = json.loads(data)
            # donneeshoraire et res = json de horaire de mozaik
            print(res)
            # For each events in donneeshoraire, loop to find if contain event at the same time
            # loop a travers horaire de mozaik
            for i in range(len(res)):

                    if res[i]['locaux'] :
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
                    print(event)
                    eventcreation = service.events().insert(
                        calendarId=calendarid,
                        body=event
                    ).execute()
                    print(eventcreation)




    except HttpError as error:
        print('An error occurred: %s' % error)






if __name__ == '__main__':
    main()