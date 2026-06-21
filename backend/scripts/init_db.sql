-- MAX VPS - Initial DB roles
-- Создаём отдельного пользователя для приложения + readonly для будущих задач

-- (Не нужно на этапе разработки — пользователь maxvps уже создан через POSTGRES_USER)
-- Этот файл — для будущих миграций (роли readonly, web_users и т.д.)

-- В будущем (когда подключимся к прод-БД бота):
-- CREATE ROLE maxvps_readonly LOGIN PASSWORD 'change_me';
-- GRANT CONNECT ON DATABASE vpnhubbotdb TO maxvps_readonly;
-- GRANT USAGE ON SCHEMA public TO maxvps_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO maxvps_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO maxvps_readonly;

SELECT 'MAX VPS DB initialized' AS status;
