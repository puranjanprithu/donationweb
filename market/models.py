from market import db, bcrypt ,login_manager
from flask_login import UserMixin
from datetime import datetime
# UserMixin() is used to add is_authenticated,is_active, is_anonymous,get_id() methods to user class

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(50),nullable=False,unique=True)
    email_address=db.Column(db.String(58),nullable=False,unique=True)
    password_hash=db.Column(db.String(68),nullable=False,unique=True)
    budget=db.Column(db.Integer(), nullable=False , default=1000)
    items=db.relationship('Item',backref='owned_user', lazy=True)
    paymenet_details=db.relationship('PaymentDetail',backref='paymenet_details', lazy=True)

    def __repr__(self):
        return f'Iem {self.username}'
    
    @property 
    def password(self):
        return self.password
    
    @property
    def prettier_budget(self):
        if len(str(self.budget))>=4:
            return f'$ {str(self.budget)[:-3]},{str(self.budget)[-3:]}'
        else:
            return f"{self.budget}"
        
    @password.setter
    def password(self,plain_text_password):
        self.password_hash =bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self,item_obj):
        return self.budget >= item_obj.price  

    def can_sell(self,item_obj):
        return  item_obj in self.items

class Category(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(30),nullable=False, unique=True)
    item_detail=db.relationship('Item',backref='item_detail', lazy=True)
    def __repr__(self):
        return f" ('{self.id}','{self.name}') "

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30),nullable=False, unique=True)
    heading=db.Column(db.String(40),nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False,unique=True)
    price=db.Column(db.Integer(), nullable=False)
    raised=db.Column(db.Integer(), nullable=False,default=0)
    acheived = db.Column(db.Boolean(), nullable=False, default="False")

    category=db.Column(db.Integer(),db.ForeignKey('category.id'))
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    def __repr__(self):
        return f'{self.name}'

    def buy(self, user):
        self.owner= user.id
        user.budget -= self.price
        db.session.commit()
    
    def sell(self, user):
        self.owner= None
        user.budget += self.price
        db.session.commit()

class PaymentDetail(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    payment_amt=db.Column(db.Integer(), nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.now())
    user_id=db.Column(db.Integer(), db.ForeignKey('user.id'))
    item_id=db.Column(db.Integer(), db.ForeignKey('item.id'))
    item_name=db.Column(db.Integer(), db.ForeignKey('item.name'))


db.create_all()