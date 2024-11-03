import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import logging

from pandas import DataFrame

import config
from texts import reduce_text, surplus_text, saving_text, overspending_text, saving_goal_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_path),
        logging.StreamHandler()
    ]
)


def validate_file_and_read(file_path: str) -> DataFrame | None:
    try:
        # Attempt to read the CSV file
        df = pd.read_csv(file_path)

        # Check if required columns exist
        required_columns = ['Date', 'Category', 'Amount']
        if not all(col in df.columns for col in required_columns):
            logging.error(f"CSV must contain the following columns: {required_columns}")
            raise ValueError(f"CSV must contain the following columns: {required_columns}")

        # Convert the 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if df['Date'].isnull().any():
            logging.error("Some dates couldn't be parsed properly.")
            raise ValueError("Some dates couldn't be parsed properly.")

        # Ensure 'Amount' is numeric
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        if df['Amount'].isnull().any():
            logging.error("Some amounts couldn't be parsed properly.")
            raise ValueError("Some amounts couldn't be parsed properly.")

        df['Date'] = pd.to_datetime(df['Date'])

        # Add new columns for the year and month (useful for grouping by year and month)
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        logging.info("Data loaded successfully!")
        return df

    except FileNotFoundError:
        logging.error(f"Error: The file '{file_path}' does not exist.")
        return None

    except ValueError as ve:
        logging.error(f"Data error: {ve}")
        return None

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None


def process_financial_data(df: pd.DataFrame) -> list:
    # Get unique year-month combinations
    unique_months = df[['Year', 'Month']].drop_duplicates().sort_values(by=['Year', 'Month'])

    # List to store the generated charts (Figures)
    charts = []
    carryover_budget = 0  # Start with no carryover

    # Process data for each month
    for _, row in unique_months.iterrows():
        year = row['Year']
        month = row['Month']

        # Filter data for the current month
        monthly_df = df[(df['Year'] == year) & (df['Month'] == month)]

        # Summarize data by category for this month
        monthly_summary = monthly_df.groupby('Category')['Amount'].sum().reset_index()

        # Separate earnings and expenses
        expenses = monthly_summary[monthly_summary['Amount'] < 0]
        earnings = monthly_summary[monthly_summary['Amount'] > 0]

        # Total expenses and earnings
        total_expenses = expenses['Amount'].sum()
        total_earnings = earnings['Amount'].sum()

        # Add the carryover to earnings for budget calculation
        adjusted_earnings_with_carryover = total_earnings + carryover_budget

        # Expense-to-income ratio (for the current month only)
        current_month_expense_income_ratio = (abs(total_expenses) / total_earnings * 100) if total_earnings != 0 else 0

        # Generate a pie chart for this month's expenses
        fig1, ax1 = plt.subplots(figsize=(6, 6))

        # Pie chart for expenses (without axis and layout numbers)
        ax1.axis('equal')  # Remove layout axes
        if not expenses.empty:
            ax1.pie(
                abs(expenses['Amount']),
                labels=expenses['Category'],
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.Paired.colors
            )
            ax1.set_title(f'Expense Distribution - {month}/{year}')
        else:
            ax1.text(0.5, 0.5, 'No Expenses', horizontalalignment='center', verticalalignment='center')

        # Save the pie chart figure
        charts.append(fig1)

        # Generate a separate figure for the financial summary message
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.axis('off')  # Remove the axes for the message plot

        # Budget check considering carryover
        if adjusted_earnings_with_carryover > abs(total_expenses):
            savings = adjusted_earnings_with_carryover - abs(total_expenses)
            budget_message = f"You are within budget and saving ${savings:,.2f} after carryover."
        else:
            overspending = abs(total_expenses) - adjusted_earnings_with_carryover
            budget_message = f"You are overspending by ${overspending:,.2f} after carryover."

        # Current month's expense-to-income feedback (without carryover)
        if total_earnings > abs(total_expenses):
            expense_message = (saving_text(current_month_expense_income_ratio))
        else:
            expense_message = (overspending_text(current_month_expense_income_ratio))

        # Update the carryover for next month
        carryover_budget = savings if adjusted_earnings_with_carryover > abs(total_expenses) else -overspending

        recommendations = calculate_savings_recommendations(df, year, month)

        # Text to display in the chart area, breaking the message into shorter lines
        financial_summary = f"""
        Total Expenses: ${abs(total_expenses):,.2f}
        Total Earnings (current month): ${total_earnings:,.2f}
        Expense-to-Income Ratio (current month): {current_month_expense_income_ratio:.2f}%
        
        {budget_message}
        
        {expense_message}
        
        Updated budget for next month: ${carryover_budget:,.2f}
        
        Recommendations:
        {"\n".join(recommendations)}
        """
        ax2.text(0.5, 0.5, financial_summary, horizontalalignment='center', verticalalignment='center', fontsize=12,
                 bbox=dict(facecolor='lightgrey', alpha=0.5))

        # Save the message figure
        charts.append(fig2)

        # Close figures to free memory
        plt.close(fig1)
        plt.close(fig2)

    # Return the list of generated charts
    return charts


