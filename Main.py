import time, sys, os, random, json
from rich import print as rprint
import rich , Engine
from datetime import date
from Engine import Game

Game.disable_quickedit()
Game.window('Game',50,40)

Engine.layout = Engine.Layout()
Engine.console = Engine.Console()

Engine.layout.split_column(
    Engine.Layout(name='Main',ratio=1),
    Engine.Layout(name='Side',ratio=2)
)


#---------
GameVersion = "0.0.6"
SaveFilePath = os.getenv('APPDATA')+"\SuperNiceGame"
try: 
    os.mkdir(SaveFilePath) 
except OSError as error: 
    pass
#---------


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
                x.Use()
                break
    
    def SellItem(self,Name):
        if len(player.Inventory) <= 0: return
        for x in player.Inventory:
            if Name == x.name:
                x.Sell()
                break
    
    def RemoveEquipment(self,EquipedItem):
        item = Item.FindItem(EquipedItem)
        if item == None: return Engine.Text("You have nothing equiped!")
        if player.Equiped[item.EquipPlace] != None:
            player.Equiped[item.EquipPlace] = None
            player.Inventory.append(item)
            return Engine.Text("You've taken off a %s" % item.name)
        return Engine.Text("You don't have that item equiped")

    def UsePotion(self,Name:str):
        self.PotionHealProcent = 0.25
        SideText = Engine.Text("")
        match Name:
            case 'Health Potion':
                if self.Potions[Name] <= 0:
                    SideText.append("You don't have any Health Potions")
                    Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory"))
                    Game.wait_for_input()
                    return
                self.Potions[Name] -= 1
                HealthBefore = round(player.GetHealth())
                Heal = round(player.GetMaxHealth() * self.PotionHealProcent)
                player.SetHealth(player.GetHealth() + Heal)
                HealthAfter = round(player.GetHealth())
                HealValue = HealthAfter - HealthBefore
                SideText.append("You've used a Health Potion\n")
                SideText.append("It healed you for %s \n" %HealValue)
                SideText.append("Current health %s/%s \n" %(round(player.GetHealth()),player.GetMaxHealth()))
                Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory"))
                Game.wait_for_input()
    
    def SetAllStats(self,NewStats,NewClass): #TODO load class
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

class CharacterClass:

    Classes = []

    def __init__(self,Name:str,MaxHealth:int,Attack:int,Defence:int):
        self.Name = Name
        self.Stats = {
            'Health' : MaxHealth,
            'MaxHealth' : MaxHealth,
            'Attack' : Attack,
            'Defence' : Defence
        }
        CharacterClass.Classes.append(self)

class LootTable:
    def __init__(self):
        self.Loot = []
        self.PossibleLoot = []
    
    def addLoot(self,Item,Weight:int):
        self.Drop = {
            'Item': Item,
            'Weight' : Weight
        }
        self.PossibleLoot.append(self.Drop)

    def Roll(self):
        self.Loot = []
        self.AllWeights = 0
        self.Dropped = None
        self.previous = None
        for x in self.PossibleLoot:
            self.LootItem = {
                'Item': None,
                'MinChance': 0,
                'MaxChance': 0
            }
            self.AllWeights += x['Weight']
            self.LootItem['Item'] = x['Item']
            if self.previous == None:
                self.LootItem['MinChance'] = 1
                self.LootItem['MaxChance'] = x['Weight']
            else:
                self.LootItem['MinChance'] = (self.previous['MaxChance'] + 1)
                self.LootItem['MaxChance'] = (self.previous['MaxChance'] + x['Weight'])
            self.Loot.append(self.LootItem)
            self.previous = self.LootItem
        rng = random.randint(1,self.AllWeights)
        for x in self.Loot:
            if rng <= x['MaxChance'] and rng >= x['MinChance']:
                if x['Item'] != None:
                    self.Dropped = x
        if self.Dropped != None:
            player.Inventory.append(self.Dropped['Item'])
        if self.Dropped == None:
            return None
        return self.Dropped['Item'].name

