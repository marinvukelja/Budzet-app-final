# Budget Management Web Application

A comprehensive Django-based web application for managing personal budgets.

## Features

Core Functionality
- Track income and expenses - Record all financial transactions
- Categorize transactions - Organize spending by categories
- Set and monitor saving goals - Track progress towards financial goals
- Visualize financial data - Interactive charts and graphs
- Multiple Accounts/Portfolios - Manage different accounts (cash, bank, credit cards)
- Budget Management - Set monthly, quarterly, or yearly budgets per category
- Budget vs Reality Analysis - Compare planned vs actual spending
- Recurring Transactions - Automate regular payments (salaries, bills)
- Enhanced Dashboard - Comprehensive overview with budget status
- Account Balance Tracking - Real-time balance updates
- Budget Alerts - Visual warnings for overspending

## How to run locally

1. Clone this repository:
   ```bash
   git clone https://github.com/marinvukelja/budzet-projekt.git
   cd budzet-projekt
   ```

2. Create and activate a virtual environment:
   python -m venv .venv
   .venv\Scripts\activate   # On Windows


3. Install dependencies:
   pip install -r requirements.txt

4. Apply migrations and create superuser:
   py manage.py migrate
   py manage.py createsuperuser
   

5. Run the development server:
   py manage.py runserver

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.


#Usage Tips

1. Start with Accounts - Create your accounts first
2. Set up Categories - Organize your spending categories
3. Create Budgets - Set realistic budgets for each category
4. Add Recurring Transactions - Automate regular payments
5. Monitor Dashboard - Check your financial health regularly
6. Use Analysis - Review budget performance monthly

# budget-management-app-final
