# Импорт библиотек для работы с PostgreSQL, CSV, регулярками и системой
import psycopg2
from config import params
# Импорт библиотек для работы с PostgreSQL, CSV, регулярками и системой
import csv
# Импорт библиотек для работы с PostgreSQL, CSV, регулярками и системой
import re , sys

a = int(input('1-Add     2-Delete     3-Update     4-Show     5-csv      6-find\n'))

# Создание таблицы телефонной книги
def create_table():
    SQL = (
        '''
        CREATE TABLE IF NOT EXISTS book ( 
        Name VARCHAR(255) NOT NULL , 
        Telephone VARCHAR(11) NOT NULL
        ) 
        '''
    )

    try:
        config = psycopg2.connect(**params)
        query = config.cursor()
        query.execute(SQL)
        query.close()
        config.commit()
        
    except Exception as Error:
        print(str(Error))

create_table()


# Добавление пользователя или обновление телефона, если имя уже есть
def add_user(name, telephone):
    
    SQL = "Select * from book where name = '" + name + "';"
    t = True
    try:
        config = psycopg2.connect(**params)
        query = config.cursor()
        query.execute(SQL)
        res = query.fetchall()
        query.close()
        config.commit()

        if len(res) != 0:
            SQL = "UPDATE book SET telephone = '"+ telephone + "' WHERE name = '" + name +"';"
            update(SQL)
            t = False

    except Exception as Error:
        print(str(Error))

    if t:
        SQL = "INSERT INTO book (Name, Telephone) VALUES ('" + name + "','" + telephone +"');"
        try:
            config = psycopg2.connect(**params)
            query = config.cursor()
            query.execute(SQL)
            query.close()
            config.commit()

        except Exception as Error:
            print(str(Error))




# Удаление записи из таблицы по SQL-запросу
def drop(SQL):
    
    try:
        config = psycopg2.connect(**params)
        query = config.cursor()
        query.execute(SQL)
        query.close()
        config.commit()

    except Exception as Error:
        print(str(Error))



# Обновление записи в таблице по SQL-запросу
def update(SQL):
    try:
        config = psycopg2.connect(**params)
        query = config.cursor()
        query.execute(SQL)
        query.close()
        config.commit()

    except Exception as Error:
        print(str(Error))


# Показ записей с постраничной навигацией
def show(SQL, page):
    SQL += " OFFSET " + str((int(page)-1) * 3)  + " ROWS FETCH NEXT 3 ROWS ONLY"

    try:
        config = psycopg2.connect(**params)
        query = config.cursor()
        query.execute(SQL)
        res = query.fetchall()
        query.close()
        config.commit()
        
        if len(res)!=0:
            text = "Name                     Telephone"
            print("\033[36m {}" .format(text) )
            print("\033[0m", end='')

            for row in res:
                l = len(row[0])
                print(str(row[0]), end ="")
                for i in range(24-l):
                    print(' ', end ="")
                print(' ', end ="")
                print(str(row[1]))
                
        else: print("\033[31m {}" .format('Nothing found!') )
        print("\033[0m", end='')

    except Exception as Error:
        print(str(Error))
    




# Поиск записей по имени или телефону
def find(SQL):
    try:
        config = psycopg2.connect(**params)
        query = config.cursor()
        query.execute(SQL)
        res = query.fetchall()
        query.close()
        config.commit()
        
        if len(res)!=0:
            text = "Name                     Telephone"
            print("\033[36m {}" .format(text) )
            print("\033[0m", end='')

            for row in res:
                l = len(row[0])
                print(str(row[0]), end ="")
                for i in range(24-l):
                    print(' ', end ="")
                print(' ', end ="")
                print(str(row[1]))
                
        else: 
            print("\033[31m {}" .format('Nothing found!') )
            print("\033[0m", end='')


    except Exception as Error:
        print(str(Error))    


# Выбор: добавить запись
if a == 1:
    name = input('Write your name:   ')
    telephone = input('Write your telephone number:   ')
    x = re.search('^[0123456789]{11}$', telephone)
    if x:
        add_user(name,telephone)

    else: 
        print("\033[31m {}" .format('Telephone must include 11 digits!') )
        print("\033[0m", end='')


# Выбор: удалить запись
if a == 2:

    b = int(input('1-Delete by name     2-Delete by telephone \n'))
    if b == 1:
        name = input('Write your name:     ')
        SQL = "DELETE FROM book where name = '" + name + "';"
    if b == 2:
        telephone = input('Write your telephone number:     ')
        SQL = "DELETE FROM book where telephone = '" + telephone + "';"

    drop(SQL)


# Выбор: обновить запись
if a == 3:
    b = int(input('1-Update by name     2-Update by telephone \n'))
    if b == 1:
        name = input('Write your name:     ')
        telephone = input('Write your new telephone number:     ')
        SQL = "UPDATE book SET telephone = '"+ telephone + "' WHERE name = '" + name +"';"
    if b == 2:
        telephone = input('Write your telephone number: ')
        name = input('Write your new name:     ')
        SQL = "UPDATE book SET name = '"+ name + "' WHERE telephone = '" + telephone +"';"
    update(SQL)


# Выбор: показать записи с сортировкой и пагинацией
if a == 4:
    b = int(input('1-Sort by name     2-Sort by telephone     3-Sort by date\n'))
    if b == 1:
        SQL = 'Select * from book order by name ASC'
    if b == 2:
        SQL = 'Select * from book order by telephone ASC'
    if b == 3:
        SQL = ''
    print("Print '0', to stop pagination.")
    page = 1
    while page !=0:
        page = input('Write the page number: \n')
        if int(page) == 0:
            sys.exit()
        show(SQL, page)


# Импорт данных из CSV-файла
if a == 5:
    with open('sample.csv') as f:
        r = csv.reader(f) 
        for i in r:
            name = str(i[0])
            telephone = str(i[1])
            add_user(name,telephone)


# Поиск в таблице по имени или номеру
if a==6:
    b = int(input('1-Find by name     2-Find by telephone\n'))
    if b == 1:
        name = input("Write your name:\n")
        SQL = "SELECT * FROM book where name LIKE '"+ str(name) +"%';"
    if b == 2:
        telephone = input("Write your telephone:\n")
        SQL = "SELECT * FROM book where telephone LIKE '"+ str(telephone) +"%';"
    find(SQL)






        







