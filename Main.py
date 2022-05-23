import time, sys, os, random, json
import Engine
from datetime import date
from Engine import Game,Key

import FontSize
from Instances import *

#----Window-Setup-----#
Game.disable_quickedit()
Game.window('Game',50,35)
#Set font size to 20
FontSize.run(22)

layout = Engine.Layout()
console = Engine.Console()

layout.split_column(
    Engine.Layout(name='Main',ratio=1),
    Engine.Layout(name='SideSplit',ratio=2)
)
layout["SideSplit"].split_row(
    Engine.Layout(name='Side',ratio=1),
    Engine.Layout(name='Shop',ratio=1,visible=False)
)
#----Window-Setup-----#

#---------
GameVersion = "0.0.7"
SaveFilePath = os.getenv('APPDATA')+"\SuperNiceGame"
if not os.path.exists(SaveFilePath):
    os.mkdir(SaveFilePath)
HIGH_LIGHT_COLOR = "green"
PANEL_COLOR = "bright_white"
#--------- # TODO ADD OPTION MENU WITH OPTION TO CHANGE COLORS AND ENABLE OR DISABLE AUTOSAVE AND MORE IN THE FUTURE

class Player:
    def __init__(self):
        self.Class = None
        self.Stats = {
            'Health' : 1,
            'MaxHealth' : 1,
            'Attack' : 1,
            'Defence' : 1,
            'Speed' : 1
        }
        self.Gold = 0
        self.Inventory = []
        self.Potions = {
            'Health Potion' : 5
        }
        self.Equiped = {
            'Helmet' : None,
            'Chestplate' : None,
            'Leggins' : None,
            'LeftHand' : None,
            'RightHand' : None
        }
        self.EquipmentMaxHealth = 0
        self.EquipmentAttack = 0
        self.EquipmentDefence = 0
        self.EquipmentSpeed = 0
        self.CurrentSaveFileName = None

    def UseItem(self,Name):
        if len(player.Inventory) <= 0: return
        for x in player.Inventory:
            if Name == x.name:
                x.Use(self)
                break
        self.RecalculateStatsFromEquipment()
    
    def SellItem(self,Item):
        if len(self.Inventory) <= 0: return False
        for x in self.Inventory:
            if Item == x:
                self.Inventory.remove(x)
                self.Gold += x.Price
                return True
        return False
    
    def BuyItem(self,Item):
        if self.Gold >= Item.Price:
            self.Gold -= Item.Price
            self.Inventory.append(Item)
            return True
        return False
    
    def RemoveEquipment(self,EquipedItem):
        item = Item.FindItem(EquipedItem)
        if item == None: return Engine.Text("You have nothing equiped!")
        if player.Equiped[item.EquipPlace] != None:
            player.Equiped[item.EquipPlace] = None
            player.Inventory.append(item)
            self.RecalculateStatsFromEquipment()
            return Engine.Text("You've taken off a %s" % item.name)
        return Engine.Text("You don't have that item equiped")

    def UsePotion(self,Name:str):
        self.PotionHealProcent = 0.25
        SideText = Engine.Text("")
        match Name:
            case 'Health Potion':
                if self.Potions[Name] <= 0:
                    SideText.append("You don't have any Health Potions")
                    layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %PANEL_COLOR))
                    Game.wait_for_input()
                    return
                if self.GetHealth() >= self.GetMaxHealth(): return
                self.Potions[Name] -= 1
                HealthBefore = round(player.GetHealth())
                Heal = round(player.GetMaxHealth() * self.PotionHealProcent)
                player.SetHealth(player.GetHealth() + Heal)
                HealthAfter = round(player.GetHealth())
                HealValue = HealthAfter - HealthBefore
                SideText.append("You've used a Health Potion\n")
                SideText.append("It healed you for %s \n" %HealValue)
                SideText.append("Current health %s/%s \n" %(round(player.GetHealth()),player.GetMaxHealth()))
                layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %PANEL_COLOR))
                Game.wait_for_input()
    
    def SetAllStats(self,NewStats,NewClass):
        self.Class = NewClass
        self.Stats = NewStats
    
    def ResetStats(self):
        self.Class = None
        self.Gold = 0
        self.Inventory = []
        self.Potions['Health Potion'] = 5
        self.Equiped = {
            'Helmet' : None,
            'Chestplate' : None,
            'Leggins' : None,
            'LeftHand' : None,
            'RightHand' : None
        }
        self.ResetStatsFromEquipment()
    
    def PrintStats(self):
        text = Engine.Text()
        text.append("Class: %s \n" %self.Class)
        text.append("%s/%s Health \n" %(self.GetHealth(),self.GetMaxHealth()))
        text.append('%s Attack \n' %self.GetAttack())
        text.append('%s Defence \n' %self.GetDefence())
        text.append('%s Speed \n' %self.GetSpeed())
        return text
    
    def RecalculateStatsFromEquipment(self):
        self.ResetStatsFromEquipment()
        self.AddStatsFromEquipment()

    def AddStatsFromEquipment(self):
        for equipment in self.Equiped:
            if self.Equiped[equipment] != None:
                item = Item.FindItem(self.Equiped[equipment])
                self.EquipmentMaxHealth += item.MaxHealth
                self.EquipmentAttack += item.Damage
                self.EquipmentDefence += item.Defence
                self.EquipmentSpeed += item.Speed
        player.SetMaxHealth(player.Stats['MaxHealth'] + self.EquipmentMaxHealth)
        player.SetAttack(player.Stats['Attack'] + self.EquipmentAttack)
        player.SetDefence(player.Stats['Defence'] + self.EquipmentDefence)
        player.SetSpeed(player.Stats['Speed'] + self.EquipmentSpeed)

    def ResetStatsFromEquipment(self):
        player.Stats['MaxHealth'] -= self.EquipmentMaxHealth
        player.Stats['Attack'] -= self.EquipmentAttack
        player.Stats['Defence'] -= self.EquipmentDefence
        player.Stats['Speed'] -= self.EquipmentSpeed
        self.EquipmentMaxHealth = 0
        self.EquipmentAttack = 0
        self.EquipmentDefence = 0
        self.EquipmentSpeed = 0
    
    @staticmethod
    def Die():
        player.ResetStats()

    def GetHealth(self):
        return self.Stats['Health']
    
    def SetHealth(self,Value):
        self.Stats['Health'] = Value
        if self.Stats['Health'] > self.Stats['MaxHealth']: self.Stats['Health'] = self.Stats['MaxHealth']
        if self.Stats['Health'] < 0: self.SetHealth(0)
    
    def GetMaxHealth(self):
        return self.Stats['MaxHealth']
    
    def SetMaxHealth(self,Value):
        self.Stats['MaxHealth'] = Value
        if self.Stats['MaxHealth'] < 0: self.Stats['MaxHealth'] = 0
    
    def GetAttack(self):
        return self.Stats['Attack']
    
    def SetAttack(self,Value):
        self.Stats['Attack'] = Value
        if self.Stats['Attack'] < 0: self.Stats['Attack'] = 0
    
    def GetDefence(self):
        return self.Stats['Defence']
    
    def SetDefence(self,Value):
        self.Stats['Defence'] = Value
        if self.Stats['Defence'] < 0: self.Stats['Defence'] = 0
    
    def GetSpeed(self):
        return self.Stats['Speed']
    
    def SetSpeed(self,Value):
        self.Stats['Speed'] = Value
        if self.Stats["Speed"] < 0: self.Stats["Speed"] = 0

