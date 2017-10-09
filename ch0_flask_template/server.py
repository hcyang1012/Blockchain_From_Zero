from flask import Flask
from flaskrun import flaskrun

app = Flask(__name__)
# do some Flask setup here

@app.route('/',methods=['GET'])
def route_index():
	print("Hello,Blockchain!")
	return "Hello,Blockchain!"


    
flaskrun(app)

