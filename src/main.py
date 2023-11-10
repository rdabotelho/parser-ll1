from stk_dsl_main import StkDsl

class Session:
    def __init__(self, client):
        self.client = client

class Client:
    def __init__(self, first_name, last_name, age, account):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.account = account

if __name__ == "__main__":
    client = Client('Rafael', 'Botelho', 16, '1234')
    session = Session(client)
    stk_dsl = StkDsl(session)

    while True:
        source = input("> ")
        
        if not source:
            print("Bye!")
            break
        
        stk_dsl.eval(source)
