import sqlite3

connection = sqlite3.connect("users.db")

connection.execute('CREATE TABLE user_table (username TEXT PRIMARY KEY,name TEXT,email TEXT,password TEXT,solved TEXT)')
connection.execute('CREATE TABLE list_of_questions (name TEXT PRIMARY KEY,type TEXT,difficulty TEXT)')


connection.execute("INSERT INTO user_table Values('u1','Tej','u1_1@examplemail.com','pass1','all_same_char')")
connection.execute("INSERT INTO user_table Values('u2','Ram','u2_1@examplemail.com','pass1','')")
connection.execute("INSERT INTO user_table Values('u3','Vaibh','u3_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u4','Raj','u4_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u5','Ram','u5_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u6','user_6','u6_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u7','user_7','u7_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u8','user_8','u8_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u9','user_9','u9_1@examplemail','pass1','')")
connection.execute("INSERT INTO user_table Values('u10','user_10','u10_1@examplemail','pass1','')")

fp = open('Questions/qinfo.txt')

qlist = fp.read().split(sep="\n")
for question in qlist:
    ques = question.split(sep=",")

    connection.execute("INSERT INTO list_of_questions VALUES('"+ ques[0]+ "','" + ques[1]+"','"+ques[2]+"'" +     ")")

a=connection.execute("select * from list_of_questions")

for i in a:
    print(i)
connection.commit()
connection.close()