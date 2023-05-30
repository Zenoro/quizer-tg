# quizer-tg

Семестровый проект по курсу "Совместная разработка приложений на Python".

## Постановка решаемой задачи

Данный бот создан для того, чтобы проводить викторины в виде чата в мессенджере Telegram. Программа запускается на компьютере «учителя», который является администратором, и затем по ссылке дает право ученикам проходить викторину. Бот выдает вопросы испытуемым в рандомном порядке и сохраняет результаты участников.

## Предполагаемые инструменты решения

Python библиотеки:

* `pyTelegramBotAPI (ver. 4.10.0)`

## Использование

1. (Предварительно) Получить Telegram Bot API ключ. Подготовить файл с вопросами в необходимом формате.
2. Запустить программу на стороне администратора, передав необходимые надстройки в виде консольного диалога (API ключ,).
3. Бот доступен для тестирования. Для начала теста необходимо написать `/start`
4. По завершении тестирования результаты будут переданы испытуемому, по желанию администратора можно получить полный отчет по участнику

## Запуск программы

Перед запуском программы необходимо создать колесо с помощью, например,  `pyproject-build`.

После установки пакета достаточно использовать созданный скрипт `QuizBot`, запускающий работу программы. Обратите внимание, что файл программы должен находиться в вызываемом окружении.

### Сценарии использования

Благодаря `dodo.py` файлу можно осуществлять дополнительные действия, для просмотра команд используйте `doit list` внутри клонированной папки.

### Локализация

Программа имеет английскую локализацию, для ее использования необходимо предварительно скомпилировать перевод посредством команды:

```
pybabel compile -D newbot -d QuizerBot/l10n -l eng
```

После этого необходимо пересоздать новый пакет с включенным переводом.

## Создание файла с вопросами

Всего бот позволяет использовать 3 типа вопросов: с выбором одного ответа, с выбором нескольких ответов и с вводом ответа пользователем.

Создать файл с вопросами можно по следующему алгоритму:

1. Создайте новый файл с расширением ".txt".
2. Вводите вопросы в следующем формате:

- Для вопросов, на которые нужно ответить словами, используйте тип О (ответ). Пример:

```
/O Какой язык программирования вы предпочитаете?
/Q Python
```

- Для вопросов, на которые нужно выбрать несколько вариантов ответа, используйте тип М (множественный выбор). Пример:

```
/M Какие из этих языков программирования являются объектно-ориентированными?
a. Python
b. C++
c. Java
d. Ruby
/Q b c
```

- Для вопросов, на которые нужно выбрать только один вариант ответа, используйте тип S (одиночный выбор). Пример:

```
/S Какой язык программирования часто используется для создания веб-приложений?
a. Java
b. JavaScript
c. Python
d. C++
/Q b
```

Несколько вопросов записывайте в файл последовательно в разных строках.

3. Сохраните этот файл в директрию, в котором будете запускать библиотеку.
