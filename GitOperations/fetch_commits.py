## Imports
from github import Github
import click

@click.command()
@click.option('--username', prompt='User:', help='Your GitHub username.')
@click.option('--password', help='Your GitHub password.')
@click.option('--organization', help='Target GitHub organization.')
@click.option('--repository', help='Target GitHub repository under the given organization.')
def fetch_commits(username, password, organization, repository):
	"""
	Simple program that fetches commits from a master branch for a particular repository.
	"""

	# Authenticate and create a GitHub client
	g = Github(username, password)

	# Retrieve the given organization
	org = g.get_organization(organization)

	# Retrieve the repository under the given organization
	repo = org.get_repo(repository)

	# Fetch commits from the master branch
	commits = repo.get_commits()

	# Print last 10 commit hashes, authers and stats
	for commit in commits[:20]:
		print(commit, "Author: ", commit.author, " Stats: ", commit.stats.raw_data)

if __name__ == '__main__':
    fetch_commits()