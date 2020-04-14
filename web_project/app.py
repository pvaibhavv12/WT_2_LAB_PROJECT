import flask
#from flask import Flask, render_template,url_for
from flask import *
import sqlite3
import base64
import subprocess
from subprocess import PIPE

special_key = "ab@123z445"
#some random key
app = Flask(__name__)

def validate(vkey):
    try:
        user = vkey.split(sep=".")[0]
        user = user.strip()
        print("THE USER IS ",user,sep="")
        user+='=='
        user = base64.b64decode(user.encode())
        user = user.decode()
        print("THE USER IS ",user,sep="")
        valid_user = (check_available(user)=='0')

        

        if(not valid_user):
            return "0","-1"
        
        return "1",user
    except Exception as e:
        print(e)
        return "0","0"

@app.route('/code')
@app.route('/code.html')
def temp_html():
    return render_template('code.html')

@app.route("/index")
@app.route("/index.html")
@app.route("/")
def home_page():
    return render_template('index.html')

@app.route("/about")
@app.route("/about.html")
def about_page():
    return render_template('about.html')

@app.route("/question")
@app.route("/question.html")
def question_html():
    return render_template('question.html')

@app.route("/login")
@app.route("/login.html")
def login_page():
    return render_template('login.html')

@app.route("/register")
@app.route("/register.html")
def register_page():
    return render_template('register.html')

@app.route("/register_user",methods=['GET'])
def register_new_user():
    
    try:
        userName=flask.request.values.get('userName')
        userPass=flask.request.values.get('userPass')
        name=flask.request.values.get('name')
        email=flask.request.values.get('email')
        
        connection = sqlite3.connect("users.db")
        ins = "INSERT INTO user_table VALUES('" + str(userName) +"','" + str(name) + "','" +str(email)+ "','" + str(userPass) + "', '')"
        connection.execute(ins)
        connection.commit()
        connection.close()
        
        return "inserted > "+userName
    except Exception as e:
        print('exception', e)
        return "Failed to insert!"

@app.route("/register_user/check_user/<user_name>",methods=['POST','GET'])
def check_available(user_name):
    
    try:
        print("In check_availabe user :",user_name,sep="")
        available = 1 
        connection = sqlite3.connect("users.db")
        query = "SELECT username from user_table"

        

        res = connection.execute(query)

        for u in res:
            
            if(u[0]==user_name):
                available = 0

        connection.close()
        
        return str(available)
    except:
        return "Failed to check!"

@app.route("/login/user_login",methods=['GET'])
def user_login():
    validation_key = ''
    userName=flask.request.values.get('userName')
    userPass=flask.request.values.get('userPass')
    valid_user = (check_available(userName) == '0')

    if (not valid_user):
        return "User not registered!"
    
    try:
        
        
        connection = sqlite3.connect("users.db")
        query = "SELECT password from user_table where username = '" + userName +"' "
        res = connection.execute(query)
        
        password_match = 0

        for a in res:
            print(a[0], userPass)
            if(a[0] == userPass):
                password_match = 1

        if(not(password_match)):
            return "Wrong Password"

        validation_key = base64.b64encode(userName.encode()).decode() + "." + base64.b64encode(special_key.encode()).decode()
        connection.close()
        print(validation_key)
        return validation_key
    except Exception as e:
        print(e)
        return "Failed to validate user"

@app.route("/list_all_questions/<validation_key>",methods=['GET'])
def list_of_question(validation_key):
    
    num_of_questions=flask.request.values.get('quesNum')
    num_of_questions=int(num_of_questions)

    valid_user,name_of_valid_user = validate(validation_key)
    print("VALID USER :: ",valid_user,name_of_valid_user)
    if (valid_user == "0"):
        return "Invalid Validation Key \n Please Login Again"
    
    return_json = {}
    
    connection = sqlite3.connect("users.db")
    
    question_list=[]
    return_string=""

    return_type=""
    type_list=[]

    res=connection.execute("select name,type from list_of_questions")

    for a in res:

        question_list.append(a[0])
        type_list.append(a[1])

    if(num_of_questions >= len(question_list)):
        return "0"

    if(num_of_questions==0):

        for i in range(7):
            return_string = return_string + question_list[i] + "," 
            return_type = return_type + type_list[i] + ","

        return_json["quesNum"]=7
    else:
        inc =3
        inc = min(len(question_list)-num_of_questions,3)
        for i in range(num_of_questions,num_of_questions+inc):
            return_string = return_string + question_list[i] + ","
            return_type = return_type + type_list[i] + ","

        return_json["quesNum"]=num_of_questions+inc

    return_string.rstrip(",")
    return_type.rstrip(",")
    

    return_json["quesList"] = return_string
    return_json["quesType"] = return_type
    return_json["user"] = name_of_valid_user
    connection.close()
    
    return jsonify(return_json)
    

