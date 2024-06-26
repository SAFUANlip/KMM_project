# KMM_project

**Проект по предмету "Компьютерное моделирование" на 4 курсе, МФТИ ФАЛТ. Весна 2024 года**

**Цель**: Моделирование работы ЗРС

![sim_app.gif](docs%2Fgif%2Fsim_app.gif)

## Архитектура проекта:
![img.png](docs/img/img.png)

## Состав команды "Синий Шуршунчик":
![team.png](docs/img/team.png)


### Структура репозитория
```
- docs/
  - img/ изображения
  - documentation_espd/ документация
  - gif/ гиф
- exec/ 
  - simulation_app_ui/ 
  - example_configs/ примеры конфигураций ВО
- logs/ логи
- simulation_app_ui/ 
  - configure_view/ - гуи 
  - images/ - спрайты
- simulation_process/
  - modules_classes/ - классы модулей
  - messages_classes/ - классы сообщений
  - utils/ 
- tests/ - тесты
```

<br>[Ссылка на Руководство Оператора](docs/documentation_espd/operator_manual.pdf)
<br> [Ссылка на Руководство Программиста](docs/documentation_espd/programmist_manual.pdf)
<br>[Ссылка на YouTrack, где распределены все задачи по ходу проекта](https://km-pgithubroject.youtrack.cloud/agiles/160-2/current)
<br>[Ссылка на UML-диаграмму](https://drive.google.com/file/d/1ucT0xLzZWOYp1hiXnceom4LKOXFYfxBC/view?usp=sharing)


### Настройка окружения

Установка окружения

```
pip install -r requirements.txt
```

### Как собрать exe?
```
pyinstaller.exe --onefile --windowed app.py
```

### Как запустить проект?
- запустить файл app.py (нужен питон)
- запустить файл [exec/app.exec](exec/app.exe) (не нужен питон)


## Справочная информация
### РЛС
В РЛС кругового типа обзор происходит по винтовой траектории:
![RadarRound](docs/img/img_RadarRound.png)
В РЛС секторного типа обзор происходит по зигзагообразной траектории:
![RadarSector](docs/img/img_RadarSector.png)

Диапозон действия РЛС различных типов варьируется до **500 км**, минимальная дальность обнаружения составляет 30 м.


В составе зенитных ракетных комплексов разных типов есть свои собственные РЛС для сопровождения целей и управления стрельбой. Например, система войсковой ПВО С-300В комплектуется станциями, способными засекать и брать на сопровождение воздушные цели на дальностях до 150 км. 

Дальность действия РЛС в составе нашего моделируемого комплекса фиксированная - 50 км.

Ошибка определения дальности до объекта < 50 м. Относительная ошибка определения скорости объекта - 5*10^(-4).

Источники для дальности РЛС:
1. https://www.ql-journal.ru/ru/node/667?ysclid=lw0dhcehpv972223721
2. https://www.radartutorial.eu/01.basics/rb10.ru.html
3. https://topwar.ru/198738-obnaruzhenie-i-soprovozhdenie-radiolokacionnye-stancii-v-specoperacii.html

Источники для ошибки определения дальности:
1. https://www.radartutorial.eu/01.basics/rb17.ru.html

Источники для ошибки определения скорости объектов:
1. http://www.mes-conference.ru/data/year2022/pdf/D028.pdf

### Самолет
- изначально скорость равна **555 м/c**
- ограничение скорости для самолета **220 - 700 м/c**

### ЗУР
- Дефолтная скорость равна **1200 м/с**
- ограничение скорости для самолета **1100 - 2200 м/c**

