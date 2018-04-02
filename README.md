# Project 3D Printing Machines

## Description
There are a variety of 3D printing techniques for part printing applications. Within each technique, there are various machines from different manufacturers. In this project, an application is developed to dynamically display 3D printing technology and machines as well as user registration and authentication system. Registered users have the ability to create new technology and machine, while original author/users have the ability to create, edit, and delete their own items. 

## Technologies 
- HTML
- CSS
- Bootstrap
- Python
- Flask
- Jinja2
- SQLAchemy

## Setup
Prior to running an application, you need to install or setup the following items:
- Install Python
- Install VirtualBox
- Install Vagrant
- Download `project-item-catalog` folder
- Place the above folder inside `vagrant` directory

## Run Program
- Start virtual machine by running `vagrant up`
- then `vagrant ssh` to log into virtual machine
- change directory to `cd /vagrant/project-item-catalog`
- Initiate initial database by running `python initial_data.py` 
- Once initial data added, run applicaiton with `python app.py`
- In your browser, go to `http://localhost:5000/technology`

## License
This project is licensed under the MIT License