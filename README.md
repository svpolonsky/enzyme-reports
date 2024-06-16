# Report expenses for an Enzyme vault

## Setup project

I tested the code only on Ubuntu 22.04.

### Start Python virtual environment

```sh
python3 -m venv env
source env/bin/activate
```

### Install dependencies

```sh
pip install -r requirements.txt
```

### Add API keys to your `.env` file

```txt
MORALIS_API_KEY=...
COINGECKO_API_KEY=...
```

You can get free API keys from both API providers

## Query Enzyme API to download transactions as JSON

At present, I use Buf Studio to [access the API](https://buf.build/studio/avantgardefinance/enzyme/enzyme.enzyme.v1.EnzymeService):

1. Add the target URL: [https://api.enzyme.finance/](https://api.enzyme.finance/)

2. In `Body`, add vault `address`

3. In `Headers` add authorization header (the site provide free API tokens):
    - `Key`: `Authorization`
    - `Value`: `Bearer API-token`

4. In Method field, first select repository `avantgardefinance/enzyme`, next `GetVaultActivities`

5. Send the request, save the response JSON to `vault-activity.json` in project root directory

## Run Python script to generate report

```sh
python report.py
```
