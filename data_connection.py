# data connection
import pymysql
from datetime import datetime
# DDL
'''
CREATE TABLE `posts`(
post_id varchar(15),
created_time int,  
data_collection_time int,
comment_link varchar(100),

comment_data_json longtext, 
post_data_json varchar(4000),
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
                         database='R_Science',
                         connect_timeout=60)  # 记得新建
    return db

def store_post_full(args_tuple, db, cursor):
    '''
        存储所有的data
        args_tuple 包括 post_data_json, comment_data_json, article_origin_link, data_collection_time, comment_link
    '''
    sql = """
        UPDATE posts
        SET post_data_json = %s,
            comment_data_json = %s,
            article_origin_link = %s,
            data_collection_time = %s
        WHERE comment_link = %s;
    """
    try:
       # 执行sql语句
       cursor.execute(sql, args_tuple)
       # 提交到数据库执行
       db.commit()
       return 1
    except TimeoutError as timoout:
        return store_post_full(args_tuple, db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[-1]) +"\n")
        print(str(e))
        db.rollback()
        return str(e)

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
    except TimeoutError as timoout:
        store_post_half(args_tuple, db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)
    

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
    except TimeoutError as timoout:
        store_user(args_tuple, db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(args_tuple[0]) +"\n")
        print(str(e))
        db.rollback()
    

def get_task(db, cursor):
    '''获取一个task'''
    sql = f"""
        SELECT post_id, created_time, data_collection_time, comment_link
            FROM posts 
            WHERE comment_data_json is NULL
                AND created_time < {int(datetime.today().timestamp()) - 864000}  
            ORDER by created_time ASC
            LIMIT 1;
    """  # 864000 = 10*24*60*60 就是10天前
    try:
        # 执行sql语句
        cursor.execute(sql)
        selected_task = cursor.fetchall()[0]
        # 提交到数据库执行
        post_id, created_time, data_collection_time, comment_link = selected_task
        occupy_sql = """
                UPDATE posts
                SET comment_data_json = %s
                WHERE comment_link = %s ;
            """
        values = (int(datetime.today().timestamp()),comment_link)
        
        cursor.execute(occupy_sql, values)

        db.commit()
        return post_id, created_time, data_collection_time, comment_link
    except TimeoutError as timoout:
        # 重新传输一遍遍
        return get_task(db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(comment_link) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)
    
def store_article(article_origin_link, article_data_json, db, cursor):
    '''存储post的article的信息
    args_tuple 包括 article_data_json, article_origin_link
     '''
    sql = """
        UPDATE posts
        SET article_data_json = %s
        WHERE article_origin_link = %s;
    """
    try:
       # 执行sql语句
       cursor.execute(sql, (article_data_json, article_origin_link))
       # 提交到数据库执行
       db.commit()
       return 1
    except TimeoutError as timoout:
        store_post_half(article_origin_link, article_data_json, db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(article_origin_link) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)

def get_article_task(db, cursor):
    '''获取一个article 的 task'''
    sql = f"""
        SELECT article_origin_link
            FROM posts 
            WHERE post_data_json is NOT NULL
                AND article_data_json is NULL
            ORDER by RAND()  
            LIMIT 1;
    """  # ORDER by RAND()  实现随机获取
    try:
        # 执行sql语句
        cursor.execute(sql)
        selected_task = cursor.fetchall()[0]
        # 提交到数据库执行
        article_origin_link = selected_task[0] # 无需下面的occupy，这个一般单线程即可，而且随机获取本身也较低概率重复
        db.commit()
        return article_origin_link
    
    except TimeoutError as timoout:
        # 重新传输一遍遍
        return get_task(db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(article_origin_link) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)
    

def check_queue(db, cursor):
    sql = 'select count(*) from posts where comment_data_json is NULL;'
    try:
       # 执行sql语句
       cursor.execute(sql)
       # 提交到数据库执行
       selected_task = cursor.fetchall()[0][0]
        # 提交到数据库执行
       db.commit()
       return selected_task  # 返回队列中仍有的任务数量
    except TimeoutError as timoout:
        check_queue(db, cursor)
    except Exception as e:
       # 如果发生错误则回滚
        with open("./error_report.txt", "a") as f:
            f.write(str(e) + "|" + str(sql) +"\n")
        # print(str(e))
        db.rollback()
        return str(e)
    

if __name__ == '__main__':
    db = get_db()
    cursor = db.cursor()
    print(get_task(db, cursor))