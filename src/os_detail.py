# Importing packages
import subprocess
from tqdm import tqdm


class ScriptRunner:
    def __init__(self, script):
        self.__script = script

    def run(self, args):
        # returns the stdout of the script
        output = subprocess.check_output([self.__script, args]).decode('utf-8')
        # extract the last but one line printed(which is the OS name)
        return output.split('\n')[-2]


if __name__ == '__main__':
    result = {}
    image_list = open('image_list.txt', 'r')
    script_runner = ScriptRunner('./fetch_os_details.sh')

    for image in tqdm(image_list, desc="Images", position=2):
        os = script_runner.run(image.strip())
        if os in result:
            result[os] += 1
        else:
            result[os] = 1

    for key, value in result.items():
        print('{}: {}'.format(key, value))
