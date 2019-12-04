# Tracing security fixes for docker images

## Installation and Deployment:
### Deliverable 1:

### Deliverable 2:

## Vision and Goals of the Project:

It is important to understand the pattern in which various security issues are fixed in the real world. 
Understanding this pattern is going to be useful to drive the automated remediations for similar security fixes in future. The goal of the project is to conduct a study on identifying how quickly OS package managers release patches to fix identified security threats. This will provide an oppertunity for developers to choose the OS and the OS packages which are less prone to security vulnerabilities or ones which are quick to rectify them. Developers can use the results of the study to identify which OS packages better conform to their security standards.

The base goals are:
* Trace Dockerfile for official docker images from their respective GitHub repositories and trace how quickly OS packages they rely on have addressed the secuirty vulnerabilities in them
	* E.g. when new security vulnerability (CVE) is announced, how soon a release with the corresponding remediation is available. 
* Conduct a study to identify the most common OS which docker images rely on

## Users and Personas

The key end-user of the study will be developers so that they can identify package publishers who are proactive towards fixing security threats
Developers and security analysts can use the results of the study to identify packages that are updated quickly and are reliable in terms of fixing any security vulnerability quickly. It can help decide the course of action while deciding two packages that have the same functionality
Developers can also use the tool to identify common OS distributions used by official docker images
Researches can further the study by incorporating the publishing history of OS distributions not targetted by this study (like Alpine, Centos, etc) to provide a single source of truth for developers to use while identifying potential packages to use

## Scope and features of the project:

The study consists of two deliverables. The first is an analysis on how quickly security vulnerabilities are fixed in OS packages identified by their use in offical docker images. The second part is the identification of OS distribution the official docker images rely on.
* Study on security fixes on OS packages:
	* Analyze a subset of the official docker images published on DockerHub and identify security vulnerabilities fixed in the OS packages they use and generate a report containing information regarding the speed at which an identified security threat is fixed.

* Study on os distribution:
	* Identify the Operating Systems which official docker images rely on

## Solution Concept:

### System Components:

Below is a description of the system components and concepts that will be used to accomplish our goals:

* Security Vulnerability: A vulnerability is a problem in a project's code that could be exploited to damage the confidentiality, integrity, or availability of the project or other projects that use its code. Depending on the severity level and the way your project uses the dependency, vulnerabilities can cause a range of problems for your project or the people who use it.

* CVE: In order to track vulnerabilities in packages, CVEs can be used. MITRE's [Common Vulnerabilities and Exposures (CVE) List](https://cve.mitre.org/) is a list of entries - each containing an identification number, a description, and at least one public reference, for publicly known cybersecurity vulnerabilities.

* Docker: Docker is a set of platform-as-a-service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files; they can communicate with each other through well-defined channels.

* Docker Hub: [Docker Hub](https://docs.docker.com/docker-hub/) is a service provided by Docker for finding and sharing container images with your team. It is a registry of Docker images. You can think of the registry as a directory of all available Docker images. If required, one can host their own Docker registries and can use them for pulling images.

* Dockerfile: Docker can build images automatically by reading the instructions from a Dockerfile. A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. Using docker build users can create an automated build that executes several command-line instructions in succession.

* Clair:  [Clair](https://github.com/coreos/clair) is an open-source container vulnerability scanner recently released by CoreOs. The tool cross-checks if a Docker image's operating system and any of its installed packages match any known insecure package versions. The vulnerabilities are fetched from OS-specific common vulnerabilities and exposures (CVE) databases.

### Global Architectural Structure

The development process will involve a set of manual tasks initially which, upon completion, will be repeated over a larger set of images and repositories, using automation. All the scripts are a part of a Python project which will be containerized using a docker image. Overview for the process is sequential and as follows:
* Choose 20 official dockers images from DockerHub, and obtain the list of URLs to their respective GitHub repositories. Make sure that the images have been built from repositories hosted on GitHub.
* For each repository, get the commit history, which will be a list of metadata corresponding to each commit.
* For each commit in this commit history, identify if the commit involved a change in the Dockerfile. We only filter out such commits into another list of commits.
* For each such commit from the filtered list, build the image of the project at that commit instance and input this container image to Clair tool.
* Clair gives back a report of security vulnerabilities identified for each input image. Store these reports in a database.
* Compare reports of 2 consecutive commit images (consecutive in terms of timestamp), and identify if any security threat was remediated amongst these commits.
* Traceback these reports to the actual commits and run 'git diff' command to see line changes made in Dockerfile. This will help us realise what type of fix this was.
* Also, keep track of timestamp between the commit it was fixed, and the time it was published in CVE (to verify how fast it was fixed).
* Associate the change made with the security vulnerability resolved so that it can be useful for future comparisons and resourceful insights.

## Acceptance Criteria

* Provides a successful study on how quickly security vulnerabilities are resolved in official docker images.
* Corpus of fixes associated with identified security threats which can be used for automatic remediation

Stretch goals:
* Automate the process of fixing the vulnerabilities and creating a PR for the fix
* A machine learning model to provide recommendations to the developer about the fix

## Presentations

* [Sprint 1](https://docs.google.com/presentation/d/1u_rIKK8wvnD7Xvt3UBjcM73yTEVpwdkq6YXQhtvllKQ/edit#slide=id.gc6fa3c898_0_0)
* [Sprint 2](https://docs.google.com/presentation/d/1g8OgQm3UC-3eg0PtpMjehUXxjZoMXTra6UJSPKpe8sg/edit#slide=id.g6326875e59_2_14)
* [Sprint 3](https://docs.google.com/presentation/d/1nO3L1yo2AQMYrWhZjRftRH6G1ljoQjPp54FURNxAFJ8/edit?usp=sharing)
* [Sprint 4](https://docs.google.com/presentation/d/138kz-S86585wOn3MGHJQFPMt40wDxpc5-HM6qvw6NRQ/edit?ts=5dc48c1c#slide=id.gc6f980f91_0_42)
* [Sprint 5](https://docs.google.com/presentation/d/1AK94dqiRsv9oadfjd2UsOvm9WsR1RbAyVLnNqvT9lOY/edit?ts=5dd5c132#slide=id.g758161e409_0_130)
____________