player = Player()


def SavesMenu():
    saves = []
    for file in os.listdir(SaveFilePath):
        filename = os.fsdecode(file)
        if filename.endswith(".json"): 
            saves.append(file)
    Target = 0
    ExitIndex = len(saves)
    while True:
        MainText = Engine.Text("")
        SideText = Engine.Text("")
        MainText.append("Found %s save files" %len(saves)).stylize(HIGH_LIGHT_COLOR,6,8)
        for index , name in enumerate(saves):
            if index == Target: SideText.append('> %s \n' % name.split(".")[0] ,style="u %s" %HIGH_LIGHT_COLOR)
            else: SideText.append('%s \n' % name.split(".")[0])
            
        MainText.append('\nChoose a save file you want to load')
        if ExitIndex == Target: SideText.append('> Go to menu',style="u %s" %HIGH_LIGHT_COLOR)
        else: SideText.append('Go to menu')

        layout['Main'].update(Engine.Panel(MainText,style="%s" %PANEL_COLOR))
        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                Target -= 1
                if Target < 0: Target = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                Target += 1
                if Target > ExitIndex: Target = 0
            case Key.KEY_enter | Key.KEY_space :
                if Target == ExitIndex: return False
                if Load(str(saves[Target]).split(".json")[0]) == 0: return False
                return True

