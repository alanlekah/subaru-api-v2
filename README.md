# Subaru V2 Lambda API

## Notes
This project only works with Python3.6, the selenium + lambda compatability issues are too much to deal with if you try > 3.7.

## Usage
- Create a lambda folder in the root of this project and place the following files:
  - chromedriver
  - headless-chromium

The following versions have been tested as working:
- chromedriver 2.43
- severless-chrome 1.0.0-55
- selenium == 3.14

Run `make init` which should setup your Zappa project to use with lambda + API gateway

## Zappa Settings - Needed for Configuration

You will most likely want to include the following after the `zappa init` step (without the < > symbols):

    "slim_handler": true,
    "environment_variables": {
        "PIN": "< SUBARU STARLINK PIN - 4 DIGITS >",
        "SECURITY_Q&A": "< LIST OF SECURITY QUESTIONS AND ANSWERS IN THE FORMAT - 'QUESTION1:ANSWER1,QUESTION2:ANSWER2,QUESTION3:ANSWER3' >",
        "USERNAME": "< SUBARU LOGIN - USERNAME >",
        "PASSWORD": "< SUBARU LOGIN - PASSWORD >"
    },
    "timeout_seconds": 70

## Disclaimer

Subaru has no official V1 API. This project may not work forever. Use at your own risk but raise issues as needed.