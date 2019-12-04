from fetch_date_diffs import GithubCli
from connect_postgres import PostgresOps
from scrape_vulnerability_timestamps import AnalyzeTimeStamps
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import click
from tqdm import tqdm
from datetime import datetime

@click.command()
@click.option('--username', prompt='User', help='Your GitHub username.')
@click.option('--password', prompt=True, hide_input=True, help='Your GitHub password.')
@click.option('--api_key', prompt='XForce API Key', hide_input=True, help='XForce API Key')
def save_clair_reports(username, password, api_key):
    """
    Entry function
    :param username: Github Username
    :param password: Github Password
    :param api_key: XForce API Key
    """
    cli_obj = GithubCli(username, password, api_key)

    dockerfiles = cli_obj.fetch_dockerfiles()
    packages = []
    for image_name in dockerfiles:
        if dockerfiles[image_name]:
            packages.append(dockerfiles[image_name])
    packages = [j for i in packages for j in i]
    packages = list(set(packages))

    print("Fetching information for", len(packages), "packages.")
    postgres_obj = PostgresOps(packages)
    postgres_obj.connect()
    clair_db_reports = postgres_obj.get_clair_reports()

    clair_db_reports.to_csv("outputs/clair_reports.csv", index=False)

@click.command()
@click.option('--api_key', prompt='XForce API Key', hide_input=True, help='XForce API Key')
def analyze_date_diff(api_key):
    tqdm.pandas()

    full_data_path = "outputs/clair_reports.csv"
    data = pd.read_csv(full_data_path, index_col=0)
    plt.figure(figsize=(10, 10))
    data.Package.value_counts()[::-1].plot('barh',
                                           title="Number of vulnerabilities per package in the full data")
    plt.savefig("outputs/Number_of_vulnerabilities_per_package_in_the_full_data.png")

    analyze_ts = AnalyzeTimeStamps(api_key)

    ## Deduplicating
    data['OS_base_name'] = data.apply(lambda row: row['OS'].split(":")[0], axis=1)
    data = data[~data[['Package', 'Vulnerability', 'Package_Version', 'OS_base_name']].duplicated()]

    ## Fetching dates when vulnerabilities were reported and fixed
    data['Date_Reported'] = data.progress_apply(lambda r:
                                                analyze_ts.fetch_xforce_timestamp(r['Vulnerability']),
                                                axis=1)
    data['Date_Fixed'] = data.progress_apply(lambda row:
                                             analyze_ts.fetch_version_timestamp(row['OS'],
                                                                                row['Package'],
                                                                                row['Package_Version']),
                                             axis=1)

    def get_date_diff(row):
        date_format = "%Y-%m-%d"
        if row['Date_Fixed']:
            fixed = datetime.strptime(row['Date_Fixed'], date_format)
        else:
            fixed = None
        if row['Date_Reported']:
            reported = datetime.strptime(row['Date_Reported'], date_format)
        else:
            reported = None
        if fixed and reported:
            return abs((fixed - reported).days)
        else:
            return None

    data['Days_For_Fix'] = data.progress_apply(lambda row: get_date_diff(row), axis=1)

    data.to_csv('outputs/vulnerability_timestamps.csv')
    columns = ['Package', 'Vulnerability', 'OS', 'Package_Version', 'OS_base_name',
               'Date_Reported', 'Date_Fixed', 'Days_For_Fix']
    data = data[columns]

    ## Plotting analysis
    plt.figure(figsize=(10, 10))
    data.Package.value_counts()[::-1].plot('barh',
                                            title="Number of vulnerabilities per package in the de-duplicated data")
    plt.savefig("outputs/Number_of_vulnerabilities_per_package_in_the_dedup_data.png")

    plt.figure(figsize=(10, 10))
    data.OS.value_counts()[::-1].plot('barh',
                                      title="OS Distribution")
    plt.savefig("outputs/OS_Distribution")

    day_fixed_df = data[~data['Days_For_Fix'].isnull()]
    plt.figure(figsize=(10, 10))
    df = day_fixed_df['Days_For_Fix'][day_fixed_df['OS_base_name'] == 'debian']
    ax = df.plot('hist',
                 weights=np.ones_like(df.index) / len(df.index),
                 title="Time for package vulnerability fixes for Debian")
    ax.set(xlabel='No of days')
    plt.savefig("outputs/Debian_Vulnerability_Fixes.png")

    plt.figure(figsize=(10, 10))
    df = day_fixed_df['Days_For_Fix'][day_fixed_df['OS_base_name'] == 'ubuntu']
    ax = df.plot('hist',
                 weights=np.ones_like(df.index) / len(df.index),
                 title="Time for package vulnerability fixes for Ubuntu")
    ax.set(xlabel='No of days')
    plt.savefig("outputs/Ubuntu_Vulnerability_Fixes.png")

    debian_info = data[data['OS_base_name'] == 'debian']
    print("For Debian:")
    print(len(debian_info[~debian_info['Date_Reported'].isnull()]), "vulnerabilities were reported")
    print(len(debian_info[~debian_info['Date_Fixed'].isnull()]), "vulnerabilities were fixed")

    ubuntu_info = data[data['OS_base_name'] == 'ubuntu']
    print("For Ubuntu:")
    print(len(ubuntu_info[~ubuntu_info['Date_Reported'].isnull()]), "vulnerabilities were reported")
    print(len(ubuntu_info[~ubuntu_info['Date_Fixed'].isnull()]), "vulnerabilities were fixed")


if __name__ == '__main__':
    if not os.path.exists("outputs"):
        os.mkdir("outputs/")

    save_reports = input("Enter (Y/N) to fetch clair reports:")
    if save_reports == "Y":
        save_clair_reports()
        print("Clair reports are saved in the outputs directory.")
    elif save_reports == "N":
        pass
    else:
        print("Please enter either Y or N to fetch clair reports")

    analyze_timestamps = input("Enter (Y/N) to analyze time for security fixes to be applied:")

    if analyze_timestamps == "Y":
        analyze_date_diff()
    elif analyze_timestamps == "N":
        pass
    else:
        print("Please enter either Y or N  to analyze time for security fixes to be applied")
