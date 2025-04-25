import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="Batyr2007"
    )
    print("Подключение к базе данных успешно.")
except Exception as e:
    print("Ошибка подключения:", e)
    exit()

cur = conn.cursor()


cur.execute("""
    CREATE TABLE IF NOT EXISTS PhoneBook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE
    );
""")
conn.commit()

# Функция: поиск по шаблону
cur.execute("""
CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT pb.id, pb.first_name, pb.phone
    FROM PhoneBook pb
    WHERE pb.first_name ILIKE '%' || pattern || '%'
       OR pb.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;
""")

# Процедура: вставка или обновление
cur.execute("""
CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM PhoneBook WHERE first_name = p_name) THEN
        UPDATE PhoneBook SET phone = p_phone WHERE first_name = p_name;
    ELSE
        INSERT INTO PhoneBook(first_name, phone) VALUES (p_name, p_phone);
    END IF;
END;
$$;
""")

# Процедура: массовая вставка с валидацией
cur.execute("""
CREATE OR REPLACE PROCEDURE insert_many_users(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    bad_data TEXT := '';
BEGIN
    FOR i IN 1 .. array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^\\+\\d{11}$' THEN
            BEGIN
                INSERT INTO PhoneBook(first_name, phone)
                VALUES (p_names[i], p_phones[i])
                ON CONFLICT (phone) DO NOTHING;
            EXCEPTION WHEN OTHERS THEN
                bad_data := bad_data || '(' || p_names[i] || ', ' || p_phones[i] || ') ';
            END;
        ELSE
            bad_data := bad_data || '(' || p_names[i] || ', ' || p_phones[i] || ') ';
        END IF;
    END LOOP;

    RAISE NOTICE 'Некорректные записи: %', bad_data;
END;
$$;
""")

# Функция: постраничный вывод
cur.execute("""
CREATE OR REPLACE FUNCTION get_phonebook_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM PhoneBook
    ORDER BY id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
""")

# Процедура: удаление по имени или телефону
cur.execute("""
CREATE OR REPLACE PROCEDURE delete_user(p_name VARCHAR DEFAULT NULL, p_phone VARCHAR DEFAULT NULL)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM PhoneBook WHERE first_name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM PhoneBook WHERE phone = p_phone;
    ELSE
        RAISE NOTICE 'Нужно указать имя или номер для удаления';
    END IF;
END;
$$;
""")

conn.commit()
print("Все функции и процедуры успешно созданы.")

# Вставка/обновление одного пользователя
cur.execute("CALL insert_or_update_user(%s, %s);", ("Baga", "+77000000000"))

# Вставка нескольких пользователей (массивы)
names = ['Erke', 'Anuar', 'Beka']
phones = ['+77012345678', '+77098765432', '123456']
cur.execute("CALL insert_many_users(%s, %s);", (names, phones))

# Поиск по шаблону
cur.execute("SELECT * FROM search_phonebook(%s);", ("770",))
print("\nРезультаты поиска по шаблону '770':")
for row in cur.fetchall():
    print(row)

# Постраничный вывод (первые 2 записи)
cur.execute("SELECT * FROM get_phonebook_paginated(%s, %s);", (2, 0))
print("\nПервая страница (2 записи):")
for row in cur.fetchall():
    print(row)

# Удаление по имени
cur.execute("CALL delete_user(p_name := %s);", ("Beka",))

conn.commit()

# Вывод текущих данных
cur.execute("SELECT * FROM PhoneBook ORDER BY id;")
print("\nТекущие записи в таблице:")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
print("\nСоединение с БД закрыто.")
