-- Drops
DROP VIEW IF EXISTS feed_posts;
DROP TABLE IF EXISTS follows;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS blacks;

-- Users
CREATE TABLE users (
    usr         TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    phone       TEXT,
    pwd         TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Follows
CREATE TABLE follows (
    follower_usr   TEXT NOT NULL,
    followee_usr   TEXT NOT NULL,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (follower_usr, followee_usr),
    CHECK (follower_usr <> followee_usr),
    FOREIGN KEY (follower_usr) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (followee_usr) REFERENCES users(usr) ON DELETE CASCADE
);

-- Blocks
CREATE TABLE blocks (
    blocker_usr  TEXT NOT NULL,
    blocked_usr  TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (blocker_usr, blocked_usr),
    CHECK (blocker_usr <> blocked_usr),
    FOREIGN KEY (blocker_usr) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (blocked_usr) REFERENCES users(usr) ON DELETE CASCADE
);

-- Posts
CREATE TABLE posts (
    id           INTEGER PRIMARY KEY,
    author_usr   TEXT NOT NULL,
    content      TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 360),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (author_usr) REFERENCES users(usr) ON DELETE CASCADE
);

-- Helpful indexes
CREATE INDEX idx_follows_follower ON follows(follower_usr);
CREATE INDEX idx_follows_followee ON follows(followee_usr);
CREATE INDEX idx_blocks_blocker ON blocks(blocker_usr);
CREATE INDEX idx_blocks_blocked ON blocks(blocked_usr);
CREATE INDEX idx_posts_author_created ON posts(author_usr, created_at DESC);
