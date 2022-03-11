from unittest import TestCase

from app import app
from models import db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Tests for views for Users."""
    
    def setUp(self):
        """Add a test user."""
        
        User.query.delete()
        
        user = User(first_name = "Test", last_name = "User")
        db.session.add(user)
        db.session.commit()
        
        self.user_id = user.id
        self.user = user
        
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        
    def test_list_users(self):
        """Test the home route and listing users."""
        with app.test_client() as client:
            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test User', html)
            
    def test_show_user(self):
        """Test showing a user."""
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Test User</h1>', html)
            self.assertIn("https://images.unsplash.com/photo-1533738363-b7f9aef128ce?ixlib=rb-1.2.1&amp;ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&amp;auto=format&amp;fit=crop&amp;w=735&amp;q=80", html)
            
    def test_add_user(self):
        """Test adding user."""
        with app.test_client() as client:
            data = {"first-name": "FirstTest2", "last-name": "LastTest2", "image-url": "https://images.unsplash.com/photo-1491609154219-ffd3ffafd992?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"}
            resp = client.post("/users/new", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>FirstTest2 LastTest2</h1>", html)

    def test_edit_user(self):
        """Test editing a user."""
        with app.test_client() as client:    
            data = {"first-name": "EditTest", "last-name": "EditUser", "image-url": "https://images.unsplash.com/photo-1491609154219-ffd3ffafd992?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"}
            resp = client.post(f"/users/{self.user_id}/edit", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>EditTest EditUser</h1>", html)
            
    def test_delete_user(self):
        """Test deleting a user."""
        with app.test_client() as client:
            resp = client.post(f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">All Users</h1>', html)
            self.assertNotIn('Test User', html)
            
    def test_new_post_form_route(self):
        """Test the route to show form for new posts."""
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/posts/new")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>New Post for {self.user.full_name}</h1>', html)
            
    def test_adding_new_post(self):
        """Test adding new post to database."""
        with app.test_client() as client:    
            data = {'title': 'Test Title', 'content': 'Test Content', 'user_id': self.user_id}
            resp = client.post(f"/users/{self.user_id}/posts/new", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>{self.user.full_name}</h1>', html)