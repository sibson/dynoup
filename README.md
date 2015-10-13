[![Circle CI](https://circleci.com/gh/sibson/dynoup.svg?style=svg)](https://circleci.com/gh/sibson/dynoup)

# Deploy and Setup

  1. [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)
  1. heroku clients:create dynoup https://your-app-name.herokuapp.com/auth/heroku/callback/

# Usage


DynoUp will run checks against a configured URL, which should be some endpoint in your application.
It should return either a 200 OK if everything is OK or 503 Server Unavailable to indicate dynoup should scale up the process type.

# Development

You can test the server locally by starting it with

    1. heroku plugins:install https://github.com/heroku/heroku-oauth
    1. heroku clients:create dynoup http://localhost:5000/auth/heroku/callback/
    1. python webapp.py

The worker can be run with

    ./bin/worker.sh
