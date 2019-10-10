# GitHub Operations

This directory contains scripts and notebooks that will help in analyzing the GitHub repositories corresponsing to the official docker images.

## Installations

* We will be using the [PyGithub](https://pygithub.readthedocs.io/en/latest/introduction.html) library to communicate with the [Github API v3.](http://developer.github.com/v3). 
* The [Click](https://click.palletsprojects.com/en/7.x/) library will also be used to create command line tools from the github scripts.

Both the libraries can be installed via pip:

```
# PyGithub
pip install PyGithub

# Click
pip install click
```

## Usage

```
python fetch_commits.py --username YOUR_USERNAME --password YOUR_PASSWORD --organization docker-library --repository python
```
will print last 20 commits stats for [docker-library/python](https://github.com/docker-library/python).

```
Options:
  --username TEXT      Your GitHub username.
  --password TEXT      Your GitHub password.
  --organization TEXT  Target GitHub organization.
  --repository TEXT    Target GitHub repository under the given organization.
  --help               Show this message and exit.
```
__________

## Running it in a docker container
Build the container by running the command :
```
Docker build -t gitoperations .
```
Run the container which will start the fetch_commit.py script :
```
docker run -p  80:80 gitoperations —username ‘username’ —password ‘password’  --organization docker-library --repository python
```
 
