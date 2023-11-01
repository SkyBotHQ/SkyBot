# Telegram-Twitter-Base 

Manage your Twitter account from the comfort of Telegram.

## Development

### 1. Clone the Repository and Set Up the Environment

#### 1.1. Clone the Repository

Clone the repository into your local machine by running the following command:
```bash
gh repo clone bigsky77/twitter-telegram-base && cd twitter-agent
```

#### 1.2. Create a Python Virtual Environment
This step is optional, but highly recommended to avoid package conflicts. Run the following command to create a virtual environment named `venv`:
```bash
python -m venv venv
```

#### 1.3. Activate the Virtual Environment

To activate the virtual environment, run the following command:

```bash
source venv/bin/activate
```

#### 1.4. Install the Required Packages

The application dependencies are listed in the requirements.txt file. Install them by running the following command:

``` bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

#### 2.1. Copy the Sample Environment File
Run the following command to copy the contents of .env.example to a new file named .env:

``` bash
cp .env.example .env
```

#### 2. Run the code 
Now that your .env file is fully configured, run the agent with the following command:

``` bash
python main.py

```

## Stripe


## Heroku

Webhooks for this app are processed by a seperate twitter-telegram-base-server model.  This model updates the database when it recieves Stripe Events.


## TODO

1) Add image uploads
2) Speech to text
3) Thread support
4) AI training
5) AI edits
6) AI automatic replies
7) Multiple users per account
8) In-Line tweeting
9) Gif support
10) Support for a quie
11) Custome prompts
12) AI architecture
# SkyBot
