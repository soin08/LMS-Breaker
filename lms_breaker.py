from lmsbreaker import Breaker, LMS_LoginError, LMS_PercentError, LMS_SessionError, LMS_UnitError, LMS_UnknownError
import getpass

def input_int(input_sign):
    try:
        num = int(input(input_sign))
        return num
    except ValueError:
        print("Число не может быть буквой, глупый бледнолицый!")
        input_int(input_sign)


breaker = Breaker()
print("Здравствуй, ленивый бледнолицый бездарь.")
print("Тебя приветствует шаман племени  Нес Пирс")
print("Введи логин и пароль.")

username = input("логин--> ")
password = getpass.getpass("пароль--> ")

print("Пляшем с бубном...")

try:

    breaker.login(username, password)
    units = breaker.get_units()

    print("Доступные задания:")
    for i in range(0, len(units)):
        print("№%s : %s" % (str(i+1), units[ i ]['unit_title']))

    unit_num = input_int("№ задания-->")

    print("Введи минимальный и максимальный процент выполнения каждого задания. Результат всегда будет между этими двумя значениями.")

    percent_min = input_int("МИН. процент--> ")
    percent_max = input_int("МАКС. процент--> ")

    print("Пляшем с бубном...")

    breaker.attempt(units, unit_num, percent_min, percent_max)

    print("Шаман успешно решил адание "+str(unit_num))
    print("\"Каждое животное знает гораздо больше, чем ты\"")
    print("                               Племя Нес Пирс")

except LMS_PercentError:
    print("Шаман сообщает: глупый бледнолицый что-то напутал с процентами. Бледнолицые всегда славились своей вопиющей невнимательностью.")

except LMS_LoginError:
     print("Шаман сообщает: неверный логин / пароль. Бледнолицые всегда славились своей вопиющей невнимательностью.")

except LMS_SessionError:
    print("Шаман сообщает, что у вас уже есть открытые сессии. Вероятно, вы уже зашли в систему LMS через браузер. Cambridge LMS допускает только одну активную сессию, поэтому выйдите из системы и попробуйте снова.")
    print("С бледнолицыми дела всегда идут туго.")

except LMS_UnitError:
    print("Введен неверный номер юнита!")
    print("Шамана племени Нес Пирс не удастcя одурачить!")

except LMS_UnknownError:

    print("Шамана племени Нес Пирс порозила молния! Его смерть останется на твоей ленивой совести, а юнит так и не был решен.")

finally:
     breaker.logout()
