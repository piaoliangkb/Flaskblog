from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post

def users(count=100):
    faker = Faker()
    i = 0
    while i < count:
        u = User(email=faker.email(), username=faker.user_name(),
                 password='password',
                 name=faker.name(), location=faker.city(),
                 about_me=faker.text(), member_since=faker.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        # 防止faker生成重复的用户名和电子邮件，如果重复则抛出异常
        except IntegrityError:
            db.session.rollback()

def posts(count=100):
    faker = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count-1)).first()
        p = Post(body=faker.text(), timestamp=faker.past_date(), author=u)
        db.session.add(p)
    db.session.commit()