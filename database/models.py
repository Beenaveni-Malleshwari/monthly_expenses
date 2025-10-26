from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd

db = SQLAlchemy()

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    budget_limit = db.Column(db.Float, default=0.0)
    color = db.Column(db.String(7), default='#007bff')  # Hex color
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'budget_limit': self.budget_limit,
            'color': self.color
        }