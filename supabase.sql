-- Run these in Supabase → SQL Editor
-- Only run what's missing — skip tables you've already created

create table if not exists user_events (
  id          bigint generated always as identity primary key,
  user_id     text not null,
  category    text not null,
  brand       text,
  created_at  timestamptz default now()
);

create table if not exists user_preferences (
  id          bigint generated always as identity primary key,
  user_id     text not null,
  category    text not null,
  clicks      int  default 1,
  unique (user_id, category)
);

create table if not exists offer_history (
  id          bigint generated always as identity primary key,
  user_id     text not null,
  segment     text,
  category    text,
  created_at  timestamptz default now()
);

create table if not exists wishlist (
  id                bigint generated always as identity primary key,
  user_id           text not null,
  name              text not null,
  category          text,
  price             text,
  discounted_price  text,
  rating            text,
  created_at        timestamptz default now()
);
