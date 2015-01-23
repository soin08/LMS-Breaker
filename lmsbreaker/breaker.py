import re
import datetime
import random
import urllib
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

browser = mechanicalsoup.Browser()
HOST = "http://www.cambridgelms.org"

def _get_strings_percent_diff(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).ratio( )

def _get_similar_string_in_array(string, arr, percent):
    r = -1
    for i in range(0, len(arr)):
        if _get_strings_percent_diff(string, arr[ i ]) > percent :
            r = i
            break
    return r

class _Response( ):

    def __init__(self, url = False, raw_html = False):
        if url:
            response = browser.get(url)
            self.raw_html = response.text
            self.soup = response.soup if hasattr(response, "soup") else BeautifulSoup(response.text)
        if raw_html:
            self.raw_html = raw_html
            self.soup = BeautifulSoup(raw_html)

    def is_logged_in(self): #при неудачной попытке входа получаем ту-же форму, при удачной -- редирект
        return not self.soup.find(id="username")

    def is_single_session(self): #есть лишь одна открытая сессия
        return not self.soup.title.contents[0].find("Session limit exceeded") >= 0

    def get_items_from_xml(self):
        return self.soup.find("organization").find_all("item", recursive = False)[ 1 ]

    def get_unit_link(self):
        unitObj =  re.search(r'moo_quick_scorm_sco_urlMap\[(.*?)\] = \'(.*)\';', self.raw_html)
        unit_link = unitObj.group(2)
        return unit_link

    def get_id(self):
        searchObj = re.search( r'id=([0-9]+)&scoid=([0-9]+)&attempt=([0-9]+)', self.raw_html )
        _id = int(searchObj.group(1))
        return _id

    def get_scoid(self):
        searchObj = re.search( r'id=([0-9]+)&scoid=([0-9]+)&attempt=([0-9]+)', self.raw_html )
        _scoid = int(searchObj.group(2)) + 2
        return _scoid

    def get_attempt(self):
        searchObj = re.search( r'id=([0-9]+)&scoid=([0-9]+)&attempt=([0-9]+)', self.raw_html )
        _attempt = int(searchObj.group(3))
        return _attempt

    def get_sesskey(self):
        searchObj = re.search( r'sesskey=(.*)"', self.raw_html )
        _sesskey = searchObj.group(1)
        return _sesskey

    @staticmethod
    def _get_second_match_list(match_list):
        second_match_list = [ ]
        for i in range(0, len( match_list ) ):
            second_match_list.append( match_list[ i ][ 1 ] )
        return second_match_list

    def get_solved_ids_list(self):
        id_list = re.findall(r'interactions.N([0-9]+).id = \'(.*?)\';', self.raw_html) #находим id
        return _Response._get_second_match_list( id_list )

    def get_solved_descs_list(self):
        desc_list =  re.findall(r'interactions.N([0-9]+).description = \'(.*?)\';', self.raw_html) #находим описания
        return _Response._get_second_match_list( desc_list )

    def get_solved_results_list(self):
        result_list =  re.findall(r'interactions.N([0-9]+).result = \'(.*?)\';', self.raw_html) #находим результаты
        return _Response._get_second_match_list( result_list )

    def get_login_iframe_src(self):
          return self.soup.find(id="cas_iframe").attrs['src']

    def get_login_form(self):
         return self.soup.find("form")

