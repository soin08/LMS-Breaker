import re
import datetime
import random
import urllib
import requests
import mechanicalsoup
from bs4 import BeautifulSoup
from bs4 import Tag
import difflib

class LMS_BaseError(Exception):
    pass

class LMS_LoginError(LMS_BaseError):
   pass

class LMS_SessionError(LMS_BaseError):
    pass

class LMS_UnknownError(LMS_BaseError):
    pass

class LMS_UnitError(LMS_BaseError):
    pass

class LMS_PercentError(LMS_BaseError):
    pass

class LMS_MaintanceError(LMS_BaseError):
    pass


class _Browser(mechanicalsoup.Browser):
    def __init__(self,  *args, **kwargs):
        super(_Browser, self).__init__( *args, **kwargs)
        self.cacert_path = requests.certs.where()

    def set_cacert_path(self, path):
        self.cacert_path = path

    def get(self, *args, **kwargs):
        return super(_Browser, self).get(*args, verify = self.cacert_path, **kwargs)

    def post(self, *args, **kwargs):
        return super(_Browser, self).post(*args, verify = self.cacert_path, **kwargs)


def _get_strings_percent_diff(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).ratio()

def _get_similar_string_in_array(string, arr, percent):
    r = -1
    for i in range(len(arr)):
        if _get_strings_percent_diff(string, arr[i]) > percent :
            r = i
            break
    return r

class _Response():

    def __init__(self, raw_html):
            self.raw_html = raw_html
            self.soup = BeautifulSoup(raw_html)

    #при неудачной попытке входа получаем ту-же форму, при удачной -- редирект
    def is_logged_in(self):
        return not self.soup.find(id="username")

    #на сайте разрешена только одна открытая сессия
    def is_multiple_session(self):
        return self.soup.title.contents[0].find("Session limit exceeded") >= 0

    #иногда сайт на ремонте
    def is_maintance(self):
        return self.raw_html.find("undergoing maintance") > 0

    def get_items_from_xml(self):
        return self.soup.find("organization").find_all("item", recursive=False)[1]

    def get_unit_link(self):
        unitObj =  re.search(r'moo_quick_scorm_sco_urlMap\[(.*?)\] = \'(.*)\';', self.raw_html)
        unit_link = unitObj.group(2)
        return unit_link

    def get_id(self):
        searchObj = re.search(r'id=([0-9]+)&scoid=([0-9]+)&attempt=([0-9]+)', self.raw_html)
        id = int(searchObj.group(1))
        return id

    def get_scoid(self):
        searchObj = re.search(r'id=([0-9]+)&scoid=([0-9]+)&attempt=([0-9]+)', self.raw_html)
        scoid = int(searchObj.group(2)) + 2
        return scoid

    def get_attempt(self):
        searchObj = re.search(r'id=([0-9]+)&scoid=([0-9]+)&attempt=([0-9]+)', self.raw_html)
        attempt = int(searchObj.group(3))
        return attempt

    def get_sesskey(self):
        searchObj = re.search(r'sesskey=(.*)"', self.raw_html)
        sesskey = searchObj.group(1)
        return sesskey

    def is_params_redirect(self):
        return self.soup.find(id="service")

    def get_params_redirect_url(self):
         return self.soup.find(id="service")['value']

    def _get_second_match_list(self, match_list):
        second_match_list = []
        for i in range(len(match_list)):
            second_match_list.append(match_list[i][1])
        return second_match_list

    def get_solved_ids_list(self):
        id_list = re.findall(r'interactions.N([0-9]+).id = \'(.*?)\';', self.raw_html) #находим id
        return self._get_second_match_list(id_list)

    def get_solved_descs_list(self):
        desc_list = re.findall(r'interactions.N([0-9]+).description = \'(.*?)\';', self.raw_html) #находим описания
        return self._get_second_match_list(desc_list)

    def get_solved_results_list(self):
        result_list = re.findall(r'interactions.N([0-9]+).result = \'(.*?)\';', self.raw_html) #находим результаты
        return self._get_second_match_list(result_list)

    def get_login_iframe_src(self):
          return self.soup.find(id="cas_iframe").attrs['src']

    def get_login_form(self):
         return self.soup.find("form")

    def is_post_successful(self):
         return self.raw_html.find("Success") > 0

