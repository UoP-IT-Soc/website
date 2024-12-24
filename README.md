## UOP-IT-SOC-Website

This repository contains the source code for the University of Portsmouth IT Society website.

## Description

The UOP-IT-SOC-Website is a project developed by the IT Society at the University of Portsmouth. It serves as the official website for the society, providing information about events, resources, and activities for IT students and enthusiasts.

## Features

-   Event calendar
-   Member profiles
-   Resource library (to do)

## Contributing

We welcome contributions from all members of the IT Society. Please follow these steps to contribute:

1.  Fork the repository
2.  Create a new branch
3.  Make your changes
4.  Submit a pull request

## Set up

First run
`pip install -r requirements.txt`

then

A env file is needed. make a `.env` file in the main directory of the project add add `SECRET_KEY = <key here>`
if there are no users a admin account is needed. to do this add ADMIN_EMAIL = <email> and ADMIN_PASSWORD = <password> to the `.env` file.
(these are needed for the first time the project is run please create a superuser account from the admin panel)

Demo ENV file for first time setup
``` 
SECRET_KEY=awdawdwa
ADMIN_EMAIL=admin@staff.com
ADMIN_PASSWORD=test123
```

## Doucmentation

flask documentation: https://flask.palletsprojects.com/en/2.0.x/
Python documentation: https://docs.python.org/3.12/