def calculate_savings_recommendations(df: pd.DataFrame, year: int, month: int) -> list:
    recommendations = []

    monthly = df.groupby(['Year', 'Month', 'Category'])['Amount'].sum().reset_index()

    category_stats = monthly.groupby('Category')['Amount'].agg(['mean', 'std']).reset_index()

    df = df[(df["Year"] == year) & (df["Month"] == month)]

    # Calculate total income and total expenses for each category per month
    monthly_category_totals = df.groupby('Category')['Amount'].sum().reset_index()

    total_income = monthly_category_totals[monthly_category_totals['Amount'] > 0]['Amount'].sum()

    total_expenses = monthly_category_totals[monthly_category_totals['Amount'] < 0]['Amount'].sum()

    # Calculate remaining budget (income - expenses)
    remaining_budget = total_income + total_expenses  # total_expenses is negative, so this is income - expenses

    # If remaining budget is greater than 1000, recommend saving the excess as a percentage of total income
    if remaining_budget > 1000:
        savings_percentage = ((remaining_budget - 1000) / total_income) * 100
        recommendations.append(
            surplus_text(remaining_budget, savings_percentage)
        )

    else:
        for _, category_row in monthly_category_totals.iterrows():
            category = category_row['Category']
            category_amount = category_row['Amount']

            # Skip income categories (positive amounts like Salary)
            if category_amount >= 0:
                continue

            # Get average and standard deviation for this category
            category_mean = category_stats.loc[category_stats['Category'] == category, 'mean'].values[0]
            category_std = category_stats.loc[category_stats['Category'] == category, 'std'].values[0]

            # Check if the category's expenses are higher than the acceptable range (mean + 2*std)
            if category_amount < (category_mean - category_std):
                reduction_percentage = ((category_amount - (category_mean - category_std)) * -1) / (
                        category_amount * -1) * 100
                recommendations.append(
                    reduce_text(category, reduction_percentage)
                )

    return recommendations


def evaluate_savings_goal(df: pd.DataFrame, charts: list) -> list:
    try:
        # Attempt to convert user input to a float
        savings_goal = float(config.amount)
    except ValueError:
        # Handle the case where the input is not a valid float
        logging.error("Invalid input. Please enter a numeric value for your savings goal.")
    # Group the data by Year and Month to get monthly totals
    monthly_income = df.groupby(['Year', 'Month']).agg({  # Total income
        'Amount': lambda x: x[x > 0].sum()  # Total expenses
    }).reset_index()
    monthly_expense = df.groupby(['Year', 'Month']).agg({  # Total income
        'Amount': lambda x: x[x < 0].sum()  # Total expenses
    }).reset_index()

    # Calculate the average monthly income and expenses
    avg_monthly_income = monthly_income['Amount'].mean()
    avg_monthly_expenses = abs(monthly_expense['Amount'].mean())

    # Check if the savings goal can be met with the current monthly averages
    if avg_monthly_income - avg_monthly_expenses >= savings_goal:
        saving_message = (saving_goal_text(avg_monthly_expenses, avg_monthly_income, savings_goal))
    else:
        if avg_monthly_income < savings_goal:
            saving_message = "You don't earn enough to make this goal!"
        else:
            # Calculate the shortfall and the percentage reduction needed
            shortfall = savings_goal - (avg_monthly_income - avg_monthly_expenses)
            reduction_needed = (shortfall / avg_monthly_expenses)

            # Prepare a detailed reduction message for each expense category
            reduction_message = (f"Your goal was to save ${savings_goal:,.2f}. To achieve this goal,\n"
                                 f" you need to reduce expenses by a total of ${shortfall:,.2f}.\n")

            monthly_category_expenses = df[df['Amount'] < 0].groupby(['Year', 'Month', 'Category'])[
                'Amount'].sum().reset_index()
            monthly_category_expenses = monthly_category_expenses.groupby('Category')[
                'Amount'].mean().abs().reset_index()
            for _, row in monthly_category_expenses.iterrows():
                category = row['Category']
                category_avg_expense = row['Amount']
                reduction_amount = reduction_needed * category_avg_expense
                reduction_message += f"- Reduce ${reduction_amount:,.2f} from {category}.\n"

            saving_message = reduction_message

    # Append the savings message to the last chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis('off')  # Turn off the axis

    # Add the savings message as text in the figure
    ax.text(0.5, 0.5, saving_message, horizontalalignment='center', verticalalignment='center', fontsize=12,
            bbox=dict(facecolor='lightgrey', alpha=0.5))

    # Append the figure to the charts list
    charts.append(fig)

    # Return the updated list of charts
    return charts


# Full main function with the calls
if __name__ == "__main__":
    # Load transaction data
    file_path = config.file_path
    df = validate_file_and_read(file_path)

    if df is not None:
        charts = process_financial_data(df)
        evaluate_savings_goal(df, charts)

        # Save all charts to a single PDF file
        pdf_file_path = config.pdf_path
        with PdfPages(pdf_file_path) as pdf:
            for chart in charts:
                pdf.savefig(chart)  # Save the current chart to the PDF

        logging.info(f"PDF saved successfully as {pdf_file_path}")
