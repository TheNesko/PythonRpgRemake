import time, sys, os, random, json
import rich , Engine
from datetime import date
from Engine import Game

import FontSize
from Instances import *

#----Window-Setup-----#
Game.disable_quickedit()
Game.window('Game',70,30)
#Set font size to 20
FontSize.run(20)

Engine.layout = Engine.Layout()
Engine.console = Engine.Console()

Engine.layout.split_column(
    Engine.Layout(name='Main',ratio=1),
    Engine.Layout(name='SideSplit',ratio=2)
)
Engine.layout["SideSplit"].split_row(
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
            'Defence' : 1
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
                    Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %PANEL_COLOR))
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
                Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %PANEL_COLOR))
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
        text.append('%s Defence \n' %self.GetDefence(),)
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
        player.Stats['MaxHealth'] += self.EquipmentMaxHealth
        player.Stats['Attack'] += self.EquipmentAttack
        player.Stats['Defence'] += self.EquipmentDefence

    def ResetStatsFromEquipment(self):
        player.Stats['MaxHealth'] -= self.EquipmentMaxHealth
        player.Stats['Attack'] -= self.EquipmentAttack
        player.Stats['Defence'] -= self.EquipmentDefence
        self.EquipmentMaxHealth = 0
        self.EquipmentAttack = 0
        self.EquipmentDefence = 0
    
    @staticmethod
    def Die():
        player.ResetStats()

    def GetHealth(self):
        return self.Stats['Health']
    
    def SetHealth(self,Value):
        self.Stats['Health'] = Value
        if self.GetHealth() > self.GetMaxHealth(): self.SetHealth(self.GetMaxHealth())
        if self.GetHealth() < 0: self.SetHealth(0)
    
    def GetMaxHealth(self):
        return self.Stats['MaxHealth']
    
    def SetMaxHealth(self,Value):
        self.Stats['MaxHealth'] = Value
    
    def GetAttack(self):
        return self.Stats['Attack']
    
    def SetAttack(self,Value):
        self.Stats['Attack'] = Value
    
    def GetDefence(self):
        return self.Stats['Defence']
    
    def SetDefence(self,Value):
        self.Stats['Defence'] = Value

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

        Engine.layout['Main'].update(Engine.Panel(MainText,style="%s" %PANEL_COLOR))
        Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' :
                Target -= 1
                if Target < 0: Target = ExitIndex
            case 's' :
                Target += 1
                if Target > ExitIndex: Target = 0
            case '\r' | ' ':
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
            'Defence' : player.GetDefence()
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
            "Defence" : player.EquipmentDefence
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
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Can't open/load this save file!",style="red"),style="%s" %PANEL_COLOR))
        time.sleep(2)
        return 0
    if data['GameVersion'] != GameVersion:
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Save game version is diffrent form curent version\nLoad? Y/N"),style="%s" %PANEL_COLOR))
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
    Engine.layout['Shop'].visible = True
    while True:
        TargetItem = None
        ShopText = Engine.Text()
        SideText = Engine.Text()
        if ActiveWindow == 0: ExitIndex = len(player.Inventory)
        else: ExitIndex = len(ShopItems)
        if TargetOption > ExitIndex: TargetOption = 0
        if len(player.Inventory) > 0:
            for index, Item in enumerate(player.Inventory):
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
        
        if TargetItem != None: Engine.layout['Main'].update(Engine.Panel(TargetItem.ShowStats(),title=f"Gold: {player.Gold}",style="%s" %PANEL_COLOR))
        else: Engine.layout['Main'].update(Engine.Panel(player.PrintStats(),title="Player",style="%s" %PANEL_COLOR))

        Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %PANEL_COLOR))
        Engine.layout['Shop'].update(Engine.Panel(ShopText,title="Shop",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's' :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case 'a' :
                ActiveWindow -= 1
                if ActiveWindow < 0: ActiveWindow = 1
            case 'd' :
                ActiveWindow += 1
                if ActiveWindow > 1: ActiveWindow = 0
            case '\r' | ' ':
                if TargetOption == ExitIndex:
                    Engine.layout['Shop'].visible = False
                    return
                if TargetItem != None:
                    if ActiveWindow == 0: 
                        if player.SellItem(TargetItem) == True:
                            ShopItems.append(TargetItem)
                    if ActiveWindow == 1:
                        if player.BuyItem(TargetItem) == True:
                            ShopItems.remove(TargetItem)

def ShowInventory():  #TODO ADD PAGES TO INVENTORY/SHOP SO ITEMS WON'T GO BEYOND THE SCREEN
    TargetOption = 0
    while True:
        TargetItem = None
        ExitIndex = len(player.Potions) + len(player.Inventory)
        SideText = Engine.Text("")
        SideText.append("Potions: \n")
        for index, name in enumerate(player.Potions):
            if index == TargetOption: 
                SideText.append("> %s - %s\n" % (name,player.Potions[name]) ,style="u %s" %HIGH_LIGHT_COLOR)
                TargetItem = name
            else: SideText.append("%s - %s\n" % (name,player.Potions[name]))
        SideText.append("\nItems: \n")
        if len(player.Inventory) > 0:
            for index, ItemObject in enumerate(player.Inventory):
                if index+len(player.Potions) == TargetOption: 
                    SideText.append("> %s \n" % ItemObject.name ,style="u %s" %HIGH_LIGHT_COLOR)
                    TargetItem = ItemObject.name
                else: SideText.append("%s \n" % ItemObject.name)
            
        if TargetOption == ExitIndex: SideText.append("> Go back \n" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: SideText.append("Go back \n")

        ItemStats = Item.FindItem(TargetItem)
        if ItemStats != None: Engine.layout['Main'].update(Engine.Panel(ItemStats.ShowStats(),title="Player",style="%s" %PANEL_COLOR))
        else: Engine.layout['Main'].update(Engine.Panel(player.PrintStats(),title="Player",style="%s" %PANEL_COLOR))

        Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's' :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case '\r' | ' ':
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
        if ItemStats != None: Engine.layout['Main'].update(Engine.Panel(ItemStats.ShowStats(),title="Player",style="%s" %PANEL_COLOR))
        else: Engine.layout['Main'].update(Engine.Panel(player.PrintStats(),title="Player",style="%s" %PANEL_COLOR))

        Engine.layout['Side'].update(Engine.Panel(EquipmentText,title="Equipement",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's' :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case '\r' | ' ':
                if TargetOption == ExitIndex: return
                if TargetItem != None:
                    Engine.layout['Side'].update(Engine.Panel(player.RemoveEquipment(TargetItem),title="Equipement",style="%s" %PANEL_COLOR))
                    time.sleep(1)

def ChooseCharacter():
    Engine.layout['Side'].update(Engine.Panel(Engine.Text("Choose your character!"),style="%s" %PANEL_COLOR))
    TargetCharacter = 0
    ExitIndex = len(CharacterClass.Classes)
    while True: 
        text = Engine.Text("")
        for index , _ in enumerate(CharacterClass.Classes):
            if TargetCharacter == index: text.append(f"> {CharacterClass.Classes[index].Name}\n" ,style="u %s" %HIGH_LIGHT_COLOR)
            else: text.append(f"{CharacterClass.Classes[index].Name}\n")
        if TargetCharacter == ExitIndex: text.append("> Go to menu" ,style="u %s" %HIGH_LIGHT_COLOR)
        else: text.append("Go to menu")

        Engine.layout['Main'].update(Engine.Panel(text,title="Character Select",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' :
                TargetCharacter -= 1
                if TargetCharacter < 0: TargetCharacter = ExitIndex
            case 's' :
                TargetCharacter += 1
                if TargetCharacter > ExitIndex: TargetCharacter = 0
            case '\r' | ' ':
                if TargetCharacter == ExitIndex: return False

                if TargetCharacter in range(len(CharacterClass.Classes)+1):
                    player.SetAllStats(CharacterClass.Classes[TargetCharacter].Stats , CharacterClass.Classes[TargetCharacter].Name)
                    Engine.layout['Side'].update(Engine.Panel(Engine.Text(f"You've choosen {CharacterClass.Classes[TargetCharacter].Name}",style="green"),style="%s" %PANEL_COLOR))
                    time.sleep(1)
                    return True
                else:
                    Engine.layout['Side'].update(Engine.Panel(Engine.Text("Character doesn't exist!",style="red"),style="%s" %PANEL_COLOR))

def CalculateDamage(Damage:int,Defence:int):
    reduction = 1+Defence/100
    result = Damage/reduction
    return int(result)

def Fight(Monster):
    Engine.layout['Side'].update(Engine.Panel(GameNamePrint(),style="%s" %PANEL_COLOR))
    Options = ["Attack","Inventory","Equipment","Run Away"]
    TargetOption = 0
    ExitIndex = len(Options)
    enemy = Monster
    enemy.SetMaxHealth()
    while True:
        if player.GetHealth() <= 0:
            Engine.layout['Main'].update(Engine.Panel(GameNamePrint(),title="Game",style="%s" %PANEL_COLOR))
            Engine.layout['Side'].update(Engine.Panel(Engine.Text("You died!",style="red"),style="%s" %PANEL_COLOR))
            Game.wait_for_input()
            return 0
        MainText = Engine.Text("")
        SideText = Engine.Text("")

        for index , Option in enumerate(Options):
            if TargetOption == index: MainText.append("> %s \n" %Option ,style="u %s" %HIGH_LIGHT_COLOR)
            else: MainText.append("%s \n" %Option)

        SideText.append("You're now fighting %s \n"%enemy.name)
        SideText.append("%s/%s Health \n" %(enemy.Stats['Health'],enemy.Stats['MaxHealth']))
        SideText.append("%s Attack \n" %enemy.Stats['Attack'])
        SideText.append("%s Defence \n\n" %enemy.Stats['Defence'])
        SideText.append(player.PrintStats())
        Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
        Engine.layout['Main'].update(Engine.Panel(MainText,title="Fight",style="%s" %PANEL_COLOR))

        match Game.get_input():
            case 'w' :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's' :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case '\r' | ' ':
                match TargetOption:
                    case 0:
                        SideText = Engine.Text("")
                        SideText.append("You've dealt %s damage \n" %CalculateDamage(player.GetAttack() ,enemy.Stats['Defence']))
                        enemy.SetHealth(enemy.GetHealth() - CalculateDamage(player.GetAttack() ,enemy.Stats['Defence']))
                        SideText.append('%s Health %s/%s \n' %(enemy.name ,enemy.GetHealth() ,enemy.Stats['MaxHealth']))
                        if enemy.Stats['Health'] <= 0:
                            SideText.append("You've killed %s \n" %enemy.name)
                            dropped = enemy.LootTable.RollForItem(player)
                            if dropped != None:   
                                SideText.append("It dropped a %s" %dropped)
                            else:
                                SideText.append("It didn't drop anything")
                            Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
                            return 0
                        player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                        SideText.append("\n%s dealt %s damage \n" %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                        SideText.append("Player's Health %s/%s \n" %(player.Stats['Health'],player.Stats['MaxHealth']))
                        Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
                        Game.wait_for_input()
                    case 1:
                        ShowInventory()
                    case 2:
                        ShowEquipment()
                    case ExitIndex:
                        x = random.randint(0,1)
                        if x == 0:
                            Engine.layout['Side'].update(Engine.Panel(Engine.Text("You've escaped from %s" %enemy.name),style="%s" %PANEL_COLOR))
                            return 0
                        else:
                            SideText = Engine.Text("")
                            SideText.append('You failled to escape')
                            player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                            SideText.append("\n%s dealt %s damage " %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                            SideText.append("Player's Health %s/%s " %(player.Stats['Health'],player.Stats['MaxHealth']))
                            Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
                            Game.wait_for_input()

def NextTurn():
    MainText = Engine.Text("You took a next turn")
    Engine.layout['Main'].update(Engine.Panel(MainText,title=f"Health {player.GetHealth()}/{player.GetMaxHealth()}",style="%s" %PANEL_COLOR))
    rng = random.randint(0,100)
    SideText = Engine.Text("",justify="center")
    if rng in range(21,45):
        SideText.append('You found a place to rest\n')
        ProcentHealthRested = random.randint(5,25)/100
        HpRested = round(player.GetMaxHealth() * ProcentHealthRested)
        player.SetHealth(player.GetHealth()+HpRested)
        SideText.append("And recoverd %s Health\n" % HpRested)
        SideText.append("Current Health %s/%s" %(round(player.GetHealth()),player.GetMaxHealth()))
        Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
    elif rng in range(46,80):
        RandomEnemy = Monster.RollNextEnemy()
        TargetOption = 0
        while True:
            SideText = Engine.Text("")
            SideText.append('On your way you encounter a %s \n' %RandomEnemy.name)
            SideText.append('Do you want to fight?\n')
            AnswerText = Engine.Text("")
            if TargetOption == 0: AnswerText.append('Yes/No').stylize("u %s" %HIGH_LIGHT_COLOR ,0,3)
            else: AnswerText.append('Yes/No').stylize("u %s" %HIGH_LIGHT_COLOR ,4)
            
            Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(SideText,AnswerText,justify="center"),style="%s" %PANEL_COLOR))
            match Game.get_input():
                case 'w' :
                    TargetOption -= 1
                    if TargetOption < 0: TargetOption = 1
                case 's' :
                    TargetOption += 1
                    if TargetOption > 1: TargetOption = 0
                case "\r" | " ":
                    if TargetOption == 0:
                        Fight(RandomEnemy)
                        return
                    EscapeChance = random.randint(0,2)
                    if EscapeChance == 0:
                        Engine.layout['Side'].update(Engine.Panel(Engine.Text("You failed to escape from a %s" %RandomEnemy.name),style="%s" %PANEL_COLOR))
                        Fight(RandomEnemy)
                        return
                    Engine.layout['Side'].update(Engine.Panel(Engine.Text("You've escaped from a %s" %RandomEnemy.name),style="%s" %PANEL_COLOR))
                    return
    elif rng in range(81,95):
        player.Potions['Health Potion'] += 1
        SideText.append('Wow! you found a Healing potion\nYou now have %s' % player.Potions['Health Potion'])
        Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
    elif rng in range(96,100):
        rngItem = random.randint(0,len(Item.ItemBase)-1)
        founditem = Item.ItemBase[rngItem]
        player.Inventory.append(founditem)
        SideText.append('You found an %s lying on the ground' % founditem.name)
        Engine.layout['Side'].update(Engine.Panel(SideText,style="%s" %PANEL_COLOR))
    else: Engine.layout['Side'].update(Engine.Panel(Engine.Text("Nothing excites happens on your journey",justify="center"),style="%s" %PANEL_COLOR))

def Play():
    Engine.layout['Side'].update(Engine.Panel(player.PrintStats(),style="%s" %PANEL_COLOR))
    TargetOption = 0
    Options = ['Next Turn','Shop (WIP)','Inventory','Equipment','Go to menu']
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

        Engine.layout['Main'].update(Engine.Panel(MainText,title="Game",style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' :
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's' :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case '\r' | ' ':
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
                            Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(text,answerText,justify='center'),style="%s" %PANEL_COLOR))
                            match Game.get_input():
                                case 'w' :
                                    answer -= 1
                                    if answer < 0: answer = 1
                                case 's' :
                                    answer += 1
                                    if answer > 1: answer = 0
                                case '\r' | ' ':
                                    match answer:
                                        case 0:
                                            Engine.layout['Side'].update(Engine.Panel(Engine.Text("Type a save file name",justify='center'),style="%s" %PANEL_COLOR))
                                            SaveFileName = Engine.Text("")
                                            while True:
                                                userInput = Engine.msvcrt.getwch()
                                                if userInput == '\r': break
                                                SaveFileName = Engine.Text(Game.TextBoxInput(SaveFileName,userInput))
                                                HelpText = Engine.Text("Type a save file name\n")
                                                Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(HelpText,SaveFileName,justify="center"),style="%s" %PANEL_COLOR))
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
        Engine.layout['Side'].update(Engine.Panel(player.PrintStats(),style="%s" %PANEL_COLOR))

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
        Engine.layout['Side'].update(Engine.Panel(GameNamePrint(),style="%s" %PANEL_COLOR))
        for index, name in enumerate(options):
            if TargetOption == index: MainText.append("> %s \n" %name ,style="u %s" %HIGH_LIGHT_COLOR)
            else: MainText.append("%s \n" %name)

        Engine.layout['Main'].update(Engine.Panel(MainText,title="Menu" ,style="%s" %PANEL_COLOR))
        match Game.get_input():
            case 'w' | "\r'P'":
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's' :
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case '\r' | ' ':
                match TargetOption:
                    case 0:
                        if ChooseCharacter():
                            player.CurrentSaveFileName = ('AutoSave-%s-%s' %(player.Class,date.today()))
                            Play()
                    case 1:
                        if SavesMenu() == True:
                            Play()
                    case 2:
                        Engine.layout['Side'].update(Engine.Panel(DeveloperInfoMenu(),style="%s" %PANEL_COLOR))
                        Game.wait_for_input()
                    case ExitIndex:
                        sys.exit()
    return

def DeveloperInfoMenu():
    text = Engine.Text("")
    text.append("Development info\n\n",style="cyan")
    text.append("Game Roadmap:\n",style="deep_sky_blue4")
    text.append("1.Add shops and currency\n2.Balance current gameplay\n3.Add more Items and Monsters\n")
    text.append("4.Add Leveling system and exp gathering from fights\n5.Expand loot tables and refactor it's code\n\n")
    text.append("Change Log:\n",style="spring_green4")
    text.append("Changed the game to work with the new GUI\nfixed some crashes\nfor now removed selling items and gold\n\n")
    text.append("Currently adding shops(shop is done) and merchants\nMerchants you will be able to encounter in the wilderness.")
    text.append("They can sell you some really good items but they are really rare\n\n")
    text.append('Press any button to continue',style="blink bright_black")
    return text


if __name__ == '__main__':
    with Engine.Live(Engine.layout,refresh_per_second=60,screen=True) as live:
        Menu()


'''

Ideas:
1. Evade chance (not to get damaged for monsters and classes useful for ranger class)

'''