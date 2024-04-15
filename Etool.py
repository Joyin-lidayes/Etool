# -*- coding: utf-8 -*-

import re
import sys
import time
import yaml
import platform
import threading
import subprocess
from func_timeout import func_set_timeout

class Etool:
    def __init__(self,cmdPath = "./config/commend.yml", configPath = "./config/config.yml") -> None:
        self.lock = threading.Lock()
        self.ymlcmd = {}
        self.ymlconfig = {}
        self.os_name = platform.system()
        self.logname = time.strftime("%Y_%m_%d_%H_%M_%S",time.gmtime())
        self.readYML(cmdPath,configPath)

        self.action = ""
        self.nonkeywords = ["Etool help","Etool ERROR"]

    def readYML(self,cmdPath,configPath):
        with open(configPath) as fp:
            self.ymlconfig = yaml.load(fp, Loader=yaml.FullLoader)
        with open(cmdPath) as fp:
            self.ymlcmd = yaml.load(fp, Loader=yaml.FullLoader)

    def savelog(self,data):
        print(data)
        if(self.ymlconfig["savelog"]):
            if(self.ymlconfig["logname"] != "default"):
                self.logname = self.ymlconfig["logname"]
            with open(f"{self.logname}.log","a",encoding="utf-8",errors="ignore") as fp:
                fp.write(data)

    def help(self):
        cmdlist = list(self.ymlcmd.keys())
        print("*" * 15 + " Etool " + "*" * 15 + "\n")
        for item in cmdlist:
            describe = self.ymlcmd[item]["describe"]

            print(f"{cmdlist.index(item) + 1}. {item}\n    {describe}\n")

        print("*" * 15 + f" {len(cmdlist)} cmd(s) " + "*" * 15 + "\n")

    def getYAMLWord(self,para):
        try:
            ymlkeyslist = list(self.ymlcmd[self.action].keys())
        except:
            return "Etool ERROR: The instruction was not found!"

        if(self.os_name in ymlkeyslist):

            os_name = self.os_name
            os_name_para_is_none = self.ymlcmd[self.action][os_name]
            os_name_key = list(self.ymlcmd[self.action].keys())
            os_name_key.remove("describe")
            while True:
                if(os_name_para_is_none == None):
                    os_name_key.remove(os_name)
                    try:
                        os_name = os_name_key[0]
                    except:
                        return "Etool ERROR: not find command in YAML!"
                    os_name_para_is_none = self.ymlcmd[self.action][os_name]
                else:
                    break

            return self.ymlcmd[self.action][os_name][para]
        else:
            return "Etool ERROR: The platform does not support this command!"

    def isValid(self,data):
        if(any([item in data for item in self.nonkeywords])):
            raise data
        return True

    def exec(self,action,argv):
        self.action = action
        if(self.action == "help"):
            self.help()
            return "Etool help"

        cmdstrorlist = self.getYAMLWord("cmd")

        cmd = ""

        if(isinstance(cmdstrorlist, str)):
            cmd = cmdstrorlist

        elif(isinstance(cmdstrorlist, list)):
            count = 0
            for arg in cmdstrorlist:
                if("$" in arg):
                    try:
                        cmdstrorlist[cmdstrorlist.index(arg)] = argv[count]
                        count += 1
                    except:
                        return "Etool ERROR: Insufficient parameters"

            cmd = " ".join(cmdstrorlist)

        else:
            return "Etool ERROR: Tool not support this command!"

        return cmd

    def send(self,cmd,TX = None):
        self.isValid(cmd)
        timeout_in = self.getYAMLWord("timeout")
        if(timeout_in == None):
            timeout_in = 99999

        cmdprocess = None
        if(TX == None):
            if(cmd.split(" ")[0].endswith(".py")):
                cmdsend = f"python {cmd}"
            else:
                cmdsend = f"{cmd}"

            @func_set_timeout(timeout_in)
            def timeoutfunc():
                nonlocal cmdprocess
                cmdprocess = subprocess.Popen(cmdsend,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                time.sleep(0.1)
                cmdout, cmderr = cmdprocess.communicate()
                return cmdout.decode() + cmderr.decode()
            try:
                return timeoutfunc()
            except:
                cmdprocess.kill()
                return f"Etool timeout {self.action} {timeout_in}(s)"
        else:
            @func_set_timeout(timeout_in)
            def timeoutfunc():
                return TX(cmd)
            try:
                return timeoutfunc()
            except:
                return f"Etool timeout {self.action} {timeout_in}(s)"

    def result(self,execRes):
        self.savelog(execRes)
        self.isValid(execRes)

        threshold = self.getYAMLWord("threshold")
        if(not threshold):
            return True

        if(isinstance(threshold, str)):
            try:
                ctype, cthreshold, _ = tuple(threshold.split("`"))
                if(ctype == "re"):
                    result = re.findall(cthreshold,execRes)
                    if(result):
                        return True
                    else:
                        return False
                elif(ctype == "py"):
                    result = False
                    globals_dict = {'result': result,'data': execRes}
                    exec(cthreshold,globals_dict)
                    if(globals_dict["result"]):
                        return True
                    else:
                        return False
                else:
                    return "Etool ERROR: Unexpected threshold parameters!"
            except:
                if(threshold in execRes):
                    return True
                else:
                    return False

        elif(isinstance(threshold, list)):
            if((len(threshold) != 2) or (threshold[0] > threshold[1])):
                return "Etool ERROR: Unexpected threshold parameters!"
            if(threshold[0] < execRes < threshold[1]):
                return True
            else:
                return False
        else:
            return "Etool ERROR: Tool not support this threshold!"

if __name__ == "__main__":
    st = Etool()
    print(st.result(st.send(st.exec(sys.argv[1],tuple(sys.argv[2:len(sys.argv)])))))