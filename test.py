from requests import get, post, delete

print('users')

print(1, get('http://localhost:8080/api/users').json())
print(2, get('http://localhost:8080/api/users/3').json())
print(3, get('http://localhost:8080/api/users/22').json())  # нет пользователя
print(4, get('http://localhost:8080/api/users/q').json())  # не число

print(5, post('http://localhost:8080/api/users').json())  # нет словаря
print(6, post('http://localhost:8080/api/users', json={'name': 'Ann'}).json())  # не все поля
print(7, post('http://localhost:8080/api/users', json={'name': 'Ann', 'description': 'kitty',
                                                    'address': 'streamer@ya.ru', 'password': 'night-bot',
                                                    'communication': '+7(999)999-99-99'}).json())


print(8, delete('http://localhost:8080/api/users/999').json())  # id = 999 нет в базе
print(9, delete('http://localhost:8080/api/users/4').json())


print('adverts')

print(1, get('http://localhost:8080/api/adverts').json())
print(2, get('http://localhost:8080/api/adverts/3').json())
print(3, get('http://localhost:8080/api/adverts/22').json())  # нет объявления
print(4, get('http://localhost:8080/api/adverts/q').json())  # не число

print(5, post('http://localhost:8080/api/adverts').json())  # нет словаря
print(6, post('http://localhost:8080/api/adverts', json={'name': 'Мармеладные мишки'}).json())  # не все поля
print(7, post('http://localhost:8080/api/adverts', json={'name': 'Мармеладные мишки', 'id_person': 0,
                                                         'description': 'Срочно! Куплю 100 килограмм! Могу забрать и самовывозом и через доставку.',
                                                         'price': 'до 1.000.000.000', 'data': '2023-04-25 06:07:08.091011',
                                                         'id_files': 2}).json())


print(8, delete('http://localhost:8080/api/adverts/999').json())  # id = 999 нет в базе
print(9, delete('http://localhost:8080/api/adverts/5').json())