class Item:

    ItemBase = []

    def __init__(self,Name:str,Price:int,Damage:int,Defence:int,MaxHealth:int,EquipPlace:str,ClassUse=[]):
        self.name = Name
        self.Price = Price
        self.Damage = Damage
        self.Defence = Defence
        self.MaxHealth = MaxHealth
        self.EquipPlace = EquipPlace
        # if 'ClassUse' is empty that means every class can use that item
        self.ClassUse = ClassUse
        Item.ItemBase.append(self)
    
    def Use(self):
        SideText = Engine.Text("")
        if len(self.ClassUse) != 0:
            ClassesToCheck = len(self.ClassUse)
            for Class in self.ClassUse:
                if Class.Name == player.Class:
                    break
                ClassesToCheck -= 1
                if ClassesToCheck == 0:
                    SideText.append("%s is not for your class : %s" % (self.name, player.Class))
                    Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory"))
                    time.sleep(1)
                    return
        if player.Equiped[self.EquipPlace] == None:
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
            SideText.append("You've used %s" % self.name)
        else:
            SideText.append("You've exchanged a %s for %s" % (player.Equiped[self.EquipPlace], self.name))
            player.Inventory.append(Item.FindItem(player.Equiped[self.EquipPlace]))
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
        player.ResetStatsFromEquipment()
        player.AddStatsFromEquipment()
        Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory"))
        time.sleep(1)
    
    def Sell(self):
        if len(player.Inventory) <= 0: return
        for index , _ in enumerate(player.Inventory):
            if player.Inventory[index] == self:
                player.Gold += self.Price
                player.Inventory.remove(self)

    def FindItem(ItemName):
        for x in Item.ItemBase:
            if x.name == ItemName:
                return x
        return None

class Monster:

    MonsterBase = []

    def __init__(self,Name:str,MaxHealth:int,Attack:int,Defence:int,LootTable:LootTable):
        self.name = Name
        self.Stats = {
            'Health' : MaxHealth,
            'MaxHealth' : MaxHealth,
            'Attack' : Attack,
            'Defence' : Defence
        }
        self.LootTable = LootTable
        Monster.MonsterBase.append(self)
    
    def GetHealth(self):
        return self.Stats['Health']
    
    def SetHealth(self,value):
        self.Stats['Health'] = value
        if self.Stats['Health'] > self.Stats['MaxHealth']: self.Stats['Health'] = self.Stats['MaxHealth']
        if self.Stats['Health'] < 0: self.Stats['Health'] = 0
    
    def SetMaxHealth(self):
        self.Stats['Health'] = self.Stats['MaxHealth']


#=========Instances=========
player = Player()
#----Classes---
WarriorClass = CharacterClass('Warrior',120,30,20)
RangerClass = CharacterClass('Ranger',100,25,10)
MageClass = CharacterClass('Mage',70,40,5)
TitanClass = CharacterClass('Titan',1000,1000,1000)
#----Items-----

Helmet = 'Helmet'
Chestplate = 'Chestplate'
Leggins = 'Leggins'
LeftHand = 'LeftHand'
RightHand = 'RightHand'

#---Leather---
LeatherHelmet = Item('Leather Helmet',10,0,5,0,Helmet)
LeatherChestplate = Item('Leather Chestplate',10,0,7,5,Chestplate)
LeatherLeggins = Item('Leather Leggins',10,0,5,0,Leggins)
LeatherGloves = Item('Leather Gloves',10,0,5,0,LeftHand)
#---Iron---
IronHelmet = Item('Iron Helmet',10,0,5,5,Helmet,[WarriorClass])
IronChestplate = Item('Iron Chestplate',10,0,30,10,Chestplate,[WarriorClass])
IronLeggins = Item('Iron Leggins',10,0,10,0,Leggins,[WarriorClass])
IronShield = Item('Iron Shield',10,-10,20,0,LeftHand,[WarriorClass])
IronSword = Item('Iron Sword',10,10,0,0,RightHand,[WarriorClass])
IronDagger = Item('Iron Dagger',10,7,0,0,RightHand,[RangerClass,MageClass])
#---Wooden---
WoodenShield = Item('Wooden Shield',10,-5,10,0,LeftHand,[WarriorClass])
WoodenSword = Item('Wooden Sword',10,5,0,0,RightHand,[WarriorClass])
WoodenBow = Item('Wooden Bow',10,10,0,0,RightHand,[RangerClass])
#---Magic---
BegginersWand = Item('Begginers Wand',10,10,0,0,RightHand,[MageClass])
StudentCape = Item('Student Cape',10,5,5,5,Chestplate,[MageClass])
WizardHat = Item('Wizard Hat',10,5,5,0,Helmet,[MageClass])
MagicTome = Item('Magic Tome',10,10,0,0,LeftHand,[MageClass])
MagicOrb = Item('Magic Orb',10,20,0,0,LeftHand,[MageClass])
#---Other---
Chainmail = Item('Chainmail',10,0,10,5,Chestplate,[RangerClass,WarriorClass])

