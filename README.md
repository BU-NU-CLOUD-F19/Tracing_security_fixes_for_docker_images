# Tracing security fixes for docker images

## Vision and Goals of the Project:

It is important to understand the pattern in which various security issues are fixed in the real world. 
Understanding this pattern is going to be useful to drive the automated remediations for similar security fixes in future. The goal of the project is to conduct a study on identifying how quickly OS package managers release patches to fix identified security threats. This will provide an oppertunity for developers to choose the OS and the OS packages which are less prone to security vulnerabilities or ones which are quick to rectify them. Developers can use the results of the study to identify which OS packages better conform to their security standards.

The base goals are:
* Trace Dockerfile for official docker images from their respective GitHub repositories and trace how quickly OS packages they rely on have addressed the secuirty vulnerabilities in them
	* E.g. when new security vulnerability (CVE) is announced, how soon a release with the corresponding remediation is available. 
* Conduct a study to identify the most common OS which docker images rely on

## Users and Personas

The project promotes left-shift approach allowing developers to choose the OS distribution and packages which was aggresively responding to security issues. Some ways to use the study are:

### How to use the study?

 * Developers identify package publishers who are proactive towards fixing security threats
 * Developers and security analysts can use the results of the study to identify packages that are updated quickly and are reliable in terms of fixing any security vulnerability quickly. It can help decide the course of action while deciding two packages that have the same functionality
 * Developers can also use the tool to identify common OS distributions used by official docker images
 * Researches can further the study by incorporating the publishing history of OS distributions not targetted by this study (like Alpine, Centos, etc) to provide a single source of truth for developers to use while identifying potential packages to use

## Scope and features of the project:

The study consists of two deliverables. The first is an analysis on how quickly security vulnerabilities are fixed in OS packages identified by their use in offical docker images. The second part is the identification of OS distribution the official docker images rely on.
* Study on security fixes on OS packages:
	* Analyze a subset of the official docker images published on DockerHub and identify security vulnerabilities fixed in the OS packages they use and generate a report containing information regarding the speed at which an identified security threat is fixed.

* Study on os distribution:
	* Identify the Operating Systems which official docker images rely on

## System Components:

Below is a description of the system components and concepts that we used to accomplish our goals:

* Security Vulnerability: A vulnerability is a problem in a project's code that could be exploited to damage the confidentiality, integrity, or availability of the project or other projects that use its code. Depending on the severity level and the way your project uses the dependency, vulnerabilities can cause a range of problems for your project or the people who use it.

* CVE: In order to track vulnerabilities in packages, CVEs can be used. MITRE's [Common Vulnerabilities and Exposures (CVE) List](https://cve.mitre.org/) is a list of entries - each containing an identification number, a description, and at least one public reference, for publicly known cybersecurity vulnerabilities.

* Docker: Docker is a set of platform-as-a-service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files; they can communicate with each other through well-defined channels.

