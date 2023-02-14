# Swim-ai
A modeling platform for generating and implementing ML models for bathing water quality predictions

# plattform
Platform for project Digital Water City

# Objectives
In the project Digital Water City (DWC) a platform will be developed that supports bathing water managers with setting up machine learning models for bathing water quality prediction.

# Get started

This is a Django app. Django is a web development framework for Python. 
To run the app you need to have Python and you need to have the Django
framework installed. 

The following instructions were tested on Ubuntu `Ubuntu 20.04.3 LTS`
(found with `lsb_release -a`).

## Prepare communication with GitHub via SSH

Create private and public SSH key files

`ssh-keygen -t rsa -b 4096 -C "your-email-address"`

Press three times Enter:

1. Accept the default location for the files, 
2. do not use a passphrase,
3. confirm not to use a passphrase.

Copy the output of the following command to the clipboard:

`cat ~/.ssh/is_rsa.pub`

Login to github.com and open https://github.com/settings/ssh/new. 
Give a "Title" of your choice. 
Paste the content of the clipboard into the text field "Key" of the form.
Submit the form by pressing the button "Add SSH Key".

## Clone the repository

Change to a directory into which to clone this repository.

Clone the repository from GitHub into that directory.

`git clone git@github.com:wseis/swim-ai.git`

This should create a folder `swimai` in your current directory.


## Install pip for installing Python packages

`sudo apt-get install python3-pip`

## Allow for virtual environments

Virtual environments allow each project to use its own set of required 
packages. There are different solutions for managing virtual environments. 
I found two solutions:

### 1. Python package "virtualenv"

Install Python package "virtualenv"

`sudo pip3 install virtualenv`

Create a new virtual environment

`virtualenv venv`

Activate your virtual environment

`source venv/bin/activate`

(To deactivate the virtual environment, run `deactivate venv`.)

### 2. Package and environment management system "conda"

Let the administrator install conda, e.g. to `/opt/miniconda3`. 

Initialise the usage of conda

`/opt/miniconda3/bin/conda init bash`

List available conda environments

`conda info --envs`

Create a new environment with the python version you want

`conda create --name dwc python=3.10`

Activate the new environment

`conda activate dwc`

(To deactivate the environment, run `conda deactivate`)

## Install required packages into virtual environment

The Django web application depends on many Python packages each of which is 
listed in the file `requirements.txt` in the project folder. The command `pip3`
 allows to install all required packages from that file at once: 

`pip3 install -r requirements.txt`


## Set environment variables 

- `GDAL_LIBRARY_PATH` (on Ubuntu not required)
- `CLIENT_ID`
- `CLIENT_SECRET`
- `REDIRECT_URI`
- `KEYROCK_ADMIN`
- `KEYROCK_PW`
- `APP_ID`
- `AUTH_BASIC`

## Prepare the database

Run the following command to create all required tables in the database:

`python manage.py migrate`

Some tables need to be populated with data. 

This can be done via Jupyter notbooks. They can be seen as tutorials containing
text and Python code. 

Run the web application Jupyter with

`python manage.py shell_plus --notebook`

Navigate to the notebook

`notebooks/01_CreateFeatureTypes.ipynb`

and run all of its code blocks. This creates all "feature types".

Stop the notebook server with Control-C.