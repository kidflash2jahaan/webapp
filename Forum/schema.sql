create table users(
    id integer primary key autoincrement,
    name_text text not null,
    password_text text not null,
    expert_boolean boolean not null,
    admin_boolean boolean not null
);
create table questions(
    id integer primary key autoincrement,
    question_text text not null,
    answer_text text,
    asked_by_id integer not null,
    expert_id integer not null
);