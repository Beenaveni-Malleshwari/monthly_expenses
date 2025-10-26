from .models import db, Category

def init_default_categories():
    """Initialize default categories if they don't exist"""
    default_categories = [
        {'name': 'Food', 'budget_limit': 300, 'color': '#FF6384'},
        {'name': 'Transport', 'budget_limit': 200, 'color': '#36A2EB'},
        {'name': 'Entertainment', 'budget_limit': 150, 'color': '#FFCE56'},
        {'name': 'Shopping', 'budget_limit': 250, 'color': '#4BC0C0'},
        {'name': 'Bills', 'budget_limit': 400, 'color': '#9966FF'},
        {'name': 'Healthcare', 'budget_limit': 100, 'color': '#FF9F40'},
        {'name': 'Education', 'budget_limit': 200, 'color': '#FF6384'},
        {'name': 'Other', 'budget_limit': 100, 'color': '#C9CBCF'}
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data['name']).first():
            category = Category(
                name=cat_data['name'],
                budget_limit=cat_data['budget_limit'],
                color=cat_data['color']
            )
            db.session.add(category)
    
    db.session.commit()