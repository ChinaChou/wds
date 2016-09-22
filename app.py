#coding:utf-8
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import define,options
from deploy import Deploy
import tornado.web
import hashlib,uuid
import pymysql
import os,time,threading


define('mysql_host',default='localhost',help='mysql-server address')
define('mysql_user',default='bsydeploy',help='database user')
define('mysql_password',default='T0AMc+pDzhb7y',help='database password')
define('mysql_db',default='bsyops',help='default database')
define('mysql_charset',default='utf8',help='mysql charset')
define('mysql_cursorclass',default=pymysql.cursors.DictCursor)
define('mysql_autocommit',default=True,help=('auto commit transaction or not'))
define('upload_dir',default='{}'.format(os.path.join(os.path.dirname(__file__),'static/downloads')),help='file upload directory')
define('ssh_user',default='gxzb',help='ssh and sftp login name')
define('ssh_pkey',default='/home/gxzb/.ssh/id_rsa',help='ssh private key file')

class MyApp(Application):
    def __init__(self):
        handlers = [
            (r'^/',MainHandler),
            (r'^/login',LoginHandler),
            (r'^/upload',UploadHandler),
            (r'^/logout',LogoutHandler),
            (r'/downloads/(.*)',DownloadHandler),
            (r'/userInfo',UserInfoHandler),
            (r'/modifyPass',ModifyPasswordHandler),
            (r'^/showid',ShowSessionHandler)
        ]
        settings = {
            'login_url':'/',
            'cookie_secret':'Uhj4WYtrSHu2nqQbCpQjApEZSnqB2SKs7TziCIdQR2bP28Luo1sbAQ',
            'template_path':os.path.join(os.path.dirname(__file__),'templates'),
            'static_path':os.path.join(os.path.dirname(__file__),'static'),
            'autoreload':True
        }
        super(MyApp, self).__init__(handlers,**settings)
        self.session = {}
        self.db = self.db_connect()

    def db_connect(self):
        try:
            conn = pymysql.connect(
                host=options.mysql_host,
                user=options.mysql_user,
                password=options.mysql_password,
                db=options.mysql_db,
                charset=options.mysql_charset,
                cursorclass=options.mysql_cursorclass,
                autocommit=options.mysql_autocommit
            )
        except Exception as e:
            print(str(e))
        else:
            return conn


class BaseHandler(RequestHandler):
    def get_current_user(self):
        session_id = self.get_secure_cookie('PYSESSIONID')
        if session_id:
            session_id = session_id.decode()
            if session_id in app.session:
                return app.session[session_id]
        else:
            return None

    @property
    def session_id(self):
        session_id = self.get_secure_cookie('PYSESSIONID')
        if session_id:
            return session_id.decode()
        else:
            return None

    @property
    def db(self):
        try:
            with self.application.db.cursor() as cur:
                cur.execute('select 1')
                ret = cur.fetchall()
        except Exception as e:
            return self.application.db_connect()
        else:
            return self.application.db

    @property
    def session(self):
        return self.application.session

    def execute_sql(self,conn,sql):
        with conn.cursor() as cur:
            cur.execute(sql)
            ret = cur.fetchall()
        return ret


class MainHandler(BaseHandler):
    def get(self):
        if self.session_id in self.session:
            self.redirect('/userInfo')
        else:
            self.render('index.html')


class LoginHandler(BaseHandler):
    def post(self):
        username = self.get_body_argument('username')
        password = self.get_body_argument('password')
        if self.session_id in self.session:
            self.redirect('/userInfo')
        else:
            if password:
                password = hashlib.md5(password.encode()).hexdigest()
            sql = '''select username from ops_user where username = "{0}" and password = "{1}"'''.format(username,password)
            result = self.execute_sql(self.db,sql)
            if result:
                session_id = hashlib.md5(uuid.uuid4().bytes).hexdigest()
                self.set_secure_cookie('PYSESSIONID',session_id,expires_days=1,httponly=True)
                self.session[session_id] = username
                self.redirect('/userInfo')
            else:
                self.redirect('/')


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session_id in self.session:
            self.session.pop(self.session_id)
            self.set_secure_cookie('PYSESSIONID','',expires_days=0)
        self.redirect('/')


class UserInfoHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        sql = "select UserName,FullName,Email,DepartmentName from ops_user where UserName='{}'".format(self.session[self.session_id])
        userInfo = self.execute_sql(self.db,sql)
        self.render('userInfo.html',user=self.session[self.session_id],userInfo=userInfo)


class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        env_sql = "select id,envname from ops_env order by id desc"
        project_sql = "select ProjectName from ops_project"
        deploy_env = self.execute_sql(self.db,env_sql)
        deploy_projects = self.execute_sql(self.db,project_sql)
        self.render('deploy.html',user=self.session[self.session_id],deploy_env=deploy_env,deploy_projects=deploy_projects)

    @tornado.web.asynchronous
    @tornado.web.authenticated
    def post(self):
        try:
            warInfo = self.request.files['warPackage'][0]
            warName = warInfo['filename']
            env = int(self.get_body_argument('env'))
            projectName = self.get_body_argument('projectName')
        except Exception as e:
            self.render('error.html',Error="请重新选择文件,{}".format(str(e)),user=self.session[self.session_id])
        else:
            year,month,day,hour,minute,second,*_ = time.localtime()
            if env == 2:
                current_war_dir = '{}/audit/{}/{}/{}'.format(options.upload_dir,year,month,day)
                deploy_sql = "select servicename,webapps,releasename,ip from ops_PreProd where servicename='{}'".format(projectName)
            elif env == 1:
                current_war_dir = '{}/{}/{}/{}'.format(options.upload_dir,year,month,day)
                deploy_sql = '''select t1.projectname,t2.servicename,t2.webapps,t2.releasename,t3.ip from ops_project t1,ops_service t2,ops_server t3 where t1.projectname='{}' and t2.serviceid = t1.serviceid and t3.groupid = t1.groupid;'''.format(projectName)
            if not os.path.isdir(current_war_dir):
                os.makedirs(current_war_dir)

            war_path = '{}/{}'.format(current_war_dir,warName)
            if os.path.isfile(war_path):
                os.rename(war_path,'{}.{}'.format(war_path,str(year)+str(month)+str(day)+'_'+str(hour)+str(minute)+str(second)))
            try:
                with open(war_path,'wb') as f:
                    f.write(warInfo['body'])
            except Exception as e:
                self.render('error.html',user=self.session[self.session_id],Error='上传文件失败，{}'.format(str(e)))
            else:
                if projectName in warName and warInfo['content_type'] == 'application/octet-stream':
                    result = self.execute_sql(self.db,deploy_sql)
                    if result:
                        tmp_remote_path = '/tmp/{0}'.format(warName)
                        deployer = Deploy(request=self,ssh_user=options.ssh_user,pkey=options.ssh_pkey,local_path=war_path,tmp_remote_path=tmp_remote_path,data_list=result)
                        task = threading.Thread(target=deployer.deploy)
                        task.start()
                    else:
                        self.render('error.html',Error='所选环境中没有对应服务！',user=self.session[self.session_id])
                else:
                    self.render('error.html',Error='你选择的包与要发布的服务不符，请重新选择！',user=self.session[self.session_id])


class ShowSessionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(self.session)


class DownloadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,*args):
        sub_path = args[0].rstrip().rstrip('/')
        pre_path = None
        if sub_path:
            pre_sub_path = sub_path.rsplit('/',1)
            if len(pre_sub_path) > 1 and pre_sub_path[1]:
                pre_path = pre_sub_path[0]
            content = os.walk('{}/{}'.format(options.upload_dir,sub_path))
        else:
            content = os.walk(options.upload_dir)
        self.render('download.html',content=next(content),pre_path=pre_path,sub_path=sub_path,user=self.session[self.session_id])


class ModifyPasswordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('modifyPassword.html',user=self.session[self.session_id])

    @tornado.web.authenticated
    def post(self):
        new_password = self.get_body_argument('password').encode()
        cipher_password = hashlib.md5(new_password).hexdigest()
        update_sql = "update ops_user set password='{}' where username='{}'".format(cipher_password,self.session[self.session_id])
        self.execute_sql(self.db,update_sql)
        self.redirect('/logout')


if __name__ == '__main__':
    app = MyApp()
    app.listen(address='0.0.0.0',port=8000)
    IOLoop.current().start()
