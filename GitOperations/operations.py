# Imports
from github import Github
import click
from collections import defaultdict
import string
from tqdm import tqdm
import pandas as pd
from connect_postgres import PostgresOps
from analyze_vulnerability_timestamps import AnalyzeTimeStamps
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
        repo_list = open('repo_list.txt', 'r')

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


@click.command()
@click.option('--username', prompt='User', help='Your GitHub username.')
@click.option('--password', prompt=True, hide_input=True, help='Your GitHub password.')
@click.option('--api_key', prompt='XForce API Key', hide_input=True, help='XForce API Key')
def main(username, password, api_key):
    """
    Entry function
    :param username: Github Username
    :param password: Github Password
    :param api_key: XForce API Key
    """
    cli_obj = GithubCli(username, password, api_key)

    dockerfiles = cli_obj.fetch_dockerfiles()
    packages = []
    for image_name in dockerfiles:
        if dockerfiles[image_name]:
            packages.append(dockerfiles[image_name])
    packages = [j for i in packages for j in i]
    packages = list(set(packages))

    print("Fetching information for", len(packages), "packages.")
    postgres_obj = PostgresOps(packages)
    postgres_obj.connect()
    clair_db_reports = postgres_obj.get_clair_reports()
    clair_db_reports.to_csv("report.csv", index=False)


@click.command()
@click.option('--api_key', prompt='XForce API Key', hide_input=True, help='XForce API Key')
def analyze_date_diff(api_key):
    tqdm.pandas()
    report_filename = "Dedup_Report.csv"
    data = pd.read_csv(report_filename)
    analyze_ts = AnalyzeTimeStamps(api_key)

    data['Date_Reported'] = data.progress_apply(lambda r:
                                                analyze_ts.fetch_xforce_timestamp(r['Vulnerability']),
                                                axis=1)
    data['Date_Fixed'] = data.progress_apply(lambda row:
                                             analyze_ts.fetch_version_timestamp(row['OS'],
                                                                                row['Package'],
                                                                                row['Package_Version']),
                                             axis=1)

    def get_date_diff(row):
        date_format = "%Y-%m-%d"
        if row['Date_Fixed']:
            fixed = datetime.strptime(row['Date_Fixed'], date_format)
        else:
            fixed = None
        if row['Date_Reported']:
            reported = datetime.strptime(row['Date_Reported'], date_format)
        else:
            reported = None
        if fixed and reported:
            return abs((fixed - reported).days)
        else:
            return None

    data['Days_For_Fix'] = data.progress_apply(lambda row: get_date_diff(row), axis=1)

    data.to_csv('Final_Report.csv')


if __name__ == '__main__':
    # main()
    analyze_date_diff()
