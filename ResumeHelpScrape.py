from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup as bs
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
        self.chrome_driver.get('https://online.resumehelp.com/search?')
        search_box = self.chrome_driver.find_element_by_xpath('/html/body/section[1]/form/div/div/input')
        search_box.send_keys(self.job_type)
        self.chrome_driver.find_element_by_xpath('/html/body/section[1]/form/div/button').click()

    def grabbing_all_links(self):
        checker = True
        while checker:
            sleep(1)
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

    def grabbing_professional_summary(self, index):
        key_word = ['objective', 'professional summary', 'summary', 'professional summary:', 'objective:', 'summary:']
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        pf_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and key_word.__contains__(tag.get_text().lower())).get('id')
        pf_id_number = pf_id_number[13:]
        professional_summary = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and pf_id_number + '_1' in tag['id']).get_text()
        return professional_summary

    def grabbing_skills(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        s_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and 'skills' in tag.get_text().lower()).get('id')
        s_id_number = s_id_number[13:]
        skills = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and s_id_number + '_1' in tag['id']).get_text()
        return skills

    def grabbing_experience(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        exp_id_number = first_link_soup.find(
            lambda tag: tag.name == 'div' and tag.has_attr('id') and 'experience' in tag.get_text().lower()).get('id')
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
            lambda tag: tag.name == 'div' and tag.has_attr('id') and 'education' in tag.get_text().lower()).get('id')
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

    def grabbing_certifications(self, index):
        first_link_soup = bs(s.get(self.resume_links_list[index]).text, 'html.parser')
        try:
            cert_id = first_link_soup.find(lambda tag: tag.name == 'div' and tag.has_attr('id') and tag.has_attr('class') and 'certifications' in tag.get_text().lower() and 'CERT' in tag['id']).get('id')
            if cert_id:
                cert_id_number = cert_id[13:]
                cert_list = []
                for i in range(1,20):
                    try:
                        certification = first_link_soup.find(lambda tag: tag.name == 'div' and tag.has_attr('id') and cert_id_number + '_' + i.__str__() in tag[
                            'id'])
                        cert_list.append(certification)
                    except:
                        break
        except:
            pass



    def dump_json(self, professional_summary, experience, education, skills, certification, link):
        out_file = open(self.file_name, "a")
        output = {
            self.job_type: {
                "Professional Summary": professional_summary,
                "Skills": skills,
                "Experience": experience,
                "Education": education,
                "Certification": certification,
                "Link": link
            }
        }
        json.dump(output, out_file, indent=6)
        out_file.close()



# edu_count = 0
# exp_count = 0
# skill_count = 0
# pf_count = 0
# option = webdriver.ChromeOptions()
# option.add_argument('headless')
# driver = webdriver.Chrome('C:/Users/pamjw/Desktop/chromedriver.exe', options=option)
# temp = ResumeHelpScrape(driver, 'Police Officer', 'output')
# temp.load_page_and_search()
# temp.grabbing_all_links()
# print(len(temp.resume_links_list))
# for i in range(0, len(temp.resume_links_list)):
#     temp.grabbing_certifications(i)
# print(len(temp.resume_links_list))
# for i in range(0,len(temp.resume_links_list)):
#     try:
#         edu = temp.grabbing_education(i)
#         edu_count+=1
#     except AttributeError:
#         edu = ''
#     try:
#         exp = temp.grabbing_experience(i)
#         exp_count+=1
#     except AttributeError:
#         exp = ''
#     try:
#         skill = temp.grabbing_skills(i)
#         skill_count+=1
#     except AttributeError:
#         skill = ''
#     try:
#         pf = temp.grabbing_professional_summary(i)
#         pf_count+=1
#     except AttributeError:
#         pf = ''
#     #temp.dump_json(pf, exp, edu, skill, temp.resume_links_list[i])
# print("Educations Found: "+edu_count.__str__()+"/"+len(temp.resume_links_list).__str__())
# print("Experiences Found: " + exp_count.__str__() + "/" + len(temp.resume_links_list).__str__())
# print("Skills Found: " + skill_count.__str__() + "/" + len(temp.resume_links_list).__str__())
# print("PFs Found: " + pf_count.__str__() + "/" + len(temp.resume_links_list).__str__())













