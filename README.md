# Генератор данных поездок на электросамокатах

Для курса-симулятора ["dbt для инженеров данных и аналитиков"](https://inzhenerka.tech/dbt)

## Установка зависимостей

```bash
pip install .
```

## Создание новой версии

Релиз GitHub создается автоматически при пуше в ветку main.

⚠️ Не забыть загрузить файлы с данными в S3 ⚠️

## Опубликованные датасеты

- [version.txt](https://inzhenerka-public.s3.eu-west-1.amazonaws.com/scooters_data_generator/version.txt) - файл с актуальной версией данных
- [events.parquet](https://inzhenerka-public.s3.eu-west-1.amazonaws.com/scooters_data_generator/events.parquet) - события из мобильного приложения кикшеринга
- [payments.parquet](https://inzhenerka-public.s3.eu-west-1.amazonaws.com/scooters_data_generator/payments.parquet) - оплаты поездок пользователями
- [trips.parquet](https://inzhenerka-public.s3.eu-west-1.amazonaws.com/scooters_data_generator/trips.parquet) - поездки пользователей на самокатах
- [users.parquet](https://inzhenerka-public.s3.eu-west-1.amazonaws.com/scooters_data_generator/users.parquet) - пользователи кикшеринга
- [scooters_raw.sql](https://inzhenerka-public.s3.eu-west-1.amazonaws.com/scooters_data_generator/scooters_raw.sql) - SQL-дамп с данными из parquet-файлов
- [weather.json](s3://inzhenerka-public/scooters_data_generator/weather.json) - погодные данные по дням

## Автоматизированная загрузка

- [dbt Data Bot](https://t.me/inzhenerka_dbt_bot) - телеграм-бот для загрузки данных в базу через интернет
- [scooters_data_uploader](https://github.com/Inzhenerka/scooters_data_uploader) - приложение для загрузки данных в локальную базу
