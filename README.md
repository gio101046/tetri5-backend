# Tetri5 - Multiplayer Websocket Backend
[![Total alerts](https://img.shields.io/lgtm/alerts/g/gio101046/tetri5-backend.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/gio101046/tetri5-backend/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/gio101046/tetri5-backend.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/gio101046/tetri5-backend/context:python)

This repository is the backend of the multiplayer portion of the [Tetri5](https://github.com/gio101046/tetri5) game client. It uses the python `websockets` library to allow game clients to connect and communicate in real time.

## Run Locally

Use [pip](https://pip.pypa.io/en/stable/) package manager to install the required dependencies:

```bash
pip install -r requirements.txt
```

From your terminal move to the root of the project and run the following line:

```bash
python main.py 
```

In some systems you may need to run this instead:

```bash
python3 main.py 
```

## Deploy

This backend can be deployed using Heroku. Download and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-command-line) and run the following commands:

```bash
> heroku login
> heroku create
> git push heroku main
> heroku ps:scale web=1
> heroku open
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
