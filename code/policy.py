import random
from event import Event
from collections import deque
class Policy(object):


    def __init__(self,devices,app,emulator_path,android_system):
        
        self.app = app
        self.devices = devices
        self.emulator_path = emulator_path
        self.android_system = android_system
    
    def random_text(self,seed_text):
        if len(seed_text)>1:
            text_style=random.randint(3,8)
        else:
            text_style=random.randint(3,5)
        text_length=random.randint(1,5)
        nums=["0","1","2","3","4","5","6","7","8","9"]
        letters=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        symbols=[",",".","!","?"]
        i=0
        random_string=""
        print("text_style:"+str(text_style))
        
        if text_style == 0:
            while i < text_length:
                s_style=random.randint(0,2)
                if s_style==0:
                    now_letters=nums[random.randint(0,len(nums)-1)]
                    random_string=random_string+now_letters
                elif s_style==1:
                    now_letters=letters[random.randint(0,len(letters)-1)]
                    random_string=random_string+now_letters
                elif s_style==2:
                    now_letters=symbols[random.randint(0,len(symbols)-1)]
                    random_string=random_string+now_letters
                i=i+1
        elif text_style == 1:
            while i < text_length:
                now_num=nums[random.randint(0,len(nums)-1)]
                random_string=random_string+now_num
                i=i+1
        elif text_style == 2:
            while i < text_length:
                now_letters=letters[random.randint(0,len(nums)-1)]
                random_string=random_string+now_letters
                i=i+1
        elif text_style == 3:
            special_strings=["/storage/emulated/0/anymemo/"+letters[random.randint(0,len(letters)-1)],"cla","aaa","01234567890"]
            countrynum=random.randint(0,3)
            random_string=special_strings[countrynum]
        elif text_style ==4:
            random_string=letters[random.randint(0,len(letters)-1)]
        elif text_style ==5:
            random_string=nums[random.randint(0,len(nums)-1)]
        elif text_style ==6:
            index = random.randint(0, len(seed_text) - 1) 
            random_string=seed_text[:index] + letters[random.randint(0,len(letters)-1)] + seed_text[index:]
        elif text_style ==7:
            index = random.randint(0, len(seed_text) - 1) 
            random_string=seed_text[:index] + seed_text[index + 1:]
        elif text_style ==8:
            index = random.randint(0, len(seed_text) - 1) 
            random_string=seed_text[:index] + letters[random.randint(0,len(letters)-1)] + seed_text[index + 1:]
        return random_string
    
    def check_foreground(self):
        packagelist=[self.app.package_name,"com.google.android.permissioncontroller","com.android.packageinstaller","com.android.permissioncontroller"]
        lines = self.devices[0].use.dump_hierarchy()
        for package in packagelist:
            if package in lines:
                return True
        return False
    
    def choice_event(self):
        pass


