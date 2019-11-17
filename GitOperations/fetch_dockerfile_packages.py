## Imports
from github import Github
import click
from pprint import pprint
from tqdm import tqdm
from collections import defaultdict
import string
import urllib
from bs4 import BeautifulSoup

def get_dockerfiles(dockerfiles, repo, repo_contents, return_first=False):
	"""
	Helper method to recursively traverse the repo and track dockerfiles
	"""
	for content in repo_contents:
		if content.type == 'dir':
			dockerfiles = get_dockerfiles(dockerfiles, repo, repo.get_contents(content.path))
		elif content.type == 'file' and content.name.endswith('Dockerfile'):
			dockerfiles.append(content)
			if return_first:
				return dockerfiles
	return dockerfiles

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
	            if word.isupper() or (any(word.startswith(punct) for punct in string.punctuation)):
	                line = line.replace(word, "")
	        line = line.strip()
			# Add the clean line to the list of packages
	        if line:
	            packages = packages + line.split()

	return ','.join(packages)

def get_version_date(os, package, package_version):
	"""
	Get the date for when a particular version of the package was published
	"""
	if os == "ubuntu":
		url = "https://launchpad.net/ubuntu/+source/"+package+"/+publishinghistory"
	elif os ==  "debian":
		url = "https://launchpad.net/debian/+source/"+package+"/+publishinghistory"
	request = urllib.request.urlopen(url)
	html_doc = request.read().decode('utf-8')
	soup = BeautifulSoup(html_doc, 'html.parser')
	data_table_rows = soup.find("table", attrs={"class": "listing"}).find("tbody").find_all("tr")
	published_date = ''
	# For each published version history, check for the version and return published date
	for row in data_table_rows:
		cells = row.find_all("td")
		for cell in cells:
			cell_version = cell.get_text().strip()	
			if cell_version == package_version:
				cell_date = cells[1].get_text()
				cell_status = cells[2].get_text()
				if cell_date and cell_status != "Deleted":
					published_date = cell_date
					print(published_date)
					return published_date
	return published_date
	



@click.command()
@click.option('--username', prompt='User:', help='Your GitHub username.')
@click.option('--password', prompt=True, hide_input=True, help='Your GitHub password.')
def fetch_dockerfiles(username, password):
	"""
	Simple program that fetches commits from a master branch for a particular repository.
	"""

	# Authenticate and create a GitHub client
	g = Github(username, password)

	# Fetch repositories
	repo_list = open('repo_list.txt', 'r')

	dockerfile_packages_map = defaultdict(list)

	print(repo_list)

	#for repo in tqdm(repo_list, desc="Repository", position=2):
	for repo in repo_list:
		repo = repo.strip()
		org = repo.split('/')[0]
		repository = repo.split('/')[1]
		try:
			# Retrieve the given organization
			org = g.get_organization(org)
			# Retrieve the repository under the given organization
			repository = org.get_repo(repository)

			print("Accessing", repository)

			## List of Dockerfiles to be tracked
			dockerfiles = []
			# Fetch all dockerfiles in the repo
			dockerfiles = get_dockerfiles(dockerfiles,
			 						      repository,
										  repository.get_contents(''),
										  return_first=True)

			# Retrieve packages for dockerfiles in the current repository
			packages = fetch_packages_for_dockerfile(dockerfiles[0])

			# Update dockerfile_packages_map
			dockerfile_packages_map[repo] = packages

			print(len(dockerfiles), packages)

		except Exception as e:
			print('Repo does not exist: {}'.format(repo) + str(e))


if __name__ == '__main__':
    fetch_dockerfiles()
