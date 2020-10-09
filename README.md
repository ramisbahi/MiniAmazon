## Mini Amazon Project

## Installation

1. (Optional) Create a virtual environment ([command line](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) 
or with [IntelliJ](https://www.jetbrains.com/help/idea/creating-virtual-environment.html)) 
2. Install Postgres (use [this](https://stackoverflow.com/a/21080707/7386515) for Mac)
3. Install the packages listed in `requirements.txt` (run `pip3 install -r requirements.txt`)

If you're using a Mac and get an error installing `psycopg2`, try running the following command beforehand:

```
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
```

## Running Locally

Run the following command: 

```
python3 app.py
```