import requests
headers = {
    'Authorization': 'Bearer ' + authToken,
}
response = requests.get(
    'https://apiaffairesmp.mozaikportail.ca/api/organisationScolaire/calendrierScolaire/784025/1?dateDebut=2023-09-10&dateFin=2023-09-16',
    headers=headers,
)