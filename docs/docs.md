Документация за API

API се хоства локално на адрес:

http://localhost:5000

Endpoints:

1. Удостоверяване

Endpoint: /login

Метод: POST

Примерна заявка:

curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

Отговор:

{
  "access_token": "<JWT Token>"
}

2. Качване на файл

Endpoint: /upload

Метод: POST

Примерна заявка:

curl -X POST http://localhost:5000/upload \
  -H "Authorization: Bearer <JWT Token>" \
  -F "file=@path/to/your/file.txt"

Отговор:

{
  "message": "Файлът 'file.txt' е успешно качен"
}

3. Изтегляне на файл

Endpoint: /download/<file_id>

Метод: GET

Примерна заявка:

curl -X GET http://localhost:5000/download/file.txt \
  -H "Authorization: Bearer <JWT Token>"

Отговор: Избраният файл като прикачен за изтегляне.

4. Актуализиране на файл

Endpoint: /update/<file_id>

Метод: PUT

Примерна заявка:

curl -X PUT http://localhost:5000/update/file.txt \
  -H "Authorization: Bearer <JWT Token>" \
  -F "file=@path/to/your/newfile.txt"

Отговор:

{
  "message": "Файлът 'file.txt' е успешно актуализиран"
}

5. Изтриване на файл

Endpoint: /delete/<file_id>

Метод: DELETE

Примерна заявка:

curl -X DELETE http://localhost:5000/delete/file.txt \
  -H "Authorization: Bearer <JWT Token>"

Отговор:

{
  "message": "Файлът 'file.txt' е успешно изтрит"
}



Настройка и стартиране на приложението:

Prerequisites

Уверете се, че Docker и Docker Compose са инсталирани на вашата машина.

Клонирайте репото:

git clone <rehttps://github.com/Loraaa12/vot.git>
cd <s3-jwt>

Buildнете и стартирайте Docker контейнерите:

docker-compose up --build

Проверете дали приложението работи, като отворите:

http://localhost:5000



Конфигурация на Keycloak

Prerequisites
Keycloak е включен като част от файла docker-compose.yml. Уверете се, че е правилно конфигуриран и стартиран като част от стека.


Конфигурация на Keycloak

Достъп до Keycloak Admin Console:

Отворете Keycloak Admin Console:

http://localhost:8080

Влезте с username и парола

Създаване на Realm:

Отидете в Admin Console.

Изберете "Add Realm" и създайте нов Realm (напр. my-realm).

Създаване на клиент:

В рамките на вашия Realm, отидете на Clients и кликнете Create.

Попълнете формуляра и запазете клиента.

Конфигурирайте пренасочващите URI:

Задайте http://localhost:5000/* като разрешен URI за пренасочване.

Създаване на роли:

Под Roles, добавете роли като uchenici, admin и др.

Създаване на потребители:

Отидете на Users и добавете потребители.

Присвоете роли на потребителите под Role Mappings.

Интеграция с приложението
Уверете се, че URL адресът на сървъра на Keycloak, Realm и детайлите на клиента съвпадат с конфигурациите във вашето приложение.