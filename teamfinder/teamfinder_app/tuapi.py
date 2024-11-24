import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("API_KEY")

v1 = "https://restapi.tu.ac.th/api/v1"
v2 = "https://restapi.tu.ac.th/api/v2"

headers = {
    "Content-Type": "application/json",
    "Application-Key": api_key,
}

def auth(user: str, password: str) -> dict:
    """
    Authenticate user
    return status and response data
    """

    body = {
        "UserName": user,
        "PassWord": password
    }
    url = v1 + "/auth/Ad/verify"
    response = requests.post(url, json=body, headers=headers)
    status = response.status_code
    data = response.json()

    return {"status": status, "data": data}
    

def get_user_info(user: str) -> dict:
    """
    Get user information
    return status and response data
    """
        
    url = v2 + f"/profile/std/info/?id={user}"
    response = requests.get(url, headers=headers)
    status = response.status_code
    data = response.json()
    
    return {"status": status, "data": data}


def get_faculty_all() -> dict:
    """
    Get all faculty name
    """

    url = v2 + "/std/fac/all"
    response = requests.get(url, headers=headers)
    status = response.status_code
    data = response.json()
    
    return {"status": status, "data": data}