def AutoSave():
    if player.CurrentSaveFileName != "":
        Save(player.CurrentSaveFileName)

def Save(SaveName:str):
    items = []
    equiped = player.Equiped
    for x in player.Inventory:
        items.append(x.name)
    Save = {
        "PlayerClass": player.Class,
        "Player" : {
            'Health' : player.GetHealth(),
            'MaxHealth' : player.GetMaxHealth(),
            'Attack' : player.GetAttack(),
            'Defence' : player.GetDefence(),
            'Speed' : player.Stats['Speed']
        },
        "Inventory" : {
            'Gold' : player.Gold,
            'Items' : items,
            'Potions' : player.Potions,
            'Equiped' : equiped
        },
        "EquipmentBonus" : {
            "MaxHealth" : player.EquipmentMaxHealth,
            "Attack" : player.EquipmentAttack,
            "Defence" : player.EquipmentDefence,
            "Speed" : player.EquipmentSpeed
        },
        "GameVersion": GameVersion
    }
    # time.sleep(1)
    with open(SaveFilePath+"/"+SaveName +".json", "w") as write_file:
        json.dump(Save, write_file)
        write_file.close()
    player.CurrentSaveFileName = SaveName

def Load(SaveName:str):
    player.CurrentSaveFileName = SaveName.split(".json")[0]
    try:
        with open(SaveFilePath+"/"+SaveName+".json", "r") as read_file:
            data = json.load(read_file)
            read_file.close()
    except:
        layout['Side'].update(Engine.Panel(Engine.Text("Can't open/load this save file!",style="red"),style="%s" %PANEL_COLOR))
        time.sleep(2)
        return 0
    if data['GameVersion'] != GameVersion:
        layout['Side'].update(Engine.Panel(Engine.Text("Save game version is diffrent form curent version\nLoad? Y/N"),style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'n':
                return 0
    player.SetAllStats(data['Player'],data["PlayerClass"])
    player.Gold = data['Inventory']['Gold']
    player.Potions = data['Inventory']['Potions']
    player.Equiped = data['Inventory']['Equiped']
    player.EquipmentMaxHealth = data['EquipmentBonus']["MaxHealth"]
    player.EquipmentAttack = data['EquipmentBonus']["Attack"]
    player.EquipmentDefence = data['EquipmentBonus']["Defence"]
    player.EquipmentSpeed = data['EquipmentBonus']["Speed"]
    for x in data['Inventory']['Items']:
        for y in Item.ItemBase:
            if x == y.name:
                player.Inventory.append(y)
    return 1

def GenerateItemsSelled():
    SelledItems = []
    while len(SelledItems) <= 10:
        rng = random.randrange(0,len(Item.ItemBase))
        item = Item.ItemBase[rng]
        isActive = False
        for ActiveItem in SelledItems:
            if ActiveItem == item:
                isActive = True
                break
        if isActive == False: SelledItems.append(item)
    return SelledItems

def Shop(SelledItems):
    ActiveWindow = 0  # 0-inventory  1-shop
    TargetOption = 0
    ShopItems = SelledItems
    layout['Shop'].visible = True
    CurrentPage = 0
    ItemsPerPage = 10
    while True:
        Pages = [[]]
        LoopedPage = 0
        for x in player.Inventory:
            if len(Pages[LoopedPage]) >= ItemsPerPage:
                LoopedPage += 1
                Pages.append([])
            Pages[LoopedPage].append(x)

        TargetItem = None
        ShopText = Engine.Text()
        SideText = Engine.Text()
        if ActiveWindow == 0: ExitIndex = len(Pages[CurrentPage])
        else: ExitIndex = len(ShopItems)
        if TargetOption > ExitIndex: TargetOption = ExitIndex
        if len(Pages[CurrentPage]) > 0:
            for index, Item in enumerate(Pages[CurrentPage]):
                if index == TargetOption and ActiveWindow == 0: 
                    SideText.append("> %s \n" % Item.name ,style="u %s" %HIGH_LIGHT_COLOR)
                    TargetItem = Item
                else: SideText.append("%s \n" % Item.name)
        if TargetOption == ExitIndex and ActiveWindow == 0: SideText.append("> Go back \n" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: SideText.append("Go back \n")

        for index, Item in enumerate(ShopItems):
            if index == TargetOption and ActiveWindow == 1: 
                ShopText.append("> %s \n" % Item.name ,style="u %s" %HIGH_LIGHT_COLOR)
                TargetItem = Item
            else: ShopText.append("%s \n" % Item.name)
        if TargetOption == ExitIndex and ActiveWindow == 1: ShopText.append("> Go back \n" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: ShopText.append("Go back \n")
        
        if TargetItem != None: layout['Main'].update(Engine.Panel(TargetItem.ShowStats(),title=f"Gold: {player.Gold}",style="%s" %PANEL_COLOR))
        else: layout['Main'].update(Engine.Panel(player.PrintStats(),title=f"Gold: {player.Gold}",style="%s" %PANEL_COLOR))

        layout['Side'].update(Engine.Panel(SideText,title=f"Inventory Page {CurrentPage}",style="%s" %PANEL_COLOR))
        layout['Shop'].update(Engine.Panel(ShopText,title="Shop",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case Key.KEY_a | Key.KEY_Aleft :
                if ActiveWindow == 0:
                    CurrentPage -= 1
                    if CurrentPage < 0 : CurrentPage = len(Pages)-1
            case Key.KEY_d | Key.KEY_Aright :
                if ActiveWindow == 0:
                    CurrentPage += 1
                    if CurrentPage > len(Pages)-1: CurrentPage = 0
            case Key.KEY_tab:
                ActiveWindow += 1
                if ActiveWindow > 1: ActiveWindow = 0
            case Key.KEY_enter | Key.KEY_space :
                if TargetOption == ExitIndex:
                    layout['Shop'].visible = False
                    return
                if TargetItem != None:
                    if ActiveWindow == 0: 
                        if player.SellItem(TargetItem) == True:
                            ShopItems.append(TargetItem)
                    if ActiveWindow == 1:
                        if player.BuyItem(TargetItem) == True:
                            ShopItems.remove(TargetItem)

def ShowInventory(): 
    TargetOption = 0
    CurrentPage = 0
    ItemsPerPage = 10
    while True:
        Pages = [[]]
        #SET PAGES
        LoopedPage = 0
        for x in player.Inventory:
            if len(Pages[LoopedPage]) >= ItemsPerPage:
                LoopedPage += 1
                Pages.append([])
            Pages[LoopedPage].append(x)
        TargetItem = None
        ExitIndex = len(player.Potions) + len(Pages[CurrentPage])
        if TargetOption > ExitIndex: TargetOption = ExitIndex
        SideText = Engine.Text("")
        SideText.append("Potions: \n")
        for index, name in enumerate(player.Potions):
            if index == TargetOption: 
                SideText.append("> %s - %s\n" % (name,player.Potions[name]) ,style="u %s" %HIGH_LIGHT_COLOR)
                TargetItem = name
            else: SideText.append("%s - %s\n" % (name,player.Potions[name]))
        SideText.append("\nItems: \n")
        if len(Pages[CurrentPage]) > 0:
            for index, ItemObject in enumerate(Pages[CurrentPage]):
                if index+len(player.Potions) == TargetOption: 
                    SideText.append("> %s \n" % ItemObject.name ,style="u %s" %HIGH_LIGHT_COLOR)
                    TargetItem = ItemObject.name
                else: SideText.append("%s \n" % ItemObject.name)
            
        if TargetOption == ExitIndex: SideText.append("> Go back \n" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: SideText.append("Go back \n")

        ItemStats = Item.FindItem(TargetItem)
        if ItemStats != None: layout['Main'].update(Engine.Panel(ItemStats.ShowStats(),title="Player",style="%s" %PANEL_COLOR))
        else: layout['Main'].update(Engine.Panel(player.PrintStats(),title="Player",style="%s" %PANEL_COLOR))

        layout['Side'].update(Engine.Panel(SideText,title=f"Inventory Page {CurrentPage+1}/{len(Pages)}",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetOption -= 1
                if TargetOption < 0 : TargetOption = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case Key.KEY_a | Key.KEY_Aleft :
                CurrentPage -= 1
                if CurrentPage < 0 : CurrentPage = len(Pages)-1
            case Key.KEY_d | Key.KEY_Aright :
                CurrentPage += 1
                if CurrentPage > len(Pages)-1: CurrentPage = 0
            case Key.KEY_enter | Key.KEY_space :
                if TargetOption == ExitIndex: return
                if TargetItem != None:
                    player.UsePotion(TargetItem)
                    player.UseItem(TargetItem)

def ShowEquipment():
    TargetOption = 0
    ExitIndex = len(player.Equiped)
    while True:
        TargetItem = None
        EquipmentText = Engine.Text("")
        for index , name in enumerate(player.Equiped):
            ItemName = player.Equiped[name]
            if TargetOption == index:
                EquipmentText.append("> %s - %s \n" %(name,ItemName) ,style="u %s" %HIGH_LIGHT_COLOR)
                TargetItem = ItemName
            else: EquipmentText.append("%s - %s \n" %(name,ItemName))
        if TargetOption == ExitIndex: EquipmentText.append("> Go back" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: EquipmentText.append("Go back")

        ItemStats = Item.FindItem(TargetItem)
        if ItemStats != None: layout['Main'].update(Engine.Panel(ItemStats.ShowStats(),title="Player",style="%s" %PANEL_COLOR))
        else: layout['Main'].update(Engine.Panel(player.PrintStats(),title="Player",style="%s" %PANEL_COLOR))

        layout['Side'].update(Engine.Panel(EquipmentText,title="Equipement",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case Key.KEY_enter | Key.KEY_space :
                if TargetOption == ExitIndex: return
                if TargetItem != None:
                    layout['Side'].update(Engine.Panel(player.RemoveEquipment(TargetItem),title="Equipement",style="%s" %PANEL_COLOR))
                    time.sleep(1)

def ChooseCharacter():
    layout['Side'].update(Engine.Panel(Engine.Text("Choose your character!"),style="%s" %PANEL_COLOR))
    TargetCharacter = 0
    ExitIndex = len(CharacterClass.Classes)
    while True: 
        text = Engine.Text("")
        for index , _ in enumerate(CharacterClass.Classes):
            if TargetCharacter == index: text.append(f"> {CharacterClass.Classes[index].Name}\n" ,style="u %s" %HIGH_LIGHT_COLOR)
            else: text.append(f"{CharacterClass.Classes[index].Name}\n")
        if TargetCharacter == ExitIndex: text.append("> Go to menu" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: text.append("Go to menu")

        layout['Main'].update(Engine.Panel(text,title="Character Select",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetCharacter -= 1
                if TargetCharacter < 0: TargetCharacter = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                TargetCharacter += 1
                if TargetCharacter > ExitIndex: TargetCharacter = 0
            case Key.KEY_enter | Key.KEY_space :
                if TargetCharacter == ExitIndex: return False

                if TargetCharacter in range(len(CharacterClass.Classes)+1):
                    player.SetAllStats(CharacterClass.Classes[TargetCharacter].Stats , CharacterClass.Classes[TargetCharacter].Name)
                    layout['Side'].update(Engine.Panel(Engine.Text(f"You've choosen {CharacterClass.Classes[TargetCharacter].Name}",style="green"),style="%s" %PANEL_COLOR))
                    time.sleep(1)
                    return True
                else:
                    layout['Side'].update(Engine.Panel(Engine.Text("Character doesn't exist!",style="red"),style="%s" %PANEL_COLOR))

def CalculateDamage(Damage:int,Defence:int):
    reduction = 1+Defence/100
    result = Damage/reduction
    return int(result)

def CalculateEvadeChance(speed):
    if speed == 0: speed = 1
    return round(1.4*speed**0.7)+1

def Fight(Monster):  # TODO ADD EVADE CHANCE TO FIGHTS AND TRYING TO ESCAPE THE FUNCTION IS READY IN '''TEST.PY'''
    layout['Side'].update(Engine.Panel(GameNamePrint(),style="%s" %PANEL_COLOR))
    Options = ["Attack","Inventory","Equipment","Run Away"]
    TargetOption = 0
    ExitIndex = len(Options)
    enemy = Monster
    enemy.SetMaxHealth()
    while True:
        if player.GetHealth() <= 0:
            layout['Main'].update(Engine.Panel(GameNamePrint(),title="Game",style="%s" %PANEL_COLOR))
            layout['Side'].update(Engine.Panel(Engine.Text("You died!",style="red"),style="%s" %PANEL_COLOR))
            Game.wait_for_input()
            return 0
        MainText = Engine.Text("")
        SideText = Engine.Text("")

        for index , Option in enumerate(Options):
            if TargetOption == index: MainText.append("> %s \n" %Option ,style="u %s" %HIGH_LIGHT_COLOR)
            else: MainText.append("%s \n" %Option)

        SideText.append("You're now fighting %s \n"%enemy.name).stylize("red", 20,20+len(enemy.name))
        SideText.append("%s/%s Health \n" %(enemy.Stats['Health'],enemy.Stats['MaxHealth']))
        SideText.append("%s Attack \n" %enemy.Stats['Attack'])
        SideText.append("%s Defence \n" %enemy.Stats['Defence'])
        SideText.append("%s Speed \n\n" %enemy.Stats['Speed'])
        SideText.append(player.PrintStats())
        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
        layout['Main'].update(Engine.Panel(MainText,title="Fight",style="%s" %PANEL_COLOR))

        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case Key.KEY_enter | Key.KEY_space :
                match TargetOption:
                    case 0:
                        SideText = Engine.Text("",justify="center")
                        # PLAYER ATTACKS
                        if random.randint(0,100) in range(0,CalculateEvadeChance(enemy.Stats['Speed'])):
                            # ENEMY DODGED THE ATTACK
                            SideText.append("%s have dodged your attack \n" %enemy.name)
                            SideText.append('%s Health %s/%s \n\n' %(enemy.name ,enemy.GetHealth() ,enemy.Stats['MaxHealth']))
                        else:
                            SideText.append("You've dealt %s damage \n" %CalculateDamage(player.GetAttack() ,enemy.Stats['Defence']))
                            enemy.SetHealth(enemy.GetHealth() - CalculateDamage(player.GetAttack() ,enemy.Stats['Defence']))
                            SideText.append('%s Health %s/%s \n\n' %(enemy.name ,enemy.GetHealth() ,enemy.Stats['MaxHealth']))

                        if enemy.Stats['Health'] <= 0:
                            SideText.append("You've killed %s \n" %enemy.name, style="red")
                            dropped = enemy.LootTable.RollForItem(player)
                            if dropped != None:   
                                SideText.append("\nIt dropped a %s" %dropped , style="green")
                            layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
                            return 0
                        # ENEMY ATTACKS
                        if random.randint(0,100) in range(0,CalculateEvadeChance(player.GetSpeed())):
                            # PLATER DODGED THE ATTACK
                            SideText.append("You've dodged the attack \n")
                            SideText.append("Player's Health %s/%s \n" %(player.Stats['Health'],player.Stats['MaxHealth']))
                        else:
                            player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                            SideText.append("\n%s dealt %s damage \n" %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                            SideText.append("Player's Health %s/%s \n" %(player.Stats['Health'],player.Stats['MaxHealth']))
                        
                        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
                        Game.wait_for_input()
                    case 1:
                        ShowInventory()
                    case 2:
                        ShowEquipment()
                    case ExitIndex:
                        if random.randint(0,50) in CalculateEvadeChance(player.GetSpeed()):
                            layout['Side'].update(Engine.Panel(Engine.Text("You've escaped from %s" %enemy.name),style="%s" %PANEL_COLOR))
                            return 0
                        else:
                            SideText = Engine.Text("")
                            SideText.append('You failled to escape\n\n')
                            player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                            SideText.append("%s dealt %s damage \n" %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                            SideText.append("Player's Health %s/%s " %(player.Stats['Health'],player.Stats['MaxHealth']))
                            layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
                            Game.wait_for_input()

def NextTurn():
    MainText = Engine.Text("You took a next turn")
    layout['Main'].update(Engine.Panel(MainText,title=f"Health {player.GetHealth()}/{player.GetMaxHealth()}",style="%s" %PANEL_COLOR))
    rng = random.randint(0,100)
    SideText = Engine.Text("",justify="center")
    if rng in range(0,15):
        SideText.append('You found a place to rest\n')
        ProcentHealthRested = random.randint(5,25)/100
        HpRested = round(player.GetMaxHealth() * ProcentHealthRested)
        player.SetHealth(player.GetHealth()+HpRested)
        SideText.append("And recoverd %s Health\n" % HpRested).stylize("green",39,46+len(str(HpRested)))
        SideText.append("Current Health %s/%s" %(round(player.GetHealth()),player.GetMaxHealth()))
        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
    elif rng in range(16,80):
        RandomEnemy = Monster.RollNextEnemy()
        TargetOption = 0
        while True:
            SideText = Engine.Text("")
            SideText.append('On your way you encounter a \n %s \n' %RandomEnemy.name).stylize("red",30,30+len(RandomEnemy.name))
            SideText.append('Do you want to fight?\n')
            AnswerText = Engine.Text("")
            if TargetOption == 0: AnswerText.append('Yes/No').stylize("u %s" %HIGH_LIGHT_COLOR ,0,3)
            else: AnswerText.append('Yes/No').stylize("u %s" %HIGH_LIGHT_COLOR ,4)
            
            layout['Side'].update(Engine.Panel(Engine.Text.assemble(SideText,AnswerText,justify="center"),style="%s" %PANEL_COLOR))
            match Game.get_input():
                case Key.KEY_w | Key.KEY_Aup :
                    TargetOption -= 1
                    if TargetOption < 0: TargetOption = 1
                case Key.KEY_s | Key.KEY_Adown :
                    TargetOption += 1
                    if TargetOption > 1: TargetOption = 0
                case Key.KEY_enter | Key.KEY_space :
                    if TargetOption == 0:
                        Fight(RandomEnemy)
                        return
                    if random.randint(0,50) in range(0,CalculateEvadeChance(player.GetSpeed())):
                        layout['Side'].update(Engine.Panel(Engine.Text("You've escaped from a %s" %RandomEnemy.name,justify="center"),style="%s" %PANEL_COLOR))
                        return
                    layout['Side'].update(Engine.Panel(Engine.Text("You failed to escape from a %s" %RandomEnemy.name,justify="center"),style="%s" %PANEL_COLOR))
                    Game.wait_for_input()
                    Fight(RandomEnemy)
                    return
    elif rng in range(81,95):
        player.Potions['Health Potion'] += 1
        SideText.append('Wow! you found a\nHealing potion\nYou now have %s' % player.Potions['Health Potion']).stylize("green",17,31)
        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
    elif rng in range(96,100):
        rngItem = random.randint(0,len(Item.ItemBase)-1)
        founditem = Item.ItemBase[rngItem]
        player.Inventory.append(founditem)
        SideText.append('You found an\n %s \nlying on the ground' % founditem.name).stylize("green",14,14+len(founditem.name))
        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
    else:
        SideText = Engine.Text("",justify="center")
        SideText.append("You found a traces of footsteps\nAt the end of them you found\n")
        SideText.append(' %s ' % NeskoGlasses.name)
        player.Inventory.append(NeskoGlasses)
        layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))

def Play():
    layout['Side'].update(Engine.Panel(player.PrintStats(),style="%s" %PANEL_COLOR))
    TargetOption = 0
    Options = ['Next Turn','Shop','Inventory','Equipment','Go to menu']
    ExitIndex = len(Options)-1
    ShopItems = GenerateItemsSelled()
    TurnsAfterShopChange = 0
    while True:
        if player.GetHealth() <= 0: 
            player.Die()
            return 0
        MainText = Engine.Text("")
        for index , name in enumerate(Options):
            if index == TargetOption: MainText.append("> %s \n" %name ,style="u %s" %HIGH_LIGHT_COLOR)
            else: MainText.append("%s \n" %name)

        layout['Main'].update(Engine.Panel(MainText,title="Game",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case Key.KEY_s | Key.KEY_Adown :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case Key.KEY_enter | Key.KEY_space :
                match TargetOption:
                    case 0:
                        AutoSave()
                        NextTurn()
                        TurnsAfterShopChange += 1
                        if TurnsAfterShopChange >= 5:
                            ShopItems = GenerateItemsSelled()
                            TurnsAfterShopChange = 0
                        Game.wait_for_input()
                    case 1:
                        Shop(ShopItems)
                    case 2:
                        ShowInventory()
                    case 3:
                        ShowEquipment()
                    case ExitIndex:
                        answer = 0
                        while True:
                            text = Engine.Text("Do you want to save before quiting?\n")
                            answerText = Engine.Text("")
                            if answer == 0: answerText.append("Yes/No").stylize("u %s" %HIGH_LIGHT_COLOR ,0,3)
                            else: answerText.append("Yes/No").stylize("u %s" %HIGH_LIGHT_COLOR ,4)
                            layout['Side'].update(Engine.Panel(Engine.Text.assemble(text,answerText,justify='center'),style="%s" %PANEL_COLOR))
                            match Game.get_input():
                                case Key.KEY_w | Key.KEY_Aup :
                                    answer -= 1
                                    if answer < 0: answer = 1
                                case Key.KEY_s | Key.KEY_Adown :
                                    answer += 1
                                    if answer > 1: answer = 0
                                case Key.KEY_enter | Key.KEY_space :
                                    match answer:
                                        case 0:
                                            layout['Side'].update(Engine.Panel(Engine.Text("Type a save file name",justify='center'),style="%s" %PANEL_COLOR))
                                            SaveFileName = Engine.Text("")
                                            while True:
                                                userInput = Engine.msvcrt.getwch()
                                                if userInput == '\r': break
                                                SaveFileName = Engine.Text(Game.TextBoxInput(SaveFileName,userInput))
                                                HelpText = Engine.Text("Type a save file name\n")
                                                layout['Side'].update(Engine.Panel(Engine.Text.assemble(HelpText,SaveFileName,justify="center"),style="%s" %PANEL_COLOR))
                                            if str(SaveFileName) == "":
                                                if player.CurrentSaveFileName == "": 
                                                    player.CurrentSaveFileName = ('AutoSave-%s-%s' %(player.Class,date.today()))
                                                AutoSave()
                                            else: Save(str(SaveFileName))
                                            player.Die()
                                            return 0
                                        case 1:
                                            player.Die()
                                            return 0
        layout['Side'].update(Engine.Panel(player.PrintStats(),style="%s" %PANEL_COLOR))

def GameNamePrint(Style:str = "spring_green2"):
    text = Engine.Text("",justify="center")
    text.append('____ ___  ____    ____ ____ _  _ ____ \n',style=f'{Style}')
    text.append('|__/ |__] | __    | __ |__| |\/| |___ \n',style=f'{Style}')
    text.append('|  \ |    |__]    |__] |  | |  | |___ \n',style=f'{Style}')
    return text

def Menu():
    options = ['Play','Load','Development Info','Exit']
    TargetOption = 0
    ExitIndex = len(options)-1
    while True:
        MainText = Engine.Text("")
        layout['Side'].update(Engine.Panel(GameNamePrint(),style="%s" %PANEL_COLOR))
        for index, name in enumerate(options):
            if TargetOption == index: MainText.append("> %s \n" %name ,style="u %s" %HIGH_LIGHT_COLOR)
            else: MainText.append("%s \n" %name)

        layout['Main'].update(Engine.Panel(MainText,title="Menu" ,style="%s" %PANEL_COLOR))
        match Game.get_input():
            case Key.KEY_w | Key.KEY_Aup :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case Key.KEY_s | Key.KEY_Adown:
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case Key.KEY_enter | Key.KEY_space :
                match TargetOption:
                    case 0:
                        if ChooseCharacter():
                            player.CurrentSaveFileName = ('AutoSave-%s-%s' %(player.Class,date.today()))
                            Play()
                    case 1:
                        if SavesMenu() == True:
                            Play()
                    case 2:
                        layout['Side'].update(Engine.Panel(DeveloperInfoMenu(),style="%s" %PANEL_COLOR))
                        Game.wait_for_input()
                    case ExitIndex:
                        sys.exit()
    return

def DeveloperInfoMenu():
    text = Engine.Text("")
    text.append("Development info\n",style="cyan")
    text.append("Game Roadmap:\n",style="deep_sky_blue4")
    text.append("1.Add Merchants\n2.Add speed statistic which allow for:\n- Higher escape chance from monsters\n- Chance to not get hit by a monster")
    text.append("3.Balance current gameplay\n4.Add more Items and Monsters\n")
    text.append("5.Add Leveling system and exp gathering from fights\n")
    text.append("Change Log:\n",style="spring_green4")
    text.append("Changed the game to work with the new GUI\nReworked game input\nChanged Default font and screen size\n")
    text.append("Currently adding merchants and Thief events.\n")
    text.append('Press any button to continue',style="blink bright_black")
    return text


if __name__ == '__main__':
    with Engine.Live(layout,refresh_per_second=60,screen=True) as live:
        Menu()
    FontSize.run(16)
