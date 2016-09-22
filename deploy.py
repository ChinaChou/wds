import paramiko
import time

# data_list = [
#     {"releaseName": "bsy-pop-web", "ip": "192.168.2.158", "webApps": "/usr/local/pop/webapps", "serviceName": "pop"},
#     {"releaseName": "bsy-pop-web", "ip": "192.168.2.159", "webApps": "/usr/local/pop/webapps", "serviceName": "pop"},
#     {"releaseName": "bsy-pop-web", "ip": "192.168.2.160", "webApps": "/usr/local/pop/webapps", "serviceName": "pop"}
# ]


class Deploy():
    def __init__(self,request,ssh_user,pkey,local_path,tmp_remote_path,data_list):
        self._local_path = local_path
        self._tmp_remote_path = tmp_remote_path
        self._data_list = data_list
        self._ssh_user = ssh_user
        self._ssh_pkey = paramiko.RSAKey.from_private_key_file(pkey)
        self.request = request
        self._ssh = None
        self._sftp = None
        self._ssh_done = {}
        self._sftp_done = {}
        self._tunnels = {}
        self._second_time = False

    def _gen_ssh_client(self,ip):
        if ip in self._ssh_done:
            self._second_time = True
            return self._ssh_done[ip]
        else:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip,port=22,username=self._ssh_user,pkey=self._ssh_pkey,timeout=5)
            except Exception as e:
                print('SSH连接出错：'+str(e))
                self.request.finish('SSH connect timeout')
                return None
            else:
                return ssh


    def _gen_sftp_client(self,ip):
        if ip in self._sftp_done:
            return self._sftp_done[ip]
        else:
            try:
                tunnel = paramiko.Transport((ip,22))
                tunnel.connect(username=self._ssh_user,pkey=self._ssh_pkey)
                self._tunnels[ip] = tunnel
                sftp = paramiko.SFTPClient.from_transport(tunnel)
            except Exception as e:
                print('SFTP连接出错：'+str(e))
                self.request.finish('SFTP connect timeout')
                return None
            else:
                return sftp

    def _exec_cmd(self,request,cmd,ip):
        stdin,stdout,stderr = self._ssh.exec_command(cmd)
        error_msg = stderr.read()
        if error_msg:
            request.write("<p style='color:red'>{} Execute {} on {} failed,Error:{}</p>".format(time.asctime(),cmd,ip,error_msg))
            request.flush()
            return False
        else:
            return True

    def deploy(self):
        for s in self._data_list:
            ip,service_name,release_name,web_apps= s['ip'],s['servicename'],s['releasename'],s['webapps']
            self._ssh = self._gen_ssh_client(ip)

            self._sftp = self._gen_sftp_client(ip)
            stop_cmd = 'sudo service {0} stop'.format(service_name)
            start_cmd = 'sudo service {0} start'.format(service_name)
            rm_cmd = 'sudo rm -rf {0}/{1}*'.format(web_apps,release_name)
            cp_cmd = 'sudo cp {0} {1}'.format(self._tmp_remote_path,web_apps)

            if self._ssh and self._sftp:
                self.request.write("<p>{0} Stop {1} service on {2}</p>".format(time.asctime(),service_name,ip))
                self.request.flush()
                self._ssh.exec_command(stop_cmd)

                self.request.write("<p>{0} Delete related files  on {1}</p>".format(time.asctime(), ip))
                self.request.flush()
                ret = self._exec_cmd(self.request,rm_cmd,ip)
                if not ret:
                    break

                if self._second_time:
                    self.request.write("<p>{0} Since we will deploy {1}.war on the same server,so we just use {2} directly</p>".format(time.asctime(),release_name,self._tmp_remote_path))
                    self.request.flush()
                    self._second_time = False
                else:
                    self.request.write("<p>{0} Upload {1}.war to {2}</p>".format(time.asctime(), release_name, ip))
                    self.request.flush()
                    self._sftp.put(self._local_path,self._tmp_remote_path)

                self.request.write("<p>{0} Copy {1} to {2}'s {3}".format(time.asctime(),self._tmp_remote_path,ip,web_apps))
                self.request.flush()
                # self._ssh.exec_command(cp_cmd)
                ret = self._exec_cmd(self.request,cp_cmd,ip)
                if not ret:
                    break
                self.request.write("<p>{0} Sleep 12 seconds to wait {1} to stop </p>".format(time.asctime(),service_name))
                self.request.flush()
                time.sleep(12)
                self.request.write("<p>{0} Start {1} on {2}</p>".format(time.asctime(), service_name, ip))
                self.request.flush()
                # self._ssh.exec_command(start_cmd)
                ret = self._exec_cmd(self.request,start_cmd,ip)
                if not ret:
                    break

                self._ssh_done[ip] = self._ssh
                self._sftp_done[ip] = self._sftp

                self.request.write("{0}".format('-'*60))
                self.request.flush()
            else:
                self.request.write('SSH或者SFTP连接超时')
                self.request.flush()
                break

        self.request.write("<p><a href='/' style='color:red;text_decoration:none'>返回</a></p>")
        self.request.flush()

        'close ssh and sftp connection'
        for item in self._ssh_done:
            self._ssh_done[item].close()

        for item in self._sftp_done:
            self._sftp_done[item].close()

        for item in self._tunnels:
            self._tunnels[item].close()

        self._ssh = None
        self._sftp = None
        self.request.finish('All Done!')
