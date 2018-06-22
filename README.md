#### 项目demo地址：[piaoliangkb.info](http://piaoliangkb.info/)
-----------------------------------------

对照《Flask Web开发：基于Python的Web应用开发实战》编写的个人博客demo。   
目前已经实现的功能有：
- 登陆注册
- 个人信息修改
- 博客信息发布
- 博客评论 
- 文章列表页  

此外还有数据挖掘作业的两个可视化操作界面：
- MiniSearchEngine
- VectorSpaceSearch

将要添加和完善的功能包括：
- 博客界面美化
- 功能完善的markdown编辑器
- 文章标签

-----------------------------------------
### 本项目的配置和部署

#### 1.首先从github上clone本项目

    git clone https://github.com/piaoliangkb/Flaskblog.git

#### 2.建立python虚拟环境
    virtualenv venv
    source venv/bin/active
##### 2.1 安装依赖包
    pip install -r requirements.txt
##### 2.2 创建数据库
在虚拟环境中输入  

    python manage.py shell
进入交互环境

    from app.models import db,Role
    db.create_all()
    Role.insert_roles()
    //添加用户角色，默认为游客，只能发表评论
数据库创建完成。    

#### 3.nginx
nginx是一个高性能的web服务器，用来进行正向和反向代理。在nginx后部署一层gunicorn的话，静态请求通过nginx来处理，例如静态文件：*.css, *.html, *.png, *.js. 动态请求交给gunicorn处理。
##### 3.1 centOS系统上安装nginx
    yum -y install nginx
    
##### 3.2修改nginx配置文件
    
    find / -name nginx.conf
    
找到对应的nginx配置文件，进入内部修改到对应的项目位置。

    
##### 3.3 启动nginx

    nginx
或者

    service nginx start
##### 3.4 停止nginx

    service nginx stop
##### 3.5 重启nginx

    service nginx restart
##### 3.4 nginx配置文件检查

    nginx -t
##### 3.5 重新加载nginx配置
修改nginx配置文件后，需要nginx重新加载配置文件。    
    
    nginx -s reload
    
#### 4.gunicorn
Gunicorn (独角兽)是一个高效的Python WSGI Server,通常用它来运行 wsgi application(由我们自己编写遵循WSGI application的编写规范) 或者 wsgi framework(如Django,Paster).
WSGI就是这样的一个协议：它是一个Python程序和用户请求之间的接口。WSGI服务器的作用就是接受并分析用户的请求，调用相应的python对象完成对请求的处理，然后返回相应的结果。
简单来说gunicorn封装了HTTP的底层实现，我们通过gunicorn启动服务，用户请求与服务相应都经过gunicorn传输.

##### 5.1 安装gunicorn
首先进入到虚拟环境中，安装gunicorn

    pip install gunicorn
##### 5.2 后台启动gunicorn服务    

    nohup gunicorn -w 4 -b 127.0.0.1:8000 start:app &
其中start代表start.py模块，app代表flask的app。127.0.0.1：8000端口地址需要与nginx配置文件中相同。

至此配置完成。

##### 5.3 项目更改后的重新部署
需要重启gunicorn：首先找到gunicorn的进程号

    pstree -ap|grep gunicorn
![](https://upload-images.jianshu.io/upload_images/11146099-756a4db50ef6999f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
根据找到的主进程号，重启gunicorn：

    kill -HUP *****
    

    

    
