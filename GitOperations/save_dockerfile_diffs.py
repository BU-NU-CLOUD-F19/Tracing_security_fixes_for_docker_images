## Imports
from github import Github
import pymongo
import click
from pprint import pprint
from tqdm import tqdm

def add_dockerfiles(dockerfiles, repo, repo_contents):
	"""
	Helper method to recursively traverse the repo and track dockerfiles
	"""
	for content in repo_contents:
		if content.type == 'dir':
			dockerfiles = add_dockerfiles(dockerfiles, repo, repo.get_contents(content.path))
		elif content.type == 'file' and content.name.endswith('Dockerfile'):
			dockerfiles.append(content)
	return dockerfiles

def fetch_commits_for_dockerfile(dockerfile, repo):
	"""
	Helper method to fetch commits info for a particular dockerfile
	"""
	dockerfile_commits = []
	dockerfile_commit = {}
	commits = repo.get_commits(path=dockerfile.path)
	for commit in commits:
		dockerfile_commit['commit_sha'] = commit.sha
		dockerfile_commit['author'] = commit.author.name if commit.author.name else "docker-library-bot"
		dockerfile_commit['last_modified'] = commit.last_modified
		for file in commit.files:
			if file.filename == dockerfile.path:
				dockerfile_commit['patch'] = file.patch
		dockerfile_commits.append(dockerfile_commit)
	return dockerfile_commits

@click.command()
@click.option('--username', prompt='User:', help='Your GitHub username.')
@click.option('--password', help='Your GitHub password.')
@click.option('--organization', help='Target GitHub organization.')
@click.option('--repository', help='Target GitHub repository under the given organization.')
def fetch_dockerfiles(username, password, organization, repository):
	"""
	Simple program that fetches commits from a master branch for a particular repository.
	"""

	# Authenticate and create a GitHub client
	g = Github(username, password)

	# Retrieve the given organization
	org = g.get_organization(organization)

	# Retrieve the repository under the given organization
	repo = org.get_repo(repository)

	## List of Dockerfiles to be tracked
	dockerfiles = []

	# Fetch all dockerfiles in the repo
	dockerfiles = add_dockerfiles(dockerfiles, repo, repo.get_contents(''))

	# Fetch commits info for each dockerfile
	dockerfiles_info = []
	id = 0
	for dockerfile in tqdm(dockerfiles, desc="Dockerfiles", position=1):
		commits_info = fetch_commits_for_dockerfile(dockerfile, repo)
		for commit_info in tqdm(commits_info, desc="commits", position=2):
			#commit_info['_id'] = id
			commit_info['dockerfile'] = dockerfile.path
			dockerfiles_info.append(commit_info)
			id = id + 1

		# print(dockerfile)
		# pprint(commits_info)
		# print("\n\n")

	print(id)

	client = pymongo.MongoClient('mongodb://localhost:27017/')
	db_list = client.list_database_names()
	mydb = client['security_fixes_db']
	mycol = mydb['dockerfile_commits']
	for info in dockerfiles_info:
		try:
			inserted = mycol.insert_one(info)
			print(inserted)
		except pymongo.errors.DuplicateKeyError:
			continue

if __name__ == '__main__':
    fetch_dockerfiles()
