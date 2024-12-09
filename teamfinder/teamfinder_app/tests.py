from django.test import TestCase, Client
from django.contrib.messages import get_messages
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from teamfinder_app.tuapi import auth, get_user_info
from django.urls import reverse
from taggit.models import Tag
from django.contrib.auth import authenticate, login, logout, get_user, get_user_model
from teamfinder_app.models import *
from chat.models import *


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
      User = get_user_model()

      self.u1 = User.objects.create_user(
         username="6510615888",
         password="password123",
         email_address="user1@example.com",
         name="John Doe",
         major="CPE",
         faculty="ENGR",
         year=3,
      )
      UserProfile.objects.create(user=self.u1)

      self.u2 = User.objects.create_user(
         username="6601349999",
         password="password123",
         email_address="user2@example.com",
         name="Jane Smith",
         major="CS",
         faculty="SCI",
         year=2,
      )
      UserProfile.objects.create(user=self.u2)

      users = [self.u1, self.u2]
      posts = []
      recruit_posts = []
      result_posts = []
      tags = []
      faculty = ["ENGR", "SCI"]
      major = ["CPE", "CS"]

      #Create Faculty and Major tags
      Faculty.objects.create(name="ENGR",slug="ENGR",faculty="ENGR")
      Faculty.objects.create(name="SCI",slug="SCI",faculty="SCI")

      Major.objects.create(name="CPE",slug="CPE",major="CPE")
      Major.objects.create(name="CS",slug="CS",major="CS")
      
      #Create Tag
      for v in range(10):
         Tag.objects.create(name=f"T{v}")
         tags.append(f"T{v}")

      #Create Post
      for v in range(20):
         post = Post.objects.create(
            user=users[v%2],
            heading=f"H{v}",
            content=f"C{v}",
            finish=False,
         )
         posts.append(post)

      #Create RecruitPost
      for v in range(15):
         recruit = RecruitPost.objects.create(
            post=posts[v],
            status=True if v%2 else False,
         )
         a_tag = [tags[v%10]] if v%2 else tags[:v%10+1]
         recruit.tag.set(a_tag)
         recruit.save()
         recruit_posts.append(recruit)

      #Create Requirement
      for v in range(15):
         requirement = Requirement.objects.create(
            post=recruit_posts[v],
            year_min=1,
            year_max=v%6+1,
            description=f"requirement {v}"
         )
         req_faculty = faculty if v%3 == 2 else [faculty[v%2]]
         req_major = major if v%3 == 2 else [major[v%2]]
         requirement.req_faculty.set(req_faculty)
         requirement.req_major.set(req_major)

      #Create ResultPost
      for v in range(15, 20):
         post = posts[v]
         post.status = False
         post.finish = True
         post.save()
         result = ResultPost.objects.create(
            post=posts[v],
         )
         a_tag = [tags[v%10]] if v%2 else tags[:v%10+1]
         result.tag.set(a_tag)
         result.save()
         result_posts.append(result)

      #Create PostComment of posts[0]
      for v in range(7):
         PostComment.objects.create(
            post=posts[0],
            user=users[v%2],
            comment=f"Comment {v}",
            reaction="",
         )

      #Create Team and Chat Group
      for v in range(20):
         team = Team.objects.create(
            team_leader=posts[v].user,
            recruit_post=posts[v]
         )
         TeamMember.objects.create(
            team=team,
            member=posts[v].user
         )
         chat_group = ChatGroup.objects.create(
            team=team,
            admin=posts[v].user
         )
         chat_group.members.add(posts[v].user)

   def test_myaccount_case1(self):
      """test myacoount access"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get('/myaccount')
      self.assertEqual(response.request["PATH_INFO"], "/myaccount")
      self.assertEqual(response.status_code, 200) 
      self.assertEqual(response.context["username"], "6510615888")

   def test_myaccount_case2(self):
      """test myacoount access : POST Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      image_file = SimpleUploadedFile(
            name='test_image.png',
            content=b'file_content',
            content_type='image/jpeg'
        )
      data = {
         "form": image_file
      }
      response = c.post('/myaccount', data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/myaccount")
      self.assertEqual(response.status_code, 200) 
      self.assertEqual(response.context["username"], "6510615888")

   def test_my_stats_case1(self):
      """test my stats : No Feedback"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get('/mystats', follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/mystats")
      self.assertEqual(response.status_code, 200) 
      self.assertFalse(response.context["feedback"])

   def test_my_stats_case2(self):
      """test my stats : Has Feedback"""

      c = Client()
      c.login(username="6510615888", password="password123")
      Feedback.objects.create(
         team=Team.objects.get(team_id=1),
         reviewer=self.u2,
         receiver=self.u1,
         communication_pt=2,
         collaboration_pt=2,
         reliability_pt=2,
         technical_pt=2,
         empathy_pt=2,
         comment="NO"
      )
      response = c.get('/mystats', follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/mystats")
      self.assertEqual(response.status_code, 200) 
      self.assertTrue(response.context["feedback"])

   def test_homepage(self):
      """test homepage access"""

      c = Client()
      response = c.get("")
      self.assertEqual(response.request["PATH_INFO"], "")
      self.assertEqual(response.status_code, 200)

   def test_about(self):
      """test about access"""

      c = Client()
      response = c.get("/about")
      self.assertEqual(response.request["PATH_INFO"], "/about")
      self.assertEqual(response.status_code, 200)

   def test_logout(self):
      """test logout"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/logout", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/login")
      self.assertEqual(response.status_code, 200)

   def test_recruitment(self):
      """test recruitment send all recruit post that status = True"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/recruitment")
      self.assertEqual(response.request["PATH_INFO"], "/recruitment")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["posts"]), 7)
   
   def test_result(self):
      """test result send all result post"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/result")
      self.assertEqual(response.request["PATH_INFO"], "/result")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["posts"]), 5)
   
   def test_web_post_case1(self):
      """test web_post
         case1 : Successful
         who   : post's owner
      """

      c = Client()
      c.login(username="6510615888", password="password123")
      post = Post.objects.get(post_id=1)
      response = c.get("/post/1")
      self.assertEqual(response.request["PATH_INFO"], "/post/1")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["post_id"]), 1)
      self.assertTrue(response.context["is_owner"])
      self.assertTrue(response.context["is_recruit"])
      self.assertFalse(response.context["status"])
      self.assertFalse(response.context["requestable"])
      self.assertFalse(response.context["is_requested"])
      self.assertEqual(response.context["comments"].count(), 7)
       
   def test_web_post_case2(self):
      """test web_post
         case2 : Post doesn't exist
         who   : any
      """

      c = Client()
      c.login(username="6601349999", password="password123")
      response = c.get("/post/100")
      self.assertEqual(response.request["PATH_INFO"], "/post/100")
      self.assertEqual(response.status_code, 404)
      
   def test_web_post_case3(self):
      """test web_post
         case3 : can request
         who   : requestable person
      """

      c = Client()
      c.login(username="6510615888", password="password123")
      requirement = Requirement.objects.get(require_id=2)
      requirement.req_faculty.set(["ENGR", "SCI"])
      requirement.save()
      response = c.get("/post/2")
      self.assertEqual(response.request["PATH_INFO"], "/post/2")
      self.assertEqual(response.status_code, 200)
      self.assertTrue(response.context["requestable"])
      self.assertFalse(response.context["is_requested"])

   def test_web_comment_case1(self):
      """test web_comment : Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.post("/comment/1", data={"comment": "YO"}, follow=True)
      n_comment = PostComment.objects.filter(post=Post.objects.get(post_id=1)).count()
      self.assertEqual(response.request["PATH_INFO"], "/post/1")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(n_comment, 8)

   def test_web_comment_case2(self):
      """test web_comment : Post doesn't exist"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.post("/comment/90", data={"comment": "YO"}, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/comment/90")
      self.assertEqual(response.status_code, 404)

   def test_web_comment_case3(self):
      """test web_comment : Comment with blank"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.post("/comment/1", data={"comment": ""}, follow=True)
      n_comment = PostComment.objects.filter(post=Post.objects.get(post_id=1)).count()
      message = str(list(get_messages(response.wsgi_request))[0])
      self.assertEqual(response.request["PATH_INFO"], "/post/1")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(n_comment, 7)
      self.assertEqual(message, 'Please input something')

   def test_create_post_case1(self):
      """test create post : GET"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/create")
      self.assertEqual(response.request["PATH_INFO"], "/create")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["tag_list"]), 10)

   def test_create_post_case2(self):
      """test create post : POST successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      data = {
         "heading": "LOL 5 v 5",
         "content": "Pentakill",
         "tags": "T1, T20"
      }
      response = c.post("/create", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/create/requirement")
      self.assertEqual(response.status_code, 200)
      self.assertTrue(c.session['visited_create'])

   def test_create_post_case3(self):
      """test create post : POST invalid value"""

      c = Client()
      c.login(username="6510615888", password="password123")
      data = {
         "heading": "",
         "content": "",
         "tags": "T1, T20, T4, T5"
      }
      response = c.post("/create", data=data, follow=True)
      message = list(get_messages(response.wsgi_request))
      self.assertEqual(response.request["PATH_INFO"], "/create")
      self.assertEqual(response.status_code, 200)
      self.assertFalse(c.session['visited_create'])
      self.assertEqual(response.context["heading"], data["heading"])
      self.assertEqual(response.context["content"], data["content"])
      self.assertEqual(response.context["tags"], data["tags"])
      self.assertEqual(len(message), 3)

   def test_web_requirement_case1(self):
      """test web requirement : GET"""

      c = Client()
      c.login(username="6510615888", password="password123")
      session = c.session
      session["visited_create"] = True
      session.save()
      response = c.get("/create/requirement", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/create/requirement")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["faculty_list"]), 2)
      self.assertEqual(len(response.context["major_list"]), 2)

   def test_web_requirement_case2(self):
      """test web requirement : GET w/o visit create before"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/create/requirement", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/create")
      self.assertEqual(response.status_code, 200) #final status code

   def test_web_requirement_case3(self):
      """test web requirement : POST successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      session = c.session
      session["visited_create"] = True
      session["heading"] = "LOL 5 v 5"
      session["content"] = "Pentakill"
      session["tags"] = "T1, T20"
      session.save()
      data = {
         "req_faculty": "ENGR",
         "req_major": "CS",
         "min_year": "1",
         "max_year": "8",
         "description": "1 v 1 Me"
      }
      response = c.post("/create/requirement", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/recruitment")
      self.assertEqual(response.status_code, 200) #final status code
      self.assertEqual(Post.objects.all().count(), 21)
      self.assertEqual(RecruitPost.objects.all().count(), 16)
      self.assertEqual(Requirement.objects.all().count(), 16)
      self.assertEqual(Team.objects.all().count(), 21)
      self.assertEqual(TeamMember.objects.all().count(), 21)

   def test_web_requirement_case4(self):
      """test web requirement : POST invalid value"""

      c = Client()
      c.login(username="6510615888", password="password123")
      session = c.session
      session["visited_create"] = True
      session["heading"] = "LOL 5 v 5"
      session["content"] = "Pentakill"
      session["tags"] = "T1, T20"
      session.save()
      data = {
         "req_faculty": "",
         "req_major": "",
         "min_year": "5",
         "max_year": "4",
         "description": ""
      }
      response = c.post("/create/requirement", data=data, follow=True)
      message = list(get_messages(response.wsgi_request))
      self.assertEqual(response.request["PATH_INFO"], "/create/requirement")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(message), 2)
      self.assertEqual(Post.objects.all().count(), 20)
      self.assertEqual(Team.objects.all().count(), 20)
      self.assertEqual(TeamMember.objects.all().count(), 20)

   def test_web_request_case1(self):
      """test request : Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      requirement = Requirement.objects.get(require_id=2)
      requirement.req_faculty.set(["ENGR", "SCI"])
      requirement.save()
      response = c.post("/request/2", data={"message": "ขอเข้าร่วมด้วยงับ"}, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/post/2")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Request.objects.all().count(), 1)

   def test_web_request_case2(self):
      """test request : Invalid"""

      c = Client()
      c.login(username="6510615888", password="password123")
      requirement = Requirement.objects.get(require_id=2)
      requirement.req_faculty.set([])
      requirement.req_major.set([])
      requirement.save()
      response = c.post("/request/2", data={"message": "ขอเข้าร่วมด้วยงับ"}, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Request.objects.all().count(), 0)

   def test_web_request_case3(self):
      """test request : Recruit post doesn't exist"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.post("/request/200", data={"message": "ขอเข้าร่วมด้วยงับ"}, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Request.objects.all().count(), 0)

   def test_teams(self):
      """test teams"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/teams", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/teams")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["active"]), 8)
      self.assertEqual(len(response.context["finished"]), 2)

   def test_team_case1(self):
      """test team : Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/team/19", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/team/19")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(str(response.context["team_id"]), "19")
      self.assertEqual(len(response.context["members"]), 1)
      self.assertTrue(response.context["is_owner"])
      self.assertTrue(response.context["is_finish"])

   def test_team_case2(self):
      """test team : Invalid user in team"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/team/18", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/team/18")
      self.assertEqual(response.status_code, 404)

   def test_finish_case1(self): 
      """test finish : Successful, not post result"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/finish/1/no", follow=True)
      post = Post.objects.get(post_id=1)
      recruit = RecruitPost.objects.filter(post=post).first()
      self.assertEqual(response.request["PATH_INFO"], "/team/1")
      self.assertEqual(response.status_code, 200)
      self.assertTrue(post.finish)
      self.assertFalse(recruit)

   def test_finish_case2(self):
      """test finish : Successful, w/ post result"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/finish/1/yes", follow=True)
      post = Post.objects.get(post_id=1)
      recruit = RecruitPost.objects.filter(post=post).first()
      self.assertEqual(response.request["PATH_INFO"], "/post_result/1")
      self.assertEqual(response.status_code, 200)
      self.assertTrue(post.finish)
      self.assertFalse(recruit)

   def test_finish_case3(self): 
      """test finish : Fail, not met conditions"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response_1 = c.get("/finish/100/yes", follow=True)
      response_2 = c.get("/finish/2/yes", follow=True)
      response_3 = c.get("/finish/1/something", follow=True)
      self.assertEqual(response_1.request["PATH_INFO"], "/finish/100/yes")
      self.assertEqual(response_1.status_code, 404)
      self.assertEqual(response_2.request["PATH_INFO"], "/finish/2/yes")
      self.assertFalse(Post.objects.get(post_id=2).finish)
      self.assertEqual(response_2.status_code, 404)
      self.assertEqual(response_3.request["PATH_INFO"], "/finish/1/something")
      self.assertFalse(Post.objects.get(post_id=1).finish)
      self.assertEqual(response_3.status_code, 404)

   def test_finish_case4(self): 
      """test finish : Fail, already finish"""

      c = Client()
      c.login(username="6601349999", password="password123")
      post = Post.objects.get(post_id=2)
      post.finish = True
      post.save()
      response = c.get("/finish/2/yes", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/finish/2/yes")
      self.assertEqual(response.status_code, 404)

   def test_post_result_case1(self): 
      """test post result : GET"""

      c = Client()
      c.login(username="6510615888", password="password123")
      post = Post.objects.get(post_id=1)
      post.finish = True
      post.save()
      response = c.get("/post_result/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/post_result/1")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.context["heading"], "H0")

   def test_post_result_case2(self):
      """test post result : POST successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      data = {
         "heading": "เสร็จแล้วโว้ย",
         "content": "เสร็จจริงๆนะ",
         "tags": "T1, T2"
      }
      post = Post.objects.get(post_id=1)
      recruit = RecruitPost.objects.get(post=post)
      post.finish = True
      recruit.status = False
      post.save()
      recruit.save()
      response = c.post("/post_result/1", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/result")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Post.objects.get(post_id=1).heading, "เสร็จแล้วโว้ย")
      self.assertEqual(ResultPost.objects.all().count(), 6)

   def test_post_result_case3(self): 
      """test post result : POST ivalid value"""

      c = Client()
      c.login(username="6510615888", password="password123")
      data = {
         "heading": "เสร็จแล้วโว้ย",
         "content": "",
         "tags": ""
      }
      post = Post.objects.get(post_id=1)
      recruit = RecruitPost.objects.get(post=post)
      post.finish = True
      recruit.status = False
      post.save()
      recruit.save()
      response = c.post("/post_result/1", data=data, follow=True)
      message = str(list(get_messages(response.wsgi_request))[0])
      self.assertEqual(response.request["PATH_INFO"], "/post_result/1")
      self.assertEqual(response.status_code, 200)
      self.assertNotEqual(post.heading, "เสร็จแล้วโว้ย")
      self.assertEqual(ResultPost.objects.all().count(), 5)
      self.assertEqual(message, 'Must fill every field')

   def test_post_result_case4(self):
      """test post result : Fail, not met conditions"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/post_result/100", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/post_result/100")
      self.assertEqual(response.status_code, 404)

   def test_feedback_case1(self):
      """test feedback : GET"""

      c = Client()
      c.login(username="6510615888", password="password123")
      another_user = User.objects.get(username="6601349999")
      TeamMember.objects.create(
         team=Team.objects.get(team_id=1),
         member=another_user
      )
      post = Post.objects.get(post_id=1)
      post.finish = True
      post.save()
      response = c.get("/feedback/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/feedback/1")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["feedback_forms"]), 1)

   def test_feedback_case2(self):
      """test feedback : POST successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      another_user = User.objects.get(username="6601349999")
      TeamMember.objects.create(
         team=Team.objects.get(team_id=1),
         member=another_user
      )
      data = {
         "feedback_6601349999-communication_pt": 1,
         "feedback_6601349999-collaboration_pt": 1,
         "feedback_6601349999-reliability_pt": 1,
         "feedback_6601349999-technical_pt": 1,
         "feedback_6601349999-empathy_pt": 1,
         "feedback_6601349999-comment": "1 for all"
      }
      post = Post.objects.get(post_id=1)
      post.finish = True
      post.save()
      response = c.post("/feedback/1", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/teams")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Feedback.objects.all().count(), 1)

   def test_feedback_case3(self):
      """test feedback : POST invalid value"""

      c = Client()
      c.login(username="6510615888", password="password123")
      another_user = User.objects.get(username="6601349999")
      TeamMember.objects.create(
         team=Team.objects.get(team_id=1),
         member=another_user
      )
      data = {
         "feedback_6601349999-communication_pt": "",
         "feedback_6601349999-collaboration_pt": "",
         "feedback_6601349999-reliability_pt": "",
         "feedback_6601349999-technical_pt": "",
         "feedback_6601349999-empathy_pt": "",
         "feedback_6601349999-comment": ""
      }
      post = Post.objects.get(post_id=1)
      post.finish = True
      post.save()
      response = c.post("/feedback/1", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/teams")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(Feedback.objects.all().count(), 0)

   def test_feedback_case4(self):
      """test feedback : Fail, not met conditions"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/feedback/100", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/feedback/100")
      self.assertEqual(response.status_code, 404)

   def test_status_case1(self):
      """test status : Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      status_before = RecruitPost.objects.get(post_id=1).status
      response = c.get("/status/1", follow=True)
      status_after = RecruitPost.objects.get(post_id=1).status
      self.assertEqual(response.request["PATH_INFO"], "/post/1")
      self.assertEqual(response.status_code, 200)
      self.assertNotEqual(status_after, status_before)

   def test_status_case2(self):
      """test status : Fail, post doesn't exist"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/status/100", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/status/100")
      self.assertEqual(response.status_code, 404)
   
   def test_status_case3(self):
      """test status : Fail, not owner"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/status/2", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/status/2")
      self.assertEqual(response.status_code, 404)

   def test_accept_case1(self):
      """test accept : Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      Request.objects.create(
         post=Post.objects.get(post_id=1),
         user=self.u2,
         message="ขอเข้าร่วม",
         requirement=Requirement.objects.get(require_id=1)
      )
      response = c.get("/accept/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/team/1")
      self.assertEqual(response.status_code, 200)
      self.assertFalse(Request.objects.all().count())
      self.assertEqual(TeamMember.objects.all().count(), 21)

   def test_accept_case2(self):
      """test accept : Fail, request doesn't exist"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/accept/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/accept/1")
      self.assertEqual(response.status_code, 404)

   def test_accept_case3(self):
      """test accept : Fail, not post owner"""

      c = Client()
      c.login(username="6601349999", password="password123")
      Request.objects.create(
         post=Post.objects.get(post_id=1),
         user=self.u2,
         message="ขอเข้าร่วม",
         requirement=Requirement.objects.get(require_id=1)
      )
      response = c.get("/accept/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/accept/1")
      self.assertEqual(response.status_code, 404)
      self.assertEqual(Request.objects.all().count(), 1)

   def test_decline_case1(self):
      """test decline : Successful"""

      c = Client()
      c.login(username="6510615888", password="password123")
      Request.objects.create(
         post=Post.objects.get(post_id=1),
         user=self.u2,
         message="ขอเข้าร่วม",
         requirement=Requirement.objects.get(require_id=1)
      )
      response = c.get("/decline/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/team/1")
      self.assertEqual(response.status_code, 200)
      self.assertFalse(Request.objects.all().count())
      self.assertEqual(TeamMember.objects.all().count(), 20)

   def test_decline_case2(self):
      """test decline : Fail, request doesn't exist"""

      c = Client()
      c.login(username="6510615888", password="password123")
      response = c.get("/decline/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/decline/1")
      self.assertEqual(response.status_code, 404)

   def test_decline_case3(self):
      """test decline : Fail, not post owner"""

      c = Client()
      c.login(username="6601349999", password="password123")
      Request.objects.create(
         post=Post.objects.get(post_id=1),
         user=self.u2,
         message="ขอเข้าร่วม",
         requirement=Requirement.objects.get(require_id=1)
      )
      response = c.get("/decline/1", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/decline/1")
      self.assertEqual(response.status_code, 404)
      self.assertEqual(Request.objects.all().count(), 1)

   def test_search_recruit_case1(self):
      """test serach recruit : Successful"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "search": "T1, T2, T3"
      }
      response = c.post("/recruitment/search", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/recruitment/search")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.context["posts"].count(), 4)

   def test_search_recruit_case2(self):
      """test serach recruit : Fail, empty query"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "search": ""
      }
      response = c.post("/recruitment/search", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/recruitment")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["posts"]), 7)

   def test_search_recruit_case3(self):
      """test serach recruit : GET method"""

      c = Client()
      c.login(username="6601349999", password="password123")
      response = c.get("/recruitment/search", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/recruitment")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["posts"]), 7)

   def test_search_result_case1(self):
      """test serach result : Successful"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "search": "T1, T2, T3"
      }
      response = c.post("/result/search", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/result/search")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.context["posts"].count(), 2)

   def test_search_result_case2(self):
      """test serach result : Fail, empty query"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "search": ""
      }
      response = c.post("/result/search", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/result")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["posts"]), 5)

   def test_search_result_case3(self):
      """test serach result : GET method"""

      c = Client()
      c.login(username="6601349999", password="password123")
      response = c.get("/result/search", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/result")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.context["posts"]), 5)

   def test_profile_page_case1(self):
      """test profile page : Successful"""

      c = Client()
      c.login(username="6601349999", password="password123")
      response = c.get("/profile/6601349999", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/profile/6601349999")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.context["user"], User.objects.get(username="6601349999"))

   def test_profile_page_case2(self):
      """test profile page : Fail, user doesn't exist"""

      c = Client()
      c.login(username="6601349999", password="password123")
      response = c.get("/profile/6601349991", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/profile/6601349991")
      self.assertEqual(response.status_code, 404)

   def test_edit_recruitment_case1(self):
      """test edit recruitment : GET"""

      c = Client()
      c.login(username="6601349999", password="password123")
      heading = Post.objects.get(post_id=2).heading
      response = c.get("/recruitment/edit/2", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/recruitment/edit/2")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(heading, response.context["heading"])

   def test_edit_recruitment_case2(self):
      """test edit recruitment : POST Successful"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "heading": "LOL",
         "content": "ROV",
         "tags": "T1, T2, T3"
      }
      response = c.post("/recruitment/edit/2", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/post/2")
      self.assertEqual(response.status_code, 200)
      self.assertEqual("LOL", Post.objects.get(post_id=2).heading)
      self.assertEqual(3, RecruitPost.objects.get(post_id=2).tag.all().count())

   def test_edit_recruitment_case3(self):
      """test edit recruitment : Fail, post doesn't exist, doesn't owner"""

      c = Client()
      c.login(username="6601349999", password="password123")
      response_1 = c.get("/recruitment/edit/1", follow=True)
      response_2 = c.get("/recruitment/edit/100", follow=True)
      self.assertEqual(response_1.request["PATH_INFO"], "/recruitment/edit/1")
      self.assertEqual(response_1.status_code, 404)
      self.assertEqual(response_2.request["PATH_INFO"], "/recruitment/edit/100")
      self.assertEqual(response_2.status_code, 404)
      
   def test_edit_recruitment_case4(self):
      """test edit recruitment : POST invalid value"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "heading": "",
         "content": "",
         "tags": "T1, T2, T3, T4"
      }
      response = c.post("/recruitment/edit/2", data=data, follow=True)
      message = list(get_messages(response.wsgi_request))
      self.assertEqual(response.request["PATH_INFO"], "/recruitment/edit/2")
      self.assertEqual(response.status_code, 200)
      self.assertEqual("T1, T2, T3, T4", response.context["tags"])
      self.assertNotEqual(response.context["heading"], Post.objects.get(post_id=2).heading)
      self.assertEqual(len(message), 3)

   def test_edit_result_case1(self):
      """test edit result : GET"""

      c = Client()
      c.login(username="6601349999", password="password123")
      heading = Post.objects.get(post_id=16).heading
      response = c.get("/result/edit/16", follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/result/edit/16")
      self.assertEqual(response.status_code, 200)
      self.assertEqual(heading, response.context["heading"])

   def test_edit_result_case2(self):
      """test edit result : POST Successful"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "heading": "LOL",
         "content": "ROV",
         "tags": "T1, T2, T3"
      }
      response = c.post("/result/edit/16", data=data, follow=True)
      self.assertEqual(response.request["PATH_INFO"], "/post/16")
      self.assertEqual(response.status_code, 200)
      self.assertEqual("LOL", Post.objects.get(post_id=16).heading)
      self.assertEqual(3, ResultPost.objects.get(post_id=16).tag.all().count())

   def test_edit_result_case3(self):
      """test edit result : Fail, post doesn't exist, doesn't owner"""

      c = Client()
      c.login(username="6601349999", password="password123")
      response_1 = c.get("/result/edit/17", follow=True)
      response_2 = c.get("/result/edit/100", follow=True)
      self.assertEqual(response_1.request["PATH_INFO"], "/result/edit/17")
      self.assertEqual(response_1.status_code, 404)
      self.assertEqual(response_2.request["PATH_INFO"], "/result/edit/100")
      self.assertEqual(response_2.status_code, 404)
      
   def test_edit_result_case4(self):
      """test edit result : POST invalid value"""

      c = Client()
      c.login(username="6601349999", password="password123")
      data = {
         "heading": "",
         "content": "",
         "tags": "T1, T2, T3, T4"
      }
      response = c.post("/result/edit/16", data=data, follow=True)
      message = list(get_messages(response.wsgi_request))
      self.assertEqual(response.request["PATH_INFO"], "/result/edit/16")
      self.assertEqual(response.status_code, 200)
      self.assertEqual("T1, T2, T3, T4", response.context["tags"])
      self.assertNotEqual(response.context["heading"], Post.objects.get(post_id=16).heading)
      self.assertEqual(len(message), 3)