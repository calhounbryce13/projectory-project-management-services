"""
Description: project management service controller file for Projectory main program, uses data removal service for deletion.
Author: Bryce Calhoun
"""

from flask import Flask, request, make_response
from flask_cors import CORS
import requests
import model
import os

#todo: I need to add functionality to the endpoints
#todo: that will check the incoming method and set the proper 
#todo: headers for a preflight request


app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*":
                                                {"origins": "https://calhounbryce13.github.io",
                                                "methods": ["POST", "PUT", "OPTIONS"],
                                                "allow_headers": ["Content-Type"]
                                                }})


def validate_request(email, title, index, mark):
    if(email is not None and title is not None and index is not None and mark is not None):
        if(isinstance(email, str)):
            if(isinstance(title, str)):
                if(isinstance(index, int)):
                    if(isinstance(mark, int)):
                        return True
    return False

def delete_project_after_completion(userEmail, projectName):
    headers = {
            "Content-Type": "application/json",
            "x-user-email": userEmail
            }
    data = {
            "project-type": "current",
            "project-name": projectName
    }
    try:
        deleteProjectResponse = requests.delete('https://projectory-data-removal-services.onrender.com/deletion', headers=headers, json=data)
        return True
    except Exception:
        return False


@app.route('/task-manager', methods=['POST', 'OPTIONS'])
def call_model_to_mark_task():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://calhounbryce13.github.io"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.status_code = 200
        return response
    try:
        userEmail, projectTitle, taskIndex, mark = (request.json).values()
    except ValueError:
        return "Error, Invalid request", 400
    
    if(validate_request(userEmail, projectTitle, taskIndex, mark)):
        status = model.mark_project_task(UserEmail=userEmail, projectTitle=projectTitle, taskIndex=taskIndex, mark=mark)
        if(status == False):
            return "Error, Issue communicating with database" ,500
        return "success", 200
        
    return "Error, Invalid request", 400

@app.route('/completed-project-manager', methods=['PUT', 'OPTIONS'])
def call_model_to_complete_project():
    print("endpoint reached")
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://calhounbryce13.github.io"
        response.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.status_code = 200
        return response


    userEmail, projectTitle = (request.json).values()

    result = model.mark_project_complete(userEmail=userEmail, projectTitle=projectTitle)
    if(result):
        deleted = delete_project_after_completion(userEmail=userEmail, projectName=projectTitle)
        if(deleted):
            return "success", 200
    return "fail", 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
