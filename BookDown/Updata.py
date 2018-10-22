import os
import shelve
class Updata:
    def __init__(self,Basepath,datapath,baseclass = '最新全本'):
        try:
            self.file = shelve.open(datapath, writeback = True)
            for filename, cl in self.file.items():
                s =Basepath+'\\'+baseclass+'\\'+filename
                d =Basepath+'\\'+cl+'\\'+filename
                if not os.path.exists(Basepath+'\\'+cl):
                    os.makedirs(Basepath+'\\'+cl)
                os.popen(f"copy \"{s}\"  \"{d}\"")
                os.popen(f"del \"{s}\"")
                del self.file[filename]
                print("归档：",s,"->",d)
        except Exception as e:
            print("初始化错误：",e)
            self.file.close()
    def log(self,filename,cl):
        self.file[filename] = cl;
    def __del__(self):
        self.file.close();