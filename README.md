# Binance Trading Bot with Websockets

This script is a simple trading bot that uses Binance Websockets to monitor the price of a specific cryptocurrency pair (ETH/USDT in this example) and execute trading actions based on a simple momentum strategy.

## Prerequisites

Before running this script, ensure you have the following requirements:

- Python 3.6 or higher
- Required Python packages listed in `requirements.txt`. You can install them using `pip install -r requirements.txt`.
- Binance API keys (API_KEY and API_SECRET). Ensure they are set as environment variables or replace them in the script.

## Usage

1. Clone or download this repository to your local machine.

2. Install the required Python packages using the following command:

	pip install -r requirements.txt

4. Set your Binance API_KEY and API_SECRET as environment variables. Alternatively, you can directly replace them in the script.

5. Run the script using the following command:
		python trading_bot.py


## Strategy

The trading strategy implemented in this script is a simple momentum strategy. It monitors the price of the cryptocurrency pair and takes the following actions:

- When the 30-unit period (seconds) Rate of Change (ROC) becomes positive and was previously negative, it places a market BUY order for 10 units of the cryptocurrency.

- Once a position is open, it sets a trailing stop loss at 0.5% below the highest price since the position was opened.

- When the current price falls below the trailing stop loss or rises by more than 0.2%, it places a market SELL order for 10 units, closing the position.

## Important Notes

- This script is for educational purposes only. Be cautious when using it with real funds. It is strongly recommended to thoroughly test any trading strategy on a demo or testnet environment before using it in a live trading setting.

- Ensure you have an understanding of the Binance API and trading concepts before using this script for real trading.

- Use appropriate risk management techniques and consider transaction fees when implementing this or any other trading strategy.

- Handle exceptions and errors gracefully. The script includes some basic error handling, but you may want to enhance it for production use.

## Disclaimer

This script does not guarantee profits and carries risks. Use it at your own discretion and risk. The authors and contributors are not responsible for any financial losses incurred.
