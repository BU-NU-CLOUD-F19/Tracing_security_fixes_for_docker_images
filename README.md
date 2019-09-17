# Tracing security fixes for docker images

## Vision and Goals of the Project:

It is important to understand the pattern in which various security issues are fixed in the real world. 
Understanding this pattern is going to be useful to drive the automated remediations for similar security fixes in future. The goal of the project is to come up with a solution to scan the official images on DockerHub for potential security vulnerabilities and study them in order to train a model to detect such vulnerabilities and provide recommendations on fixing them. 

The base goals are:
* Trace various build manifests (Dockerfile, requirement.txt, Makefile, etc.) for official docker images from their respective GitHub repositories 
* Trace how their build manifests have evolved/changed to fix various security issues in the applications. 
	* E.g. when new security vulnerability (CVE) is announced, how a corresponding remediation is applied. 
* Conduct a study to identify how quick a security fix is done on official docker images.
* Train a model to recommend fixes for the vulnerabilities detected.
* Automate the process of creating PRs if a security threat is detected.

## Users and Personas

The key users of this product will be any admin or team that is responsible for publishing a docker image. 
It can also be individual software developers contributing to projects containing makefiles on github.

## Scope and features of the project:

* Identify fixes: Analyze a subset of the official docker images published on DockerHub and identify security vulnerabilities fixed as a result of changes in Dockerfile.
* Tag commits: Identify changes made in a commit and tag them as a security threat remediation or feature addition.
* Analyze trends: Create a report contains information regarding the speed at which an identified security threat is fixed in the official Docker Images.
* Automatic remediation: A stretch goal of the project is the automatic remediation when the security vulnerability is identified in a GitHub repository. This could automatic creation of a Pull Request containing the fix for the security threat or providing feedback in the repository with suggestions about the fixes.
* Choose a fix: Analyze the repository and providing a fix which better suits the project (When there are multiple fixes for a security threat).

## Solution Concept:

* CVE
* Clair
* Choose 20 official docker images from Dockerhub from their respective GitHub repositories, retrieve history of commits and manually see all the differences made to the makefiles. 
* Do creation of container image of past in present and feed to Clair to store list of features for that version of image.
* Verify the differences between this image and the base image. Only concerned about security issues.
* Automate the above steps using scripts for more official docker images
* Analyse the trends for remediation used by developers to fix these security issues.

### Process

* List of github repos of official images.
* For each repo, get commit history,
* For each commit in commit history, identify if change in docker file
* For each such commit, build image for that commit and input this container image to clair
* Clair gives back a report of security vulnerabilities identified for each image
* Compare reports of 2 consecutive commit images, and identify if any security threat was remediated.
* Trace back these reports to the actual commits and do git diff to see line changes made in docker file. * * Also, keep track of timestamp between the commit it was fixed, and the time it was published in CVE (to verify how fast it was fixed).
* Associate the change made with the security vulnerability resolved so that it can be useful for future comparisons.

## Acceptance Criteria

The project is deemed successful if

* it provides a successful study on how quickly security vulnerabilities are resolved in official docker images.
* a corpus of fixes associated with identified security threats which can be used for automatic remediation

Stretch goals:
* Automate the process of fixing the vulnerabilities and creating a PR for the fix
* A machine learning model to provide recommendations to the developer about the fix

## Release Planning:	

__Week 1-2__

* Literature study - Understand Dockerfiles, Clair tool requirements, Shift-left approach and CVE (Common Vulnerabilities and Exposures)
* Manually analyze official docker images, view commit history and identify how Dockerfiles evolve over time

__Week 3-4__ 

* Setup the base project
* Automate the process of fetching commit history for a given GitHub repository
* Generate a script to track changes between commits 

__Week 4-5__

* Identify commits contains a change in the Dockerfile
* Build images of the commits in the specified timestamp

__Week 6-7__

* Collect reports using Clair for the images generated
* Compare the reports to identify if a specific security threat is resolved

__Week 8-9__

* Identify the difference in the Dockerfile between commits and tag the change as a resolution for the security threat
* Run the script across identified official docker images to identify a corpus of remediations for security vulnerabilities
* Generate a report mapping the time elapsed between a security threat identification and remediation for each repository

__Week 10-11__

* Create a script to fetch the latest commit for a Github repository, build the docker image and use Claire to identify security threats
* Provide suggestions for security vulnerabilities identified in the repository using the remediations identified

____________