@app.route("/get_question_details/<question>/<validation_key>",methods=['GET'])
def get_question(question,validation_key):
    valid_user,name_of_valid_user = validate(validation_key)

    print("VALID USER :: ",valid_user)
    if (valid_user == "0"):
        return "Invalid Validation Key \n Please Login Again"


    connection = sqlite3.connect("users.db")
    res=connection.execute("select * from list_of_questions where name = '" + question + "'" )
    
    q_dict ={}

    fp1=open("Questions/" + question + "/question.txt")
    fp2=open("Questions/" + question + "/sample_input.txt")
    fp3=open("Questions/" + question + "/sample_output.txt")


    for q in res:
        
        qs=list(q)
        q_dict['user_name']=name_of_valid_user
        q_dict['name']=qs[0]
        q_dict['type']=qs[1]
        q_dict['difficulty']=qs[2]
        q_dict['question']=fp1.read()
        q_dict['sample_input']=fp2.read()
        q_dict['sample_output']=fp3.read()

    connection.close()
    fp1.close()
    fp2.close()
    fp3.close()

    return jsonify(q_dict)




    
@app.route("/evaluate_question/<validation_key>",methods=['GET'])
def evaluate_question(validation_key):
    
    input_code=flask.request.values.get('inputCode')
    print("INPUTCODE >> ",input_code)
    #language=flask.request.values.get('language')
    question=flask.request.values.get('question')
    
    valid_user,name_of_valid_user = validate(validation_key)

    #return json
    if (valid_user == "0"):
        return "Invalid Validation Key \n Please Login Again"

    valid_code = 1
    '''
    try:
        executed_output = exec(input_code)
        executed_output.strip().split(sep="\n")
    except:
        valid_code = 0
        return "Syntax Error"

    '''
    #input_code ="n=input()\nfor i in range(int(n)):\n\tprint((i+1)*2)"

    filepath ="Questions" + "\\" +  question + "\output.txt"
    filepathi="Questions" + "\\" +  question + "\input.txt"

    f_py = open('p2.py',"w")
    f_py.write(input_code)
    f_py.close()

    ifile = open(filepathi,"r")
    input_data = ifile.read()
    ifile.close()

    ofile = open(filepath,"r")
    list_test = ofile.read()
    ofile.close()

    list_test=list_test.strip()
    list_test = list_test.split("\n")
    
    '''
    fill in input code in p2.py
    pass input from input file
    '''
    try:
        p = subprocess.Popen(['python', 'p2.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = p.communicate(input=input_data.encode())
        out = out.decode().strip()
        out = out.rstrip("\r")
        executed_output = out

    except:
        print("error running script")
    if not err.decode()=="":
        return err.decode()

    executed_output = executed_output.split(sep="\n")
    for i in range(len(executed_output)):
        executed_output[i]=executed_output[i].rstrip("\r")

    
    print(list_test)
    length = len(list_test)
    correct_answers = 0
    print("AA<",executed_output,list_test)
    print("ZZZZZZZZZZ",length,len(executed_output))

    if(length!=len(executed_output)):
        return "Wrong output"

    for i in range(length):
        if(list_test[i].strip() == executed_output[i].strip()):
            correct_answers += 1
    
    res = str(correct_answers) + "/" + str(length)
    
    if(correct_answers==length):
        #add to database
        #question

        connection = sqlite3.connect("users.db")

        ress = connection.execute("SELECT solved from user_table where username ='" + name_of_valid_user + "'")

        old_solved=""
        for a in ress:
            old_solved = a[0]
            print(old_solved)
    

        new_solved = old_solved + "," + question

        query = "UPDATE user_table SET solved ='" + new_solved + "' where username ='"+ name_of_valid_user +"'"
        connection.execute(query)
        connection.commit()
        connection.close()
    
    return res

@app.route("/suggest_questions/<validation_key>",methods=['GET'])
def suggest_questions(validation_key):
    return_json={}
    valid_user,name_of_valid_user = validate(validation_key)

    #get question list of user
    input_data_ques=""
    connection = sqlite3.connect("users.db")
    
    res = connection.execute("SELECT solved from user_table where username ='" + name_of_valid_user +"'")
    
    for i in res:
        
        input_data_ques = i[0]
    
    #return json
    input_data_ques=input_data_ques.split(",")

    input_datas=""

    for a in input_data_ques:
        res = connection.execute("SELECT type,difficulty from list_of_questions where name ='"+a+"'")
        for j in res:
            input_datas = input_datas + j[0] + j[1] +","
    input_datas=input_datas.rstrip(",")

    if (valid_user == "0"):
        return "Invalid Validation Key \n Please Login Again"
    
    executed_output=""
    try:
        input_data = input_datas
        #input_data=""
        print("input predict",input_data)

        if(input_data==""):    
            input_data=input_data+"\n"
        
        p = subprocess.Popen(['python', 'prediction.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = p.communicate(input=input_data.encode())
        
        out = out.decode().strip()
        executed_output = out

        print("SUGGESTION PREDICTION :",executed_output,out,sep=" ")

    except:
        print("error running prediction script")
    
    
    q=executed_output.split(sep="\n")[0]
    type_q=executed_output.split(sep="\n")[1]

    return_json["username"]=name_of_valid_user
    return_json["questions"]=q
    return_json["type"]=type_q

    connection.close()
    return jsonify(return_json)
    

if __name__ == "__main__":
    app.run(debug=True)