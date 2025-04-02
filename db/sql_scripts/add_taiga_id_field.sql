-- Добавление поля taiga_id в таблицу bot_users
ALTER TABLE bot_users 
ADD COLUMN taiga_id INTEGER NULL;

-- Создание индекса для более быстрого поиска по taiga_id
CREATE INDEX idx_bot_users_taiga_id ON bot_users(taiga_id);

-- Комментарий к полю
COMMENT ON COLUMN bot_users.taiga_id IS 'ID пользователя в системе Taiga';