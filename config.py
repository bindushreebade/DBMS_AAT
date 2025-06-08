import os

class Config:
    SECRET_KEY = 'bindu@123'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'bindushreebade'
    MYSQL_PASSWORD = 'bindu@123'
    MYSQL_DB = 'project_manager'
    UPLOAD_FOLDER = 'static/images/profile_pics'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}