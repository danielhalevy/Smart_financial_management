import requests


def convert_to_usd(amount: float, from_currency: str) -> float:
    """
    Converts a given amount from the specified currency to USD using the Frankfurter API.

    :param amount: The amount in the source currency
    :param from_currency: The 3-letter currency code to convert from (e.g., "EUR", "AUD")
    :return: The equivalent amount in USD
    :raises: Exception if the API call fails or the currency is unsupported
    """
    try:
        # Fetch the latest conversion rate from 'from_currency' to 'USD'
        response = requests.get(f'https://api.frankfurter.app/latest?base={from_currency}&symbols=USD')

        # Raise an exception if the API request failed
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract the conversion rate for USD
        conversion_rate = data['rates']['USD']

        # Calculate and return the converted amount
        converted_amount = amount * conversion_rate
        return round(converted_amount, 2)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Frankfurter API: {e}")
        raise


# Example usage:
if __name__ == "__main__":
    amount_in_usd = convert_to_usd(100, "EUR")  # Convert 100 EUR to USD
    print(f"Converted amount: ${amount_in_usd} USD")
