# Imports
from github import Github
import click
from collections import defaultdict
import string
from tqdm import tqdm
import pandas as pd
import os
from connect_postgres import PostgresOps
from scrape_vulnerability_timestamps import AnalyzeTimeStamps
from datetime import datetime


class GithubCli:
    def __init__(self, username, password, api_key):
        self.username = username
        self.password = password
        self.api_key = api_key

    def get_dockerfiles(self, dockerfiles, repo, repo_contents, return_first=False):
        """
        Helper method to recursively traverse the repo and track dockerfiles
        """
        for content in repo_contents:
            if content.type == 'dir':
                dockerfiles = self.get_dockerfiles(dockerfiles, repo, repo.get_contents(content.path), return_first)
            elif content.type == 'file' and content.name.endswith('Dockerfile'):
                dockerfiles.append(content)
                if return_first:
                    return dockerfiles
        return dockerfiles

    @staticmethod
    def fetch_commits_for_dockerfile(dockerfile, repo):
        """
        Helper method to fetch commits info for a particular dockerfile
        """
        dockerfile_commits = []
        dockerfile_commit = {}
        commits = repo.get_commits(path=dockerfile.path)
        for commit in commits:
            for file in commit.files:
                if file.filename == dockerfile.path:
                    dockerfile_commit['commit_message'] = commit.raw_data['commit']['message']
                    dockerfile_commit['commit_sha'] = commit.sha
                    dockerfile_commit['author'] = commit.author.name if commit.author.name else "docker-library-bot"
                    dockerfile_commit['last_modified'] = commit.last_modified
                    dockerfile_commit['patch'] = file.patch
            dockerfile_commits.append(dockerfile_commit)
        return dockerfile_commits

    @staticmethod
    def fetch_packages_for_dockerfile(dockerfile):
        """
        Helper method to fetch a comma separated string of packages
        that can be installed using a particular dockerfile
        """

        install_commands = ['apk add', 'apt-get install', 'yum install']
        start = False
        current_install_command = ""
        packages = []

        # Get text content of the dockerfile
        content = dockerfile.decoded_content.decode("utf-8")

        # Parse the content for packages
        for line in content.splitlines():
            line = line.strip()
            line = line.replace("\\", "").strip()
            if not line:
                continue
            if line.startswith("#") or line.startswith("&&") or line.split(" ", 1)[0].isupper():
                start = False
            for command in install_commands:
                if command in line:
                    current_install_command = command
                    start = True
            if start:
                # Remove the command from the current line
                line = line.replace(current_install_command, "")
                words = line.split(" ")
                # Remove words in all-caps and words starting with punctuation from the current line
                for word in words:
                    if word.isupper() or "'" in word or (any(word.startswith(punct) for punct in string.punctuation)):
                        line = line.replace(word, "")
                line = line.strip()
                # Add the clean line to the list of packages
                if line:
                    packages = packages + line.split()

        return ','.join(packages)

    def fetch_dockerfiles(self):
        """
        Simple program that fetches commits from a master branch for a particular repository.
        """

        # Authenticate and create a GitHub client
        g = Github(self.username, self.password)

        # Fetch repositories
        repo_list = open('input/repo_list_mock.txt', 'r')

        dockerfile_packages_map = defaultdict(list)

        # for repo in tqdm(repo_list, desc="Repository", position=2):
        for repo in repo_list:
            repo = repo.strip()
            org = repo.split('/')[0]
            repository = repo.split('/')[1]
            try:
                # Retrieve the given organization
                org = g.get_organization(org)
                # Retrieve the repository under the given organization
                repository = org.get_repo(repository)

                print("Accessing", repository.full_name)

                # List of Dockerfiles to be tracked
                dockerfiles = []
                # Fetch all dockerfiles in the repo
                dockerfiles = self.get_dockerfiles(dockerfiles,
                                                   repository,
                                                   repository.get_contents(''),
                                                   return_first=True)

                # Retrieve packages for dockerfiles in the current repository
                packages = self.fetch_packages_for_dockerfile(dockerfiles[0])

                if packages:
                    # Update dockerfile_packages_map
                    dockerfile_packages_map[repo] = packages.split(',')

            except Exception as e:
                print('Repo does not exist: {}'.format(repo) + str(e))

        return dockerfile_packages_map

