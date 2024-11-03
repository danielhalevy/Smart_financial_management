import pytest
import pandas as pd
from rec import validate_file_and_read, process_financial_data, calculate_savings_recommendations

# Sample data for testing
valid_csv_data = """Date,Category,Amount
2024-01-01,Salary,3000
2024-01-05,Food,-500
2024-01-10,Entertainment,-700
"""
invalid_csv_data = """Date,Category,Amount
2024-01-01,Salary,3000
2024-01-05,Food,InvalidAmount
"""


def test_validate_file_and_read_valid():
    with open('C:/Users/danie/PycharmProjects/Smart Fin Man/tests/valid_transactions.csv', 'w') as f:
        f.write(valid_csv_data)

    df = validate_file_and_read('C:/Users/danie/PycharmProjects/Smart Fin Man/tests/valid_transactions.csv')

    assert df is not None
    assert df.shape[0] == 3  # Should have 3 rows
    assert df['Amount'].sum() == 1800  # 3000 - 500 - 700 = 1800


def test_validate_file_and_read_invalid():
    with open('C:/Users/danie/PycharmProjects/Smart Fin Man/tests/invalid_transactions.csv', 'w') as f:
        f.write(invalid_csv_data)

    df = validate_file_and_read('C:/Users/danie/PycharmProjects/Smart Fin Man/tests/invalid_transactions.csv')

    assert df is None


def test_process_financial_data():
    # Create a DataFrame to simulate the input
    df = pd.DataFrame({
        'Date': pd.to_datetime(['2024-01-01', '2024-01-05', '2024-01-10']),
        'Category': ['Salary', 'Food', 'Entertainment'],
        'Amount': [3000, -500, -700],
        'Year': [2024, 2024, 2024],
        'Month': [1, 1, 1]
    })

    charts = process_financial_data(df)

    assert len(charts) == 2  # Should generate one pie chart and one summary chart


def test_calculate_savings_recommendations():
    df = pd.DataFrame({
        'Year': [2024, 2024, 2024],
        'Month': [1, 1, 1],
        'Category': ['Food', 'Entertainment', 'Salary'],
        'Amount': [-500, -700, 3000]
    })

    recommendations = calculate_savings_recommendations(df, 2024, 1)

    assert isinstance(recommendations, list)  # Should return a list of recommendations
    assert len(recommendations) > 0  # Check that there is at least one recommendation

# Additional test cases can be added to cover edge cases and different scenarios.
