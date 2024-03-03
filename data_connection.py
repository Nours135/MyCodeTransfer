# data connection
import pymysql

# DDL
'''
CREATE TABLE `posts`(
post_id varchar(15) NOT NULL,
title varchar(100),
comment_cnt varchar(5),
tag varchar(15),
created_time varchar(60),  
score int,
author_id varchar(15),
author_name varchar(30),
article_origin_link varchar(100),
data_collection_time varchar(60),
comment_link varchar(100),
author_link varchar(100), 
comment_data_json longtext, 
PRIMARY KEY (`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci


CREATE TABLE `articles`(
title varchar(100),
content mediumtext,
tables int,
article_origin_link varchar(100) NOT NULL, 
data_collection_time int
PRIMARY KEY (`article_origin_link`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci


CREATE TABLE `users` (
uname varchar(30) NOT NULL, 
Post_Karma int, 
Comment_Karma int, 
cake_day varchar(30), 
slogan varchar(300), 
is_vip int, 
trophies varchar(1000),
subreddit_moderators varchar(500), 
post_times varchar(100), 
comment_times varchar(100), 
data_collect_time varchar(50),
PRIMARY KEY (`uname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

# 我觉得我不需要这个table ！！

'''



def get_db():
    db = pymysql.connect(host='111.229.241.116',
                         port=3306,
                         user='RedditProvider',
                         password='KLWDriver10086',
                         database='R_Science')  # 记得新建
    return db

def store_post_full(args_tuple, db, cursor):
    sql = """
        INSERT INTO posts (post_id, title, comment_cnt, tag, created_time, score, author_id, author_name,
               article_origin_link, data_collection_time, comment_link, author_link)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
       # 执行sql语句
       cursor.execute(sql, args_tuple)
       # 提交到数据库执行
       db.commit()
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        print(str(e))
        db.rollback()

def store_post_half():
    '''存部分post信息，作为爬取队列'''
    pass
    
def store_article(args_tuple, db, cursor):
    sql = """
        INSERT INTO articles (title, content, tables, article_origin_link, data_collection_time)
               values (%s, %s, %s, %s, %s)
    """
    try:
       # 执行sql语句
       cursor.execute(sql, args_tuple)
       # 提交到数据库执行
       db.commit()
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        print(str(e))
        db.rollback()
    
def store_user(args_tuple, db, cursor):
    sql = """
        INSERT INTO `users` (uname, Post_Karma, Comment_Karma, cake_day, slogan, is_vip, trophies,
               subreddit_moderators, post_times, comment_times, data_collect_time)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
       # 执行sql语句
       cursor.execute(sql, args_tuple)
       # 提交到数据库执行
       db.commit()
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        print(str(e))
        db.rollback()
    
def store_comment(args_tuple, db, cursor):
    sql = """
        INSERT INTO `users` ()
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
       # 执行sql语句
       cursor.execute(sql, args_tuple)
       # 提交到数据库执行
       db.commit()
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        print(str(e))
        db.rollback()

