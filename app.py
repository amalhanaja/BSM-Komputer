from sanic import Sanic
from sanic.response import text,json
import pyrebase
from asyncpg import connect, create_pool

DB_CONFIG = {
    'host': 'ec2-54-225-107-107.compute-1.amazonaws.com',
    'user': 'biesnuithsobir',
    'password': '900d16de87a2347ec24e483d29c32263e22e29a571e9946b1f54261f5dd3bdea',
    'port': '5432',
    'database': 'da70ahioc7lvfg'
}

config = {
  "apiKey": "AIzaSyCekWnawcLzSpBYe7VL-lQuVKS0BLrjE7s",
  "authDomain": "bsm-komputer.firebaseapp.com",
  "databaseURL": "https://bsm-komputer.firebaseio.com",
  "projectId": "bsm-komputer",
  "storageBucket": "bsm-komputer.appspot.com",
  "messagingSenderId": "142856474774"
}

firebase = pyrebase.initialize_app(config)

def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

def serialize_list(l):
    return [m.serialize() for m in l]

def json_object(records):
    return {dict(r.items()) for r in records}
def array_jsonify(records):
    """
    Parse asyncpg record response into JSON format
    """
    return [dict(r.items()) for r in records]
def jsonify(records):
    return [dict(r.items()) for r in records]

app = Sanic(__name__)
auth = firebase.auth()

@app.listener('before_server_start')
async def register_db(app, loop):
    app.pool = await create_pool(**DB_CONFIG, loop=loop, max_size=20)

@app.route('/login', methods=['POST'])
async def login(request):
    if 'email' not in request.json:
        return text("email cannot be empty")
    elif 'password' not in request.json:
        return text("password cannot be empty")
    else :
        user = {""}
        try:
            user = auth.sign_in_with_email_and_password(request.json['email'], request.json['password'])
        except :
            return json({"email": ""})
        print (user)
        emailVerified = auth.get_account_info(user['idToken'])['users'][0]['emailVerified']
        if emailVerified == False:
            return json({"verified": emailVerified})
        else :
            async with app.pool.acquire() as connection:
                login_sql = 'UPDATE USERS SET VERIFIED = TRUE WHERE EMAIL = ' + "'" + user['email'] + "'" +';'
                await connection.execute(login_sql)
                login_sql = 'SELECT * FROM USERS WHERE EMAIL = ' + "'" + user['email']  + "';"
                print (login_sql)
                login_result = await connection.fetch(login_sql)
            return json(jsonify(login_result)[0])
            

@app.route('/signup', methods=['POST'])
async def signup(request):
    nama = request.json['nama']
    email = request.json['email']
    password = request.json['password']
    if nama != None and email != None and password != None:
        try:
            auth.create_user_with_email_and_password(email, password)
        except :
            return json({"message": "Email telah terdaftar"})
        
        user = auth.sign_in_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        signup_sql = 'INSERT INTO USERS (NAMA, EMAIL, STATUS) VALUES (' + "'" + nama + "'" + ", '" + email + "', 'USER');"
        async with app.pool.acquire() as connection:
            login_result = await connection.fetch(signup_sql)
        print (signup_sql)
        return json({"message": "Akun telah dibuat"})
    else :
        return json({"message": "params(nama, email, password)"})
    #return text(nama)
    
    #sql = INSERT INTO USERS (NAMA, EMAIL, STATUS) VALUES (nama, email, 'USER');

if __name__ == "__main__":
    app.run(host='bsmkomputer.herokuapp.com', port=1337, workers=4)