#----Zombie----
ZombieLoot = LootTable()
ZombieLoot.addLoot(WoodenSword,10)
ZombieLoot.addLoot(WoodenShield,9)
ZombieLoot.addLoot(IronSword,4)
ZombieLoot.addLoot(IronDagger,7)
ZombieLoot.addLoot(IronShield,4)
ZombieLoot.addLoot(Chainmail,8)
ZombieLoot.addLoot(None,100)
Zombie = Monster('Zombie',60,15,20,ZombieLoot)
#----Warewolf----
WarewolfLoot = LootTable()
WarewolfLoot.addLoot(IronHelmet,7)
WarewolfLoot.addLoot(IronChestplate,5)
WarewolfLoot.addLoot(IronLeggins,7)
WarewolfLoot.addLoot(WoodenBow,10)
WarewolfLoot.addLoot(BegginersWand,10)
WarewolfLoot.addLoot(IronDagger,10)
WarewolfLoot.addLoot(IronSword,7)
WarewolfLoot.addLoot(None,100)
Warewolf = Monster("Warewolf",50,20,20,WarewolfLoot)
#----Skeleton----
SkeletonLoot = LootTable()
SkeletonLoot.addLoot(Chainmail,10)
SkeletonLoot.addLoot(LeatherHelmet,9)
SkeletonLoot.addLoot(LeatherLeggins,5)
SkeletonLoot.addLoot(LeatherGloves,7)
SkeletonLoot.addLoot(LeatherChestplate,4)
SkeletonLoot.addLoot(WoodenBow,8)
SkeletonLoot.addLoot(None,100)
Skeleton = Monster('Skeleton',45,10,10,SkeletonLoot)
#-----Ghost-----
GhostLoot = LootTable()
GhostLoot.addLoot(BegginersWand,5)
GhostLoot.addLoot(WizardHat,9)
GhostLoot.addLoot(StudentCape,10)
GhostLoot.addLoot(MagicTome,8)
GhostLoot.addLoot(None,100)
Ghost = Monster('Ghost',15,5,500,GhostLoot)
#-----Thief-----
ThiefLoot = LootTable()
ThiefLoot.addLoot(LeatherHelmet,6)
ThiefLoot.addLoot(LeatherChestplate,4)
ThiefLoot.addLoot(LeatherLeggins,5)
ThiefLoot.addLoot(LeatherGloves,7)
ThiefLoot.addLoot(IronDagger,3)
ThiefLoot.addLoot(None,100)
Thief = Monster('Thief',25,10,5,ThiefLoot)
#-----Wraith-----
WraithLoot = LootTable()
WraithLoot.addLoot(BegginersWand,9)
WraithLoot.addLoot(StudentCape,7)
WraithLoot.addLoot(MagicTome,8)
WraithLoot.addLoot(MagicOrb,5)
WraithLoot.addLoot(None,100)
Wraith = Monster('Wraith',100,15,5,WraithLoot)
#-----Wraith-----
#===========================

def ShowInventory():
    TargetOption = 0
    TargetItem = None
    while True:
        ExitIndex = len(player.Potions) + len(player.Inventory)
        SideText = Engine.Text("")
        SideText.append("Potions: \n")
        for index, name in enumerate(player.Potions):
            if index == TargetOption: 
                SideText.append("> %s - %s\n" % (name,player.Potions[name]) ,style="u")
                TargetItem = name
            else: SideText.append("%s - %s\n" % (name,player.Potions[name]))
        SideText.append("Items: \n")
        if len(player.Inventory) > 0:
            for index, Item in enumerate(player.Inventory):
                if index+len(player.Potions) == TargetOption: 
                    SideText.append("> %s \n" % Item.name ,style="u")
                    TargetItem = Item.name
                else: SideText.append("%s \n" % Item.name)
            
        if TargetOption == ExitIndex: SideText.append("> Go back \n",style="u")
        else: SideText.append("Go back \n")

        Engine.layout['Main'].update(Engine.Panel(player.PrintStats(),title="Player"))
        Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory"))
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
                    # ItemPrice = Item.FindItem(TargetItem).Price
                    # rprint("Do you want to sell %s for [yellow]%s Gold[/yellow]" %(TargetItem,ItemPrice))
                    # match input().lower():
                    #     case 'yes' | 'y':
                    #         Game.Clear()
                    #         player.SellItem(TargetItem)
                    #         rprint("You just sold %s for [yellow]%s Gold[/yellow]" %(TargetItem,ItemPrice))
                    #         Game.wait_for_input()

                

