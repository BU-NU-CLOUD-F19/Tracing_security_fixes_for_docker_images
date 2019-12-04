# Importing packages
import subprocess
import argparse
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import csv

from collections import OrderedDict
from tqdm import tqdm


class ScriptRunner:
    """
    A class responsible for running a shell script and returning the last but one line printed
    """
    def __init__(self, script):
        """
        :param script: Path of the script to execute
        """
        self.__script = script

    def run(self, docker_image):
        """
        Runs the script for the given docker image
        :param docker_image: the docker image which is analysed
        :return: the OS platform used by the docker image
        """
        # returns the stdout of the script
        output = subprocess.check_output([self.__script, docker_image]).decode('utf-8')
        # extract the last but one line printed(which is the OS name)
        return output.split('\n')[-2]


parser = argparse.ArgumentParser(description='Counts the number of images which rely on each OS')
parser.add_argument('--images', help='File containing list of images to analyse')

args = parser.parse_args()
if __name__ == '__main__':
    results = {}
    image_list = open(args.images, 'r')
    script_runner = ScriptRunner('./fetch_os_details.sh')

    for image in tqdm(image_list, desc="Images", position=2):
        os = script_runner.run(image.strip())
        if os in results:
            results[os] += 1
        else:
            results[os] = 1

    sorted_results = OrderedDict(sorted(results.items(), key=lambda x: x[1], reverse=True))

    labels = []
    val = []
    os_list = ["debian", "ubuntu", "alpine", "centos"]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

    total = 0
    other = 0

    for key, value in sorted_results.items():
        if key in os_list:
            other += value
        else:
            labels.append(key)
            val.append(value)

    labels.append("Other")
    val.append(other)

    # Save plot to file system
    plt.pie(val, labels=labels, startangle=90, colors=cm.get_cmap('Set3').colors)
    plt.axis('equal')
    plt.savefig('os_distribution.png')

    # Save the distribution data to file system
    w = csv.writer(open("os_distribution.csv", "w"))
    for key, value in results.items():
        w.writerow([key, value])