* Docker Hub: [Docker Hub](https://docs.docker.com/docker-hub/) is a service provided by Docker for finding and sharing container images with your team. It is a registry of Docker images. You can think of the registry as a directory of all available Docker images. If required, one can host their own Docker registries and can use them for pulling images.

* Dockerfile: Docker can build images automatically by reading the instructions from a Dockerfile. A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. Using docker build users can create an automated build that executes several command-line instructions in succession.

* Clair:  [Clair](https://github.com/coreos/clair) is an open-source container vulnerability scanner recently released by CoreOs. The tool cross-checks if a Docker image's operating system and any of its installed packages match any known insecure package versions. The vulnerabilities are fetched from OS-specific common vulnerabilities and exposures (CVE) databases.

* X-Force: [X-Force](https://www.ibm.com/security/services/ibm-x-force-incident-response-and-intelligence) is a cloud-based threat intelligence platform that allows you to consume, share and act on threat intelligence. It enables you to rapidly research the latest global security threats, aggregate actionable intelligence, consult with experts and collaborate with peers.

* Ubuntu and Debian Launchpad: [Launchpad](https://launchpad.net) is a web application and website that allows users to develop and maintain software, particularly open-source software. It provides API's to access various details about software including publishing history.

## Methodology and Observations:

The development process started with a research to identify and gather the required data from various sources. Python was selected as the application language due to its support of easy manipulation of data. The deliverables of the projects are available in two different scripts and a user can choose the run a script based on their requirement.

### Deliverable 1: Identify how quickly security issues are fixed in base OS packages

#### Process: 
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/workflow.JPG" alt="workflow">
</p>

**Step 1:** Identify docker images of interest and gather the project's source repository (which contains the dockerfiles) of these images

**Step 2:** Parse the individual dockerfiles to obtain a list of OS packages which are installed in it

**Step 3:** Deduplicate the packages obtained so that if a package is installed by multiple docker images, then the analysis of security fixes on the package is performed only once

**Step 4:** Query Clair's postgres database to obtain the vulnerabilities which are identified and the release versions which fixed the identified vulnerabilities in each of these packages

**Step 5:** Query X-Force to obtain the date in which each security vulnerability was reported

**Step 6:** Query Ubuntu's or Debian's launchpad to identify when the version of the package which fixed a particular security vulnerability was released

**Step 7:** The duration of a security threat is the number of days which have elapsed from the date a security vulnerabilty was reported (obtained from step 5) and when a fix was released (obtained from step 6). Compute the difference in these dates to obtain the number of days it took to fix a security threat

**Step 8:** Using the data obtained in the previous step, aggreate and plot graphs to study about the trends of security fixes in OS packages used by official docker images

### Observations:
The results obtained from running the script for deliverable 1 are as follows:

* Vulnerabilities per package in analyzed dockerfiles
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Number_of_vulnerabilities_per_package_in_the_dedup_data.png" alt="workflow">
</p>
The `openssl` package consists of the most vulnerabilities out of the ~50 packages we analysed, followed by `curl` and `binutils`.

#### Debian
***Time taken to fix any type of vulnerabilities on average***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Debian_Vulnerability_Fixes.png" alt="workflow">
</p>
This histogram shows that close to 70% of the vulnerabilities on Debian packages are fixed within 250 days of reporting.
<br/>

***Time taken to fix High severity vulnerabilities***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Debian_Vulnerability_Fixes_High.png" alt="workflow">
</p>
This histogram shows that more than 50% High severity vulnerabilities on Debian packages are fixed about 100-150 days of reporting.
<br/>

***Time taken to fix Medium severity vulnerabilities***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Debian_Vulnerability_Fixes_Medium.png" alt="workflow">
</p>
This histogram shows that almost all Medium severity vulnerabilities on Debian packages are fixed about 500-600 days of reporting, with about 70% being patched within 150 days.
<br/>

***Time taken to fix Low severity vulnerabilities***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Debian_Vulnerability_Fixes_Low.png" alt="workflow">
</p>
This histogram shows that about 75% of low vulnerabilities on Debian packages are fixed within 400 days of reporting, although the distribution is somewhat skewed over more days as developers may tend to fix them only after dealing with more critical patches.
<br/>

#### Ubuntu
***Time taken to fix any type of vulnerabilities on average***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Ubuntu_Vulnerability_Fixes.png" alt="workflow">
</p>
This histogram shows that close to 50% of the vulnerabilities on Ubuntu packages are fixed withing 100 days of reporting, which is quite impressive. Though there are some vulnerabilities in both Debian and Ubuntu packages that take 5 years to be resolved - probably due to negligence or due to the less severity of the vulnerability.
<br/>

***Time taken to fix High severity vulnerabilities***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Ubuntu_Vulnerability_Fixes_High.png" alt="workflow">
</p>
This histogram shows that about 70% of High vulnerabilities on Ubuntu packages are fixed within 200 days of reporting, which is still little short of the 50% fixed within 100-150 days for Debain packages. Although, about 30% take more or less 600-700 days to patch.
<br/>

***Time taken to fix Medium severity vulnerabilities***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Ubuntu_Vulnerability_Fixes_Medium.png" alt="workflow">
</p>
This histogram shows that almost 75% Medium severity vulnerabilities on Ubuntu packages are fixed within 300 days which is quite slow compared to Debian packages.
<br/>

***Time taken to fix Low severity vulnerabilities***
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/Ubuntu_Vulnerability_Fixes_Low.png" alt="workflow">
</p>
This histogram shows that about 65-70% Low severity vulnerabilities on Ubuntu packages are fixed within 300 days of reporting, which is almost at par with Debain packages at 75% fixed within 400 days. 
<br/>

### Deliverable 2: Identify OS distribution
#### Process:

**Step 1:** Identify docker images of interest and gather the docker image names and tags

**Step 2:** Pull each docker image and run the image in a container

**Step 3:** Export the source files used by the docker image in a specified location using the docker export command

**Step 4:** Identify the OS which the docker image relies on using the os-release file in the etc folder

**Step 5:** Aggregate data across multiple docker images and plot a chart to visualize the OS distribution

#### Observations:
The result obtained from running the script over 142 official docker images are:
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/os_distribution.JPG" alt="os_distribution">
</p>

 * We identified that Debian, Ubuntu and Alpine are the most commonly used Operating Systems to base the docker images on and an analysis on the packages belonging to these OS packages will provide us with details on security remediations in about 85% of the docker images
 * Alpine being a light-weight OS was expected to be the top choice of Operating System to use but popular to contrary belief we found that more than 50% of the official docker images rely on Debian

## Installation and Deployment:

Clone the github repository to get access to the scripts:
```
git clone https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images.git
```

To build and run the scripts, a stable version of Python3 and Pip3 is required in the system. [Install Python3](https://www.python.org/downloads/) | [Install Pip3](https://help.dreamhost.com/hc/en-us/articles/115000699011-Using-pip3-to-install-Python3-modules/)

To install all the python packages which are required using
```
pip3 install -r requirements.txt
```

Individual instructions to run the scripts for each deliverable is:

#### Deliverable 1:

To run the main script of deliverable 1, run the following command:

```
python3 deliverable1/analyze_security_fixes.py"
```

The data files are already saved in the output folder in the deliverable1 directory. But if you want to run them from scratch follow the instructions given by the script.

1. "Enter (Y/N) to fetch clair reports:"
	* If you enter 'Y', you'll need to enter the GitHub username and password and the X-Force API Key.
	* This saves a CSV with the clair report details in deliverables1/outputs folder.
	* You can skip this step if you already have the reports stored in the outputs folder by entering 'N'.
	
2. "Please enter either Y or N to fetch clair reports:"
	* If you enter 'Y', you'll need to enter the X-Force API Key.
	* This saves the analysis reports as CSVs the graphs in the deliverables1/outputs folder.
		
The command-line interface for deliverable 1 looks like this:
<p align="center">
  <img src="https://github.com/BU-NU-CLOUD-F19/Tracing_security_fixes_for_docker_images/blob/master/readme_resources/deliverable1_screenshot.png" alt="deliverable1_screenshot">
</p>

#### Deliverable 2:
Docker is a requirement for building and running the script for deliverable 2. [Install Docker](https://docs.docker.com/v17.09/engine/installation/)

The script accepts a file containing the list of docker images to analyse. You can choose to create one, or use the files present under the deliverable2/input folder.

To run the script, 

```
python3 deliverable2/analyze_os_distribution.py --images="path_to_image_list"
```
The script saves a CSV and a piechart with details of OS distribution in deliverables2/outputs folder.
____________
## Presentations

* [Sprint 1](https://docs.google.com/presentation/d/1u_rIKK8wvnD7Xvt3UBjcM73yTEVpwdkq6YXQhtvllKQ)
* [Sprint 2](https://docs.google.com/presentation/d/1g8OgQm3UC-3eg0PtpMjehUXxjZoMXTra6UJSPKpe8sg)
* [Sprint 3](https://docs.google.com/presentation/d/1nO3L1yo2AQMYrWhZjRftRH6G1ljoQjPp54FURNxAFJ8)
* [Sprint 4](https://docs.google.com/presentation/d/138kz-S86585wOn3MGHJQFPMt40wDxpc5-HM6qvw6NRQ)
* [Sprint 5](https://docs.google.com/presentation/d/1AK94dqiRsv9oadfjd2UsOvm9WsR1RbAyVLnNqvT9lOY)
* [Final Presentation](https://docs.google.com/presentation/d/1reov-Rw80hjlXjbuajsBP3rjXAhRqoLQ9E2BKuOR-j0)
____________
## Video Presentation

* [Final Project Demo](https://www.youtube.com/watch?v=wfNr2roCKlk&feature=youtu.be)
