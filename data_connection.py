# data connection
import pymysql
from datetime import datetime
# DDL
'''
CREATE TABLE `posts`(
post_id varchar(15),
created_time varchar(60),  
data_collection_time varchar(60),
comment_link varchar(100),

comment_data_json longtext, 
post_data_json varchar(800),
article_origin_link varchar(100),

PRIMARY KEY (`comment_link`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

# 以下都不要了，浓缩为 post_data_json
title varchar(100),
comment_cnt varchar(5),
tag varchar(15),
score int,
author_id varchar(15),
author_name varchar(30),
author_link varchar(100), 


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

def store_post_half(args_tuple, db, cursor):
    '''存部分post信息，作为爬取队列
    args_tuple 包括 post_id, created_time, data_collection_time, comment_link
    key为 comment_link '''
    sql = """
        INSERT INTO posts (post_id, created_time, data_collection_time, comment_link)
               values (%s, %s, %s, %s)
    """
    try:
       # 执行sql语句
       cursor.execute(sql, args_tuple)
       # 提交到数据库执行
       db.commit()
       return 1
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)
    
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


def get_task(db, cursor):
    '''获取一个task'''
    sql = """
        SELECT post_id, created_time, data_collection_time, comment_link
            FROM posts WHERE comment_data_json is NULL LIMIT 1;
    """
    try:
        # 执行sql语句
        cursor.execute(sql)
        selected_task = cursor.fetchall()[0]
        # 提交到数据库执行
        post_id, created_time, data_collection_time, comment_link = selected_task
        occupy_sql = f"""
                UPDATE comment_data_json = "{int(datetime.today().timestamp())}"
                    WHERE comment_link = "{comment_link}";
            """
        cursor.execute(occupy_sql)

        db.commit()
        return post_id, created_time, data_collection_time, comment_link
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(comment_link) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)
    
if __name__ == '__main__':
    pass