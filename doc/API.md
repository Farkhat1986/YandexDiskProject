# Для реализации автотестов API Диска необходимо:

1. Авторизоваться в Яндекс Диске
2. Перейти в Полигон по ссылке: https://yandex.ru/dev/disk/poligon/
3. Получчить токен, нажав на кнопку "Получить OAuth-токен"

Базовый URL для запросов: https://cloud-api.yandex.net

Полученный токен (ayth_token) должен быть указан в заголовках (Headers) при каждом
запросе, если не указано иное: {Authorization: OAuth auth_token}


## Тест-кейс 1: Создание папки

**Предусловие:**

* Убедиться, что папка с именем {name} не существует на Диске

**Шаги:**

1. Отправить PUT запрос на адрес v1/disk/resources?path=app:/{name}

**Ожидаемые результаты:**

	* Код ответа 201 Created
	
	* Тело ответа JSON содержит поля:

		* "href": "https://cloud-api.yandex.net/v1/disk/resources?path=app%3A%2F{name}"

		* "method": "GET"

		* "templated": false

2. Отправить GET запрос на адрес v1/disk/resources?path=app:/{name}

**Ожидаемые результаты:**

	* Код ответа 200 OK

	* В теле ответа есть поле "type": "dir" и "name": "{name}"

## Тест-кейс 2: Удаление папки

**Предусловие:**

	* Убедиться, что на Диске существует папка с именем {name} (создать её, если необходимо)

**Шаги:**

1. Отправить DELETE запрос по адресу v1/disk/resources?path=app:/{name}

**Ожидаемые результаты:**

	* Код ответа 204 No Content

	* Тело ответа содержит пустое поле

2. Отправить GET запрос по адресу v1/disk/resources?path=app:/{name}

**Ожидаемые результаты:**

	* Код ответа 404 Not Found

## Тест-кейс 3: Восстановление папки из корзины

**Предусловие:**

1. Создать папку {name}

2. Удалить папку {name} (переместить в корзину)

3. Получить метаинформацию о корзине, отправив GET запрос на адрес v1/disk/trash/resources/?path=app:/{name}

4. Из ответа сохранить значение resource_id

**Шаги:**

1. Отправить PUT запрос на адрес v1/disk/trash/resources/restore?path={name}

**Ожидаемые результаты:**

	* Код ответа: 201 Created

	* Тело ответа JSON содержит поля:

		* "href": "https://cloud-api.yandex.net/v1/disk/resources?path=app%3A%2F{name}"

		* "method": "GET"

		* "templated": false

2. Отправить GET запрос на адрес v1/disk/resources?path=app:/{name}
	
**Ожидаемые результаты:**

	* Код ответа 200 OK

	* В теле ответа есть поле "type": "dir"

## Тест-кейс 4: Создание текстового файла

**Предусловие:**

* Убедиться, что файла с именем test_file.txt не существует на Диске

**Шаги:**

1. Получить URL для загрузки, отправив GET запрос на адрес v1/disk/resources/upload?path=app:/test_file.txt

	**Ожидаемые результаты:**
		
		* Код 200 OK

		* В теле ответа 

			"method": "PUT",
    		
			"href": "https://uploader79sas.disk.yandex.net:443/upload-target/{info}",
    		
			"templated": false,
    
			"operation_id": "token"

		

2. Загрузить текстовый файл, отправив PUT запрос на URL из поля href. В теле запроса передать строку "{text}".

	**Ожидаемые результаты:**

		* Код ответа 201 Created

		* В теле ответа пусто

3. Отправить GET запрос на адрес v1/disk/resources?path=app:/test_file.txt.

	**Ожидаемый результат:**
 
		* Код ответа 200 OK

		* В теле ответа есть поле "type": "file", "name": "test_file.txt" и "mime_type": "text/plain"