import time, sys, os, random, json
from turtle import title
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
GameVersion= "0.0.3"
SaveFilePath = os.getenv('APPDATA')+"\SuperNiceGame"
CurrentSaveFileName = ""
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
            'HealthPotion' : 5
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
    
    def RemoveEquipment(self,ItemName):
        item = Item.FindItem(ItemName)
        if item == None: return

        if player.Equiped[item.EquipPlace] != None:
            player.Equiped[item.EquipPlace] = None
            player.Inventory.append(item)
            rprint("You've taken off a [blue]%s[/blue]" % item.name)
        else:
            print("You don't have that item equiped")
        Game.wait_for_input()

    def UsePotion(self,Name:str):
        self.PotionHealProcent = 0.25
        match Name:
            case 'HealthPotion':
                if self.Potions[Name] <= 0:
                    print("You don't have any Health Potions")
                    Game.wait_for_input()
                    return
                self.Potions[Name] -= 1
                HealthBefore = round(player.GetHealth())
                Heal = round(player.GetMaxHealth() * self.PotionHealProcent)
                player.SetHealth(player.GetHealth() + Heal)
                HealthAfter = round(player.GetHealth())
                HealValue = HealthAfter - HealthBefore
                print("You've used a Health Potion")
                rprint("It healed you for [green]%s[/green]" %HealValue)
                rprint("Current health [green]%s[/green]/[red]%s[/red]" %(round(player.GetHealth()),player.GetMaxHealth()))
                Game.wait_for_input()
    
    def SetAllStats(self,NewStats,Class):
        self.Class = Class
        self.Stats = NewStats
    
    def ResetStats(self):
        self.Class = None
        self.Gold = 0
        self.Inventory = []
        self.Potions['HealthPotion'] = 5
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
        text.append("Class: %s" %self.Class)
        text.append("%s/%s Health" %(self.GetHealth(),self.GetMaxHealth()))
        text.append('%s Attack' %self.GetAttack())
        text.append('%s Defence' %self.GetDefence(),)
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
        if len(self.ClassUse) != 0:
            ClassesToCheck = len(self.ClassUse)
            for Class in self.ClassUse:
                if Class.Name == player.Class:
                    break
                ClassesToCheck -= 1
                if ClassesToCheck == 0:
                    rprint("[blue]%s[/blue] is not for your class : [blue]%s[/blue]" % (self.name, player.Class))
                    Game.wait_for_input()
                    return
        if player.Equiped[self.EquipPlace] == None:
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
            rprint("You've used [blue]%s[/blue]" % self.name)
        else:
            rprint("You've exchanged a [blue]%s[/blue] for [blue]%s[/blue]" % (player.Equiped[self.EquipPlace], self.name))
            player.Inventory.append(Item.FindItem(player.Equiped[self.EquipPlace]))
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
        player.ResetStatsFromEquipment()
        player.AddStatsFromEquipment()
        Game.wait_for_input()
    
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
    
    def SetMaxHealth(self):
        self.Stats['Health'] = self.Stats['MaxHealth']


#=========Instances=========
player = Player()
#----Classes---
WarriorClass = CharacterClass('Warrior',70,30,20)
RangerClass = CharacterClass('Ranger',100,25,10)
MageClass = CharacterClass('Mage',50,40,5)
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
WizzardHat = Item('Wizzard Hat',10,5,5,0,Helmet,[MageClass])
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
WarewolfLoot.addLoot(IronChestplate,5)
WarewolfLoot.addLoot(IronLeggins,7)
WarewolfLoot.addLoot(WoodenBow,10)
WarewolfLoot.addLoot(BegginersWand,10)
WarewolfLoot.addLoot(IronDagger,10)
WarewolfLoot.addLoot(IronSword,7)
WarewolfLoot.addLoot(None,100)
Warewolf = Monster("Warewolf",70,20,30,WarewolfLoot)
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
GhostLoot.addLoot(BegginersWand,9)
GhostLoot.addLoot(WizzardHat,11)
GhostLoot.addLoot(StudentCape,10)
GhostLoot.addLoot(MagicTome,8)
GhostLoot.addLoot(MagicOrb,5)
GhostLoot.addLoot(None,100)
Ghost = Monster('Ghost',25,5,500,GhostLoot)


