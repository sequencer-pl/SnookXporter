from snookxporter.clients.snookapp import SnookAppClient
from snookxporter.dataclasses import User

USERS = [
    User(firstName='Rafał', lastName='Leszcz')
]

def run():
    snook_app_client = SnookAppClient()
    snook_app_client.get_arriving_matches_for(users=USERS)


if __name__ == '__main__':
    run()
