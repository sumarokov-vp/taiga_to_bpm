-- Добавление поля taiga_id в таблицу bot_users
ALTER TABLE bot_users 
ADD COLUMN taiga_id INTEGER NULL;

-- Создание индекса для более быстрого поиска по taiga_id
CREATE INDEX idx_bot_users_taiga_id ON bot_users(taiga_id);

-- Комментарий к полю
COMMENT ON COLUMN bot_users.taiga_id IS 'ID пользователя в системе Taiga';

-- Пример обновления данных (предполагая, что у вас есть соответствия)
-- UPDATE bot_users 
-- SET taiga_id = 27  -- ID пользователя в Taiga
-- WHERE id = 1;      -- ID пользователя в вашей системе
-- 
-- UPDATE bot_users 
-- SET taiga_id = 44  -- ID пользователя в Taiga
-- WHERE telegram_id = 384432574; -- Telegram ID пользователя