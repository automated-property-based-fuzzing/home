from policy import DMFPolicy
from device import Device
from view import View
import time,os
from util import Util
from app import App
from executor import Executor
import xml.etree.ElementTree as ET
from screen import Screen
from info import Info
import json
import shutil
from collections import deque
from datetime import datetime
class Synthesis(object):
    instance = None
    def __init__(self,device_serial,policy_name,event_num,json_name,max_time,root_path,start_time,app_path,testcase_count,app):
        Synthesis.instance = self
        self.device = Device(device_serial)
        self.policy_name = policy_name
        self.event_num = event_num
        self.device_serial = device_serial
        self.app = app
        self.policy =  self.get_policy()
        self.json_name = json_name
        self.max_time =max_time
        self.testcase_count = testcase_count
        self.root_path = root_path
        self.start_time = start_time
        self.util = Util(app_path,json_name)
        self.executor = Executor(self.device,self.app)
        self.keyview_list=[]
        self.record_data = []
    
    def get_policy(self):
        if self.policy_name=="random":
            print("Policy: Random")
            policy = DMFPolicy(self.device,self.app,60,50,40,30,10,2)
        else:
            print("No valid input policy specified. Using policy \"none\".")
            policy = None
        return policy
    
    def save_screen(self,path,event_count):
        # Screenshot
        self.device.use.screenshot(path+"/"+str(event_count)+".png")
        self.nowscreenshotpath = path+"/"+str(event_count)+".png"
        # Save xml information
        with open(path+"/"+str(event_count)+".xml", 'w', encoding='utf-8') as f:
            xml = self.device.use.dump_hierarchy()
            f.write(xml)
        # Update cache
        with open(path+"/"+str(event_count)+".xml", 'r', encoding='utf-8') as f:
            screen = Screen(f.readlines(), [])
            self.device.update_screen(screen)
        return xml

    def event_have_executed(self, event_action, event_view, visited_info):
        for info in visited_info:
            event=info.event
            # To be modified later, replace text matching with any attribute matching
            if event_action == event.action and (event_view=="" or event_view.lower() in event.view.text.lower() or event_view.lower() in event.view.description.lower() or event_view.lower() in event.view.resourceId.lower()):
                return info.event_index
        return -1
    
    def check_match(self,keyword,view):
        if view==None:
            return False
        if keyword in view.text.lower() or keyword in view.description.lower() or keyword in view.resourceId or keyword in view.className.lower():
            return True
        return False
    
    def check_find_dmf(self):
        if len(self.info_list)<1:
            return False
        dmf_type = ""
        dmf_hash=""
        dmf_length=11
        end_info = self.info_list[-1]
        visited_info = []
        visited_info.append(end_info)
        # Starting from the second last page, traverse backwards to find the start and end interface of a DMF
        for info in self.info_list[-2::-1]:
            start_info = None
            extra_object = set([x for x in end_info.childs if end_info.childs.count(x) > info.childs.count(x)])
            remove_object = set([x for x in info.childs if info.childs.count(x) > end_info.childs.count(x)])
            extra_view = None
            remove_view = None
            if end_info.hashstring == info.hashstring and end_info.childs_num==info.childs_num+1 and set(info.childs).issubset(set(end_info.childs)) and (self.event_have_executed("click","add",visited_info)!=-1 or self.event_have_executed("click","create",visited_info)!=-1 or self.event_have_executed("click","save",visited_info)!=-1 or self.event_have_executed("click","bookmark",visited_info)!=-1) and not self.check_match("search",end_info.event.view) and end_info.childs_num<7 and info.keyboard_flag == end_info.keyboard_flag:
                if next(iter(extra_object)) not in self.app.keywordlist:
                    flag = True
                    for visit in visited_info:
                        if self.check_match("search",visit.event.view):
                            flag =False
                        # Commented according to requirements
                        # if visit.event.action == "edit" and visit.event.text.lower() == next(iter(extra_object)):
                    if flag:
                        dmf_type = "add"
                        self.record_data.append(next(iter(extra_object)))
            elif end_info.event_index == info.event_index+1 and end_info.event.action == "click" and end_info.hashstring != info.hashstring and info.childs_num>0:
                for data in self.record_data:
                    if data in info.childs :
                        if "\""+data+"\"" in info.xml:
                            if "\""+data+"\"" in end_info.xml:
                                if data in end_info.event.view.text: 
                                    dmf_type = "read"
                                    remove_object = {data}
            elif end_info.hashstring == info.hashstring and (self.event_have_executed("click","delete",visited_info)!=-1 or self.event_have_executed("click","trash",visited_info)!=-1 or self.event_have_executed("click","unbookmark",visited_info)!=-1 or self.event_have_executed("click","hide",visited_info)!=-1 or self.event_have_executed("click","remove",visited_info)!=-1) and info.childs_num==end_info.childs_num+1 and set(end_info.childs).issubset(set(info.childs)) and not self.check_match("search",end_info.event.view) and end_info.childs_num<7 and info.keyboard_flag == end_info.keyboard_flag:
                if next(iter(remove_object)) not in self.app.keywordlist:
                    dmf_type = "delete"
            elif end_info.hashstring == info.hashstring and any(end_info.hashstring != visit.hashstring for visit in visited_info) and end_info.childs_num==info.childs_num and len(extra_object)==1 and len(remove_object)==1 and end_info.childs_num<7 and not self.check_match("search",end_info.event.view) and info.keyboard_flag == end_info.keyboard_flag:
                if next(iter(extra_object)) not in self.app.keywordlist and next(iter(remove_object)) not in self.app.keywordlist:
                    flag = True
                    for visit in visited_info:
                        if self.check_match("search",visit.event.view):
                            flag =False
                    for visit in visited_info:
                        if visit.event.action == "edit" and visit.event.text.lower() == next(iter(extra_object)) and flag:
                            dmf_type = "edit"
                            self.record_data.append(next(iter(extra_object)))
            elif end_info.event_index == info.event_index+2 and end_info.event.view!=None and end_info.event.view.resourceId=="com.google.android.inputmethod.latin:id/key_pos_ime_action" and "search" in end_info.xml.lower() and "search" in info.xml.lower() and self.check_match("search",info.event.view) and info.event.view!=None and info.event.view.package==self.app.package_name  :
                for visit in visited_info:
                    for child in end_info.childs:
                        if visit.event.text.lower() in child.lower() and visit.event.action == "edit" and self.check_match("search",visit.event.view):
                            dmf_type = "search"
                            remove_object = {visit.event.text}
            elif end_info.event_index == info.event_index+1 and end_info.event.view!=None and "search" in end_info.xml.lower() and "search" in info.xml.lower() and self.check_match("search",info.event.view) and info.event.view!=None and info.event.view.package==self.app.package_name  :
                for child in end_info.childs:
                    if child!=None and info.event.action != "edit" and end_info.event.action == "edit" and end_info.event.text.lower() in child.lower() and self.check_match("search",end_info.event.view):
                        dmf_type = "search"
                        remove_object = {end_info.event.text}
            if dmf_type!="":
                start_info = info
                break
            visited_info.append(info)

        if dmf_type!="":
            dmf_hash=start_info.hashstring[:5]
            dmf_length = end_info.event_index-start_info.event_index
            # Record the event sequence for reproduction
            f_end = open(self.output_path+str(self.now_testcase)+"/"+str(end_info.event_index)+".xml",'r',encoding='utf-8')
            f_start = open(self.output_path+str(self.now_testcase)+"/"+str(start_info.event_index)+".xml",'r',encoding='utf-8')
            try:
                if len(extra_object)!=0:
                    extra_view = self.findviewbytext(f_end.readlines(),next(iter(extra_object)),None)
                elif len(end_info.childs)!=0 and dmf_type=="search":
                    extra_view = self.findviewbytext(f_end.readlines(),next(iter(end_info.childs)),None)
                if len(remove_object)!=0:
                    remove_view = self.findviewbytext(f_start.readlines(),next(iter(remove_object)),None)
                    self.record_data.remove(next(iter(remove_object)))
            except Exception as ex:
                print(ex)
            repro_events = []
            for info in self.info_list:
                # Record all events
                repro_events.append(info.eventline+"\n")
                # Add special marker events
                if info.event_index == start_info.event_index and dmf_type!="search":
                    repro_events.append("start_info::"+start_info.hashstring+"::"+str(start_info.childs_num)+"::\n")
                elif info.event_index == end_info.event_index and dmf_type!="search":
                    repro_events.append("end_info::"+end_info.hashstring+"::"+str(end_info.childs_num)+"::\n")
                    if extra_view!=None:
                        repro_events.append("fail::not in::::"+extra_view.line)
                    if remove_view!=None:
                        repro_events.append("fail::in::::"+remove_view.line)

            # Generate the file recording DMF
            dirpath=self.output_path+"dmf/"+dmf_type+"_"+start_info.hashstring[:5]
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            else:
                with open(dirpath+"/all_trace.txt", 'r', encoding='utf-8') as f_exist: 
                    lines = f_exist.readlines()
                    item = lines[1].split(":")
                    events = item[2].split("->")
                    event_len = int(events[1])-int(events[0])
                    if event_len - 5 < end_info.event_index-start_info.event_index:
                        print("find long:"+dmf_type+":"+str(start_info.event_index)+"->"+str(end_info.event_index))
                        return "",dmf_length,dmf_hash
                        
            self.f_dmf = open(dirpath+"/all_trace.txt",'w',encoding='utf-8')
            print(dmf_type+":"+str(start_info.event_index)+"->"+str(end_info.event_index))
            if dmf_type == "search":
                self.f_dmf.write(dmf_type+"::"+start_info.hashstring[:5]+"::"+next(iter(extra_object),"").replace("\n"," ")+"::"+next(iter(remove_object),"").replace("\n"," ")+"\nTest case:"+str(self.now_testcase)+":"+str(start_info.event_index-1)+"->"+str(end_info.event_index)+"\nstart:"+str(start_info.json)+"\nend:"+str(end_info.json)+"\n")
            else:
                self.f_dmf.write(dmf_type+"::"+start_info.hashstring[:5]+"::"+next(iter(extra_object),"").replace("\n"," ")+"::"+next(iter(remove_object),"").replace("\n"," ")+"\nTest case:"+str(self.now_testcase)+":"+str(start_info.event_index)+"->"+str(end_info.event_index)+"\nstart:"+str(start_info.json)+"\nend:"+str(end_info.json)+"\n")
            shutil.copy(self.output_path+str(self.now_testcase)+"/"+str(start_info.event_index)+".png",dirpath+"/start_info.png")
            shutil.copy(self.output_path+str(self.now_testcase)+"/"+str(end_info.event_index)+".png",dirpath+"/end_info.png")
            self.f_dmf.writelines(repro_events)
            self.f_dmf.flush()
            self.f_dmf_all.write("Test case:"+str(self.now_testcase)+":"+str(start_info.event_index)+"->"+str(end_info.event_index)+"::"+dmf_type+"::"+start_info.hashstring[:5]+"::"+str(time.time()-self.start_time)+"::"+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"\n")
            self.f_dmf_all.flush()

        return dmf_type,dmf_length,dmf_hash
    
    
            


    def explore_and_findDMF(self,target_dmf,start_testcase,target_hash):
        
        # Initialization
        self.device.connect()
        if self.app.package_name!="com.ss.android.lark":
            self.device.install_app(self.app.app_path)
        
        # Generate output folder
        self.output_path = self.root_path+"/"+self.json_name+"screen/instantiate/"
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            os.makedirs(self.output_path+"dmf")
        if os.path.exists(self.output_path+"dmf/dmf_info.txt"):
            self.f_dmf_all = open(self.output_path+"dmf/dmf_info.txt",'a',encoding='utf-8')
        else:
            self.f_dmf_all = open(self.output_path+"dmf/dmf_info.txt",'w',encoding='utf-8')
        self.f_dmf_all.write("Start time:"+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"\n")
        self.now_testcase =start_testcase
        # during_time=time.time() - self.start_time

        
        # Initialize crash log
        if not os.path.exists(self.output_path+"dmf/logcat.txt"):
            self.f_logcat = open(self.output_path+"dmf/logcat.txt",'w',encoding='utf-8')
            self.f_logcat.close()
        self.device.log_crash(self.output_path+"dmf/logcat.txt")
        self.f_logcat = open(self.output_path+"dmf/logcat.txt",'r',encoding='utf-8')
        logcat_lines=self.f_logcat.readlines()
        self.f_logcat.close()
        self.device.update_logcat(logcat_lines)

        # Continue searching for dmf while test cases have not reached the limit
        while self.now_testcase<self.testcase_count+start_testcase and self.now_testcase<100 :
            # Create a folder to store this test case
            if not os.path.exists(self.output_path+str(self.now_testcase)):
                os.makedirs(self.output_path+str(self.now_testcase))
            # Record all executed information
            self.collected_data = []
            self.info_list = []
            self.last_events = deque(maxlen=5)
            # Record test information for this test case
            self.f_event = open(self.output_path+str(self.now_testcase)+"/info_record.json",'w',encoding='utf-8')
            # Initialization of this test case
            if self.app.package_name!="com.ss.android.lark":
                self.device.clear_app(self.app)
            self.device.start_app(self.app)
            self.executor.start_app_skip()
            self.now_event = 0
            self.save_screen(self.output_path+str(self.now_testcase),self.now_event)

            # Each test case has at most event_num events
            while self.now_event<self.event_num:
                # Select an event, mark its target widget on the screenshot, and execute it
                self.policy.set_info(self.record_data,self.last_events)
                event = self.policy.choice_event(self.device,self.now_event,False,target_dmf,0)
                print(str(self.now_event))
                self.util.draw_event(event,self.nowscreenshotpath)
                execute_result=self.executor.execute_event(self.device,event,0)
                # if execute_result == True:
                    
                # After executing the event, wait if still loading
                time.sleep(1)
                waittime = 0
                while waittime<10 and (self.device.use(className="android.widget.ProgressBar",packageName=self.app.package_name).exists and self.app.package_name!="com.ss.android.lark" or (self.device.use(text="...").exists and self.app.package_name=="io.github.hidroh.materialistic")):
                    time.sleep(1)
                    waittime=waittime+1
                
                # Update state information, take screenshot
                self.last_events.append(event.line)
                self.now_event=self.now_event+1
                self.executor.skip()
                xml=self.save_screen(self.output_path+str(self.now_testcase),self.now_event)
                info =Info(self.now_event,event,xml,self.app)
                info.get_info(self.app)

                # Record: 1. event index, 2. screen hash without list, 3. number of items in the list, 4. which data are in the list, 5. possible dmf of current event, 6. event information, 7. xml reached after execution
                json_data={"num": self.now_event,"hash": info.hashstring, "childs_num": info.childs_num, "childs": info.childs,"dmf":info.matching_strings,"eventline":info.eventline,"xml":info.simplified_xml}
                info.add_json_info(json.dumps(json_data))
                self.info_list.append(info)
                self.f_event.write(json.dumps(json_data) + ',\n')
                self.f_event.flush()
                self.collected_data.append(json_data)

                # Check whether a dmf has been executed
                check_result,num,hash = self.check_find_dmf()
                # Break if the target DMF is found
                if check_result==target_dmf and num<=11 and (hash in target_hash or "" in target_hash):
                    return self.now_testcase+1
                
                # Record crash
                f = open(self.output_path+"dmf/logcat.txt")
                logcat_lines=f.readlines()
                f.close()
                self.device.update_logcat(logcat_lines)
                if self.device.last_logcat!=self.device.now_logcat:
                    for line in self.device.now_logcat:
                        if line not in self.device.last_logcat:
                            self.f_event.write(line)
                            self.f_event.flush()
            self.now_testcase = self.now_testcase+1
        return self.now_testcase

    def findviewinstance(self,now_layout, resourceId, className, text):
        view=None
        instance = 0
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            if resourceId!=None and resourceId == view.resourceId:
                if view.text == text:
                    return instance
                else:
                    instance = instance+1
            elif className!=None and className == view.className:
                if view.text == text:
                    return instance
                else:
                    instance = instance+1
            else:
                continue
        return None

    def findviewbytext(self,now_layout, text, not_view):
        
        view=None
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            if text != view.text :
                continue
            else:
                if not_view!=None:
                    if not_view.resourceId == view.resourceId and not_view.className == view.className:
                        break
                return view
        return None
    


    
   