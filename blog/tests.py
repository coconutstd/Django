from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User

def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name = name,
        description = description
    )

    return category

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category,
    )

    return blog_post

class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def test_category(self):
        category = create_category()

        post_000 = create_post(
            title='The first post',
            content='Hello World. We are the world',
            author=self.author_000,
            category=category,
        )

        self.assertEqual(category.post_set.count(), 1)

    def test_post(self):
        category = create_category()
        post_000 = create_post(
            title='The first post',
            content='Hello World. We are the world',
            author=self.author_000,
            category=category,
        )


# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def check_nav_bar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        self.assertIn('미분류 (1)', category_card.text)  #### 미분류 (1) 있어야 함
        self.assertIn('정치/사회 (1)', category_card.text)  #### 정치/사회 (1) 있어야 함



    def test_post_list_no_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, 'Blog')

        self.check_nav_bar(soup)
        # navbar = soup.find('div', id='navbar')
        # self.assertIn('Blog', navbar.text)
        # self.assertIn('About me', navbar.text)

        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다',soup.body.text)

    def test_post_list_with_post(self):
        post_000 = create_post(
            title = 'The first post',
            content='Hello World. We are the world',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The Second post',
            content='Seconde Second Second',
            author=self.author_000,
            category=create_category(name='정치/사회')
        )

        self.assertGreater(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다', body.text)
        self.assertIn(post_000.title, body.text)

        # category card 에서
        self.check_right_side(body)

        main_div = soup.find('div', id='main_div')
        self.assertIn('정치/사회', main_div.text)  #### 첫번째 포스트에는 '정치/사회' 있어야 함
        self.assertIn('미분류', main_div.text)  #### 두번째 포스트에는 '미분류' 있어야 함


    def test_post_detail(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World. We are the world',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The Second post',
            content='Seconde Second Second',
            author=self.author_000,
            category=create_category(name='정치/사회')
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000.get_absolute_url(), '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))

        self.check_nav_bar(soup)

        self.check_right_side(soup)