class Breaker():

    def __init__(self):
        self._browser = _Browser()
        self.HOST = "http://www.cambridgelms.org"

    def set_cacert_path(self, path):
        self._browser.set_cacert_path(path)

    def _browser_get(self, server_addr):
        return self._browser.get(server_addr).text

    def _browser_post(self, post_addr, body):
        return self._browser.post(post_addr, body).text

    def _browser_submit(self, form, submit_addr):
        return self._browser.submit(form, submit_addr).text

    @staticmethod
    def _validate_percent(percent_min, percent_max):
        return  (0 <= percent_min <= 100 and 0 <= percent_max <= 100 and percent_min <= percent_max)

    @staticmethod
    def _validate_units(unit_list, units_chosen):
        for unit in units_chosen:
            if not unit in unit_list:
                return False
        return True

    @staticmethod
    def _get_interaction_dict(num, id, result, description, timestamp):
        return  {
            'cmi__interactions__'+str(num)+'__id': id,
            'cmi__interactions__'+str(num)+'__result' : result,
            #можно отправить любую строку - будет видно на сайте
            'cmi__interactions__'+str(num)+'__description' : description,
            'cmi__interactions__'+str(num)+'__latency' : "",
            #это время не показывается на сайте, но для надежности установим и его
            'cmi__interactions__'+str(num)+'__timestamp' : timestamp,
        }

    def _get_tasks(self, unit_link):
        #ссылка на манифест с id заданий
        manifest_link = self.HOST + unit_link + "cdsmmanifest.xml"
        xml = self._browser_get(manifest_link)
        response = _Response(xml)
        items = response.get_items_from_xml()
        #ссылка на xml с описаниями
        desc_link = self.HOST + unit_link + "menu_info.xml"
        response = self._browser_get(desc_link)
        desc_soup = BeautifulSoup(response)

        tasks = []

        for item in items:
            task_title = item.find("title")
            if type(task_title) is Tag:
                the_title = task_title.get_text().replace(" ", "_").replace('"', r'\"').replace("'", "\'")
                task = {'title' : the_title, 'activities' : []}
                activities = item.find_all("item",  recursive=False)

                for activity in activities:
                    #id для post-запроса - заголовок с нижним подчеркиванием вместо пробелов
                    act_id = activity.find("title").get_text().replace(" ", "_").replace('"', r'\"').replace("'", "\'")
                    #id чтобы найти описание
                    act_desc_id = activity['identifier']
                    desc_node = desc_soup.find(id=act_desc_id)
                    if desc_node: #почему-то иногда к активити нет описания (наблюдается в 12м юните)
                        act_desc = desc_node.find("learning_objective").get_text()
                        act = {'id' : act_id, 'desc' : act_desc}
                        task['activities'].append(act)

                tasks.append(task)

        return tasks

    def _solve(self, units, percent_min, percent_max):
         for unit in units:
            params_url = self.HOST+"/lms/mod/scorm/quickview.js.php?id="+str(unit['unit_id'])
            params_html = self._browser_get(params_url)
            response = _Response(params_html)
            #на первый запрос получаем редирект
            if response.is_params_redirect():
                params_url = response.get_params_redirect_url()
                params_html = self._browser_get(params_url)
                response = _Response(params_html)

            id = response.get_id()
            scoid = response.get_scoid()
            attempt = response.get_attempt()
            unit_link = response.get_unit_link()
            tasks = self._get_tasks(unit_link)
            sesskey_url = self.HOST + "/lms/mod/scorm/api.php?id="+str(id)+"&scoid="+str(scoid)+"&attempt="+str(attempt)
            sesskey_html = self._browser_get(sesskey_url)
            response = _Response(sesskey_html)
            sesskey = response.get_sesskey()

            #формируем запрос для каждого задания
            for i in range(len(tasks)):
                activities_num = len(tasks[i]['activities'])
                #как долго решали
                minutes = random.randint(8, 20)
                seconds = random.randint(0, 59)
                #раздел "Before you begin" всегда решаем на 100% - он слишком простой
                if re.search(r'Before_you_begin', tasks[i]['title']):
                    minutes = random.randint(1, 3)

                cmi__total_time = "PT"+str(minutes)+"M"+str(seconds)+"S"
                #формируем запрос
                body = {
                    'id' : id,
                    'scoid' : scoid + i,
                    'sesskey' : sesskey,
                    'cmi__score__scaled' : 100, #ниже перезапишем с учетом percent_max и percent_min
                    'cmi__score__raw' : 100,
                    'cmi__score__min' : 0,
                    'cmi__score__max' : 100,
                    'cmi__total_time' : cmi__total_time,
                    'cmi__completion_status': "completed",
                    'cmi__exit': "suspend",
                    'cmi__progress_measure' : 1,
                    'cmi__success_status': "passed",
                    'attempt' : attempt,
                }

                solved_params_url = self.HOST + "/lms/mod/scorm/api.php?id="+str(id)+"&scoid="+str(scoid + i)+"&attempt="+str(attempt)
                solved_params_html = self._browser_get(solved_params_url)
                response = _Response(solved_params_html)

                solved_ids = response.get_solved_ids_list()
                solved_descs = response.get_solved_descs_list()
                solved_results = response.get_solved_results_list()

                for j in range(0, len(solved_ids)):
                    """
                    Нужно чистое описание без экранирования. Сравниваем его с описанием, которое достали из xml.
                    Если равны - то это задание уже было решено.
                    не сравниваем по id т.к. не знаем точно, как сервер модифицирует id активити.
                    В большенстве случаев сравнение удается, но иногда нет -- не рискуем.
                    """
                    solved_descs[j] = solved_descs[j].replace("\\", "")
                    result = solved_results[j]
                    if  result.strip() == "":
                        result = 0
                    solved_results[j] = float(result)

                """
                Cохраним все рандомные проценты, чтобы потом вычеслить общий процент выполнения.
                Добавим в запрос сначала все уже решенные задания, чтобы не нарушать порядок заданий.
                """
                results = []
                for j in range(len(solved_ids)):
                    act_id = solved_ids[j]
                    act_result = random.randint(percent_min*10, percent_max*10) / 1000
                    act_desc = solved_descs[j].replace('"', r'\"').replace("'", r"\'")
                    minutes_spent = random.randint(5, 17)

                    if re.search(r'Before_you_begin', act_id):
                        act_result = 1
                        minutes_spent = minutes

                    if solved_results[j] > act_result:
                        act_result = solved_results[j]

                    time_after_solving = datetime.datetime.now() + datetime.timedelta(minutes=minutes_spent)
                    act_timestamp = urllib.parse.quote_plus(time_after_solving.strftime("%y-%m-%dT%H:%M:%S"))
                    body.update(Breaker._get_interaction_dict(j, act_id, act_result, act_desc , act_timestamp))
                    results.append(act_result)

                #добавляем все остальные задания
                counter = 0
                for j in range(activities_num):
                    #с id путаница - проще проверять по описанию
                    solved_index = _get_similar_string_in_array(tasks[i]['activities'][j]['desc'], solved_descs, .85)
                    if solved_index < 0: #новое задание которое не решали
                        act_id = tasks[i]['activities'][j]['id']
                        act_result = random.randint(percent_min*10, percent_max*10) / 1000
                        act_desc = tasks[i]['activities'][j]['desc'].replace('"', r'\"').replace("'", r"\'")
                        minutes_spent = random.randint(5, 17)

                        if re.search(r'Before_you_begin', act_id):
                            act_result = 1
                            minutes_spent = minutes

                        time_after_solving = datetime.datetime.now() + datetime.timedelta(minutes=minutes_spent)
                        act_timestamp = urllib.parse.quote_plus(time_after_solving.strftime("%y-%m-%dT%H:%M:%S"))
                        body.update(Breaker._get_interaction_dict(len(solved_ids)+counter, act_id, act_result, act_desc, act_timestamp))
                        results.append(act_result)
                        counter += 1

                if activities_num > 0:
                    score_scaled = round(sum(results) / (activities_num * 1.0), 4)
                    score_raw = score_scaled * 100
                    body['cmi__score__scaled'] = score_scaled
                    body['cmi__score__raw'] = score_raw

                    post_url = self.HOST + "/lms/mod/scorm/datamodel.php"
                    post_html = self._browser_post(post_url, body)
                    response = _Response(post_html)

                    if not response.is_post_successful():
                         raise LMS_UnknownError("Неизвестная ошибка")


    def login(self, username, password):
        login_url = self.HOST + "/touchstone/p/splash"
        login_html = self._browser_get(login_url)
        response = _Response(login_html)
        if response.is_multiple_session():
            raise LMS_SessionError("Сессия уже открыта")
        if response.is_maintance():
            raise LMS_MaintanceError("Сайт LMS на ремонте. Попробуйте позднее.")
        #ссылка на iframe с формой входа
        login_iframe_src = response.get_login_iframe_src()
        login_iframe_html = self._browser_get(login_iframe_src)
        response = _Response(login_iframe_html)

        login_form = response.get_login_form()
        login_form.find(id="username")['value'] = username
        login_form.find(id="password")['value'] = password
        #пытаемся войти
        submit_html = self._browser_submit(login_form, self.HOST + "/touchstone/p"+login_form.attrs['action'])
        response = _Response(submit_html)
        if response.is_logged_in():
            #получаем js редирект, переходим по нему
            redirect_url = response.soup.find(id="service")['value']
            redirect_html = self._browser_get(redirect_url)
            response = _Response(redirect_html)

            if response.is_multiple_session(): #lms не разрешает более одной сессии
                raise LMS_SessionError("Сессия уже открыта")
        else:
            raise LMS_LoginError("Неверный логин / пароль")

    def logout(self):
        self._browser_get(self.HOST+"/touchstone/p/caslogout")

    def get_units(self):
        units_url = self.HOST+"/touchstone/p/frontpage"
        units_html = self._browser_get(units_url)
        response = _Response(units_html)
        #находим блок со ссылкой на задания
        self_study_block = response.soup.find("div", {"class" : "instituion"})
        if not self_study_block:
            raise LMS_UnknownError("Неизвестная ошибка")

        the_tr = self_study_block.find("tr", {"class" : "views-row-last"})
        #получаем ссылку на workbook
        wb_href = the_tr.find("a").attrs['href']
        #ссылка, по которой lms загружает список workbookов
        pkg_url = self.HOST+wb_href+"/packages"
        pkg_html = self._browser_get(pkg_url)
        response = _Response(pkg_html)
        #получаем контейнер с юнитами
        unit_box = response.soup.find(id="scormbox-container")
        units = unit_box.findAll("div", {"class" : "scorm-box"})
        unit_list = []

        for unit in units: #формируем список юнитов
            unit_a = unit.find("h3").find("a")
            unit_title = unit_a.get_text()
            unit_url = unit_a.attrs['href']
            searchObj = re.search(r'id=([0-9]+)', unit_url)
            unit_id = int(searchObj.group(1))
            unit_list.append({'unit_title' : unit_title, 'unit_id' : unit_id})

        return unit_list

    def attempt(self, unit_list, units_chosen, percent_min, percent_max):
        if not Breaker._validate_units(unit_list, units_chosen):
            raise LMS_UnitError("Ошибка выбора задания")
        if not Breaker._validate_percent(percent_min, percent_max):
            raise LMS_PercentError("Ошибка в значениях процентов")

        self._solve(units_chosen, percent_min, percent_max)
