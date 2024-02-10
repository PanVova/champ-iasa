# champ-iasa

## Installation
To set up the project locally, follow these steps:
### Docker installation
1. Replace the `NEWSAPI_KEY` in the [docker-compose.yml](docker-compose.yml) file with your own NewsAPI key.
2. Execute the following command to run the project.
```bash
docker compose up
```
### Alternative installation
1. Create the virtual environment.
```bash
python -m venv .venv
```
2. Activate the virtual environment.
- For Windows, use:
```bash
.venv\Scripts\activate
```
- For macOS/Linux, use:
```bash
source .venv/bin/activate
```
3. Install the dependencies and run the project.
```bash
pip install -r requirements.txt
flask run
```