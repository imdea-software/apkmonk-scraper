# Apkmonk Scraper

This is a python script that allows to crawl the apkmonk.com website. Given a list of Android apps, identified with their package name, the script visits the corresponding pages on apkmonk.com and downloads all the available releases of an APK file. 

## Requirements and installation

The script has requires `python3.x` in order to work, and uses `Selenium` and `Luigi`.
The easiest way to run the script is to install the required modules with the `pip` command as follows:

`pip install -r requirements.txt`

## Usage
The script takes mandatory parameters: 

`list-apps-file` is the path to a file with the list of apps for which you want to download previous versions. The format of this file should be 1 package name per line

`output-folder` is the folder where you want the apps to be downloaded. The script will create one sub folder for each packagename in this folder.

Moreover it is possible to specify the number of parallel tasks to speed up the crawling by using the `workers` parameter. By default there is only one worker. 

Create a `luigi.cfg` file in the current directory to setup all the parameters if you do not want to specify them dynamically:

`cp luigi.cfg.skel luigi.cfg` 

and change the path to the list of files and the output folder if needed.
Then you can launch the script as follows:

`python -m luigi --module ApkmonkScraper ScrapeApps --list-apps-file=list_of_apps.txt --output-folder=/Users/gorla/apkmonk --workers 4 --local-scheduler`

