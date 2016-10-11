# Simple crawler

Требуется написать систему, которая выдает различную статистику по сайту habrahabr.ru  
Для этого требуется:  
1) Написать программу, которая бы обкачивала все посты с habrahabr.ru за сегодняшний день. При повторном запуске программа не должна обкачивать те посты, которые уже скачаны ранее.  
2) WEB API, реализующее следующие интерфейсы:  
- Получить список всех пользователей, публиковавших статьи за указанный период времени.  
- Получить все посты с временем публикации для заданного автора и заданный период времени.  
- Получить IDF заданного слова относительно постов, скачанных за указанный день.  
<br />

Для запуска необходимо (первые 2 пункта можно пропустить и установить зависимости руками):  
1) Cобрать deb пакет  
`debuild -us -uc`

2) Установить пакет и зависимости на машине  
`sudo dpkg --force-depends -i && sudo apt-get update && sudo apt-get install -f`

3) Зайти в папку с проектом и активировать virtualenv  
`virtualenv venv && source venv/bin/activate`

4) Установить зависимости через pip3  
`pip3 install -r requirements.txt`