class Breaker( ):

    @staticmethod
    def _validate_percent(percent_min, percent_max):
        return  (0 <= percent_min <= 100 and 0 <= percent_max <= 100 and percent_min <= percent_max)

    @staticmethod
    def _validate_unit(unit_list, unit_num):
        return 0 < unit_num <= len(unit_list)

    @staticmethod
    def _get_interaction_dict(num, _id, result, description, timestamp):
        return  {
                    'cmi__interactions__'+str(num)+'__id': _id,
                    'cmi__interactions__'+str( num )+'__result' : result,
                    'cmi__interactions__'+str( num )+'__description' : description, #можно отправить любую строку - будет видно на сайте
                    'cmi__interactions__'+str( num )+'__latency' : "",
                    'cmi__interactions__'+str( num )+'__timestamp' : timestamp, #это время не показывается на сайте, но для надежности установим и его
                }


    def _get_tasks(self, unit_link):

        #ссылка на манифест с id заданий
        manifest_link = HOST + unit_link + "cdsmmanifest.xml"
        response = _Response(manifest_link)
        items = response.get_items_from_xml( )
        #ссылка на xml с описаниями
        desc_link = HOST + unit_link + "menu_info.xml"
        response = browser.get(desc_link)
        desc_soup = BeautifulSoup(response.text)

        tasks = [ ]

        for item in items:
            task_title = item.find("title")
            if type(task_title) is Tag:

                the_title = task_title.get_text().replace(" ", "_").replace('"', r'\"').replace("'", "\'")
                task = { 'title' : the_title, 'activities' : [ ] }
                activities = item.find_all("item",  recursive = False)

                for activity in activities:
                    #id для post-запроса - заголовок с нижним подчеркиванием вместо пробелов
                    act_id = activity.find("title").get_text().replace(" ", "_").replace('"', r'\"').replace("'", "\'")
                    #id чтобы найти описание
                    act_desc_id = activity['identifier']
                    desc_node = desc_soup.find(id=act_desc_id)
                    if desc_node: #почему-то иногда к активити нет описания (наблюдается в 12м юните)
                        act_desc = desc_node.find("learning_objective").get_text( )
                        act = { 'id' : act_id, 'desc' : act_desc }
                        task['activities'].append( act )

                tasks.append(task)

        return tasks

    def _solve(self, unit_list, unit_num, percent_min, percent_max):
        #получаем динамически сгенерированный js
         #на первый запрос получаем редирект
        response = browser.get( HOST+"/lms/mod/scorm/quickview.js.php?id="+str( unit_list[ unit_num - 1 ][ 'unit_id' ]) )
        #теперь то что надо
        #response = browser.get(response.soup.find( id="service" )[ 'value' ] )
        #ищем id, scoid и attempt
        params_url = response.soup.find( id="service" )[ 'value' ]
        r = _Response( params_url )
        _id = r.get_id( )
        _scoid = r.get_scoid( )
        _attempt = r.get_attempt( )
        #ищем ссылку на юнит и достаем задания
        unit_link = r.get_unit_link( )
        tasks = self._get_tasks(unit_link)
        #достаем sesskey
        sesskey_url = HOST + "/lms/mod/scorm/api.php?id="+str(_id)+"&scoid="+str(_scoid)+"&attempt="+str(_attempt)
        response = _Response(sesskey_url)
        _sesskey = response.get_sesskey( )

        #формируем запрос для каждого задания
        for i in range(0, len( tasks ) ):

            activities_num = len(tasks[ i ]['activities'])
            #как долго решали
            minutes = random.randint(8, 20)
            seconds = random.randint(0, 59)

            if re.search(r'Before_you_begin', tasks[ i ]['title']): #раздел "Before you begin" всегда решаем на 100% - он слишком простой
                minutes = random.randint(1, 3)

            cmi__total_time = "PT"+str(minutes)+"M"+str(seconds)+"S"

            body = { #формируем запрос
                'id' : _id,
                'scoid' : _scoid + i,
                'sesskey' : _sesskey,
                'cmi__score__scaled' : 100, #ниже перезапишем с учетом percent_max и percent_min
                'cmi__score__raw' : 100,
                'cmi__score__min' : 0,
                'cmi__score__max' : 100,
                'cmi__total_time' : cmi__total_time,
                'cmi__completion_status': "completed",
                'cmi__exit': "suspend",
                'cmi__progress_measure' : 1,
                'cmi__success_status': "passed",
                'attempt' : _attempt,
            }

            solved_params_url = HOST + "/lms/mod/scorm/api.php?id="+str( _id )+"&scoid="+str( _scoid + i )+"&attempt="+str( _attempt )
            response = _Response(solved_params_url)

            solved_ids = r.get_solved_ids_list( )
            solved_descs = r.get_solved_descs_list( )
            solved_results = r.get_solved_results_list( )

            for j in range(0, len( solved_ids ) ):
                #нужно чистое описание без экранирования. Сравниваем его с описанием, которое достали из xml. Если равны - то это задание уже было решено.
                #не сравниваем по id т.к. не знаем точно, как сервер модифицирует id активити. В большенстве случаев сравнение удается, но иногда нет -- не рискуем.
                desc = desc_list[ j ].replace("\\", "")
                solved_descs.append( desc )
                result = result_list[ j ]
                if  result.strip() == "":
                    result = 0
                solved_results.append( float( result ) )

            results = [ ] #сохраним все рандомные проценты, чтобы потом вычеслить общий процент выполнения

            #добавим в запрос сначала все уже решенные задания, чтобы не нарушать порядок заданий
            for j in range(0, len(solved_ids)):
                act_id = solved_ids[ j ]
                act_result = random.randint(percent_min*10, percent_max*10) / 1000
                act_desc = solved_descs[ j ].replace('"', r'\"').replace("'", r"\'")
                minutes_spent = random.randint(5, 17)

                if re.search(r'Before_you_begin', act_id):
                    act_result = 1
                    minutes_spent = minutes

                if solved_results[ j ] > act_result:
                    act_result = solved_results[ j ]

                time_after_solving = datetime.datetime.now( ) + datetime.timedelta( minutes = minutes_spent )
                act_timestamp = urllib.parse.quote_plus( time_after_solving.strftime("%y-%m-%dT%H:%M:%S") )
                body.update( Breaker._get_interaction_dict(j, act_id, act_result, act_desc , act_timestamp) )
                results.append( act_result )

            #добавляем все остальные задания
            counter = 0
            for j in range(0, activities_num):
                #с id путаница - проще проверять по описанию
                solved_index = _get_similar_string_in_array( tasks[ i ][ 'activities' ][ j ][ 'desc' ], solved_descs, .85 )
                if solved_index < 0: #новое задание которое не решали
                    act_id = tasks[ i ]['activities'][ j ][ 'id' ]
                    act_result = random.randint(percent_min*10, percent_max*10) / 1000
                    act_desc = tasks[ i ]['activities'][ j ][ 'desc' ].replace('"', r'\"').replace("'", r"\'")
                    minutes_spent = random.randint(5, 17)

                    if re.search(r'Before_you_begin', act_id):
                        act_result = 1
                        minutes_spent = minutes

                    time_after_solving = datetime.datetime.now() + datetime.timedelta( minutes = minutes_spent )
                    act_timestamp = urllib.parse.quote_plus( time_after_solving.strftime("%y-%m-%dT%H:%M:%S") )
                    body.update( Breaker._get_interaction_dict(len(solved_ids) + counter, act_id, act_result, act_desc, act_timestamp) )
                    results.append( act_result )
                    counter += 1

            score_scaled = round(sum(results) / (activities_num * 1.0), 4)
            score_raw = score_scaled * 100
            body['cmi__score__scaled'] = score_scaled
            body['cmi__score__raw'] = score_raw

            post_url = HOST+"/lms/mod/scorm/datamodel.php"

            response = browser.post(post_url, body)

            if response.text.find("Success") < 0:
               raise LMS_UnknownError("Неизвестная ошибка")


    def login(self, username, password): #использовать во внешних модулях

        login_url = HOST + "/touchstone/p/splash"
        respone = _Response( login_url )
        #ссылка на iframe с формой входа
        login_iframe_src = respone.get_login_iframe_src( )
        #сама форма
        response = _Response( login_iframe_src )
        login_form = response.get_login_form( )
        #заполняем форму данными
        login_form.find(id="username")['value'] = username
        login_form.find(id="password")['value'] = password
        #пытаемся войти
        response = browser.submit( login_form, HOST + "/touchstone/p"+login_form.attrs['action'] )
        if _Response(raw_html = response.text).is_logged_in( ):
            #получаем js редирект, переходим по нему
            redirect_url = response.soup.find(id="service")['value']
            response = _Response(redirect_url)

            if not response.is_single_session( ): #lms не разрешает более одной сессии
                raise LMS_SessionError("Сессия уже открыта")

        else:
            raise LMS_LoginError("Неверный логин / пароль")

    def logout(self): #использовать во внешних модулях
        browser.get(HOST+"/touchstone/p/caslogout")

    def get_units(self): #использовать во внешних модулях
        response = browser.get(HOST+"/touchstone/p/frontpage")
        #находим блок со ссылкой на задания
        self_study_block = response.soup.find("div", {"class" : "instituion"})
        if not self_study_block:
            raise LMS_UnknownError

        the_tr = self_study_block.find("tr", {"class" : "views-row-last"})
        #получаем ссылку на workbook
        wb_href = the_tr.find("a").attrs['href']
        #ссылка, по которой lms загружает список workbookов
        pkg_url = HOST+wb_href+"/packages"
        response = browser.get(pkg_url)
        #получаем контейнер с юнитами
        unit_box = response.soup.find(id="scormbox-container")
        units = unit_box.findAll("div", {"class" : "scorm-box"})
        unit_list = [ ]

        for unit in units: #формируем список юнитов
            unit_a = unit.find("h3").find("a")
            unit_title = unit_a.get_text( )
            unit_url = unit_a.attrs[ 'href' ]
            unit_id = int(unit_url[ len( unit_url ) - 4 : ]) #4 последних символа
            unit_list.append( { 'unit_title' : unit_title, 'unit_id' : unit_id } )

        return unit_list

    def attempt(self, unit_list, unit_num, percent_min, percent_max): #использовать во внешних модулях

        if not Breaker._validate_unit(unit_list, unit_num):
            raise LMS_UnitError
        if not Breaker._validate_percent(percent_min, percent_max):
            raise LMS_PercentError

        self._solve(unit_list, unit_num, percent_min, percent_max)
