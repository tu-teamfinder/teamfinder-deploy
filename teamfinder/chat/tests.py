from django.test import TestCase, Client
from taggit.models import Tag
from teamfinder_app.models import *
from django.contrib.auth import get_user_model
from chat.models import *
from chat.forms import *




# Create your tests here.
class TestChatViews(TestCase):

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

        self.u3 = User.objects.create_user(
            username="6601347777",
            password="password123",
            email_address="user3@example.com",
            name="Jong Jong",
            major="CS",
            faculty="SCI",
            year=1,
        )
        UserProfile.objects.create(user=self.u3)

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
        
    def test_access_chat_as_member(self):
        """test access chat as member"""

        c = Client()
        c.login(username="6510615888", password="password123")
        response = c.get('/chat/1')
        self.assertEqual(response.request["PATH_INFO"], "/chat/1")
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.context["group_id"], "1")

    def test_access_chat_not_member(self):
        """test access chat as not member"""

        c = Client()
        c.login(username="6601349999", password="password123")
        response = c.get('/chat/1')
        self.assertEqual(response.request["PATH_INFO"], "/chat/1")
        self.assertEqual(response.status_code, 404) 
    
    def test_access_chat_default_group(self):
        """test access chat as member with default group id"""

        c = Client()
        c.login(username="6510615888", password="password123")
        response = c.get('/chat/default')
        self.assertEqual(response.request["PATH_INFO"], "/chat/default")
        self.assertEqual(response.status_code, 302) 
        response = c.get("/chat/default", follow=True)
        self.assertEqual(response.request["PATH_INFO"], "/chat/1")
        self.assertEqual(response.status_code, 200)
    
    def test_group_message_creation(self):
        """Test that GroupMessage instances are created correctly."""
        c = Client()
        c.login(username="6510615888", password="password123")
        data={'body': 'This is a test message.'}
        response = c.post('/chat/1', data, follow=True)
    
    def test_htmx_message_creation(self):
        """Test creating a chat message with an HTMX request."""
        c = Client()
        c.login(username="6510615888", password="password123")
        user = self.u1
        # Simulate an HTMX request
        data = {"body": "Test message"}
        headers = {"HTTP_HX-Request": "true"}  # HTMX header
        response = c.post('/chat/1', data, **headers)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'chat_message_p.html')
        
        # Validate the message object creation
        self.assertEqual(GroupMessage.objects.count(), 1)
        message = GroupMessage.objects.first()
        self.assertEqual(message.body, "Test message")
        self.assertEqual(message.author, user)
        self.assertEqual(message.group, ChatGroup.objects.filter(members=user).first())

        # Check context in response
        self.assertIn('message', response.context)
        self.assertIn('user', response.context)
        self.assertEqual(response.context['message'], message)
        self.assertEqual(response.context['user'], user)
    
    def test_access_chat_no_chat(self):
        """test access chat as you don't have any team yet"""
        c = Client()
        c.login(username="6601347777", password="password123")
        response = c.get('/chat/default')
        self.assertEqual(response.request["PATH_INFO"], "/chat/default")
        self.assertEqual(response.status_code, 200) 

