import sys
from lmsbreaker import Breaker

#данные пользователя
username = "username"
password = "password"
 #номер юнита, который хотим решить
unit_num = 0
#минимальный и максимальный процент выполнения каждого задания
percent_min = 90
percent_max = 100

breaker = Breaker()

try:
    breaker.login(username, password)
    units = breaker.get_units()
    breaker.attempt(units, units[unit_num], percent_min, percent_max)
    print("Юнит успешно выполнен.")
except:
    print("Произошла ошибка! Юнит не был решен. Попробуйте еще раз.")
    print(sys.exc_info())
finally:
     #всегда закрываем сессию
     breaker.logout()
