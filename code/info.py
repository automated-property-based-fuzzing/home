import xml.etree.ElementTree as ET
import hashlib,re

class Info(object):

    def __init__(self, event_index, event, xml, app):
        self.event_index = event_index
        self.event = event
        self.xml = xml
        self.keywordlist = app.keywordlist
        self.package_name = app.package_name
    
    def add_json_info(self,json):
        self.json = json

    def find_first_text(self,node):
        """递归查找节点中的第一个非空文本"""
        if 'text' in node.attrib and node.attrib['text'].strip():
            return node.attrib['text'].strip()
        for child in node:
            result = self.find_first_text(child)
            if result:
                return result
        return None
    
    def statistic_childs(self,views):
        childs = []
        for rv in views:
            # 提取代表性文本
            for child in rv:
                #测试用，正式版注释
                if "NONE" in child.attrib['text']:
                    continue
                if self.package_name not in child.attrib['package']:
                    continue
                rep_text = self.find_first_text(child)
                if rep_text!=None:
                # and rep_text not in self.keywordlist:
                    childs.append(rep_text)
        return childs
    
    def remove_all_under(self,views,root):
        for rv in views:
            for parent in root.iter():
                if rv in list(parent):
                    parent.remove(rv)
                    break
    
    def update_eventline(self):
        self.eventline=str(self.event_index)+"::"+self.event.action+"::"+self.event.text+"::"+self.event.view.line.strip()+"::"+self.event.view.xpath

    def get_info(self, app):
        self.matching_strings=[]
        dmf_keyword_list = ["add","delete","remove","trash","save","more option","create","search","edit","trash","rename"]
        # Non-start/back type events
        if self.event.view!=None:
            self.eventline=str(self.event_index)+"::"+self.event.action+"::"+self.event.text+"::"+self.event.view.line.strip()+"::"+self.event.view.xpath
            # Check whether the current event is a DMF-type event
            self.matching_strings = [s for s in dmf_keyword_list if s.lower() in self.event.view.line.lower()]
        # Start/back type events
        else:
            self.eventline=str(self.event_index)+"::"+self.event.action
        
        # Flag indicating whether the keyboard is open
        self.keyboard_flag = False
        keyboard_list = ["com.google.android.inputmethod.latin","com.sohu.inputmethod.sogouoem"]
        root = ET.fromstring(self.xml)
        # 1. Remove all nodes whose package is not the specified package name
        for parent in root.iter():
            children_to_remove = [child for child in list(parent) if child.attrib.get('package') != app.package_name ]
            for child in children_to_remove:
                parent.remove(child)
                if child.attrib.get('package') in keyboard_list:
                    self.keyboard_flag = True
        # Find all RecyclerView nodes
        recycler_views = [element for element in root.findall(".//*") if 'RecyclerView' in element.get('class', '')]
        list_views = [element for element in root.findall(".//*") if 'ListView' in element.get('class', '')]
        # 2. Count the number of direct child nodes in each RecyclerView
        self.childs=self.statistic_childs(recycler_views)
        if self.childs==[]:
            self.childs=self.statistic_childs(list_views)
        # 3. Remove all RecyclerView nodes and their contents
        self.remove_all_under(recycler_views,root)
        self.remove_all_under(list_views,root)
        # 4. Create a new XML tree containing only the specified attributes
        for node in root.iter():
            # Determine which attributes to remove
            keys_to_remove = [key for key in node.attrib.keys() if key not in ["resource-id", "class", "content-desc", "text"]]
            # If class is "android.widget.EditText", also remove the text attribute
            if node.attrib.get("class", "") == "android.widget.EditText" and "text" in node.attrib:
                keys_to_remove.append("text")
            # Remove unnecessary attributes
            for key in keys_to_remove:
                node.attrib.pop(key)
        self.simplified_xml = ET.tostring(root, encoding='unicode')
        # 5. Generate and return the hash value
        # self.simplified_xml=re.sub(r'text="[^"]*"', 'text=""', self.simplified_xml)
        temp = self.simplified_xml.replace(' ','')
        self.hashstring = hashlib.sha256(temp.encode('utf-8')).hexdigest()
        self.childs_num = len(self.childs)
