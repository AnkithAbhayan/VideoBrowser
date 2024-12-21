import sys
import os
import json
from core.core import Gui

class Client:
    def __init__(self,args):
        self.client_data = []
        self.path=""
        try:
            file = open("data/data.json","r")
            data = json.load(file)
            file.close()
            self.path=data["path"]
        except:
            pass
        
        if len(args)>1:
            self.path=args[1]
        
        if not os.path.isdir(self.path):
            if len(args)==1:
                print("No path detected. Continuing.")
            else:
                print("Invalid path argument. Skipping.")
            self.save_path("")
            self.path=""

    def load_files(self,path):
        self.client_data = []
        if path:
            self.path=path
            self.client_data = [os.path.join(self.path,item) for item in os.listdir(self.path)]

        new=[]
        for i in range(len(self.client_data)):
            if self.client_data[i][-4:] in [".mp4",".mkv",".mov",".flv",".avi"]:
                new.append(self.client_data[i])
        self.client_data = new
        return self.client_data, self.path

    def save_path(self,path):
        data = {"path":path}
        with open("data/data.json","w") as JsonFile:
            json.dump(data,JsonFile)

MyClient = Client(sys.argv)
MyClient.load_files(MyClient.path)

GuiClient = Gui(MyClient)
