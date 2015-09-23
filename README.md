[![Circle CI](https://circleci.com/gh/sibson/dynoup.svg?style=svg)](https://circleci.com/gh/sibson/dynoup)

# Deploy and Setup

  1. [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)
  1. heroku clients:create dynoup https://your-app-name.herokuapp.com/auth/heroku/callback/

# Usage

# Development

You can test the server locally by starting it with

  1. heroku clients:create dynoup http://localhost:5000/auth/heroku/callback/
  1. python webapp.py

The worker can be run with

    rqworker
