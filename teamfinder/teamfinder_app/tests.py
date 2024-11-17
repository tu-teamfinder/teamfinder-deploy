from django.test import TestCase, Client
from unittest.mock import patch, MagicMock
from teamfinder_app.tuapi import auth, get_user_info
from django.urls import reverse
from taggit.models import Tag
from django.contrib.auth import authenticate, login, logout, get_user
import django.contrib.auth.models as authmodel
from teamfinder_app.models import (
    User, Faculty, Group, GroupMember, Message, Post, RecruitPost, Requirement, Feedback, DirectMessage
)


# class TestAPI(TestCase):
#    @patch("teamfinder_app.tuapi.os.getenv")     # Mock os.getenv
#    @patch("teamfinder_app.tuapi.requests.post")  # Mock requests.post
#    @patch("teamfinder_app.tuapi.load_dotenv")
#    def test_auth(self, mock_getenv, mock_post, mock_load_dotenv):
#       # Mocking os.getenv to simulate the presence of an API key
#       mock_getenv.return_value = "mock_api_key"
#       mock_load_dotenv.return_value = None # Prevent loading the actual `.env` file

#       # Mocking the response from requests.post
#       mock_response = MagicMock()
#       mock_response.status_code = 200  # Simulate a successful API call
#       mock_response.json.return_value = {"token": "mock_token"}  # Mock JSON response
#       mock_post.return_value = mock_response

#       result = auth(user="test_user", password="test_password")

#       self.assertEqual(result["status"], 200)  
#       self.assertEqual(result["data"], {"token": "mock_token"})  

#       # Ensure `requests.post` was called with the correct arguments
#       mock_post.assert_called_once_with(
#          "https://restapi.tu.ac.th/api/v1/auth/Ad/verify",
#          json={"UserName": "test_user", "PassWord": "test_password"},
#          headers={
#                "Content-Type": "application/json",
#                "Application-Key": "mock_api_key"
#          }
#       )

class TestViews(TestCase):

   def setUp(self):
      id1 = "6510615888"
      pass1 = "password123"
      id2 = "660134999"
      pass2 = "password123"
      u1 = authmodel.User.objects.create_user(
         username = id1,
         password = pass1
      )
      u1.save()

      u2 = authmodel.User.objects.create_user(
         username = id2,
         password = pass2
      )
      u2.save()

      user1 = User.objects.create(
         user_id="6510615888",
         password="password123",
         email_address="user1@example.com",
         name="John Doe",
         major="Computer Engineering",
         faculty="Engineering",
         year=3,
      )
      user2 = User.objects.create(
         user_id="660134999",
         password="password123",
         email_address="user2@example.com",
         name="Jane Smith",
         major="Civil Law",
         faculty="Law",
         year=2,
      )

   def test_protected_view_access(self):
      """test view"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get(reverse('myaccount'))
      self.assertEqual(response.request["PATH_INFO"], "/myaccount")
      self.assertEqual(response.status_code, 200)  

   def test_index_return_index(self):
      """test if index return homepage"""

      c = Client()
      response = c.get("")
      self.assertEqual(response.request["PATH_INFO"], "")
      self.assertEqual(response.status_code, 200)

   def test_aboutPage(self):
      """test if about page working correctly"""

      c = Client()
      response = c.get("/about")
      self.assertEqual(response.request["PATH_INFO"], "/about")
      self.assertEqual(response.status_code, 200)

   def test_recruitmentPage(self):
      """test if recruitment page working correctly"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/recruitment")
      self.assertEqual(response.request["PATH_INFO"], "/recruitment")
      self.assertEqual(response.status_code, 200)
   
   def test_createPage(self):
      """test if create recruitment post page working correctly"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/create")
      self.assertEqual(response.request["PATH_INFO"], "/create")
      self.assertEqual(response.status_code, 200)
   
   def test_create_recruitment_post_valid(self):
      """test posting recruitment post with correct values"""

      c = Client()
      c.login(username="6510615888", password="password123")
      post_value = {
            "heading": "Health Hackathon",
            "content": "Need experience devs",
            "amount": 1,
            "tags": '[{"value": "Machine Learning"}, {"value": "Data Science"}, {"value": "Kaggle"}]'
      }
      response = c.post("/create", data=post_value, follow=True)
      self.assertEqual(response.request['PATH_INFO'], "/create/requirement")
   
   def test_create_recruitment_post_invalid(self):
      """test posting recruitment post with incorrect values"""
      
      c = Client()
      c.login(username="6510615888", password="password123")
      post_value = {
           "heading": "Health Hackathon",
            "content": "12312",
            "amount": -10,
            "tags": '[{"value": "Machine Learning"}, {"value": "Data Science"}, {"value": "Kaggle"}]'
      }
      response = c.post("/create", data=post_value, follow=True)
      self.assertEqual(response.request['PATH_INFO'], "/create")

   def test_create_recruitment_post_invalid_2(self):
      """test posting recruitment post with incorrect values 2"""

      c = Client()
      c.login(username="6510615888", password="password123")
      post_value = {
           "heading": "Health Hackathon",
            "content": "12312",
            "amount": 0,
            "tags": ""
      }
      response = c.post("/create", data=post_value, follow=True)
      self.assertEqual(response.request['PATH_INFO'], "/create")

   # def test_create_requirement_valid(self):
   #    """test input requirement with correct values"""

   #    c = Client()
   #    c.login(username="6510615888", password="password123")
   #    post_value = {
   #          "heading": "Health Hackathon",
   #          "content": "Need experience devs",
   #          "amount": 1,
   #          "tags": "Machine Learning, Data Science, Kaggle"
   #    }
   #    response = c.post("/create", data=post_value, follow=True)
   #    self.assertEqual(response.request['PATH_INFO'], "/create/requirement")
   #    post_value = {
   #        "req_faculty": "Engineering",
   #        "req_major": "Computer Engineering",
   #        "year": "2",
   #        "description": "Web Developers"
   #    }
   #    response = c.post("/create/requirement", data=post_value, follow=True)
   #    self.assertEqual(response.request['PATH_INFO'], "/recruitment")
   
   # def test_create_requirement_invalid(self):
   #    """test input requirement with incorrect values"""

   #    c = Client()
   #    c.login(username="6510615888", password="password123")
   #    post_value = {
   #        "req_faculty": 123,
   #        "req_major": "Chemical Engineering",
   #        "year": "two",
   #        "description": "AAAAAAAAAA"
   #    }
   #    response = c.post("/create/requirement", data=post_value, follow=True)
   #    self.assertEqual(response.request['PATH_INFO'], "/create/requirement")
   
   # def test_create_requirement_lack(self):
   #    """test input requirement with empty values"""

   #    c = Client()
   #    c.login(username="6510615888", password="password123")
   #    post_value = {
   #        "req_faculty": "",
   #        "req_major": "",
   #        "year": "",
   #        "description": ""
   #    }
   #    response = c.post("/create/requirement", data=post_value, follow=True)
   #    self.assertEqual(response.request['PATH_INFO'], "/create/requirement")
   
   def test_logout(self):
      """test if logout working correctly"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/logout", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/login")
      self.assertEqual(response.status_code, 200)
