'''Selenium script to crawl apkmonk to download all the apks of all
the apps specified in a txt file (one package name per line).

Usage: python -m luigi --module ApkmonkScraper ScrapeApps
                       --list-apps-file=list_of_apps.txt
                       --output-folder=/Users/gorla/apkmonk
                       --workers 1
                       --local-scheduler
'''

import fnmatch
import logging
import luigi
import os

from selenium import webdriver
from time import sleep

logger = logging.getLogger('luigi-interface')

'''Represents the input file with the list of apps to download. The
file needs to have one app package name per line.

'''

class ListAppsFile(luigi.ExternalTask):
    list_apps_file = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.list_apps_file)


'''Scrape the apkmonk page for an app specified with a package
name. Place the downloaded apks in the output folder.

'''
class ScrapeApkMonkForApp(luigi.Task):

    package_name = luigi.Parameter()
    output_folder = luigi.Parameter()
    headless_browser = luigi.BoolParameter(default=False)

    def output(self):
        return luigi.LocalTarget(self.output_folder)

    def run(self):
        logger.info("** Scraping APK Monk for apk "+self.package_name)

        options = webdriver.ChromeOptions()
        if self.headless_browser:
            options.add_argument('headless')
        prefs = {"download.default_directory" : self.output_folder}
        options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(options=options)

        # visiting app page and retrieving all links.
        driver.get("https://www.apkmonk.com/app/"+self.package_name)
        if "<h1>Not Found</h1>" in driver.page_source:
            logger.warning("** "+self.package_name+" not found on apk monk!!!")
        link_elems = driver.find_elements_by_xpath("//a[@href]")
        
        download_links = set()
        for l in link_elems[1:]:
            if "download-app" in l.get_attribute("href"):
                download_links.add(l.get_attribute("href"))
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        num_downloaded_files = fnmatch.filter(os.listdir(self.output_folder), '*.apk')
        for dl in download_links:
            logger.info("** Downloading ... "+dl)
            driver.get(dl)
            sleep(2)
            
            # check that file has been downloaded, otherwise wait up
            # to 1 minute
            for wait in range(10):
                if fnmatch.filter(os.listdir(self.output_folder), '*.apk') == num_downloaded_files:
                    sleep(6)
                else:
                    break
            if fnmatch.filter(os.listdir(self.output_folder), '*.apk') == num_downloaded_files:
                logger.warning("** "+dl+ " has not been downloaded!")
            else:
                num_downloaded_files = fnmatch.filter(os.listdir(self.output_folder), '*.apk')

        driver.close()

'''Scrape the apkmonk pages of all the apps in the input file.

'''
class ScrapeApps(luigi.WrapperTask):

    list_apps_file = luigi.Parameter()
    output_folder = luigi.Parameter()

    def requires(self):
        with open(self.list_apps_file, 'r') as f:
            for app in f.read().splitlines():
                yield ScrapeApkMonkForApp(package_name=app,
                                          output_folder=os.path.join(self.output_folder,app))

if __name__ == '__main__':
    luigi.run(['ScrapeApps', '--workers', '1', '--local-scheduler'])

