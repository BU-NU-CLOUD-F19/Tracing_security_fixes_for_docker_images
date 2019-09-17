# Tracing security fixes for docker images

## Vision and Goals of the Project:

It is important to understand the pattern in which various security issues are fixed in the real world. 
Understanding this pattern is going to be useful to drive the automated remediations for similar security fixes in future. The goal of the project is to come up with a solution to scan the official images on DockerHub for potential security vulnerabilities and study them in order to train a model to detect such vulnerabilities and provide recommendations on fixing them. 

The base goals are:
* Trace various build manifests (Dockerfile, requirement.txt, Makefile, etc.) for official docker images from their respective GitHub repositories 
* Trace how their build manifests have evolved/changed to fix various security issues in the applications. 
	* E.g. when new security vulnerability (CVE) is announced, how the corresponding remediation is applied. 
* Conduct a study to identify how quick a security fix is done on official docker images.
* Train a model to recommend fixes for the vulnerabilities detected.
* Automate the process of creating PRs if a security threat is detected.

## Users and Personas

The key users of this product will be any admin or team that is responsible for publishing a docker image. 
It can also be individual software developers contributing to projects containing manifests on github.

## Scope and features of the project:

* Identify fixes: Analyze a subset of the official docker images published on DockerHub and identify security vulnerabilities fixed as a result of changes in Dockerfile.
* Tag commits: Identify changes made in a commit and tag them as a security threat remediation or feature addition.
* Analyze trends: Create a report contains information regarding the speed at which an identified security threat is fixed in the official Docker Images.
* Automatic remediation: A stretch goal of the project is the automatic remediation when the security vulnerability is identified in a GitHub repository. This could automatic creation of a Pull Request containing the fix for the security threat or providing feedback in the repository with suggestions about the fixes.
* Choose a fix: Analyze the repository and providing a fix which better suits the project (When there are multiple fixes for a security threat).

## Solution Concept:

### System Components:

Below is a description of the system components and concepts that will be used to accomplish our goals:

* Security Vulnerability: A vulnerability is a problem in a project's code that could be exploited to damage the confidentiality, integrity, or availability of the project or other projects that use its code. Depending on the severity level and the way your project uses the dependency, vulnerabilities can cause a range of problems for your project or the people who use it.

* CVE: In order to track vulnerabilities in packages, CVEs can be used. MITRE's [Common Vulnerabilities and Exposures (CVE) List](https://cve.mitre.org/) is a list of entries - each containing an identification number, a description, and at least one public reference, for publicly known cybersecurity vulnerabilities.

* Docker: Docker is a set of platform-as-a-service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files; they can communicate with each other through well-defined channels.

* Docker Hub: [Docker Hub](https://docs.docker.com/docker-hub/) is a service provided by Docker for finding and sharing container images with your team. 

* Dockerfile: Docker can build images automatically by reading the instructions from a Dockerfile. A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. Using docker build users can create an automated build that executes several command-line instructions in succession.

* Clair:  [Clair](https://github.com/coreos/clair) is an open-source container vulnerability scanner recently released by CoreOs. The tool cross-checks if a Docker image's operating system and any of its installed packages match any known insecure package versions. The vulnerabilities are fetched from OS-specific common vulnerabilities and exposures (CVE) databases.

### Global Architectural Structure

The development process will involve a set of manual tasks initially which, upon completion, will be repeated over a larger set of images and repositories, using automation. Overview for the process is sequential and as follows:
* Choose 20 official dockers images from DockerHub, and obtain the list of URLs to their respective GitHub repositories.
* For each repository, get the commit history, which will be a list of metadata corresponding to each commit.
* For each commit in this commit history, identify if the commit involved a change in the Dockerfile. We only filter out such commits into another list of commits.
* For each such commit from the filtered list, build the image of the project at that commit instance and input this container image to Clair tool.
* Clair gives back a report of security vulnerabilities identified for each input image. Store these reports in a database.
* Compare reports of 2 consecutive commit images (consecutive in terms of timestamp), and identify if any security threat was remediated amongst these commits.
* Trace back these reports to the actual commits and run 'git diff' command to see line changes made in dockerfile. This will help us realise what type of fix this was.
* Also, keep track of timestamp between the commit it was fixed, and the time it was published in CVE (to verify how fast it was fixed).
* Associate the change made with the security vulnerability resolved so that it can be useful for future comparisons and resourceful insights.

## Acceptance Criteria

* Provides a successful study on how quickly security vulnerabilities are resolved in official docker images.
* Corpus of fixes associated with identified security threats which can be used for automatic remediation

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

