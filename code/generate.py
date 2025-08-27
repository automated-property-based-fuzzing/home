from device import Device
from view import View
from event import Event
from executor import Executor
import time,shutil,os
from util import Util
from info import Info

class Generate(object):
    instance = None
    def __init__(self,device_serial,app,clear_and_start_flag,json_name,root_path):
        Generate.instance = self
        self.device = Device(device_serial)
        self.app =app
        self.clear_and_start_flag = clear_and_start_flag
        self.executor = Executor(self.device,self.app)
        self.util = Util(self.app.app_path,json_name)
        self.root_path = root_path
        self.json_name = json_name

        #Connect device and initialize
        self.device.connect()
        
    def generate_dmf(self,input_path,input_file_name):
        f_event = open(input_path+"/"+input_file_name,'r',encoding='utf-8')
        lines=f_event.readlines()
        f_event.close()
        info_line = lines.pop(0)
        testcase_line = lines.pop(0)
        start_line = lines.pop(0)
        end_line = lines.pop(0)
        info=info_line.split("::")
        # start_dict = json.loads(start_line.split('start:')[1])
        # end_dict = json.loads(end_line.split('end:')[1])
        self.trypairs = []
        self.try_num =0
        self.init_path = os.path.join(input_path,str(self.try_num))
        self.shortest_trace_path = ""
        
        f_final = open(os.path.join(input_path,"short_trace.txt"),'w',encoding='utf-8')
        flag = self.generate_force(testcase_line,input_path,f_final,lines)
        if not flag:
            return
        add_name = info[2]
        delete_name = info[3]
        self.shortest_trace_path = os.path.join(input_path,"-1")
        events =self.parse_events(input_path,"short_trace.txt",add_name,delete_name)
        self.info_to_dmf(input_path,info,events)

    def generate_force(self,line,input_path,f,lines):
        item = line.split(":")
        testcase = item[1]
        events = item[2].split("->")
        start_event_num = events[0]
        end_event_num = events[1]
        if int(end_event_num)-int(start_event_num)>11:
            return False
        j=0
        i=int(start_event_num)
        if not os.path.exists(os.path.join(input_path,str(-1))):
            os.makedirs(os.path.join(input_path,str(-1)))
        while i<int(end_event_num)+1:
            src = os.path.join(self.root_path+self.json_name+"screen/instantiate/",testcase,str(i)+".xml")
            dst = os.path.join(input_path,str(-1),str(j)+".xml")
            shutil.copy(src, dst)
            src = os.path.join(self.root_path+self.json_name+"screen/instantiate/",testcase,str(i)+".png")
            dst = os.path.join(input_path,str(-1),str(j)+".png")
            shutil.copy(src, dst)
            print()
            i=i+1
            j=j+1
        for line in lines:
            items= line.split("::")
            if items[0].isdigit() and int(items[0])>int(start_event_num) and int(items[0])<=int(end_event_num):
                f.write(line)
                f.flush()
        return True

    def reduce_trace(self,faillines,f_reduce,start_dict,end_dict,input_path):
        newlines=faillines
        init_len = len(faillines)
        while True:
            if not os.path.exists(os.path.join(input_path,str(self.try_num))):
                os.makedirs(os.path.join(input_path,str(self.try_num)))
            eventslist=self.lines_to_events(newlines)
            replayresult=self.replay(eventslist,f_reduce,os.path.join(input_path,str(self.try_num)+"/"))
            if replayresult==True:
                faillines = newlines
            elif init_len==len(newlines):
                return False
            newlines = self.greedy_delete_events(faillines,f_reduce,0,start_dict['num'])
            if faillines == newlines:
                newlines = self.greedy_delete_events(faillines,f_reduce,start_dict['num'],end_dict['num'])
                if faillines==newlines:
                    return faillines
        
    def greedy_delete_events(self,lines,f_reduce,low_bound,high_bound):
        findflag = False
        indexlist = []
        for line in lines:
            items = line.split("::")
            if items[0].isdigit():
                indexlist.append(int(items[0]))
        lines.reverse()
        for line in lines:
            items = line.split("::")
            if items[1].startswith("start") and (0,int(items[0])+1) not in self.trypairs:
                trypair = (0,int(items[0])+1)
                self.trypairs.append(trypair)
                self.try_num=self.try_num+1
                f_reduce.write("try:"+str(self.try_num)+",trypair:0,"+str(int(items[0])+1)+"\n")
                f_reduce.flush()
                newlines = []
                for line in lines:
                    items = line.split("::")
                    index = items[0]
                    if not index.isdigit() or int(index)>=trypair[1]:
                        newlines.append(line)
                newlines.reverse()
                lines.reverse()
                return newlines
        for line in lines:
            items = line.split("::")
            if items[0].isdigit() and len(items)>2:
                view=View(items[3],[])
                for index in indexlist:
                    trypair = (index,int(items[0]))
                    if int(items[0])-1>index and trypair not in self.trypairs and int(items[0])<=high_bound and index>=low_bound:
                        f_xml = open(self.init_path+"/"+str(index-1)+".xml",'r',encoding='utf-8')
                        xmllines=f_xml.readlines()
                        # if items[1]=="edit" and view.resourceId!="":#特殊
                        #     view.text=""
                        if self.findviewinlayout(xmllines,view) == True:
                            self.trypairs.append(trypair)
                            self.try_num=self.try_num+1
                            f_reduce.write("try:"+str(self.try_num)+",trypair:"+str(index)+","+items[0]+"\n")
                            f_reduce.flush()
                            findflag=True
                            break
                if findflag == True:
                    newlines = []
                    for line in lines:
                        items = line.split("::")
                        index = items[0]
                        if not index.isdigit() or int(index)<trypair[0] or int(index)>=trypair[1]:
                            newlines.append(line)
                    newlines.reverse()
                    lines.reverse()
                    return newlines
        lines.reverse()
        return lines

    def delete_events(self,lines):
        findflag=False
        indexlist = []
        indexlist.append(0)
        for line in lines:
            items = line.split("::")
            if items[0].isdigit() and len(items)>2:
                view=View(items[3],[])
                print(items[0])
                print(view.line)
                indexlist.append(int(items[0]))
                startnum = 0
                while startnum<int(items[0])-1:
                    trypair = (startnum,int(items[0]))
                    if trypair in self.trypairs or startnum not in indexlist:
                        startnum = startnum+1
                        continue
                    f_xml = open(self.init_path+"/"+str(startnum)+".xml",'r',encoding='utf-8')
                    xmllines=f_xml.readlines()
                    findresult = self.findviewinlayout(xmllines,view)
                    if findresult == True:
                        # result=self.util.compare_images(self.init_path+"/"+str(startnum)+".png",self.init_path+"/"+items[0]+".png")
                        self.trypairs.append(trypair)
                        findflag=True
                        break
                    startnum= startnum+1
            if findflag == True:
                newlines = []
                for line in lines:
                    items = line.split("::")
                    index = items[0]
                    if not index.isdigit() or int(index)<=trypair[0] or int(index)>=trypair[1]:
                        newlines.append(line)
                return newlines
        return lines

    def findviewinlayout(self, now_layout, eventview):
        view=None
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            if eventview.className!="" and eventview.className != view.className:
                continue
            elif eventview.description!="" and eventview.description != view.description:
                continue
            elif eventview.resourceId!="" and eventview.resourceId != view.resourceId:
                continue
            elif eventview.text!="" and eventview.text != view.text:
                continue
            elif view.package != self.app.package_name:
                continue
            return True
        return False

    def lines_to_events(self,lines):   
        eventslist = []
        for line in lines:
            if "_info::" in line:
                items = line.split("::")
                flag_event = Event(None, items[0], self.device, items[2])
                flag_event.set_text(items[1].strip())
                eventslist.append(flag_event)
            elif "fail::" in line or "mid::" in line:
                enditems = line.split("::")
                check_event = Event(None, enditems[1], self.device, 0)
                check_event.set_text(enditems[3].strip())
                check_event.set_line(line)
                eventslist.append(check_event)
            elif "::" in line :
                items = line.split("::")
                # if int(items[0])>=self.start_testcase:
                if len(items)>2:
                    view=View(items[3],[])
                    view.xpath = items[4].strip()
                    execute_event = Event(view, items[1], self.device, 0)
                    if items[1]=="edit":
                        execute_event.set_text(items[2])
                else:
                    execute_event = Event(None, items[1].strip(), self.device, 0)
                execute_event.set_line(line)
                eventslist.append(execute_event)
        return eventslist

    def replay(self,eventslist,f,path): 
        start_info = None
        if self.clear_and_start_flag == "True":
            if self.app.package_name!="com.ss.android.lark":
                self.device.install_app(self.app.app_path)
            self.device.use.set_orientation("n")
            self.device.clear_app(self.app)
            self.device.start_app(self.app)
            time.sleep(1)
        self.device.use.screen_on()
        event_num =0
        self.device.use.screenshot(path+str(event_num)+".png")
        xml = self.device.use.dump_hierarchy()
        f_xml = open(path+str(event_num)+".xml",'w',encoding='utf-8')
        f_xml.write(xml)
        f_xml = open(path+str(event_num)+".xml",'r',encoding='utf-8')
        xmllines=f_xml.readlines()
        for event in eventslist:
            print(str(event_num))
            if "start_info" in event.action:
                start_info = Info(event_num,event,xml,self.app.keywordlist)
                start_info.get_info(self.app)
            elif "end_info" in event.action:
                end_info = Info(event_num,event,xml,self.app.keywordlist)
                end_info.get_info(self.app)
                if start_info!=None:
                    hash_condition= start_info.event.text == end_info.event.text and start_info.hashstring!=end_info.hashstring
                    childs_condition = int(end_info.event.event_count) - int(start_info.event.event_count) != end_info.childs_num - start_info.childs_num
                else:
                    hash_condition = end_info.event.text != end_info.hashstring
                    childs_condition = end_info.childs_num<1
                if hash_condition or childs_condition:
                    print(str(event_num)+"::repro fail::"+event.line+"\n")
                    f.write(str(event_num)+"::repro fail::"+event.line+"\n")
                    f.flush()
                    return False
                else:
                    print(str(event_num)+"::repro success::"+event.line+"\n")
                    f.write(str(event_num)+"::repro success::"+event.line+"\n")
                    f.flush()
            elif event.action == "in" or event.action == "not in":
                eventview = View(event.text,[])
                if (self.findviewinlayout(xmllines,eventview) and event.action == "in") or (not self.findviewinlayout(xmllines,eventview) and event.action == "not in"):
                    print(str(event_num)+"::repro fail::"+event.line+"\n")
                    f.write(str(event_num)+"::repro fail::"+event.line+"\n")
                    f.flush()
                    return False
                    # self.device.use.screenshot(path+"repro fail"+str(datetime.now())+".png")
                else:
                    print(str(event_num)+"::repro success::"+event.line+"\n")
                    f.write(str(event_num)+"::repro success::"+event.line+"\n")
                    f.flush()
            else:
                event_num = event_num + 1
                executeresult=self.executor.execute_event(self.device,event,0)
                if executeresult == False:
                    print("execute fail::"+str(event_num))
                    f.write(str(event_num)+"::execute fail::"+event.line)
                    f.flush()
                    return False
                else:
                    f.write(str(event_num)+"::execute success::"+event.line)
                    f.flush()
                time.sleep(1)
                self.device.use.screenshot(path+str(event_num)+".png")   
                xml = self.device.use.dump_hierarchy()
                f_xml = open(path+str(event_num)+".xml",'w',encoding='utf-8')
                f_xml.write(xml)
                f_xml = open(path+str(event_num)+".xml",'r',encoding='utf-8')
                xmllines=f_xml.readlines()
        
        self.shortest_trace_path = path
        return True

    def parse_events(self,input_path,input_file,add_name,delete_name):
        f = open(input_path+"/"+input_file,'r',encoding='utf-8')
        lines=f.readlines()
        f.close()
        uiautomator_commands = []
        event_num = 0
        for line in lines:
            command=""
            parts = line.split('::')
            if len(parts) < 2:
                continue
            if parts[0].isdigit():
                event_num=event_num+1
                event_id = event_num
            else:
                continue
            action = parts[1]
            if len(parts) < 3:
                if action.startswith("back"):
                    command="d.press(\"back\")"
                elif action.startswith("start"):
                    command="d.press(\"back\")"
            else:
                text=parts[2]
                if len(parts) > 3:
                    value = parts[3] 
                    view = View(value,[])
                if view.description!="" and view.description!="#any#" and view.resourceId!="" and view.resourceId!="#any#":
                    command = f'd(description="{view.description},resourceId="{view.resourceId}")'
                elif view.description!="" and view.description!="#any#":
                    command = f'd(description="{view.description}")'
                elif view.text!="" and view.text!="#any#" and view.text.strip()!=add_name.strip() and view.text.strip()!=delete_name.strip() and view.text.lower() in (keyword.lower() for keyword in self.app.keywordlist) and view.className!="android.widget.EditText" and len(view.text)>1:
                    command = f'd(text="{view.text}")'
                elif view.className=="android.widget.EditText" and action=="edit":
                    f = open(self.shortest_trace_path+"/"+str(event_id-1)+".xml",'r',encoding='utf-8')
                    xmllines=f.readlines()
                    instance=self.findviewinstancebyclassName(xmllines,view)
                    if instance!=None:
                        command = f'd(className="{view.className}",instance={instance})'
                    else:
                        instance=self.findviewinstancebyclassName(xmllines,view)
                        command = f'd(className="{view.className}")'
                elif view.resourceId!="" and view.resourceId!="#any#":
                    f = open(self.shortest_trace_path+"/"+str(event_id-1)+".xml",'r',encoding='utf-8')
                    xmllines=f.readlines()
                    instance=self.findviewinstancebyresourceId(xmllines,view)
                    if instance!=None:
                        command = f'd(resourceId="{view.resourceId}",instance={instance})'
                    else:
                        instance=self.findviewinstancebyresourceId(xmllines,view)
                        command = f'd(resourceId="{view.resourceId}")'
                elif view.className!="" and view.className!="#any#":
                    f = open(self.shortest_trace_path+"/"+str(event_id-1)+".xml",'r',encoding='utf-8')
                    xmllines=f.readlines()
                    instance=self.findviewinstancebyclassName(xmllines,view)
                    if instance!=None:
                        command = f'd(className="{view.className}",instance={instance})'
                    else:
                        instance=self.findviewinstancebyclassName(xmllines,view)
                        command = f'd(className="{view.className}")'
                else:
                    command = f'd(xpath="{view.bounds}")'
                if action == 'click':
                    command=command+".click();"
                elif action == 'edit':
                    command=command+f'.set_text("{text}");'
                elif action == 'longclick':
                    command=command+".long_click();"
            uiautomator_commands.append(command)
        if "search" in input_path:
            uiautomator_commands.append("d.press(\"back\")")

        return '\n'.join(uiautomator_commands[0:len(uiautomator_commands)])    
    
    def findviewinstancebyresourceId(self,now_layout, targetview):
        view=None
        instance = 0
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            if targetview.resourceId!=None and targetview.resourceId == view.resourceId:
                if view.same(targetview):
                    return instance
                else:
                    instance = instance+1
            else:
                continue
        return None

    def findviewinstancebyclassName(self,now_layout, targetview):
        view=None
        instance = 0
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            if targetview.className!=None and targetview.className == view.className:
                if view.same(targetview):
                    return instance
                else:
                    instance = instance+1
            else:
                continue
        return None
    
    def findviewbytext(self,now_layout, text, not_view):
        findview=None
        for line in now_layout:
            if "<node" not in line or "/>" not in line:
                continue
            view = View(line,[])
            import re
            viewtext = re.search(r'text=[\'"](.*?)[\'"]', line).group(1)
            if text != viewtext :
                continue
            else:
                if not_view!=None:
                    if not_view.resourceId == view.resourceId and not_view.className == view.className:
                        continue
                if view.resourceId=="":
                    findview = view
                    continue
                return view
        return findview
    
    def findedithavetext(self,now_layout, text, not_view):
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            import re
            viewtext=re.search(r'text="(.*?)"', line).group(1)
            if viewtext in text and len(viewtext)>1:
                print()
            # if (text not in viewtext and viewtext not in text) or viewtext=="" or "android.widget.EditText" not in line:
            if not (((viewtext in text) and len(viewtext)>1) or ((text in viewtext or viewtext in text) and "android.widget.EditText" in line and viewtext!="")):
                continue
            else:
                if not_view!=None:
                    if not_view.resourceId == view.resourceId and not_view.className == view.className:
                        break
                return view
        return None
    
    def info_to_dmf(self,input_path,info,dd):
        print("Record start")
        type = info[0]
        datatype = info[1]
        add_name = info[2]
        delete_name = info[3].strip()

        xmllist = []
        files = os.listdir(self.shortest_trace_path)

        import re
        def extract_number(filename):
            match = re.search(r'\d+', filename)
            if match:
                return int(match.group())
            return 0
        sorted_files = sorted(files, key=extract_number)
        for filename in sorted_files:
            if filename.endswith(".xml"):
                print(self.shortest_trace_path+"/"+filename)
                f = open(self.shortest_trace_path+"/"+filename,'r',encoding='utf-8')
                lines=f.readlines()
                xmllist.append(lines)
        print("--------------------------")
        #Parsing the recording script of weditor to obtain DMF

        events = []
        views = []
        lines = dd.split("\n")
        num = 0
        for line in lines:
            if line.strip()!="":
                returnvalue=self.get_info(line,num,type,datatype,add_name)
                if returnvalue!=None:
                    num=num+1
                    views.append(returnvalue[0])
                    events.append(returnvalue[1])
                    
        
        #Get and generate additional information
        name = type+" "+datatype
        if type == "add":
            add_name_widget=None
            extra_object = None
            i=len(xmllist)-1
            while i>0:
                i=i-1
                add_name_widget = self.findviewbytext(xmllist[i],add_name,None)
                if add_name_widget==None:
                    add_name_widget = self.findedithavetext(xmllist[i],add_name,None)
                if add_name_widget!=None:
                    add_name_layout = i
                    if add_name_widget.className=="android.widget.EditText":
                        add_name_instance=self.findviewinstancebyclassName(xmllist[i],add_name_widget)
                        add_name_resourceId = ""
                        add_name_className = add_name_widget.className
                    elif add_name_widget.resourceId!="":
                        add_name_instance=self.findviewinstancebyresourceId(xmllist[i],add_name_widget)
                        add_name_resourceId = add_name_widget.resourceId
                        add_name_className = ""
                    elif add_name_widget.className!="":
                        add_name_instance=self.findviewinstancebyclassName(xmllist[i],add_name_widget)
                        add_name_resourceId = ""
                        add_name_className = add_name_widget.className
                    else:
                        print("wrong")
                    break
            extra_object = self.findviewbytext(xmllist[len(xmllist)-1],add_name,None)
            extra_object_resourceId = ""
            extra_object_className = ""
            if extra_object.resourceId!="":
                extra_object_resourceId = extra_object.resourceId
            elif extra_object.className!="":
                extra_object_className = extra_object.className
            else:
                print("wrong")
            views.append({"name": "add_name","UI_layout_num": str(add_name_layout),"text": "","resource-id": add_name_resourceId,"class": add_name_className,"content-desc": "","xpath": "","instance": str(add_name_instance)})
            views.append({"name": "extra_object","UI_layout_num":str(num),"text": "add_name.text","resource-id": extra_object_resourceId,"class": extra_object_className,"content-desc": "","xpath": "","instance": ""})
            views.append({"name": "pre_widget","UI_layout_num":"0","text": "","resource-id": extra_object_resourceId,"class": extra_object_className,"content-desc": "","xpath": "","instance": ""})
            views.append({"name": "search_widget","UI_layout_num":"0","text": "","resource-id": "","class": "android.widget.EditText","content-desc": "","xpath": "","instance": ""})
            results=[{"operator": "add","object": "add_name.text"}]
            preconditions=[{"widget": "e1_widget","relation": "in","UI_layout_num": "0","datatype":""},
                {"widget": "search_widget","relation": "not in","UI_layout_num": "0","datatype":""},
                {"UI_layout_num": "0","datatype": datatype,"relation": "smaller","widget": ""},
                {"UI_layout_num": "0","datatype": "","relation": "smaller::5","widget": "pre_widget"}]
            postconditions=[{"widget": "extra_object","relation": "in","UI_layout_num": str(num),"datatype":""}]
        elif type == "delete":
            delete_name_widget=None
            i=len(xmllist)-1
            while i>0:
                i=i-1
                delete_name_widget = self.findviewbytext(xmllist[i],delete_name,None)
                if delete_name_widget!=None:
                    delete_name_layout = i
                    if delete_name_widget.className=="android.widget.EditText":
                        delete_name_instance=self.findviewinstancebyclassName(xmllist[i],delete_name_widget)
                        delete_name_resourceId = ""
                        delete_name_className = delete_name_widget.className
                    elif delete_name_widget.resourceId!="":
                        delete_name_instance=self.findviewinstancebyresourceId(xmllist[i],delete_name_widget)
                        delete_name_resourceId = delete_name_widget.resourceId
                        delete_name_className = ""
                    elif delete_name_widget.className!="":
                        delete_name_instance=self.findviewinstancebyclassName(xmllist[i],delete_name_widget)
                        delete_name_resourceId = ""
                        delete_name_className = delete_name_widget.className
                        continue
                    else:
                        print("wrong")
                    break
            remove_object = self.findviewbytext(xmllist[0],delete_name,None)
            remove_object_resourceId = ""
            remove_object_className = ""
            if remove_object.resourceId!="":
                remove_object_resourceId = remove_object.resourceId
            elif remove_object.className!="":
                remove_object_className = remove_object.className
            else:
                print("wrong")
            views.append({"name": "delete_name","UI_layout_num": str(delete_name_layout),"text": "","resource-id": delete_name_resourceId,"class": delete_name_className,"content-desc": "","xpath": "","instance": str(delete_name_instance)})
            views.append({"name": "remove_object","UI_layout_num":str(num),"text": "delete_name.text","resource-id": remove_object_resourceId,"class": remove_object_className,"content-desc": "","xpath": "","instance": ""})
            results=[{"operator": "delete","object": "delete_name.text"}]
            preconditions=[{"widget": "e1_widget","relation": "in","UI_layout_num": "0","datatype":""}]
            postconditions=[{"widget": "remove_object","relation": "not in","UI_layout_num": str(num),"datatype":""}]
        elif type == "edit":
            add_name_widget=None
            extra_object = None
            i=len(xmllist)-1
            while i>0:
                i=i-1
                add_name_widget = self.findviewbytext(xmllist[i],add_name,None)
                if add_name_widget!=None:
                    add_name_layout = i
                    if add_name_widget.className=="android.widget.EditText":
                        add_name_instance=self.findviewinstancebyclassName(xmllist[i],add_name_widget)
                        add_name_resourceId = ""
                        add_name_className = add_name_widget.className
                    elif add_name_widget.resourceId!="":
                        add_name_instance=self.findviewinstancebyresourceId(xmllist[i],add_name_widget)
                        add_name_resourceId = add_name_widget.resourceId
                        add_name_className = ""
                    elif add_name_widget.className!="":
                        add_name_instance=self.findviewinstancebyclassName(xmllist[i],add_name_widget)
                        add_name_resourceId = ""
                        add_name_className = add_name_widget.className
                    else:
                        print("wrong")
                    break
            extra_object = self.findviewbytext(xmllist[len(xmllist)-1],add_name,None)
            extra_object_resourceId = ""
            extra_object_className = ""
            if extra_object!=None:
                if extra_object.resourceId!="":
                    extra_object_resourceId = extra_object.resourceId
                elif extra_object.className!="":
                    extra_object_className = extra_object.className
                else:
                    print("wrong")
            views.append({"name": "add_name","UI_layout_num": str(add_name_layout),"text": "","resource-id": add_name_resourceId,"class": add_name_className,"content-desc": "","xpath": "","instance": str(add_name_instance)})
            views.append({"name": "extra_object","UI_layout_num":str(num),"text": "add_name.text","resource-id": extra_object_resourceId,"class": extra_object_className,"content-desc": "","xpath": "","instance": ""})
            views.append({"name": "pre_widget","UI_layout_num":"0","text": "","resource-id": extra_object_resourceId,"class": extra_object_className,"content-desc": "","xpath": "","instance": ""})

            delete_name_widget=None
            i=len(xmllist)-1
            while i>0:
                i=i-1
                delete_name_widget = self.findviewbytext(xmllist[i],delete_name,None)
                if delete_name_widget!=None:
                    delete_name_layout = i
                    if delete_name_widget.className=="android.widget.EditText":
                        delete_name_instance=self.findviewinstancebyclassName(xmllist[i],delete_name_widget)
                        delete_name_resourceId = ""
                        delete_name_className = delete_name_widget.className
                    elif delete_name_widget.resourceId!="":
                        delete_name_instance=self.findviewinstancebyresourceId(xmllist[i],delete_name_widget)
                        delete_name_resourceId = delete_name_widget.resourceId
                        delete_name_className = ""
                    elif delete_name_widget.className!="":
                        delete_name_instance=self.findviewinstancebyclassName(xmllist[i],delete_name_widget)
                        delete_name_resourceId = ""
                        delete_name_className = delete_name_widget.className
                        continue
                    else:
                        print("wrong")
                    break
            remove_object = self.findviewbytext(xmllist[0],delete_name,None)
            remove_object_resourceId = ""
            remove_object_className = ""
            if remove_object.resourceId!="":
                remove_object_resourceId = remove_object.resourceId
            elif remove_object.className!="":
                remove_object_className = remove_object.className
            else:
                print("wrong")

            views.append({"name": "delete_name","UI_layout_num": str(delete_name_layout),"text": "","resource-id": delete_name_resourceId,"class": delete_name_className,"content-desc": "","xpath": "","instance": str(delete_name_instance)})
            views.append({"name": "remove_object","UI_layout_num":str(num),"text": "delete_name.text","resource-id": remove_object_resourceId,"class": remove_object_className,"content-desc": "","xpath": "","instance": ""})
            views.append({"name": "search_widget","UI_layout_num":"0","text": "","resource-id": "","class": "android.widget.EditText","content-desc": "","xpath": "","instance": ""})

            results=[{"operator": "delete","object": "delete_name.text"},{"operator": "add","object": "add_name.text"}]
            preconditions=[{"widget": "e1_widget","relation": "in","UI_layout_num": "0","datatype":""},
                {"widget": "search_widget","relation": "not in","UI_layout_num": "0","datatype":""},
                {"UI_layout_num": "0","datatype": "","relation": "smaller::5","widget": "pre_widget"}]
            postconditions=[{"widget": "extra_object","relation": "in","UI_layout_num": str(num),"datatype":""},{"widget": "remove_object","relation": "not in","UI_layout_num": str(num),"datatype":""}]
        elif type == "search":
            input_name = delete_name
            search_name = delete_name
            search_object = None
            i=len(xmllist)
            while i>0:
                i=i-1
                search_name_widget = self.findviewbytextclassName(xmllist[i],input_name,"android.widget.EditText")
                if search_name_widget!=None:
                    search_name_layout = i
                    if search_name_widget.resourceId!="":
                        search_name_instance=self.findviewinstancebyresourceId(xmllist[i],search_name_widget)
                        search_name_resourceId = search_name_widget.resourceId
                        search_name_className = ""
                    elif search_name_widget.className!="":
                        search_name_instance=self.findviewinstancebyclassName(xmllist[i],search_name_widget)
                        search_name_resourceId = ""
                        search_name_className = search_name_widget.className
                        continue
                    else:
                        print("wrong")
                    break
            search_object = self.findviewbytext(xmllist[len(xmllist)-1],search_name,search_name_widget)
            search_object_resourceId = ""
            search_object_className = ""
            if search_object!=None:
                if search_object.resourceId!="":
                    search_object_resourceId = search_object.resourceId
                elif search_object.className!="":
                    search_object_className = search_object.className
                else:
                    print("wrong")
            views.append({"name": "search_name","UI_layout_num": str(search_name_layout),"text": "","resource-id": search_name_resourceId,"class": search_name_className,"content-desc": "","xpath": "","instance": str(search_name_instance)})
            views.append({"name": "search_object","UI_layout_num":str(num),"text": "search_name.text","resource-id": search_object_resourceId,"class": search_object_className,"content-desc": "","xpath": "","instance": ""})
            
            results=[]
            preconditions=[{"widget": "e1_widget","relation": "in","UI_layout_num": "0","datatype":""},{"widget": "","relation": "is not empty","UI_layout_num": "","datatype":datatype}]
            postconditions=[{"widget": "search_object","relation": "in","UI_layout_num": str(num),"datatype":""}]
        
        elif type == "read":
            read_name = delete_name
            read_object = None
            i=len(xmllist)-1
            while i>0:
                i=i-1
                read_name_widget = self.findviewbytext(xmllist[i],read_name,None)
                if read_name_widget!=None:
                    read_name_layout = i
                    if read_name_widget.resourceId!="":
                        read_name_instance=self.findviewinstancebyresourceId(xmllist[i],read_name_widget)
                        read_name_resourceId = read_name_widget.resourceId
                        read_name_className = ""
                    elif read_name_widget.className!="":
                        read_name_instance=self.findviewinstancebyclassName(xmllist[i],read_name_widget)
                        read_name_resourceId = ""
                        read_name_className = read_name_widget.className
                        continue
                    else:
                        print("wrong")
                    break
            read_object = self.findviewbytext(xmllist[len(xmllist)-1],read_name,read_name_widget)
            read_object_resourceId = ""
            read_object_className = ""
            if read_object!=None:
                if read_object.resourceId!="":
                    read_object_resourceId = read_object.resourceId
                elif read_object.className!="":
                    read_object_className = read_object.className
                else:
                    print("wrong")
            views.append({"name": "read_name","UI_layout_num": str(read_name_layout),"text": "","resource-id": read_name_resourceId,"class": read_name_className,"content-desc": "","xpath": "","instance": str(read_name_instance)})
            views.append({"name": "read_object","UI_layout_num":str(num),"text": "read_name.text","resource-id": read_object_resourceId,"class": read_object_className,"content-desc": "","xpath": "","instance": ""})
            
            results=[]
            preconditions=[{"widget": "e1_widget","relation": "in","UI_layout_num": "0","datatype":""}]
            postconditions=[{"widget": "read_object","relation": "in","UI_layout_num": str(num),"datatype":""}]

        #Generate json file based on information
        data = {"widgets": views,"events":events,"impacts":results,"preconditions":preconditions,"name":name,"type":type,"datatype":datatype,"post-conditions":postconditions,"proportion":"10"}
        import json
        json_string = json.dumps(data)
        f = open(input_path+"/test.json",'w',encoding='utf-8')
        f.write(json_string)
        f.flush()
        f.close()

    def get_info(self,line,num,type,datatype,add_name):
        print("line:"+line)
        resourceId=""
        text=""
        description=""
        xpath=""
        instance=""
        action="#any#"
        className=""
        edittext=""
        keys = line.split("\",")
        for key in keys:
            if "resourceId=" in key:
                keyword = "resourceId"
                returnkey = self.findkeyword(key,keyword)
                resourceId = returnkey
            elif "className=" in key:
                keyword = "className"
                returnkey = self.findkeyword(key,keyword)
                className = returnkey
            elif "description=" in key:
                keyword = "description"
                returnkey = self.findkeyword(key,keyword)
                description = returnkey
            elif "xpath=" in key:
                keyword = "xpath"
                returnkey = self.findkeyword(key,keyword)
                xpath = returnkey
            elif "instance=" in key:
                keyword = "instance"
                returnkey = key[key.find("instance=")+9:key.find("instance=")+10]
                instance = returnkey
            elif "text=" in key:
                keyword = "text"
                returnkey = self.findkeyword(key,keyword)
                text = returnkey
                
        if "long_click" in line or "longclick" in line:
            action = "longclick"
        elif "click" in line:
            action = "click"
        elif "set_text" in line:
            action = "edit"
            num1=line.find("set_text(")
            returnkey = line[num1+10:len(line)]
            num2=returnkey.find("\")")
            if num2>-1:
                returnkey = returnkey[0:num2]
            edittext = returnkey
        elif "scroll" in line:
            if "forward" in line and "vert" in line:
                action = "scroll_forward"
            elif "backward" in line and "vert" in line:
                action = "scroll_backward"
            elif "horiz" in line and "toEnd" in line:
                action = "scroll_right"
            else:
                action = "scroll_left"    
        elif "drag" in line:
            action = "drag"
            num1 = line.find("drag(")
            returnkey = line[num1+5:len(line)]
            num2=returnkey.find(")")
            if num2>-1:
                returnkey = returnkey[0:num2]
            edittext = returnkey
        elif "press(\"back\")" in line:
            action = "back"
        if type=="search" and action=="edit":
            edittext = datatype+"::random"
        elif action=="edit" and add_name==edittext:
            edittext="random"
        print("resourceId:"+resourceId)
        print("text:"+text)
        print("description:"+description)
        print("xpath:"+xpath)
        print("action:"+action)
        print("edittext:"+edittext)
        print("instance:"+instance)
        print("******************")
        widget = {"name":"e"+str(num+1)+"_widget","UI_layout_num":str(num),"text":text,"resource-id":resourceId,"class":className,"content-desc":description,"xpath":xpath,"instance": instance}
        event = {"widget":"e"+str(num+1)+"_widget","action": action,"text": edittext,"force":True}
        if action !="#any#":
            returnvalue = (widget,event)
            return returnvalue
        else:
            return None

    def findviewbytextclassName(self,now_layout, text, className):
        findview=None
        for line in now_layout:
            if "<node" not in line:
                continue
            view = View(line,[])
            if className != view.className or text!=view.text:
                continue
            if view.resourceId=="":
                findview= view
                continue
            else:
                return view
        return findview
    
    def  findkeyword(self,key,keyword):
        num1=key.find(keyword+"=")
        returnkey = key[num1+len(keyword)+2:len(key)]
        num2=returnkey.find("\"")
        if num2>-1:
            returnkey = returnkey[0:num2]
        return returnkey
    