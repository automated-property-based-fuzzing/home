import time
import subprocess
class Executor(object):

    def __init__(self,device,app):
        
        self.app = app
        self.device = device
    
    def skip(self):
        try:
            if "org.wikipedia.alpha" in self.app.package_name and self.device.use(description="Navigate up").exists and (self.device.use(text="Create an account").exists or self.device.use(text="Wikipedia languages").exists):
                self.device.use(description="Navigate up").click()
                time.sleep(1)
            if "aard2" in self.app.package_name and self.device.use(resourceId="itkach.aard2:id/dictionaries_empty_btn_scan").exists:
                self.device.use(resourceId="itkach.aard2:id/dictionaries_empty_btn_scan").click()
                time.sleep(1)
                self.device.use(description="Show roots").click()
                time.sleep(1)
                self.device.use(resourceId="android:id/title", textContains="Download").click()
                time.sleep(1)
                self.device.use(resourceId="android:id/title", text="freedict-deu-eng-0.3.4.slob").click()
            if self.device.use(text="MORE").exists and "org.liberty" in self.app.package_name:
                self.device.use(text="MORE").click()
                time.sleep(1)
                if self.device.use(text="Card list").exists:
                    self.device.use(text="Card list").click()
                    time.sleep(1)
            if "fr.free.nrw.commons" in self.app.package_name and self.device.use(resourceId="fr.free.nrw.commons:id/skip_login").exists:
                self.device.use(resourceId="fr.free.nrw.commons:id/skip_login").click()
                time.sleep(1)
                self.device.use(text="YES").click()
                time.sleep(1)
        except Exception as ex:
            print(ex)

    def start_app_skip(self):
        try:
            if "amaze" in self.app.package_name:
                time.sleep(1)
                self.device.use(textContains="Allow").click()
            if "org.liberty" in self.app.package_name:
                time.sleep(1)
                while self.device.use(text="ALWAYS ALLOW").exists:
                    self.device.use(text="ALWAYS ALLOW").click()
                    time.sleep(1)
                if self.device.use(resourceId="android:id/button1").exists:
                    self.device.use(resourceId="android:id/button1").click()
                    time.sleep(1)
                if self.device.use(resourceId="org.liberty.android.fantastischmemo:id/icon").exists:
                    self.device.use(resourceId="org.liberty.android.fantastischmemo:id/icon", instance=1).click()
                    time.sleep(1)
                if self.device.use(resourceId="org.liberty.android.fantastischmemo:id/file_name", text="2.db").exists:
                    self.device.use(resourceId="org.liberty.android.fantastischmemo:id/file_name", text="2.db").click()
                    time.sleep(1)
                if self.device.use(text="Card list").exists:
                    self.device.use(text="Card list").click()
            if "org.wikipedia.alpha" in self.app.package_name:
                time.sleep(1)
                self.device.use(resourceId="org.wikipedia.alpha:id/fragment_onboarding_skip_button").click()
                time.sleep(1)
                self.device.use(resourceId="org.wikipedia.alpha:id/navigation_bar_item_small_label_view", text="Saved").click()
            elif "aard2" in self.app.package_name:
                time.sleep(1)
                self.device.use(resourceId="itkach.aard2:id/dictionaries_empty_btn_scan").click()
                time.sleep(1)
                self.device.use(description="Show roots").click()
                time.sleep(1)
                self.device.use(resourceId="android:id/title", textContains="Download").click()
                time.sleep(1)
                self.device.use(resourceId="android:id/title", text="freedict-deu-eng-0.3.4.slob").click()
            elif "simpletask" in self.app.package_name:
                time.sleep(1)
                self.device.use(resourceId="nl.mpcjanssen.simpletask:id/login").click()
                time.sleep(1)
                if "emulator" in self.device.device_serial:
                    self.device.use(resourceId="com.android.permissioncontroller:id/permission_allow_button").click()
                else:
                    self.device.use(resourceId="com.lbe.security.miui:id/permission_allow_foreground_only_button").click()
                time.sleep(1)
                self.device.use(resourceId="android:id/button1").click()
            elif "anki" in self.app.package_name:
                time.sleep(1)
                self.device.use(resourceId="com.ichi2.anki:id/get_started").click()
                time.sleep(1)
                self.device.use(resourceId="com.ichi2.anki:id/switch_widget").click()
                time.sleep(1)
                self.device.use(resourceId="com.lbe.security.miui:id/permission_allow_foreground_only_button").click()
                time.sleep(1)
                self.device.use(resourceId="com.ichi2.anki:id/continue_button").click()
            elif "markor" in self.app.package_name:
                time.sleep(1)
                self.device.use(resourceId="net.gsantner.markor:id/next").click()
                time.sleep(1)
                self.device.use(resourceId="net.gsantner.markor:id/next").click()
                time.sleep(1)
                self.device.use(resourceId="android:id/button1").click()
                time.sleep(1)
                self.device.use(resourceId="com.android.packageinstaller:id/permission_allow_button").click()
                time.sleep(1)
                self.device.use(resourceId="net.gsantner.markor:id/next").click()
                time.sleep(1)
                self.device.use(resourceId="net.gsantner.markor:id/next").click()
                time.sleep(1)
                self.device.use(resourceId="net.gsantner.markor:id/next").click()
                time.sleep(1)
                self.device.use(resourceId="net.gsantner.markor:id/done").click()
            time.sleep(1)
        except Exception as ex:
            print(ex)
        
    def execute_event(self,device,event,num):
        device.use.screen_on()
        try:
            print("------------------")
            if event.action == "click":
                print("click"+event.view.line+"\n")
                device.click(event.view)
            elif event.action == "longclick":
                print("longclick"+event.view.line+"\n")
                device.longclick(event.view)
            elif event.action == "edit":
                print("edit"+event.view.line+"\n")
                device.edit(event.view,event.text)
            elif event.action == "drag":
                print("drag"+event.text+"\n")
                device.drag(event.text)
            elif event.action == "back":
                print("back"+"\n")
                device.use.press("back")
            elif event.action == "home":
                device.use.press("home")
                print("home"+"\n") 
            elif event.action == "naturalscreen":
                print("naturalscreen"+"\n")
                device.use.set_orientation("n")
            elif event.action == "leftscreen":
                print("leftscreen"+"\n")
                device.use.set_orientation("l")
            elif event.action == "start":
                if event.data=="":
                    print("start"+"\n")
                    device.stop_app(self.app)
                    device.start_app(self.app)
                else:
                    subprocess.run(["adb","-s",device.device_serial,"shell","am","start","-n",event.data], stdout=subprocess.PIPE)
                time.sleep(5)
            elif event.action == "stop":
                print("stop")
                device.stop_app(self.app)
            elif event.action == "clear":
                print("clear")
                device.clear_app(self.app)
            elif event.action == "sleep":
                print("sleep")
                time.sleep(int(event.text))
            elif event.action == "scrollto":
                print("scrollto")
                device.scrollto(event.text)
            elif "scroll" in event.action:
                device.scroll(event.view,event.action)
            
            print(device.device_serial+":end execute\n")
            return True
        except Exception as ex:
            if num ==0:
                print(ex)
                return self.execute_event(device,event,1)
            else:
                print(ex)
                return False
   
    