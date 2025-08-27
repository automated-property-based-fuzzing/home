from threading import Timer
import time, os
from device import Device
from app import App
from record import Record
from checkdmf import CheckRecord
from fuzzing import Fuzzing
from generate import Generate
from synthesis import Synthesis

class NonCrashDetector(object):
    instance = None
    def __init__(self,device_serial,root_path,app_path,choice,policy_name,testcase_count,event_num,json_name,testcase_path,result_path,max_time,start_testcase,clear_and_start_flag,input_path,input_file_name,target_hash):
        
        NonCrashDetector.instance = self
        self.app_path = app_path
        self.root_path = root_path
        self.device_serial = device_serial
        self.timeout = 0
        self.choice = choice
        self.policy_name = policy_name
        self.testcase_count = testcase_count
        self.event_num = event_num
        self.json_name = json_name
        self.testcase_path = testcase_path
        self.result_path = result_path
        self.max_time = max_time
        self.start_testcase = start_testcase
        self.clear_and_start_flag = clear_and_start_flag
        self.input_path = os.path.join("output",json_name+"screen","instantiate","dmf")
        self.input_file_name = input_file_name
        self.target_hash = target_hash

    def start(self):
        self.timer = Timer(self.timeout, self.stop)
        self.timer.start()
        self.start_time = time.time()
        
        if self.choice == "1":
            self.app = App(self.app_path)
            self.fuzzing = Fuzzing(
            device_serial=self.device_serial,
            app_path=self.app_path,
            root_path=self.root_path,
            policy_name = self.policy_name,
            event_num = self.event_num,
            testcase_count = self.testcase_count,
            json_name = self.json_name,
            app = self.app,
            start_time=self.start_time,
            max_time = self.max_time,
            start_testcase = self.start_testcase,
            result_path=self.result_path)
            self.fuzzing.start()
        elif self.choice == "2":
            self.app = App(self.app_path)
            self.synthesis = Synthesis(
            device_serial=self.device_serial,
            policy_name = self.policy_name,
            event_num = self.event_num,
            json_name = self.json_name,
            max_time = self.max_time,
            root_path = self.root_path,
            start_time = self.start_time,
            app_path = self.app_path,
            testcase_count = self.testcase_count,
            app = self.app)
            testcase=self.start_testcase
            testcase=self.synthesis.explore_and_findDMF("all",testcase,[""])
            self.generate = Generate(
            device_serial=self.device_serial,
            app=self.app,
            clear_and_start_flag = self.clear_and_start_flag,
            json_name = self.json_name,
            root_path = self.root_path)
            items = os.listdir(self.input_path)
            f_exception = open(os.path.join(self.input_path, "exception.txt"),'w',encoding='utf-8')
            dirs = [item for item in items if os.path.isdir(os.path.join(self.input_path, item))]
            for dir in dirs:
                try:
                    self.generate.generate_dmf(os.path.join(self.input_path,dir)+"/",self.input_file_name)
                except Exception as ex:
                    print(ex)
                    f_exception.write(str(ex))
                    f_exception.flush()
        elif self.choice=="3":
            self.app = App(self.app_path)
            self.record = Record(
            root_path=self.root_path,
            device_serial=self.device_serial,
            app=self.app,
            json_name=self.json_name)
            self.record.start()
        elif self.choice=="4":
            self.app = App(self.app_path)
            self.checkRecord = CheckRecord(
            root_path=self.root_path,
            device_serial=self.device_serial,
            app=self.app,
            json_name=self.json_name)
            self.checkRecord.start()
        elif self.choice=="5":
            self.screenshot()
       

    def screenshot(self):
        self.device = Device(self.device_serial)
        self.device.connect()
        self.device.use.screen_on()
        self.device.use.screenshot(self.root_path+self.device_serial+".png")
        xml = self.device.use.dump_hierarchy()
        f = open(self.root_path+self.device_serial+".xml",'w',encoding='utf-8')
        f.write(xml)
        
    def stop(self):
        self.enabled = False
        # print(time.time()-self.start_time)