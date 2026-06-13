# AI Agent Network for E-commerce Customer Service

Streamlit-приложение с SQLite, Router и ровно тремя AI-агентами для e-commerce:

1. **Customer Support Agent**
2. **Order Management Agent**
3. **Product Recommendation Agent**

Новых агентов в проекте нет. Router выбирает одного из этих трех агентов и сохраняет причину выбора.
Эти три агента являются публичной customer-facing сетью для guests и regular users.

## Концепция

Приложение теперь работает как простая multi-role платформа:

- **Guest** может пользоваться чатом без регистрации.
- **Regular User** может зарегистрироваться, войти, задавать вопросы и прикреплять фото товара.
- **Store** может зарегистрироваться как магазин, заполнить профиль, управлять своими товарами и смотреть базовую аналитику интереса к товарам.

Старые технические функции вроде загрузки документов, DOCX/PPTX artifacts и materials management сохранены в коде, но не показываются в обычном пользовательском интерфейсе.

## Аккаунты

При регистрации пользователь выбирает:

- `Regular User`
- `Store`

Пароли не хранятся в открытом виде. Используется salted SHA-256 hash.

Guest mode доступен без логина.

Login и Register вынесены в отдельные Streamlit pages:

- `pages/Login.py`
- `pages/Register.py`

В основной странице у guest-пользователя кнопки **Login** и **Register** находятся в top-right области. У regular user там показывается email/username и **Logout**. У store account показывается store name или username и компактное меню `...` с пунктами **Store Dashboard** и **Logout**.

Рядом с auth controls расположен компактный theme switcher:

- `System`: следует browser/system preference через CSS media query;
- `Light`: включает светлые CSS-переменные;
- `Dark`: включает тёмные CSS-переменные.

Выбор темы хранится в `st.session_state.theme_mode` на время текущей сессии.

Стандартный Streamlit header, toolbar, footer и automatic multipage sidebar navigation скрыты CSS-ом, поэтому sidebar показывает только кастомный role-based интерфейс приложения.

### Registration Requirements

Registration form содержит:

- username;
- email;
- email verification code;
- password;
- confirm password;
- account type.

Email validation простая:

- должен содержать `@`;
- должен содержать `.`;
- не должен содержать пробелы.

### Email Verification

Регистрация требует подтверждения email:

1. пользователь вводит email;
2. нажимает **Send code** рядом с email field;
3. приложение отправляет 6-значный verification code на email;
4. пользователь вводит код в поле **Verification code**;
5. аккаунт создается только если код правильный, не истек и еще не был использован.

Код действует 10 минут. В SQLite хранится только hash кода, plain code не сохраняется.
Если пользователь запрашивает новый код, предыдущие unused codes для этого email становятся недействительными.

Для отправки email нужно настроить SMTP в `.env`. Для Gmail обычно нужен app password, а не обычный пароль аккаунта.

Password должен:

- быть минимум 8 символов;
- содержать хотя бы одну uppercase Latin letter;
- содержать хотя бы одну lowercase Latin letter;
- содержать хотя бы одну digit;
- содержать хотя бы один special character из набора `! @ # $ % ^ & * ( ) _ - + = ? .`;
- содержать только Latin letters, digits и разрешенные special characters;
- не содержать пробелы;
- не содержать Cyrillic characters;
- не содержать другие Unicode symbols.

Примеры валидных паролей: `Password1!`, `Store2025@`, `My-Shop9#`.

### Forgot Password

На Login page есть **Forgot password?**.

Это placeholder flow:

- пользователь вводит email;
- приложение проверяет, есть ли email в SQLite;
- реальная отправка email и reset tokens пока не реализованы.

### Persistent Login / Sessions

После успешного login приложение создает secure random session token через `secrets.token_urlsafe(32)`.
Raw token сохраняется в browser cookie `ecommerce_ai_session`, а в SQLite хранится только SHA-256 hash токена.

Session хранится в таблице `user_sessions` и истекает через 7 дней. При refresh страницы приложение читает cookie, проверяет token hash в базе и восстанавливает:

- user id;
- username;
- email;
- account type.

Logout отзывает session token в SQLite, удаляет cookie и очищает `st.session_state`.
Для локальной разработки cookie работает с non-secure настройками. Persistent login требует dependency `streamlit-cookies-manager`.

### Account Deletion

Logged-in users могут permanently delete account из account menu.

Удаление требует:

- typed confirmation `DELETE`;
- current password.

Regular user deletion удаляет:

- user account;
- user sessions;
- user chat history;
- email verification records for that email;
- user product interaction records.

Store account deletion дополнительно удаляет только данные этого магазина:

- store profile;
- store products;
- store product analytics.

Удаление не затрагивает других users, другие stores, чужие products или global app settings.

## Store Mode

Магазин получает dashboard с разделами:

- **Store Profile**
- **Product Database**
- **Product Analytics**
- **Store Assistant**
- **Preview Chat**

В профиле магазина можно указать:

- название магазина, обязательно;
- описание, опционально;
- сайт, опционально;
- физический адрес, опционально;
- GPS / Map link, опционально.

Используется одно универсальное поле карты: `gps_map_url`. В него можно вставить 2GIS, Yandex Maps, Google Maps или любую другую ссылку на карту.

## Product Database

Товары хранятся в SQLite и принадлежат конкретному магазину.

Поля товара:

- `store_id`
- `product_id`
- `name`
- `barcode`
- `price`
- `description`
- `image_path`
- `image_url`
- `image_description`
- `category`

Store users могут:

- добавлять товары;
- импортировать товары из CSV/XLSX;
- добавлять основное фото товара;
- просматривать свои товары;
- искать по ID, названию, barcode и описанию;
- редактировать товар;
- заменить или удалить фото товара;
- удалять товар;

