from django.test import TestCase, Client
from unittest.mock import patch, MagicMock
from teamfinder_app.tuapi import auth, get_user_info
from taggit.models import Tag

from teamfinder_app.models import (
    User, Faculty, Group, GroupMember, Message, Post, RecruitPost, Requirement, Feedback, DirectMessage
)


class TestAPI(TestCase):

   @patch("teamfinder_app.tuapi.os.getenv")     # Mock os.getenv
   @patch("teamfinder_app.tuapi.requests.post")  # Mock requests.post
   def test_auth(self, mock_getenv, mock_load_dotenv, mock_post):
      # Mocking os.getenv to simulate the presence of an API key
      mock_getenv.return_value = "mock_api_key"
      mock_load_dotenv.return_value = None # Prevent loading the actual `.env` file

      # Mocking the response from requests.post
      mock_response = MagicMock()
      mock_response.status_code = 200  # Simulate a successful API call
      mock_response.json.return_value = {"token": "mock_token"}  # Mock JSON response
      mock_post.return_value = mock_response

      result = auth(user="test_user", password="test_password")

      self.assertEqual(result["status"], 200)  
      self.assertEqual(result["data"], {"token": "mock_token"})  

      # Ensure `requests.post` was called with the correct arguments
      mock_post.assert_called_once_with(
         "https://restapi.tu.ac.th/api/v1/auth/Ad/verify",
         json={"UserName": "test_user", "PassWord": "test_password"},
         headers={
               "Content-Type": "application/json",
               "Application-Key": "mock_api_key"
         }
      )

class TestViews(TestCase):

   def setUp(self):
      self.user1 = User.objects.create(
         user_id="6510615888",
         password="password123",
         email_address="user1@example.com",
         name="John Doe",
         major="Computer Engineering",
         faculty="Engineering",
         year=3,
      )
      self.user2 = User.objects.create(
            user_id="660134999",
            password="password123",
            email_address="user2@example.com",
            name="Jane Smith",
            major="Civil Law",
            faculty="Law",
            year=2,
      )
      
   def test_login(self):
      """test """
      pass
   
   def test_index_return_homepage(self):
      """test if index return homepage"""
      c = Client()
      response = c.get("")
      self.assertEqual(response["Location"], "/homepage")
      self.assertEqual(response.status_code, 200)
   
   def test_aboutPage(self):
      """test if about page working correctly"""
      c = Client()
      response = c.get("/about")
      self.assertEqual(response["Location"], "/about")
      self.assertEqual(response.status_code, 200)

   def test_recruitmentPage(self):
      """test if recruitment page working correctly"""
      c = Client()
      response = c.get("/recruitment")
      self.assertEqual(response["Location"], "/recruitment")
      self.assertEqual(response.status_code, 200)
   
   def test_createPage(self):
      """test if create recruitment post page working correctly"""
      c = Client()
      response = c.get("/create")
      self.assertEqual(response["Location"], "/create")
      self.assertEqual(response.status_code, 200)
   
   def test_create_recruitment_post_valid(self):
      """test posting recruitment post with correct values"""
      c = Client()
      post_value = {
           "heading": "Health Hackathon",
            "content": "Need experience devs",
            "amount": 1,
            "tags": "Machine Learning, Data Science, Kaggle"
      }
      response = c.post("/create", data=post_value, follow=True)
      self.assertEqual(response.request['PATH_INFO'], "/create/requirement")
   
   def test_create_recruitment_post_invalid(self):
      """test posting recruitment post with incorrect values"""
      c = Client()
      post_value = {
           "heading": "Health Hackathon",
            "content": "12312",
            "amount": -10,
            "tags": ",,"
      }
      response = c.post("/create", data=post_value, follow=True)
      self.assertEqual(response.request['PATH_INFO'], "/create")

   def test_create_recruitment_post_lack(self):
      """test posting recruitment post with empty values"""
      c = Client()
      post_value = {
           "heading": None,
            "content": None,
            "amount": None,
            "tags": None
      }
      response = c.post("/create", data=post_value, follow=True)
      self.assertEqual(response.request['PATH_INFO'], "/create")
      
   def test_logout(self):
      """test if logout working correctly"""
      c = Client()
      response = c.get("/logout")
      self.assertEqual(response["Location"], "/login")
      self.assertEqual(response.status_code, 200)
