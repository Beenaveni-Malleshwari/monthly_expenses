from .models import db, Expense, Category
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import func, extract

class ExpenseCRUD:
    @staticmethod
    def create_expense(amount, description, category, date=None):
        """Create a new expense record"""
        if date is None:
            date = datetime.utcnow()
        elif isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
            
        expense = Expense(
            amount=amount,
            description=description,
            category=category,
            date=date
        )
        db.session.add(expense)
        db.session.commit()
        return expense
    
    @staticmethod
    def get_expense(expense_id):
        """Get expense by ID"""
        return Expense.query.get(expense_id)
    
    @staticmethod
    def get_all_expenses():
        """Get all expenses ordered by date"""
        return Expense.query.order_by(Expense.date.desc()).all()
    
    @staticmethod
    def update_expense(expense_id, amount=None, description=None, category=None, date=None):
        """Update expense record"""
        expense = Expense.query.get(expense_id)
        if not expense:
            return None
            
        if amount is not None:
            expense.amount = amount
        if description is not None:
            expense.description = description
        if category is not None:
            expense.category = category
        if date is not None:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            expense.date = date
            
        db.session.commit()
        return expense
    
    @staticmethod
    def delete_expense(expense_id):
        """Delete expense record"""
        expense = Expense.query.get(expense_id)
        if expense:
            db.session.delete(expense)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_expenses_by_date_range(start_date, end_date):
        """Get expenses within date range"""
        return Expense.query.filter(
            Expense.date.between(start_date, end_date)
        ).order_by(Expense.date.desc()).all()
    
    @staticmethod
    def get_category_totals(start_date=None, end_date=None):
        """Get total amounts by category"""
        query = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        )
        
        if start_date and end_date:
            query = query.filter(Expense.date.between(start_date, end_date))
            
        return query.group_by(Expense.category).all()
    
    @staticmethod
    def get_monthly_totals(year=None):
        """Get monthly totals for the year"""
        if year is None:
            year = datetime.utcnow().year
            
        monthly_totals = db.session.query(
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(extract('year', Expense.date) == year)\
         .group_by(extract('month', Expense.date))\
         .order_by('month').all()
        
        return monthly_totals
    
    @staticmethod
    def get_expenses_dataframe(start_date=None, end_date=None):
        """Convert expenses to pandas DataFrame for analysis"""
        if start_date and end_date:
            expenses = Expense.query.filter(
                Expense.date.between(start_date, end_date)
            ).all()
        else:
            expenses = Expense.query.all()
            
        data = [expense.to_dict() for expense in expenses]
        return pd.DataFrame(data)

class CategoryCRUD:
    @staticmethod
    def create_category(name, budget_limit=0.0, color='#007bff'):
        """Create a new category"""
        category = Category(name=name, budget_limit=budget_limit, color=color)
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def get_all_categories():
        """Get all categories"""
        return Category.query.all()
    
    @staticmethod
    def get_category(category_id):
        """Get category by ID"""
        return Category.query.get(category_id)
    
    @staticmethod
    def update_category(category_id, name=None, budget_limit=None, color=None):
        """Update category"""
        category = Category.query.get(category_id)
        if not category:
            return None
            
        if name is not None:
            category.name = name
        if budget_limit is not None:
            category.budget_limit = budget_limit
        if color is not None:
            category.color = color
            
        db.session.commit()
        return category
    
    @staticmethod
    def delete_category(category_id):
        """Delete category"""
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False