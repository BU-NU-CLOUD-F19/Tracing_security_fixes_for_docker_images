# Importing packages
import argparse
import requests

from tqdm import tqdm
from github import Github, GithubException


class GithubConnector:
    @staticmethod
    def __decode_base_package_from_command(command):
        try:
            package = command.split()[1]
            return package.split(':')[0]
        except IndexError:
            return None

    def __init__(self, username, password, repo, *argv):
        self.__username = username
        self.__password = password
        self.__repo = repo
        self.__arguments = argv
        self.__githubInstance = None
        self.__repoInstance = None

    def __authorize(self):
        if self.__githubInstance is None:
            self.__githubInstance = Github(self.__username, self.__password)

    def fetch_root(self):
        if self.__repoInstance is None:
            return []
        return self.__repoInstance.get_contents('')

    def fetch_content(self, path):
        if self.__repoInstance is None:
            return []
        return self.__repoInstance.get_contents(path)

    def fetch_all_files_flattened(self, extension=''):
        root = self.fetch_root()
        return self.__fetch_files_recursively(root, extension, [])

    def __fetch_files_recursively(self, contents, extension, files):
        for content in contents:
            if content.type == 'dir':
                files = self.__fetch_files_recursively(self.fetch_content(content.path), extension, files)
            elif content.type == 'file' and content.name.endswith(extension):
                files.append(content)
        return files

    def __check_repo(self):
        if self.__githubInstance is None:
            return False
        self.__repoInstance = self.__githubInstance.get_repo(self.__repo)
        return self.__repoInstance is not None

    def __fetch_docker_files(self):
        return self.fetch_all_files_flattened(extension='Dockerfile')

    def __fetch_base_package_from_docker_file(self, dockerfile):
        file_content = requests.get(dockerfile.download_url)

        for line in file_content.iter_lines():
            sanitized_line = line.decode('utf-8').strip()
            if sanitized_line == '' or sanitized_line.startswith('#'):
                continue
            return self.__decode_base_package_from_command(sanitized_line)

    def fetch_base_packages(self, ret=None):
        if ret is None:
            ret = {}

        base_packages = []

        self.__authorize()
        if not self.__check_repo():
            raise AttributeError('The provided repo does not exist or the'
                                 ' user does not have enough privileges to'
                                 ' access the repository: {}'.format(self.__repo))

        # Fetch all the docker files in the repo
        docker_files = self.__fetch_docker_files()

        # Retrieve the base packages form all the dockerfiles
        for dockerfile in docker_files:
            base_packages.append(self.__fetch_base_package_from_docker_file(dockerfile))

        # Calculate the usages
        for package in base_packages:
            if package is None:
                continue

            if package in ret:
                ret[package] += 1
            else:
                ret[package] = 1

        return ret


parser = argparse.ArgumentParser(description='Fetches packages from docker files in github.')
parser.add_argument('--user', help='Github username')
parser.add_argument('--password', help='Github account password')

args = parser.parse_args()
if __name__ == '__main__':
    result = {}
    repo_list = open('repo_list.txt', 'r')

    for repo in tqdm(repo_list, desc="Repository", position=2):
        g = GithubConnector(args.user, args.password, repo.strip())
        try:
            g.fetch_base_packages(result)
        except GithubException:
            print('Repo does not exist: {}'.format(repo))

    for key, value in result.items():
        print('{}: {}'.format(key, value))
