import sqlite3

connection = sqlite3.connect('products.db')
cursor = connection.cursor()


def initiate_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    price INTEGER NOT NULL
    )
    """)


def create_products():
    medicine_list = ['catharsis', 'nostalgia', 'relax', 'smile']
    vitamine_list = ['радостин', 'ностальгиксин', 'релаксин', 'пакостин']
    for i in range(len(medicine_list)):
        cursor.execute(f"INSERT INTO Products ('id', 'title', 'description', 'price') VALUES (?, ?, ?, ?)",
                       (f'{i + 1}', f'{medicine_list[i]}', f'{vitamine_list[i]}', f'{(i + 1) * 100}'))


def get_all_products():
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    return products


initiate_db()
# create_products()
get_all_products()
connection.commit()
# connection.close()
