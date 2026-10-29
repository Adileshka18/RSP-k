-- 000001_init_schema: начальная схема БД SavorLink (B2B-маркетплейс поставщиков и покупателей).
--
-- Схема в 3НФ: у каждой таблицы суррогатный первичный ключ, все неключевые атрибуты
-- зависят только от ключа своей таблицы. Справочные данные (предприятие, категория,
-- пользователь) хранятся один раз и подключаются внешними ключами.
--
-- Правила ON DELETE:
--   CASCADE  — запись является «частью» родителя и без него не имеет смысла
--              (позиции заказа, позиции корзины, избранное, сообщения чата).
--   RESTRICT — запись является историческим или юридически значимым фактом,
--              её нельзя терять молча (заказы, платежи, документы, история статусов).

BEGIN;

-- ────────────────────────────────────────────────
-- ПЕРЕЧИСЛЕНИЯ
-- ────────────────────────────────────────────────

CREATE TYPE user_role AS ENUM ('ADMIN', 'BUYER', 'SUPPLIER');
CREATE TYPE order_status AS ENUM ('CREATED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE payment_status AS ENUM ('PENDING', 'PAID', 'FAILED', 'REFUNDED');
CREATE TYPE document_type AS ENUM ('INVOICE', 'CONTRACT', 'ACT');

-- ────────────────────────────────────────────────
-- КЛЮЧЕВЫЕ ТАБЛИЦЫ
-- ────────────────────────────────────────────────

-- Предприятие (поставщик или покупатель)
CREATE TABLE enterprises (
    id          BIGSERIAL PRIMARY KEY,
    short_name  TEXT        NOT NULL,
    inn         TEXT        NOT NULL,
    region      TEXT        NOT NULL,
    city        TEXT,
    phone       TEXT,
    email       TEXT,
    description TEXT,
    logo_url    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_enterprises_short_name UNIQUE (short_name),
    CONSTRAINT ck_enterprises_short_name_not_blank CHECK (btrim(short_name) <> ''),
    -- ИНН юрлица — 10 цифр, ИП — 12 цифр
    CONSTRAINT ck_enterprises_inn_format CHECK (inn ~ '^[0-9]{10}([0-9]{2})?$')
);

-- Пользователь системы
CREATE TABLE users (
    id            BIGSERIAL PRIMARY KEY,
    email         TEXT        NOT NULL,
    password_hash TEXT        NOT NULL,
    token_version INTEGER     NOT NULL DEFAULT 0,
    role          user_role   NOT NULL,
    phone         TEXT,
    first_name    TEXT,
    last_name     TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_email_format CHECK (email LIKE '_%@_%'),
    CONSTRAINT ck_users_token_version_non_negative CHECK (token_version >= 0)
);

-- Связь «многие ко многим»: пользователь работает в нескольких предприятиях
CREATE TABLE user_enterprises (
    user_id       BIGINT NOT NULL,
    enterprise_id BIGINT NOT NULL,

    CONSTRAINT pk_user_enterprises PRIMARY KEY (user_id, enterprise_id),
    -- связь без пользователя или предприятия бессмысленна
    CONSTRAINT fk_user_enterprises_user
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_enterprises_enterprise
        FOREIGN KEY (enterprise_id) REFERENCES enterprises (id) ON DELETE CASCADE
);
-- user_id покрыт первичным ключом (первая колонка), enterprise_id — нет
CREATE INDEX idx_user_enterprises_enterprise_id ON user_enterprises (enterprise_id);

-- Справочник категорий товаров
CREATE TABLE categories (
    id   BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,

    CONSTRAINT uq_categories_name UNIQUE (name),
    CONSTRAINT ck_categories_name_not_blank CHECK (btrim(name) <> '')
);

-- Товар поставщика
CREATE TABLE products (
    id                BIGSERIAL PRIMARY KEY,
    name              TEXT           NOT NULL,
    description       TEXT,
    price             NUMERIC(12, 2) NOT NULL,
    min_order_qty     INTEGER,
    quantity_in_stock INTEGER,
    enterprise_id     BIGINT         NOT NULL,
    category_id       BIGINT         NOT NULL,
    created_at        TIMESTAMPTZ    NOT NULL DEFAULT now(),

    CONSTRAINT ck_products_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT ck_products_price_positive CHECK (price > 0),
    CONSTRAINT ck_products_min_order_qty_non_negative CHECK (min_order_qty >= 0),
    CONSTRAINT ck_products_stock_non_negative CHECK (quantity_in_stock >= 0),
    -- товары принадлежат предприятию: удалили поставщика — удалились его товары
    CONSTRAINT fk_products_enterprise
        FOREIGN KEY (enterprise_id) REFERENCES enterprises (id) ON DELETE CASCADE,
    -- нельзя удалить категорию, пока в ней есть товары
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
);
CREATE INDEX idx_products_enterprise_id ON products (enterprise_id);
CREATE INDEX idx_products_category_id ON products (category_id);

-- Заказ покупателя у поставщика
CREATE TABLE orders (
    id                   BIGSERIAL PRIMARY KEY,
    status               order_status   NOT NULL DEFAULT 'CREATED',
    total_amount         NUMERIC(14, 2),
    buyer_enterprise_id  BIGINT         NOT NULL,
    seller_enterprise_id BIGINT         NOT NULL,
    created_at           TIMESTAMPTZ    NOT NULL DEFAULT now(),

    CONSTRAINT ck_orders_total_amount_non_negative CHECK (total_amount >= 0),
    -- заказ — финансовый факт: предприятие с заказами удалить нельзя
    CONSTRAINT fk_orders_buyer_enterprise
        FOREIGN KEY (buyer_enterprise_id) REFERENCES enterprises (id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_seller_enterprise
        FOREIGN KEY (seller_enterprise_id) REFERENCES enterprises (id) ON DELETE RESTRICT
);
CREATE INDEX idx_orders_buyer_enterprise_id ON orders (buyer_enterprise_id);
CREATE INDEX idx_orders_seller_enterprise_id ON orders (seller_enterprise_id);

-- Позиция заказа. price — цена на момент заказа, а не копия products.price:
-- цена товара потом может измениться, а сумма заказа — нет.
CREATE TABLE order_items (
    id         BIGSERIAL PRIMARY KEY,
    order_id   BIGINT         NOT NULL,
    product_id BIGINT         NOT NULL,
    quantity   INTEGER        NOT NULL,
    price      NUMERIC(12, 2) NOT NULL,

    CONSTRAINT uq_order_items_order_product UNIQUE (order_id, product_id),
    CONSTRAINT ck_order_items_quantity_positive CHECK (quantity > 0),
    CONSTRAINT ck_order_items_price_non_negative CHECK (price >= 0),
    -- позиция — часть заказа
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
    -- нельзя удалить товар, который уже был заказан: потеряется история заказов
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
);
-- order_id покрыт уникальным индексом (первая колонка)
CREATE INDEX idx_order_items_product_id ON order_items (product_id);

-- ────────────────────────────────────────────────
-- ОСТАЛЬНЫЕ ТАБЛИЦЫ ПРИЛОЖЕНИЯ
-- ────────────────────────────────────────────────

-- История смены статусов заказа
CREATE TABLE order_history (
    id         BIGSERIAL PRIMARY KEY,
    order_id   BIGINT       NOT NULL,
    status     order_status NOT NULL,
    changed_by BIGINT       NOT NULL,
    changed_at TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_order_history_order
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
    -- журнал действий: нельзя удалить пользователя, менявшего статусы заказов
    CONSTRAINT fk_order_history_changed_by
        FOREIGN KEY (changed_by) REFERENCES users (id) ON DELETE RESTRICT
);
CREATE INDEX idx_order_history_order_id ON order_history (order_id);
CREATE INDEX idx_order_history_changed_by ON order_history (changed_by);

-- Корзина (одна на пользователя)
CREATE TABLE carts (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT      NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- UNIQUE заодно служит индексом по внешнему ключу
    CONSTRAINT uq_carts_user_id UNIQUE (user_id),
    CONSTRAINT fk_carts_user
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
    id         BIGSERIAL PRIMARY KEY,
    cart_id    BIGINT  NOT NULL,
    product_id BIGINT  NOT NULL,
    quantity   INTEGER NOT NULL,

    CONSTRAINT uq_cart_items_cart_product UNIQUE (cart_id, product_id),
    CONSTRAINT ck_cart_items_quantity_positive CHECK (quantity > 0),
    CONSTRAINT fk_cart_items_cart
        FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
    -- корзина временная: удалённый товар просто исчезает из корзин
    CONSTRAINT fk_cart_items_product
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
CREATE INDEX idx_cart_items_product_id ON cart_items (product_id);

-- Избранные товары
CREATE TABLE favorites (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT      NOT NULL,
    product_id BIGINT      NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_favorites_user
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_favorites_product
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uq_favorite ON favorites (user_id, product_id);
CREATE INDEX idx_favorites_product_id ON favorites (product_id);

-- Избранные поставщики
CREATE TABLE enterprise_favorites (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT      NOT NULL,
    enterprise_id BIGINT      NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_enterprise_favorites_user
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_enterprise_favorites_enterprise
        FOREIGN KEY (enterprise_id) REFERENCES enterprises (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uq_enterprise_favorite ON enterprise_favorites (user_id, enterprise_id);
CREATE INDEX idx_enterprise_favorites_enterprise_id ON enterprise_favorites (enterprise_id);

-- Оплата заказа (одна на заказ)
CREATE TABLE payments (
    id         BIGSERIAL PRIMARY KEY,
    order_id   BIGINT         NOT NULL,
    amount     NUMERIC(14, 2) NOT NULL,
    status     payment_status NOT NULL,
    created_at TIMESTAMPTZ    NOT NULL DEFAULT now(),

    CONSTRAINT uq_payments_order_id UNIQUE (order_id),
    CONSTRAINT ck_payments_amount_non_negative CHECK (amount >= 0),
    -- нельзя удалить заказ, по которому прошла оплата
    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT
);

-- Документы по заказу (счёт, договор, акт)
CREATE TABLE documents (
    id         BIGSERIAL PRIMARY KEY,
    order_id   BIGINT        NOT NULL,
    type       document_type NOT NULL,
    file_url   TEXT          NOT NULL,
    created_at TIMESTAMPTZ   NOT NULL DEFAULT now(),

    -- юридически значимые документы не удаляются вместе с заказом
    CONSTRAINT fk_documents_order
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT
);
CREATE INDEX idx_documents_order_id ON documents (order_id);

-- Отзыв пользователя о предприятии
CREATE TABLE enterprise_reviews (
    id                   BIGSERIAL PRIMARY KEY,
    author_user_id       BIGINT      NOT NULL,
    target_enterprise_id BIGINT      NOT NULL,
    rating               INTEGER     NOT NULL,
    comment              TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_author_target_review UNIQUE (author_user_id, target_enterprise_id),
    CONSTRAINT ck_enterprise_reviews_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT fk_enterprise_reviews_author
        FOREIGN KEY (author_user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_enterprise_reviews_target
        FOREIGN KEY (target_enterprise_id) REFERENCES enterprises (id) ON DELETE CASCADE
);
CREATE INDEX idx_enterprise_reviews_target_enterprise_id ON enterprise_reviews (target_enterprise_id);

-- Отзыв предприятия-покупателя о товаре
CREATE TABLE product_reviews (
    id                   BIGSERIAL PRIMARY KEY,
    author_enterprise_id BIGINT      NOT NULL,
    product_id           BIGINT      NOT NULL,
    rating               INTEGER     NOT NULL,
    comment              TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_author_product_review UNIQUE (author_enterprise_id, product_id),
    CONSTRAINT ck_product_reviews_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT fk_product_reviews_author
        FOREIGN KEY (author_enterprise_id) REFERENCES enterprises (id) ON DELETE CASCADE,
    CONSTRAINT fk_product_reviews_product
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
CREATE INDEX idx_product_reviews_product_id ON product_reviews (product_id);

-- Чат двух пользователей. user_min/user_max вычисляет сама СУБД — они нужны,
-- чтобы пара (1, 2) и пара (2, 1) считались одним и тем же чатом.
CREATE TABLE chats (
    id         BIGSERIAL PRIMARY KEY,
    user1_id   BIGINT      NOT NULL,
    user2_id   BIGINT      NOT NULL,
    user_min   BIGINT GENERATED ALWAYS AS (LEAST(user1_id, user2_id)) STORED,
    user_max   BIGINT GENERATED ALWAYS AS (GREATEST(user1_id, user2_id)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_chats_different_users CHECK (user1_id <> user2_id),
    CONSTRAINT fk_chats_user1
        FOREIGN KEY (user1_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_chats_user2
        FOREIGN KEY (user2_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX idx_chats_user1 ON chats (user1_id);
CREATE INDEX idx_chats_user2 ON chats (user2_id);
CREATE UNIQUE INDEX uq_chats_users ON chats (user_min, user_max);

CREATE TABLE messages (
    id         BIGSERIAL PRIMARY KEY,
    chat_id    BIGINT      NOT NULL,
    sender_id  BIGINT      NOT NULL,
    content    TEXT        NOT NULL,
    is_read    BOOLEAN     NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_messages_content_length CHECK (btrim(content) <> '' AND length(content) <= 4000),
    CONSTRAINT fk_messages_chat
        FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_sender
        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX idx_messages_chat_id ON messages (chat_id);
CREATE INDEX idx_messages_sender_id ON messages (sender_id);

-- ────────────────────────────────────────────────
-- НАЧАЛЬНОЕ ЗАПОЛНЕНИЕ СПРАВОЧНИКА
-- ────────────────────────────────────────────────

INSERT INTO categories (name) VALUES
    ('Овощи и зелень'),
    ('Мясо и птица'),
    ('Молочные продукты'),
    ('Бакалея'),
    ('Напитки');

COMMIT;
