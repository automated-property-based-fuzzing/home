class App(object):

    def __init__(self, app_path):
        assert app_path is not None
        self.app_path = app_path
        

        self.keywordlist = self.decompile(app_path,"apk_files")

        from androguard.core.apk import APK
        self.apk = APK(self.app_path)
        self.package_name = self.apk.get_package()
        self.main_activity = self.apk.get_main_activity()
        self.permissions = self.apk.get_permissions()
        self.activities = self.apk.get_activities()
        print("Main activity:"+self.main_activity)
        print("Package name:"+self.package_name)


    def decompile(self,app_path,out_path):
        import os
        #use apktool
        cmd = 'apktool d -f '+app_path+' -o '+out_path
        print('--------Start Working with apktool--------')
        os.system(cmd)
        print('-----------------------------\nwork all done,output file in:\n'
            +out_path+'\n-----------------------------\n')
        # os.system('pause')
        keywordlist = []
        try:
            f = open(out_path+"/res/values/"+'strings.xml','r',encoding='utf-8')
            lines=f.readlines()
            f.close()
            for line in lines:
                num1=line.find("\">")
                num2=line.find("</")
                string=line[num1+2:num2]
                keywordlist.append(string)
        except Exception as ex:
            print(ex)
        return keywordlist