Regular users и guests не могут управлять товарами.

### Product Import

Store accounts могут импортировать product database в разделе **Store Dashboard → Product Database → Import products**.

Поддерживаемые форматы:

- CSV
- XLSX

Required columns:

- `product_id`
- `name`
- `barcode`
- `price`
- `description`

Optional columns:

- `image_path`
- `image_url`
- `category`

`barcode` и `description` могут быть пустыми, но сами columns должны присутствовать в файле.
`price` должен быть numeric.

Import behavior:

- если `product_id` уже существует у текущего store, товар обновляется;
- если `product_id` новый, товар создается;
- invalid rows skipped and shown in validation report;
- imported products always belong only to the logged-in store;
- `image_path` attaches only if the local file exists;
- `image_url` is stored as reference only, image downloading is not implemented yet.

## Product Recommendation Agent

Когда Router выбирает `Product Recommendation Agent`, система ищет подходящие товары по всем магазинам и добавляет их в контекст агента.

В контекст попадает:

- product name;
- price;
- description;
- store name;
- website link, если заполнен;
- physical address, если заполнен;
- GPS / Map link, если заполнен.
- product image description, если заполнено.

Агент должен явно говорить, когда рекомендация основана на product database.

## Product Images And Similar Image Search

Store accounts могут загрузить одно основное фото для каждого товара в **Product Database**.

Поддерживаемые форматы:

- JPG
- JPEG
- PNG
- WEBP

Максимальный размер файла: 5 MB.

Файлы сохраняются локально в:

```text
data/product_images/
```

В базе хранится относительный путь `image_path`. Если изображение удалено с диска, приложение не должно падать.

Guest и regular user могут прикрепить изображение рядом с chat input и отправить запрос вроде:

- `Найди похожий товар`
- `Есть что-то похожее?`
- `Find similar product`

Такие запросы обрабатывает **Product Recommendation Agent**. Новый публичный агент не добавляется.

Если `AI_VISION_MODEL` и `AI_API_KEY` настроены, приложение пытается описать uploaded image через vision model и ищет товары по:

- product name;
- short description;
- product image description;
- user text;
- budget, если указан.

Если vision недоступен или запрос к vision model не удался, приложение не падает. Агент получает fallback context и просит пользователя описать товар, если похожий продукт нельзя найти по тексту.

Примеры вопросов:

- `Посоветуй смартфон до 150000 ₸`
- `Где купить наушники?`
- `Есть ли ноутбук для учёбы?`
- `Найди товар похожий на этот`

## Product Analytics

Когда пользовательский запрос связан с товарами магазина, приложение сохраняет запись в `product_interactions`.

Store dashboard показывает:

- total product-related questions;
- top mentioned products;
- top recommended products;
- recent related queries.

Для визуализации используются обычные Streamlit tables/metrics.

## Store Assistant

Store accounts используют **Store Assistant** внутри dashboard.

Это не четвертый customer-facing AI agent и не часть публичной 3-agent сети. Это внутренний admin helper для сотрудников магазина.

Store Assistant помогает:

- искать товары своего магазина;
- показывать товары дешевле заданной цены;
- предложить изменение цены, описания или barcode;
- предложить изменение адреса или website;
- объяснять analytics;
- показывать recent product queries.

Safety rules:

- Store Assistant работает только с товарами текущего logged-in store.
- Изменения цены, описания, barcode, адреса и website проходят через pending confirmation.
- Confirm / Cancel показываются до применения изменений.
- Удаление товаров не выполняется автоматически.
- Если команда неоднозначна, assistant просит уточнение.

## Photo Upload

Guest и regular user могут прикрепить фото товара рядом с полем ввода.

Поддерживаемые форматы:

- JPG
- JPEG
- PNG
- WEBP

Если vision-анализ недоступен, приложение не падает. Оно добавляет к запросу безопасную заметку:

`User uploaded an image. Vision analysis is not available yet.`

## Clear Chat

В customer chat есть кнопка **Clear chat**.

Перед очисткой приложение показывает подтверждение:

- **Confirm**
- **Cancel**

После подтверждения очищаются видимые сообщения и история, которая используется как chat context для текущего пользователя:

- guest очищает только текущую browser/session историю;
- logged-in user очищает только свою историю;
- store account может очистить chat только в **Preview Chat**.

Очистка чата не удаляет:

- users;
- store profiles;
- products;
- product analytics;
- email verification data;
- login sessions.

## Environment

Создайте `.env` рядом с `app.py`:

```env
AI_API_KEY=your_api_key_here
AI_MODEL=gpt-4o-mini
AI_VISION_MODEL=gpt-4o-mini
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com
EMAIL_DEBUG=false
COOKIE_PASSWORD=change_this_to_a_long_random_secret
DEBUG_MODE=false
```

API-ключи не хранятся в коде.
SMTP credentials тоже не хранятся в коде.
`COOKIE_PASSWORD` используется cookie manager для защиты browser cookie values. Это один application-wide secret из `.env`, а не per-user значение. Для реального запуска задайте длинную случайную строку.

Для локальной разработки можно установить:

```env
EMAIL_DEBUG=true
```

В этом режиме приложение не подключается к SMTP, но генерирует и сохраняет verification code как обычно. Код показывается в интерфейсе и логах только для разработки.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
streamlit run app.py
```

## SQLite Tables

Создаются автоматически при старте:

- `users`
- `user_sessions`
- `email_verification_codes`
- `store_profiles`
- `products`
- `product_interactions`
- `chat_messages`
- existing document/artifact tables for backward compatibility

## Структура

```text
ecommerce_ai_agents/
├── app.py
├── agents/
├── config/
├── services/
├── storage/
├── ui/
├── readers/
├── rag/
└── generators/
```