class RandomPolicy(Policy):
    def __init__(self,device,app,
                pro_click,pro_longclick,pro_scroll,pro_edit,pro_back,pro_home):
        
        self.pro_click = pro_click
        self.pro_longclick = pro_click+pro_longclick
        self.pro_scroll = pro_click+pro_longclick+pro_scroll
        self.pro_edit = pro_click+pro_longclick+pro_scroll+pro_edit
        self.pro_back = pro_click+pro_longclick+pro_scroll+pro_edit+pro_back
        self.pro_home = pro_click+pro_longclick+pro_scroll+pro_edit+pro_back+pro_home
        self.pro_all=pro_click+pro_longclick+pro_scroll+pro_edit+pro_back+pro_home
        self.app = app
        self.device = device

    def choice_event(self,device,event_count,flag,keyview_list):

        for view in device.screen.allleafviews:
            ankicondition = view.package == "com.ichi2.anki" and view.resourceId == "com.ichi2.anki:id/get_started"
            wikiCondition = view.package == "org.wikipedia.alpha" and (view.resourceId == "org.wikipedia.alpha:id/fragment_onboarding_skip_button" or view.description == "Navigate up")
            myexpenseCondition= view.package == "org.totschnig.myexpenses" and (view.resourceId == "org.totschnig.myexpenses:id/suw_navbar_next" or view.resourceId == "org.totschnig.myexpenses:id/suw_navbar_done")
            markorCondition =  view.package == "net.gsantner.markor" and (view.resourceId == "net.gsantner.markor:id/next" or view.resourceId == "net.gsantner.markor:id/done")
            if myexpenseCondition or markorCondition or wikiCondition or ankicondition:
                print("skip===================skip")
                event = Event(view, "click", device, event_count)
                return event
        
        event_type = random.randint(0,self.pro_all-1)
        inapplist=[self.app.package_name,"com.lbe.security.miui","com.google.android.packageinstaller","com.google.android.permissioncontroller","com.android.packageinstaller","com.android.permissioncontroller"]
        click_classname_lists=["android.widget.RadioButton","android.view.View","android.widget.ImageView","android.widget.View","android.widget.CheckBox","android.widget.Button","android.widget.Switch","android.widget.ImageButton","android.widget.TextView","android.widget.CheckedTextView","android.widget.TableRow","android.widget.EditText","android.support.v7.widget.ar"]
        click_classname_lists_important=["android.widget.CheckBox","android.widget.Button","android.widget.Switch"]
        click_package_lists=[self.app.package_name,"com.lbe.security.miui","com.google.android.apps.messaging","android","com.android.settings","com.google.android","com.google.android.packageinstaller",
        "com.google.android.inputmethod.latin","com.google.android.permissioncontroller","com.android.packageinstaller","com.android.permissioncontroller"]
        # print("random:"+str(event_type))
        if flag==False and str(self.device.get_current_app()) not in inapplist:
            backorstart = random.randint(0,5)
            print(self.device.get_current_app()+str(inapplist))
            if backorstart==0:
                event = Event(None, "back", device,event_count)
            else:
                event = Event(None, "start", device,event_count)
        elif event_type<self.pro_click:
            views=[]
            import_views=[]
            for view in device.screen.allleafviews:
                if view.package in click_package_lists and (view.text!="DENY" and view.text!="EXIT"):
                    views.append(view)
                if (view.className in click_classname_lists_important or view.description!="") and view.package in click_package_lists and (view.text!="DENY" and view.text!="EXIT"):
                    import_views.append(view)
            if len(views)>0:
                special = random.randint(0,3)
                if special != 0 and len(import_views)>0:
                    event_view_num = random.randint(0,len(import_views)-1)
                    event_view = import_views[event_view_num]
                else:
                    event_view_num = random.randint(0,len(views)-1)
                    event_view = views[event_view_num]
                event = Event(event_view, "click", device,event_count)  
            else:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,keyview_list)
        elif event_type<self.pro_longclick:
            views=[]
            for view in device.screen.allleafviews:
                if view.className in click_classname_lists and view.package in click_package_lists and (view.longClickable=="true" or view.clickable=="true") and view.text!="DENY" and view.text!="EXIT":
                    views.append(view)
            if len(views)>0:
                event_view_num = random.randint(0,len(views)-1)
                event_view = views[event_view_num]
                event = Event(event_view, "longclick", device,event_count)
            else:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,keyview_list)
        elif event_type<self.pro_scroll:
            # print("scroll")
            # if device.use(scrollable=True).count<1:
            #     # print("re_choice")
            #     event = self.choice_event(device,event_count,True,keyview_list)
            # else:
            views=[]
            for view in device.screen.allleafviews:
                if view.scrollable=="true" and view.package in click_package_lists:
                    views.append(view)
            if len(views)>0:
                event_view_num = random.randint(0,len(views)-1)
                event_view = views[event_view_num]
                direction_list = ["backward","forward","right","left"]
                direction_num = random.randint(0,len(direction_list)-1)
                event = Event(event_view, "scroll_"+direction_list[direction_num], device,event_count)
            else:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,keyview_list)
        elif event_type<self.pro_edit:
            # print("edit")
            if device.use(className="android.widget.EditText").count<1:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,keyview_list)
            else:
                views=[]
                for view in device.screen.allleafviews:
                    if view.className == "android.widget.EditText":
                        views.append(view)
                if len(views)>0:
                    event_view_num = random.randint(0,len(views)-1)
                    event_view = views[event_view_num]
                    event = Event(event_view, "edit", device,event_count)
                    text = self.random_text(event_view.text)
                    event.set_text(text)
                else:
                    # print("re_choice")
                    event = self.choice_event(device,event_count,True,keyview_list)
        elif event_type<self.pro_back:
            # print("back")
            if self.app.main_activity != device.use.app_current()['activity']:
                event = Event(None, "back", device,event_count)
            else:
                event = self.choice_event(device,event_count,True,keyview_list)
        else:
            # print("home")
            event = Event(None, "start", device,event_count)
        if event.view !=None and not event.view.notin(keyview_list):
            event = self.choice_event(device,event_count,True,keyview_list)
        return event

        



