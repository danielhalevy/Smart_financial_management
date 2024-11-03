def reduce_text(category, reduction_percentage):
    return (f"Reduce {category} expenses by {reduction_percentage:.2f}%. \n"
            f"It seems this is an unusual spending amount for this month")


def surplus_text(remaining_budget, savings_percentage):
    return (f"Your budget has a surplus of ${remaining_budget:.2f}. \n"
            f"Consider saving {savings_percentage:.2f}% of your income for this month.")


def overspending_text(current_month_expense_income_ratio):
    return (f"Try to reduce expenses this month,\n "
            f"with an expense-to-income ratio of {current_month_expense_income_ratio:.2f}%.")


def saving_text(current_month_expense_income_ratio):
    return (f"You are saving this month,\n "
            f"with an expense-to-income ratio of {current_month_expense_income_ratio:.2f}%.")


def saving_goal_text(avg_monthly_expenses, avg_monthly_income, savings_goal):
    return (f"Your average monthly income (${avg_monthly_income:,.2f})\n"
            f" and expenses (${avg_monthly_expenses:,.2f}) \n"
            f"are on track to meet your savings goal of ${savings_goal:,.2f}. \n"
            f"Continue in the same course to reach your target.")
