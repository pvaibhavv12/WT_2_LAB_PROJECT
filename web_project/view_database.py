import sqlite3

connection = sqlite3.connect("users.db")
'''
    userName="u2"
    userPass="usrp"
    name="usr"
    email="mmm"

    ins = "INSERT INTO user_table VALUES('" + str(userName) +"','" + str(userPass) + "','" +str(name)+ "','" + str(email) + "')"
    print(ins)
    connection.execute(ins)
    connection.commit()
'''
valid_user="u1"
res=connection.execute("SELECT solved from user_table where username ='" + valid_user +"'")
res=connection.execute("SELECT * from user_table") 

for a in res:
    print(a)

connection.commit()
connection.close()