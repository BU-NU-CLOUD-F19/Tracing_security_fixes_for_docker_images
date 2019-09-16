# Tracing_security_fixes_for_docker_images

## Vision and Goals of the Project:

It is important to understand the pattern in which various security issues are fixed in the real world. 
Understanding this pattern is going to be useful to drive the automated remediations for similar security fixes in future. The goal of the project is to come up with a solution to scan the official images on DockerHub for potential security vulnerabilities and study them in order to train a model to detect such vulnerabilities and provide recommendations on fixing them. 

The base goals are:
* Trace various build manifests (Dockerfile, requirement.txt, Makefile, etc.) for official docker images from their respective github repositories 
* Trace how their build manifests have evolved/changed to fix various security issues in the applications. 
	* E.g. when new security vulnerability (CVE) is announced, how a corresponding remediation is applied. 
* Conduct a study to identify how quick a security fix is done on official docker images.
* Train a model to recommend fixes for the vulnerabilities detected.
* Automate the process of creating PRs if a security threat is detected.

## Users and Personas

The key users of this product will be any admin or team that is responsible for publishing a docker image. 
It can also be individual software developers contributing to projects containing makefiles on github.
The product won’t  be applicable to users who expect to be alerted regarding security vulnerabilities in their source code.

## Scope and features of the project:
The scope of the project is a subset of official docker images published on DockerHub. 
One of the stretch goals will be the automatic remediation of the security threats by creating a PR with the fix to the repo.
If there are multiple fixes for a security threat, then analyzing the docker image and determining the fix which better matches the project.
The product won’t consider security vulnerabilities in the source code.

### Features:
* Identifies changes made in a commit and tag them as a security threat or a feature addition.
* Demonstrates how a security threat is fixed in a particular commit.
* Identifies what are the trends followed by developer while fixing these vulnerabilities.
* Proves why shift-left paradigm is better
* Outputs a visualization on the various metrics learned while performing the study (TBD).

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

The project can be deemed successful if

* it provides a successful study on how to detect security threats and learn how quickly these vulnerabilities are resolved.
* a machine learning model is trained to provide recommendations

A stretch goal will be to automate the process of fixing the vulnerabilities and creating a PR for the fix.

## Release Planning:	

### Week 1-2 :

* Literature study - understanding docker files, Clair tool requirements, Shift-left approach and CVEs.
* Manually analyzing official docker images and find how the docker files change in the corresponding github repositories.

### Week 3-4 : 

* Setup the base project
* Automate the process of fetching commit history for a given github repository
* Writing scripts to track changes between commits 

### Week 4-5 : 

* Identifying commits which cause a change in the Dockerfile
* Building images of these commits in the specified timestamp

### Week 6-7 :
* Generating reports using Clair for the images generated.
* Comparing the reports to identify specific security threat resolved

### Week 8-9 : 

* Identifying the difference in the dockerfile between the commits and tagging the change as a resolution for the security threat
* Running the script across identified official docker images to identify a corpus of remediations for security threats
* Generate a report mapping the time elapsed between a security threat identification and remediation for each repository.

### Week 10-11 : 

* Creating a script capable of fetching the latest commit for a Github repository, building the docker image and running Claire on the image to identify security threats.
*Using the resolutions discovered to provide suggestions to resolve the security vulnerabilities identified in the repo.

____________