def ShowEquipment():
    TargetOption = 0
    TargetItem = None
    ExitIndex = len(player.Equiped)
    while True:
        EquipmentText = Engine.Text("")
        for index , name in enumerate(player.Equiped):
            Item = player.Equiped[name]
            if TargetOption == index:
                EquipmentText.append("> %s - %s \n" %(name,Item),style="u")
                TargetItem = Item
            else: EquipmentText.append("%s - %s \n" %(name,Item))
        if TargetOption == ExitIndex: EquipmentText.append("> Go back", style="u")
        else: EquipmentText.append("Go back")
        Engine.layout['Side'].update(Engine.Panel(EquipmentText,title="Equipement"))
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
                    Engine.layout['Side'].update(Engine.Panel(player.RemoveEquipment(TargetItem),title="Equipement"))
                    time.sleep(1)

def ChooseCharacter():
    Engine.layout['Side'].update(Engine.Panel(Engine.Text("Choose your character!")))
    TargetCharacter = 0
    ExitIndex = len(CharacterClass.Classes)
    while True: 
        text = Engine.Text("")
        for index , _ in enumerate(CharacterClass.Classes):
            if TargetCharacter == index: text.append(f"> {CharacterClass.Classes[index].Name}\n",style="u")
            else: text.append(f"{CharacterClass.Classes[index].Name}\n")
        if TargetCharacter == ExitIndex: text.append("> Go to menu",style="u")
        else: text.append("Go to menu")

        Engine.layout['Main'].update(Engine.Panel(text,title="Character Select"))
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
                    Engine.layout['Side'].update(Engine.Panel(Engine.Text(f"You've choosen {CharacterClass.Classes[TargetCharacter].Name}",style="green")))
                    time.sleep(1)
                    return True
                else:
                    Engine.layout['Side'].update(Engine.Panel(Engine.Text("Character doesn't exist!",style="red")))

def RollNextEnemy() -> Monster:
    value = random.randint(0,len(Monster.MonsterBase)-1)
    return Monster.MonsterBase[value]

def NextTurn():
    MainText = Engine.Text("You took a next turn")
    Engine.layout['Main'].update(Engine.Panel(MainText,title=f"Health {player.GetHealth()}/{player.GetMaxHealth()}"))
    rng = random.randint(0,100)
    SideText = Engine.Text("",justify="center")
    if rng in range(0,20):
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Lucky you! Nothing happend",justify="center")))
    elif rng in range(21,45):
        SideText.append('You found a place to rest\n')
        ProcentHealthRested = random.randint(5,25)/100
        HpRested = round(player.GetMaxHealth() * ProcentHealthRested)
        player.SetHealth(player.GetHealth()+HpRested)
        SideText.append("And recoverd %s Health\n" % HpRested)
        SideText.append("Current Health %s/%s" %(round(player.GetHealth()),player.GetMaxHealth()))
        Engine.layout['Side'].update(Engine.Panel(SideText))
    elif rng in range(46,80):
        RandomEnemy = RollNextEnemy()
        TargetOption = 0
        while True:
            SideText = Engine.Text("")
            SideText.append('On your way you encounter a %s \n' %RandomEnemy.name)
            SideText.append('Do you want to fight?\n')
            AnswerText = Engine.Text("")
            if TargetOption == 0: AnswerText.append('Yes/No').stylize("u",0,3)
            else: AnswerText.append('Yes/No').stylize("u",4)
            
            Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(SideText,AnswerText,justify="center")))
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
                        Engine.layout['Side'].update(Engine.Panel(Engine.Text("You failed to escape from a %s" %RandomEnemy.name)))
                        Fight(RandomEnemy)
                        return
                    Engine.layout['Side'].update(Engine.Panel(Engine.Text("You've escaped from a %s" %RandomEnemy.name)))
                    return
    elif rng in range(81,95):
        player.Potions['Health Potion'] += 1
        SideText.append('Wow! you found a Healing potion\nYou now have %s' % player.Potions['Health Potion'])
        Engine.layout['Side'].update(Engine.Panel(SideText))
    elif rng in range(96,100):
        rngItem = random.randint(0,len(Item.ItemBase)-1)
        founditem = Item.ItemBase[rngItem]
        player.Inventory.append(founditem)
        SideText.append('You found an %s lying on the ground' % founditem.name)
        Engine.layout['Side'].update(Engine.Panel(SideText))
    
