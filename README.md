# crypto-killer
Bot to kill all bots

## Prerequisites
1. install [pyenv](https://github.com/pyenv/pyenv)
2. install 3.11 
```bash
pyenv install 3.11
```
3. install [poetry](https://python-poetry.org/docs/#installation)
4. Setup environment (recommended command because poetry not always automatically 
pick up python version from pyenv)
```bash
poetry env use -- $(which python)
```
4. Install dependencies
```bash
poetry install
```
5. Setup infrastructure (mongodb etc.)
```bash
docker-compose up -d
```

## Usage
1. Create `.env` (see `.env.example`)
2. Optionally edit settings in `src/main.py`:
- `TICKERS_POLL_INTERVAL_IN_SECONDS` - interval for tickers polling
3. Run script. It will fetch all tickers that contains `USDT` and store it in the Database
```bash
python src/run.py
```
4. Go to `http://localhost:8081/db/crypto_killer/TickerStat` to see fetched tickers

or run using your IDE

## Development
### Add new exchange
1. Add constant for exchange to `Exchange` enum in `src/constant.py`
2. Add appropriate api class in `EXCHANGE_TO_API_MAP` mapper in `src/constant.py`
3. Add service to `src/exchanges/<your-new-exchange/service.py` and inherit it from
`exchanges.base.service.BaseExchangeService`
4. Override methods that you need (usually you need only `get_config` to set credentials)
5. Add `EXCHANGE` class attribute for your service
6. Add your service to `_get_services()` function in `src/main.py`


### Code style
1. Configure pre-commit hooks
```bash
pre-commit install
```
