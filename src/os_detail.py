# Importing packages
import subprocess
import argparse

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
    result = {}
    image_list = open(args.images, 'r')
    script_runner = ScriptRunner('./fetch_os_details.sh')

    for image in tqdm(image_list, desc="Images", position=2):
        os = script_runner.run(image.strip())
        if os in result:
            result[os] += 1
        else:
            result[os] = 1

    for key, value in result.items():
        print('{}: {}'.format(key, value))