def Fight(Monster:Monster):
    Engine.layout['Side'].update(Engine.Panel(GameNamePrint()))
    Options = ["Attack","Inventory","Equipment","Run Away"]
    TargetOption = 0
    ExitIndex = len(Options)
    enemy = Monster
    enemy.SetMaxHealth()
    while True:
        if player.GetHealth() <= 0:
            Engine.layout['Main'].update(Engine.Panel(GameNamePrint(),title="Game"))
            Engine.layout['Side'].update(Engine.Panel(Engine.Text("You died!",style="red")))
            Game.wait_for_input()
            return 0
        MainText = Engine.Text("")
        SideText = Engine.Text("")

        for index , Option in enumerate(Options):
            if TargetOption == index: MainText.append("> %s \n" %Option)
            else: MainText.append("%s \n" %Option)

        SideText.append("You're now fighting %s \n"%enemy.name)
        SideText.append("%s/%s Health \n" %(enemy.Stats['Health'],enemy.Stats['MaxHealth']))
        SideText.append("%s Attack \n" %enemy.Stats['Attack'])
        SideText.append("%s Defence \n\n" %enemy.Stats['Defence'])
        SideText.append(player.PrintStats())
        Engine.layout['Side'].update(Engine.Panel(SideText))
        Engine.layout['Main'].update(Engine.Panel(MainText,title="Fight"))

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
                            dropped = enemy.LootTable.Roll()
                            if dropped != None:   
                                SideText.append("It dropped a %s" %dropped)
                            else:
                                SideText.append("It didn't drop anything")
                            Engine.layout['Side'].update(Engine.Panel(SideText))
                            return 0
                        player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                        SideText.append("\n%s dealt %s damage \n" %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                        SideText.append("Player's Health %s/%s \n" %(player.Stats['Health'],player.Stats['MaxHealth']))
                        Engine.layout['Side'].update(Engine.Panel(SideText))
                        Game.wait_for_input()
                    case 1:
                        ShowInventory()
                    case 2:
                        ShowEquipment()
                    case ExitIndex:
                        x = random.randint(0,1)
                        if x == 0:
                            Engine.layout['Side'].update(Engine.Panel(Engine.Text("You've escaped from %s" %enemy.name)))
                            return 0
                        else:
                            SideText = Engine.Text("")
                            SideText.append('You failled to escape')
                            player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                            SideText.append("\n%s dealt %s damage " %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                            SideText.append("Player's Health %s/%s " %(player.Stats['Health'],player.Stats['MaxHealth']))
                            Engine.layout['Side'].update(Engine.Panel(SideText))
                            Game.wait_for_input()

def CalculateDamage(Damage:int,Defence:int):
    reduction = 1+Defence/100
    result = Damage/reduction
    return int(result)

def Play():
    Engine.layout['Side'].update(Engine.Panel(player.PrintStats()))
    TargetOption = 0
    Options = ['Next Turn','Shop (WIP)','Inventory','Equipment','Go to menu']
    ExitIndex = len(Options)-1
    while True:
        if player.GetHealth() <= 0: 
            player.Die()
            return 0
        MainText = Engine.Text("")
        for index , name in enumerate(Options):
            if index == TargetOption: MainText.append("> %s \n" %name,style="u")
            else: MainText.append("%s \n" %name)

        Engine.layout['Main'].update(Engine.Panel(MainText,title="Game"))
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
                        Game.wait_for_input()
                        Engine.layout['Side'].update(Engine.Panel(player.PrintStats()))
                    case 1:
                        pass
                    case 2:
                        ShowInventory()
                        Engine.layout['Side'].update(Engine.Panel(player.PrintStats()))
                    case 3:
                        ShowEquipment()
                        Engine.layout['Side'].update(Engine.Panel(player.PrintStats()))
                    case ExitIndex:
                        answer = 0
                        while True:
                            text = Engine.Text("Do you want to save before quiting?\n")
                            answerText = Engine.Text("")
                            if answer == 0: answerText.append("Yes/No").stylize("u",0,3)
                            else: answerText.append("Yes/No").stylize("u",4)
                            Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(text,answerText,justify='center')))
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
                                            Engine.layout['Side'].update(Engine.Panel(Engine.Text("Type a save file name",justify='center')))
                                            SaveFileName = Engine.Text("")
                                            while True:
                                                userInput = Engine.msvcrt.getwch()
                                                if userInput == '\r': break
                                                SaveFileName = Engine.Text(Game.TextBoxInput(SaveFileName,userInput))
                                                HelpText = Engine.Text("Type a save file name\n")
                                                Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(HelpText,SaveFileName,justify="center")))
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

