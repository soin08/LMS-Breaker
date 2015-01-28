# LMS-Breaker
Решай любое задание из своего аккаунта на [cambridgelms.org] за считанные секунды.

Доступен графический интерфейс.

***Внимание!*** Перед запуском необходимо закрыть вашу текущую сессию на сайте cambridgelms.org!

### Запуск

Запуск с графическим интерфейсом (GUI):
```sh
$ python lms_breaker_gui.py
```

Запуск для работы из shell:
```sh
$ python lms_breaker_shell.py
```

Установочный файл для Windows скоро будет доступен.

### Требования

LMS-Breaker написан на Python 3 и использует следующие пакеты:

- mechanicalsoup
- BeautifulSoup
- PyQt4 для GUI
- py2exe для генерации exe

### Сборка

```sh
$ python setup.py py2exe
```

### Версия
2.0

[cambridgelms.org]:http://cambridgelms.org
