from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json
import requests
s = requests.session()


def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

class ResumeHelpScrape:

    def __init__(self, chrome_driver, job_type, file_name):
        self.chrome_driver = chrome_driver
        self.job_type = job_type
        self.file_name = file_name
        self.resume_links_list = []

    def load_page_and_search(self):
        self.chrome_driver.get('https://online.resumehelp.com/search')
        search_box = self.chrome_driver.find_element_by_xpath('/html/body/section[1]/form/div/div/input')
        search_box.send_keys(self.job_type)
        self.chrome_driver.find_element_by_xpath('/html/body/section[1]/form/div/button').click()

    def grabbing_all_links(self):
        checker = True
        while checker:
            html = self.chrome_driver.page_source
            soup = bs(html, 'html.parser')
            resume_links = soup.find_all(
                lambda tag: tag.name == 'a' and tag.has_attr('class') and tag['class'][
                    0] == 'read-more' and tag.has_attr(
                    'href') and tag.get_text() == 'View Resume')
            for links in resume_links:
                self.resume_links_list.append('https://online.resumehelp.com/' + links.get('href'))
                next_button = soup.find(lambda tag: tag.name == 'a' and tag.has_attr('data-url') and tag.has_attr(
                    'data-pageindex') and tag.get_text() == ' ❯')
            try:
                next_page = self.chrome_driver.find_element_by_xpath(xpath_soup(next_button))
                next_page.click()
            except:
                checker = False
                pass
            sleep(0.1)

    def grabbing_professional_summary(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        pf_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and tag.get_text() == 'Professional Summary').get('id')
        pf_id_number = pf_id_number[13:]
        professional_summary = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and pf_id_number + '_1' in tag['id']).get_text()
        return professional_summary

    def grabbing_skills(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        s_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and tag.get_text() == 'Skills').get('id')
        s_id_number = s_id_number[13:]
        skills = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and s_id_number + '_1' in tag['id']).get_text()
        return skills

    def grabbing_experience(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        exp_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and tag.get_text() == 'Experience').get('id')
        exp_id_number = exp_id_number[13:]
        experience_list = []
        for i in range(1, 10):
            try:
                experience = first_link_soup.find(
                    lambda tag: tag.name == 'div' and tag.has_attr('id') and exp_id_number + '_' + i.__str__() in tag[
                        'id']).get_text()
                experience_list.append(experience)
            except:
                break
        return experience_list

    def grabbing_education(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        edu_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and tag.get_text() == 'Education').get('id')
        edu_id_number = edu_id_number[13:]
        education_list = []
        for i in range(1, 10):
            try:
                education = first_link_soup.find(
                    lambda tag: tag.name == 'div' and tag.has_attr('id') and edu_id_number + '_' + i.__str__() in tag[
                        'id']).get_text()
                education_list.append(education)
            except:
                break
        return education_list

    def dump_json(self, professional_summary, experience, education, skills):
        out_file = open(self.file_name, "a")
        output = {
            self.job_type: {
                "Professional Summary": professional_summary,
                "Skills": skills,
                "Experience": experience,
                "Education": education
            }
        }
        json.dump(output, out_file, indent=6)
        out_file.close()












