# PancakeSwap Epoch Fetcher

This project is a script that interacts with PancakeSwap's prediction contract on the Binance Smart Chain (BSC). It allows you to fetch historical round results, including the outcome (Bull, Bear, or Draw) and winning odds for each epoch.

## Features

- Fetch results for a range of epochs or the latest N epochs.
- Calculate and display winning odds for both Bull and Bear positions.
- Save results to a CSV file for easy analysis.

## Requirements

- Python 3.6+
- [Web3.py](https://web3py.readthedocs.io/en/stable/): Python library for interacting with the Ethereum blockchain.
- BscScan API key (required to fetch the ABI of the PancakeSwap contract).

## Setup Instructions

1. Clone the repository:

   ```sh
   git clone https://github.com/KOKOSde/pancakeswap-epoch-results-BNB.git
   cd pancakeswap-epoch-results-BNB
   ```

2. Install the required packages using `requirements.txt`:

   ```sh
   pip install -r requirements.txt
   ```

3. Obtain a BscScan API key:

   - Go to [BscScan](https://bscscan.com/register) and create an account.
   - Once registered, log in and navigate to the API Keys section to generate a new API key.

4. Update the `api_key.json` file with your BscScan API key:

   ```json
   {
     "bscscan_api_key": "your_api_key_here"
   }
   ```

5. Run the script:

   ```sh
   python main.py
   ```

   You will be prompted to either fetch the latest epochs or specify a range of epochs.

## Usage

### Command Line Arguments

- **--latest\_n**: Fetch results for the latest N epochs.
- **--start\_epoch** and **--end\_epoch**: Fetch results for a specific range of epochs.

Example:

```sh
python main.py --latest_n 5
```

This will fetch results for the latest 5 epochs, excluding the latest 2 that are ongoing or yet to start.

Alternatively, you can run the script without any arguments and it will prompt you for the necessary information.

## Example Output

The results will be saved to a CSV file named `epoch_results.csv` with the following columns:

- **Epoch**: The epoch number.
- **Result**: The outcome of the epoch (Bull, Bear, or Draw).
- **Bull Odds**: The calculated odds for the Bull position.
- **Bear Odds**: The calculated odds for the Bear position.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This script is intended for educational purposes only. Please use it responsibly. The script interacts with blockchain data and uses real-time data from PancakeSwap.

## Contributing

Feel free to submit a pull request or open an issue if you have suggestions or want to contribute to the project.