class DMFPolicy(Policy):
    def __init__(self,device,app,
                pro_click,pro_longclick,pro_scroll,pro_edit,pro_back,pro_home):
        
        self.pro_click = pro_click
        self.pro_longclick = pro_click+pro_longclick
        self.pro_scroll = pro_click+pro_longclick+pro_scroll
        self.pro_edit = pro_click+pro_longclick+pro_scroll+pro_edit
        self.pro_back = pro_click+pro_longclick+pro_scroll+pro_edit+pro_back
        self.pro_home = pro_click+pro_longclick+pro_scroll+pro_edit+pro_back+pro_home
        self.pro_all=pro_click+pro_longclick+pro_scroll+pro_edit+pro_back+pro_home
        self.app = app
        self.device = device
        self.record_data = []
        self.last_events = deque(maxlen=5)
    
    def set_info(self,record_data,last_events):
        self.record_data = record_data
        self.last_events = last_events
    
    def check_match(self,keyword,view):
        if keyword in view.text.lower() or keyword in view.description.lower() or keyword in view.resourceId or keyword in view.className.lower():
            return True

    def choice_event(self,device,event_count,flag,target_dmf,turn):
        if turn>10:
            event = Event(None, "start", device,event_count)
            return event
        event_type = random.randint(0,self.pro_all-1)
        inapplist=[self.app.package_name,"com.lbe.security.miui","com.google.android.packageinstaller","com.google.android.permissioncontroller","com.android.packageinstaller","com.android.permissioncontroller"]
        click_classname_lists_important=["android.widget.Button","android.widget.ImageView","android.widget.ImageButton"]
        click_package_lists=[self.app.package_name,"com.lbe.security.miui","com.google.android.apps.messaging","android","com.android.settings","com.google.android","com.google.android.packageinstaller","com.google.android.permissioncontroller","com.android.packageinstaller","com.android.permissioncontroller","com.google.android.inputmethod.latin"]

        for view in device.screen.realallviews:
            myexpenseCondition= view.package == "org.totschnig.myexpenses" and (view.resourceId == "org.totschnig.myexpenses:id/suw_navbar_next" or view.resourceId == "org.totschnig.myexpenses:id/suw_navbar_done")
            markorCondition =  view.package == "net.gsantner.markor" and (view.resourceId == "net.gsantner.markor:id/next" or view.resourceId == "net.gsantner.markor:id/done")
            amazeCondition = view.package == "com.amaze.filemanager" and view.resourceId == "com.amaze.filemanager:id/pathname" and (len(self.last_events)!=5 or "com.amaze.filemanager:id/pathname" not in self.last_events[4])
            if myexpenseCondition or markorCondition or amazeCondition:
                print("skip===================skip")
                event = Event(view, "click", device, event_count)
                return event
        
        dmf_events=[]
        item_views = []
        for view in device.screen.allleafviews:    
            item_cond = any(view.text == data for data in self.record_data)
            if (target_dmf=="delete" or target_dmf=="edit" or target_dmf=="all" or target_dmf=="read") and view.package in click_package_lists and item_cond:
                item_views.append(view)
                longClickEvent = Event(view, "longclick", device, event_count)  
                if longClickEvent.line not in self.last_events and target_dmf!="read": 
                    dmf_events.append(longClickEvent)
                    dmf_events.append(longClickEvent)
                ClickEvent = Event(view, "click", device, event_count)  
                if ClickEvent.line not in self.last_events: 
                    dmf_events.append(ClickEvent) 
                    dmf_events.append(ClickEvent)

        for view in device.screen.allleafviews:
            event = Event(view, "click", device, event_count) 
            
            if (target_dmf=="search" or target_dmf=="all") and "com.google.android.inputmethod.latin:id/key_pos_ime_action" in view.resourceId and (len(self.last_events)==0 or self.last_events[len(self.last_events)-1].startswith("edit")):
                return event
            if (target_dmf=="search" or target_dmf=="all") and "android.widget.EditText" in view.className and (len(self.last_events)!=0 and "search" in self.last_events[len(self.last_events)-1] and self.last_events[len(self.last_events)-1].startswith("click")):
                event = Event(view, "edit", device, event_count)
                if len(self.record_data)>0:
                    text_num = random.randint(0,len(self.record_data)-1)
                    text = self.record_data[text_num]
                else:
                    text = self.random_text(view.text)
                event.set_text(text) 
                return event
            # cond = any(self.check_match(next(iter(add_data)),view) for add_data in self.record_data)
            
            search_cond = (target_dmf=="search" or target_dmf=="all") and (self.check_match("search",view) or self.check_match("lookup",view)) and not self.check_match("close",view) and not self.check_match("edit",view) and not self.check_match("layout",view)
            
            delete_cond = (target_dmf=="delete" or target_dmf=="all") and (self.check_match("delete",view) or self.check_match("trash",view) or self.check_match("hide",view) or self.check_match("remove",view) or self.check_match("more options",view)) 
            
            edit_cond = (target_dmf=="edit" or target_dmf=="all") and (self.check_match("rename",view) or self.check_match("save",view) or self.check_match("update",view) or self.check_match("more options",view) or self.check_match("list",view)) 
            
            add_cond = (len(item_views)<1 or target_dmf=="add" or target_dmf=="read" or target_dmf=="all" or target_dmf=="edit") and ((self.check_match("new",view) and self.check_match("button",view)) or self.check_match("add",view) or self.check_match("save",view) or self.check_match("create",view) or self.check_match("ok",view) ) 
            
            if view.package in click_package_lists and (search_cond or delete_cond or add_cond or edit_cond) and len(view.text)<20 and event.line not in self.last_events: 
                dmf_events.append(event)

        for view in device.screen.allleafviews:
            if self.check_match("edittext",view) and view.package in click_package_lists:
                event = Event(view, "edit", device, event_count)
                text = self.random_text(view.text)
                event.set_text(text)
                if event.line not in self.last_events and len(self.last_events)>0: 
                    for keytext in self.app.keywordlist:
                        if view.text==keytext and not self.last_events[len(self.last_events)-1].startswith("edit") and random.randint(0,1)==0:
                            return event
                    dmf_events.append(event)
                break
        # if len(dmf_events)<1:
        #     event = Event(None, "back", device, event_count)
        #     if event.line not in self.last_events: 
        #         dmf_events.append(event)
        print("DMF event:"+ str(len(dmf_events)))
        if target_dmf=="all":
            exe_dmf = random.randint(0,4)
        else:
            exe_dmf = random.randint(0,1)
        if exe_dmf == 0 and len(dmf_events)>0:
            event_num = random.randint(0,len(dmf_events)-1)
            event = dmf_events[event_num]  
            print("**DMF EVENT**")
            return event
        
        if flag==False and str(self.device.get_current_app()) not in inapplist:
            backorstart = random.randint(0,5)
            print(self.device.get_current_app()+str(inapplist))
            if backorstart==0:
                event = Event(None, "back", device,event_count)
            else:
                event = Event(None, "start", device,event_count)
        elif event_type<self.pro_click:
            views=[]
            import_views=[]
            for view in device.screen.allleafviews:
                if view.package in click_package_lists and (view.text.lower()!="deny" and view.text.lower()!="exit"):
                    views.append(view)
                if (view.className in click_classname_lists_important or view.description!="") and view.package in click_package_lists and (view.text.lower()!="deny" and view.text.lower()!="exit" and view.text.lower()!="cancel"):
                    import_views.append(view)
            if len(views)>0:
                special = random.randint(0,3)
                if special != 0 and len(import_views)>0:
                    event_view_num = random.randint(0,len(import_views)-1)
                    event_view = import_views[event_view_num]
                else:
                    event_view_num = random.randint(0,len(views)-1)
                    event_view = views[event_view_num]
                event = Event(event_view, "click", device,event_count)  
            else:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,target_dmf,turn+1)
        elif event_type<self.pro_longclick:
            views=[]
            for view in device.screen.allleafviews:
                if view.package in click_package_lists and (view.text.lower()!="deny" and view.text.lower()!="exit"):
                    views.append(view)
            if len(views)>0:
                event_view_num = random.randint(0,len(views)-1)
                event_view = views[event_view_num]
                event = Event(event_view, "longclick", device,event_count)
            else:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,target_dmf,turn+1)
        elif event_type<self.pro_scroll:
            views=[]
            for view in device.screen.allleafviews:
                if view.scrollable=="true" and view.package in click_package_lists:
                    views.append(view)
            if len(views)>0:
                event_view_num = random.randint(0,len(views)-1)
                event_view = views[event_view_num]
                direction_list = ["backward","forward","right","left"]
                direction_num = random.randint(0,len(direction_list)-1)
                event = Event(event_view, "scroll_"+direction_list[direction_num], device,event_count)
            else:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,target_dmf,turn+1)
        elif event_type<self.pro_edit:
            # print("edit")
            if device.use(className="android.widget.EditText").count<1:
                # print("re_choice")
                event = self.choice_event(device,event_count,True,target_dmf,turn+1)
            else:
                views=[]
                for view in device.screen.allleafviews:
                    if view.className == "android.widget.EditText" and view.package in click_package_lists:
                        views.append(view)
                if len(views)>0:
                    event_view_num = random.randint(0,len(views)-1)
                    event_view = views[event_view_num]
                    # if event_view.resourceId!="" :
                    #     event_view.line = re.sub("text=\"[^\"]*\"", "text=\"#any#\"", event_view.line)
                    event = Event(event_view, "edit", device,event_count)
                    text = self.random_text(event_view.text)
                    event.set_text(text)
                else:
                    # print("re_choice")
                    event = self.choice_event(device,event_count,True,target_dmf,turn+1)
        elif event_type<self.pro_back:
            # print("back")
            if self.app.main_activity != device.use.app_current()['activity']:
                event = Event(None, "back", device,event_count)
            else:
                event = self.choice_event(device,event_count,True,target_dmf,turn+1)
        else:
            # print("home")
            event = Event(None, "start", device,event_count)
        
        if (event.line in self.last_events and turn<5 and event.action!="start") or "log out" in event.line.lower() or "logout" in event.line.lower():
            event = self.choice_event(device,event_count,True,target_dmf,turn+1)
        
        return event
        