#===========================

def ShowInventory():
    while True:
        Game.Clear()
        rprint("[yellow]Gold %s[/yellow]" % player.Gold)
        rprint("[blue]Inventory[/blue]")
        if not len(player.Inventory) <= 0:
            for x in player.Inventory:
                print(x.name)
        rprint("\n[blue]Potions[/blue]")
        for x in player.Potions:
            print(x,"-",player.Potions[x])
        rprint("\nType the name of and item you want to use\nType [red]'Sell'[/red] before an Item to sell it\n0.Go back")
        answer = input()
        Game.Clear()
        if answer.lower().split(" ")[0] == "sell":
            ItemForSell = answer.split(" ",1)[1]
            if Item.FindItem(ItemForSell) != None:
                ItemPrice = Item.FindItem(ItemForSell).Price
                rprint("Do you want to sell %s for [yellow]%s Gold[/yellow]" %(ItemForSell,ItemPrice))
                match input().lower():
                    case 'yes' | 'y':
                        Game.Clear()
                        player.SellItem(ItemForSell)
                        rprint("You just sold %s for [yellow]%s Gold[/yellow]" %(ItemForSell,ItemPrice))
                        Game.wait_for_input()
        match answer:
            case '0':
                return 0
            case _:
                player.UsePotion(answer)
                player.UseItem(answer)

def ShowEquipment():
    while True:
        Game.Clear()
        rprint("[blue]Equipment[/blue]")
        for x in player.Equiped:
            print(x,"-",player.Equiped[x])
        rprint("\nType the name of and item you want to use\n0.Go back")
        x = input()
        Game.Clear()
        match x:
            case '0':
                return 0
            case _:
                player.RemoveEquipment(x)

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
            case 'w':
                TargetCharacter -= 1
                if TargetCharacter < 0: TargetCharacter = ExitIndex
            case 's':
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
    rng = random.randint(0,100)
    if rng in range(0,30):
        print('Lucky you! Nothing happend')
        Game.wait_for_input()
    elif rng in range(31,50):
        print('You found a place to rest')
        ProcentHealthRested = random.randint(5,25)/100
        HpRested = round(player.GetMaxHealth() * ProcentHealthRested)
        player.SetHealth(player.GetHealth()+HpRested)
        rprint("And recoverd [green]%s[/green] Health" % HpRested)
        rprint("Current Health [green]%s[/green]/[red]%s[/red]" %(round(player.GetHealth()),player.GetMaxHealth()))
        Game.wait_for_input()
    elif rng in range(51,80):
        RandomEnemy = RollNextEnemy()
        rprint('Oh no you came across a [blue]%s[/blue]' %RandomEnemy.name)
        Game.wait_for_input()
        Fight(RandomEnemy)
    elif rng in range(81,95):
        player.Potions['HealthPotion'] += 1
        print('Wow! you found a Healing potion\nYou now have %s' % player.Potions['HealthPotion'])
        Game.wait_for_input()
    elif rng in range(96,100):
        rngItem = random.randint(0,len(Item.ItemBase)-1)
        founditem = Item.ItemBase[rngItem]
        player.Inventory.append(founditem)
        rprint('You found an [blue]%s[/blue] lying on the ground' % founditem.name)
        Game.wait_for_input()
    
