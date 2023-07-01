CREATE database ndd;
USE ndd;
CREATE TABLE users (
    id int AUTO_INCREMENT PRIMARY KEY,
    account varchar(80),
    password varchar(80),
    email varchar(100),
    category ENUM ('admin', 'manager','general','guest') DEFAULT 'general',
    UNIQUE (account)
);
INSERT INTO users (account, password, email, category) VALUES ('admin', SHA2('admin', 256), 'kaminyou@cmdm.csie.ntu.edu.tw', 'admin');
INSERT INTO users (account, password, email, category) VALUES ('manager', SHA2('manager', 256), 'kaminyou@cmdm.csie.ntu.edu.tw', 'manager');
INSERT INTO users (account, password, email, category) VALUES ('general', SHA2('general', 256), 'kaminyou@cmdm.csie.ntu.edu.tw', 'general');
INSERT INTO users (account, password, email, category) VALUES ('guest', SHA2('guest', 256), 'kaminyou@cmdm.csie.ntu.edu.tw', 'guest');