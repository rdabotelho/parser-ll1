from myparser import Parser

class Session:
    def __init__(self, client):
        self.client = client

class Client:
    def __init__(self, first_name, last_name, age):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age

if __name__ == "__main__":
    client = Client('Rafael', 'Botelho', 16)
    session = Session(client)
    
    result = Parser(session, False).execute("client.first_name")
    print(result)