def Fight(Monster:Monster):
    Game.Clear()
    enemy = Monster
    enemy.SetMaxHealth()
    while True:
        if player.GetHealth() <= 0:
            print("You died!")
            Game.wait_for_input()
            return 0
        rprint("You're now fighting [blue]%s[/blue] "%enemy.name)
        rprint("[green]%s[/green]/[red]%s[/red] Health" %(enemy.Stats['Health'],enemy.Stats['MaxHealth']))
        rprint("[red]%s[/red] Attack " %enemy.Stats['Attack'])
        rprint("[red]%s[/red] Defence " %enemy.Stats['Defence'])
        rprint("1.Attack\n2.inventory\n3.Show Stats\n0.Run Away")
        next_move = Game.get_input()
        Game.Clear()
        match next_move:
            case '1':
                rprint("[blue]You[/blue]'ve dealt [red] %s[/red] damage " %CalculateDamage(player.GetAttack(),enemy.Stats['Defence']))
                enemy.Stats['Health'] -= CalculateDamage(player.GetAttack(),enemy.Stats['Defence'])
                rprint('%s Health [green]%s[/green]/[red]%s[/red]' %(enemy.name,enemy.Stats['Health'],enemy.Stats['MaxHealth']))
                if enemy.Stats['Health'] <= 0:
                    rprint("You've killed [red]%s[red]" %enemy.name)
                    dropped = enemy.LootTable.Roll()
                    if not dropped == None:   
                        rprint("It dropped a [green]%s[/green]" %dropped)
                    Game.wait_for_input()
                    return 0
                player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                rprint("\n[blue]%s[/blue] dealt [red]%s[/red] damage " %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                rprint("Player's Health [green]%s[/green]/[red]%s[/red] " %(player.Stats['Health'],player.Stats['MaxHealth']))
                Game.wait_for_input()
                Game.Clear()
            case '2':
                ShowInventory()
                Game.Clear()
            case '3':
                player.PrintStats()
                Game.Clear()
            case '0':
                x = random.randint(0,1)
                if x == 0:
                    print('You escaped safely')
                    Game.wait_for_input()
                    return 0
                else:
                    print('You failled to escape')
                    player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                    rprint("\n[blue]%s[/blue] dealt [red]%s[/red] damage " %(enemy.name,CalculateDamage(enemy.Stats['Attack'],player.GetDefence())))
                    rprint("Player's Health [green]%s[/green]/[red]%s[/red] " %(player.Stats['Health'],player.Stats['MaxHealth']))
                    Game.wait_for_input()
                    Game.Clear()
            case _:
                Game.Clear()

def CalculateDamage(Damage:int,Defence:int):
    reduction = 1+Defence/100
    result = Damage/reduction
    return int(result)

def Play():
    Engine.layout['Side'].update(Engine.Panel(GameNamePrint()))
    TargetOption = 0
    Options = ['Next Turn','Shop (WIP)','Inventory','Equipment','Show Stats','Go to menu']
    ExitIndex = len(Options)-1
    while True:
        if player.GetHealth() <= 0: 
            player.Die()
            return 0
        MainText = Engine.Text("")
        for index , name in enumerate(Options):
            if index == TargetOption: MainText.append("> %s \n" %name)
            else: MainText.append("%s \n" %name)

        Engine.layout['Main'].update(Engine.Panel(MainText,title="Game"))
        match Game.get_input():
            case 'w':
                TargetOption -= 1
                if TargetOption < 0: TargetOption = ExitIndex
            case 's':
                TargetOption += 1
                if TargetOption > ExitIndex: TargetOption = 0
            case '\r' | ' ':
                match TargetOption:
                    case 0:
                        NextTurn()
                    case 1:
                        pass
                    case 2:
                        ShowInventory()
                    case 3:
                        ShowEquipment()
                    case 4:
                        Engine.layout['Side'].update(Engine.Panel(player.PrintStats()))
                    case 5:
                        while True:
                            Game.Clear()
                            Engine.layout['Side'].update(Engine.Panel(Engine.Text("Do you want to save before quiting? Yes/No",justify='center')))
                            match Game.get_input():
                                case 'y':
                                    Engine.layout['Side'].update(Engine.Panel(Engine.Text("Type a save file name",justify='center')))
                                    SaveFileName = Engine.Text("")
                                    while True:
                                        userInput = Game.get_input()
                                        if userInput == '\r' and SaveFileName != "": break
                                        SaveFileName = Engine.Text(Game.TextBoxInput(SaveFileName,userInput))
                                        HelpText = Engine.Text("Type a save file name\n")
                                        Engine.layout['Side'].update(Engine.Panel(Engine.Text.assemble(HelpText,SaveFileName)))
                                    Save(str(SaveFileName))
                                    player.Die()
                                    return 0
                                case 'n':
                                    return 0
                                case _:
                                    break

def GameNamePrint(Style:str = "red"):
    text = Engine.Text("",justify="center")
    text.append('____ ___  ____    ____ ____ _  _ ____ \n',style=f'{Style}')
    text.append('|__/ |__] | __    | __ |__| |\/| |___ \n',style=f'{Style}')
    text.append('|  \ |    |__]    |__] |  | |  | |___ \n',style=f'{Style}')
    return text

def Menu():
    Engine.layout['Side'].update(Engine.Panel(GameNamePrint()))
    Engine.layout['Main'].update(Engine.Panel(Engine.Text("1.Play\n2.Load\n3.Development Info\n0.Exit"),title="Menu"))
    match Game.get_input():
        case '0':
            sys.exit()
        case '1':
            if ChooseCharacter():
                CurrentSaveFileName = f'AutoSave-{player.Class}{date.today()}'
                Play()
        case '2':
            if SavesMenu():
                Play()
        case '3':
            Engine.layout['Side'].update(Engine.Panel(DeveloperInfoMenu()))
            Game.wait_for_input()
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
            case 'w':
                Target -= 1
                if Target < 0: Target = ExitIndex
            case 's':
                Target += 1
                if Target > ExitIndex: Target = 0
            case '\r' | ' ':
                if Target == ExitIndex: return False
                if Load(saves[Target]) == 0: return False
    return True

        
def AutoSave():
    if CurrentSaveFileName != "":
        Save(CurrentSaveFileName)

def Save(SaveName:str):
    items = []
    equiped = player.Equiped
    for x in player.Inventory:
        items.append(x.name)
    Save = {
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
        "PlayerClass": player.Class,
        "GameVersion": GameVersion,
    }
    time.sleep(1)
    with open(SaveFilePath+"/"+SaveName +".json", "w") as write_file:
        json.dump(Save, write_file)
    CurrentSaveFileName = SaveName

def Load(SaveName:str):
    CurrentSaveFileName = SaveName
    Game.Clear()
    try:
        with open(SaveFilePath+"/"+SaveName+".json", "r") as read_file:
            data = json.load(read_file)
    except:
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Can't load this save file!",style="red")))
        time.sleep(2)
        return 0
    if data['GameVersion'] != GameVersion:
        Engine.layout['Side'].update(Engine.Panel(Engine.Text("Save game version is diffrent form curent version\nLoad? Y/N")))
        answer = input().lower()
        if answer == "n": return 0
    
    player.SetAllStats(data['Player'],data['PlayerClass'])
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
    text.append("Added auto save\n")
    text.append("fixed some crashes\n")
    text.append("Currently reworking GUI\n")
    text.append('Press any button to continue',style="blink bright_black")
    return text



if __name__ == '__main__':
    with Engine.Live(Engine.layout,screen=True) as live:
        while True:
            Menu()


'''
---------------------------------------------
Ideas:
1. Evade chance (not to get damaged for monsters and classes useful for ranger class)
---------------------------------------------
TO DO:
Gold ---DONE---
shop ---NEXT---
Add Gold To loot table
Add more Items
Add more Monsters
Add EXP and LEVELS to player and Monsters
Balance the game
---------------------------------------------
'''