def GameNamePrint(Style:str = "red"):
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
        Engine.layout['Side'].update(Engine.Panel(GameNamePrint()))
        for index, name in enumerate(options):
            if TargetOption == index: MainText.append("> %s \n" %name , style="u")
            else: MainText.append("%s \n" %name)

        Engine.layout['Main'].update(Engine.Panel(MainText,title="Menu"))
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
                        Engine.layout['Side'].update(Engine.Panel(DeveloperInfoMenu()))
                        Game.wait_for_input()
                    case ExitIndex:
                        sys.exit()
    return

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
        MainText.append("Found %s save files" %len(saves)).stylize("bright_black",6,8)
        for index , name in enumerate(saves):
            if index == Target: SideText.append('> %s \n' % name.split(".")[0] ,style="u light_cyan1")
            else: SideText.append('%s \n' % name.split(".")[0])
            
        MainText.append('\nChoose a save file you want to load')
        if ExitIndex == Target: SideText.append('> Go to menu',style="u honeydew2")
        else: SideText.append('Go to menu')

        Engine.layout['Main'].update(Engine.Panel(MainText))
        Engine.layout['Side'].update(Engine.Panel(SideText))
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
        "GameVersion": GameVersion
    }
    # time.sleep(1)
    with open(SaveFilePath+"/"+SaveName +".json", "w") as write_file:
        json.dump(Save, write_file)
        write_file.close()
    player.CurrentSaveFileName = SaveName

def Load(SaveName:str):
    player.CurrentSaveFileName = SaveName.split(".json")[0]
    Game.Clear()
    try:
        with open(SaveFilePath+"/"+SaveName+".json", "r") as read_file:
            data = json.load(read_file)
            read_file.close()
    except:
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Can't open/load this save file!",style="red")))
        time.sleep(2)
        return 0
    if data['GameVersion'] != GameVersion:
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Save game version is diffrent form curent version\nLoad? Y/N")))
        match Game.get_input():
            case 'n':
                return 0
    player.SetAllStats(data['Player'],data["PlayerClass"])
    player.Gold = data['Inventory']['Gold']
    player.Potions = data['Inventory']['Potions']
    player.Equiped = data['Inventory']['Equiped']
    for x in data['Inventory']['Items']:
        for y in Item.ItemBase:
            if x == y.name:
                player.Inventory.append(y)
    return 1

def Debug():
    pass


def DeveloperInfoMenu():
    text = Engine.Text("")
    text.append("Development info\n\n",style="cyan")
    text.append("Game Roadmap:\n",style="deep_sky_blue4")
    text.append("1.Add shops and currency\n")
    text.append("2.Balance current gameplay\n")
    text.append("3.Add more Items and Monsters\n")
    text.append("4.Add Leveling system and exp gathering from fights\n")
    text.append("5.Expand loot tables and refactor it's code\n\n")
    text.append("Change Log:\n",style="spring_green4")
    text.append("Changed the game to work with the new GUI\n")
    text.append("fixed some crashes\n")
    text.append("for now removed selling items and gold\n")
    text.append("Currently adding shops and merchants\n")
    text.append('Press any button to continue',style="blink bright_black")
    return text



if __name__ == '__main__':
    with Engine.Live(Engine.layout,screen=True) as live:
        Menu()


'''

Ideas:
1. Evade chance (not to get damaged for monsters and classes useful for ranger class)

'''