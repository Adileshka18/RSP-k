-- Откат 000001_init_schema: удаляем объекты в порядке, обратном созданию,
-- чтобы сначала уходили таблицы, которые ссылаются на другие.

BEGIN;

DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS chats;
DROP TABLE IF EXISTS product_reviews;
DROP TABLE IF EXISTS enterprise_reviews;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS enterprise_favorites;
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS order_history;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS user_enterprises;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS enterprises;

DROP TYPE IF EXISTS document_type;
DROP TYPE IF EXISTS payment_status;
DROP TYPE IF EXISTS order_status;
DROP TYPE IF EXISTS user_role;

COMMIT;
