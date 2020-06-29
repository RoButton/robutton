# RoButton

A REST API for [Switchbots](https://www.switch-bot.com/) that allows to control actions, settings and timers.

Among other possibilities, setting up a webserver on a RaspberryPi in combination with an app capable of sending custom HTTP requests (e.g. [HTTP-Shortcuts](https://github.com/Waboodoo/HTTP-Shortcuts) for Android), allows to control SwitchBots by phone outside of the BLE range (without a Hub).

The REST API uses the [Switchbot Python API](https://github.com/RoButton/switchbotpy) for BLE communication.

## Getting Started

### Prerequisites

The setup is tested on a RaspberryPi 3 with the Raspbian Buster OS in combination with SwitchBots running firmware 4.4 and 4.5

### Installing

Install pipenv if you don't have it and then install the environment from the `Pipfile` (from the root directory):
```
pip install pipenv
```
```
pipenv install
```

Afterwards, Flask can be started with the following command:
```
pipenv run python src/main.py
```


### Usage

The REST API uses the Python API to communicate with the SwitchBots.


The following endpoints are available:

| Name                                       | Method | Endpoint                                          |
| ------------------------------------------ |--------| ------------------------------------------------- |
| Login (use password to receive token)      | POST   | ` /switchbot/api/v1/login`                        |
| Perform Action (press, turn on, turn off)  | POST   | `/switchbot/api/v1/bot/{bot_id}/actions`          |
| Find all SwitchBots                        | GET    | `/switchbot/api/v1/bots`                          |
| Get Settings                               | GET    | `/switchbot/api/v1/bot/{bot_id}`                  |
| Update Settings                            | PATCH  | `/switchbot/api/v1/bot/{bot_id}`                  |
| Get all timers                             | GET    | `/switchbot/api/v1/bot/{bot_id}/timers`           |
| Add a timer                                | POST   | `/switchbot/api/v1/bot/{bot_id}/timers`           |
| Update multiple timers at once             | PATCH  | `/switchbot/api/v1/bot/{bot_id}/timers` |
| Update a timer                             | PATCH  | `/switchbot/api/v1/bot/{bot_id}/timer/{timer_id}` |
| Delete Timer                               | DELETE | `/switchbot/api/v1/bot/{bot_id}/timer/{timer_id}` |


To get more details about how to use the REST API, start the Flask app with: `pipenv run python src/main.py` and then use the endpoint `/doc/openapi.json` to obtain a [OPEN API](https://www.openapis.org/) specification.

Additionally, I provide a Postman collection in the `/postman` folder which can be imported to try the API. (Start with the Login request to obtain a bearer token which is used for all other endpoints)

## Deployment

For the deployment of the Switchbot REST API it is recommended to run the Flask application in combination with Nginx and Gunicorn.


## Authors

* **Nicolas Küchler** - *Initial work* - [nicolas-kuechler](https://github.com/nicolas-kuechler)
