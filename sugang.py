from selenium import webdriver
from bs4 import BeautifulSoup
import telegram
import time


class Sugang:
    my_token = "YOUR TOKEN"
    bot = telegram.Bot(token=my_token)
    chat_id = bot.getUpdates()[0].message.chat.id
    __ID = "YOUR ID"
    __PASSWORD = "YOUR PASSWORD"
    list_s = []
    list_p = []

    def __init__(self, num):
        self.num = num
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        self.driver = webdriver.Chrome('chrome/chromedriver', options=options)

    def access_id_pwd(self):
        # 로그인하고 접속하는 ㅎ마수
        self.driver.get('https://hisnet.handong.edu/login/login.php')
        self.driver.implicitly_wait(1)
        ID = self.driver.find_element_by_xpath(
            '''//*[@id="loginBoxBg"]/table[2]/tbody/tr/td[5]/form/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/span/input''')
        ID.send_keys(self.__ID)
        pwd = self.driver.find_element_by_xpath(
            '''//*[@id="loginBoxBg"]/table[2]/tbody/tr/td[5]/form/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/input''')
        pwd.send_keys(self.__PASSWORD)
        self.driver.find_element_by_xpath(
            '''//*[@id="loginBoxBg"]/table[2]/tbody/tr/td[5]/form/table/tbody/tr[3]/td/table/tbody/tr/td[2]/input''').click()
        self.driver.implicitly_wait(2)
        self.driver.get('https://hisnet.handong.edu/for_student/course/PLES330M.php')

    def go_search_page(self, f_subject, f_professor):
        # 수업과 교수님을 선택하는  함수
        subject = self.driver.find_element_by_xpath('''//*[@id="att_list1"]/tbody/tr[3]/td[2]/span/input''')
        subject.send_keys(f_subject)
        professor = self.driver.find_element_by_xpath('''//*[@id="att_list1"]/tbody/tr[3]/td[1]/span/input''')
        professor.send_keys(f_professor)
        self.driver.find_element_by_xpath('''//*[@id="att_list1"]/tbody/tr[2]/td[4]/span/a/img''').click()
        self.driver.find_element_by_xpath('''//*[@id="att_list1"]/tbody/tr[3]/td[2]/span/input''').clear()
        self.driver.find_element_by_xpath('''//*[@id="att_list1"]/tbody/tr[3]/td[1]/span/input''').clear()
        self.driver.implicitly_wait(2)

    def parsing(self):
        # element들을 뽑아오는 함수
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find("table", {"id": "att_list"})
        table_body = table.find('tbody')

        raw_data = []
        rows = table_body.find_all('tr')

        # 검색된 data를 저장한다
        for i in range(len(rows) - 1):
            subject = rows[i + 1].find_all('td')
            raw_data.append(subject)

        data = []
        for l in raw_data:
            s = l[3].get_text()
            p = l[5].get_text()
            t = l[6].get_text()
            cap = int(l[8].get_text())
            reg = int(l[9].get_text())
            data.append([s, p, t, cap, reg])

        # 정리된 data를 리턴한다
        return data

    def ask_question(self):
        print(self.num, "개의 수업을 찾겠습니다.\n")
        for i in range(self.num):
            self.list_s.append(input("찾고 싶은 수업을 적어 주세요 "))
            self.list_p.append(input("그 수업의 교수님을 적어주세요 "))
        print("이제 찾도록 해보겠습니다. 수강신청 화이팅\n")

    def search(self):
        for i in range(self.num):
            self.go_search_page(self.list_s[i], self.list_p[i])
            final_list = self.parsing()
            self.is_empty_seat(final_list)
            time.sleep(1)

    def search_timer(self):
        start_time = time.time()
        while True:
            end_time = time.time()
            if (end_time-start_time) > 21600: # 6 시간
                q = input("중단하시겠습니까? (Y/N)")
                if q.lower() == 'y':
                    break
                elif q.lower() == "n":
                    start_time = time.time()
            self.search()
            for i in range(10):
                print("..........\n")
                time.sleep(1)
            print("........잠시 쉬는중\n\n\n")
            time.sleep(20)
            print("........다시 시작")

    def is_empty_seat(self, save):
        for s in save:
            word = s[0] + "-" + s[1] + "-" + s[2]
            if s[3] > s[4] and s[3] != 0:
                str1 = word + " 비었습니다!!!!!!\n\n\n"
                print(str1)
                self.bot.send_message(chat_id=self.chat_id, text=str1)
            else:
                print(word+" 꽉참")

    def quit(self):
        self.driver.quit()


if __name__ == "__main__":
    number = int(input("몇개의 과목을 찾으실건가요? "))
    sugang = Sugang(number)
    sugang.access_id_pwd()  # 히스넷에 접속한다
    sugang.ask_question()  # 찾을 수업과 교수님을 입력한다
    sugang.search_timer()  # 본격적으로 찾는다
    sugang.quit()
