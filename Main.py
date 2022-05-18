import time, sys, os, random, json
from Engine import Game

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
            print("You've taken off a %s" % item.name)
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
                print("It healed you for %s" %HealValue)
                print("Current health %s/%s" %(round(player.GetHealth()),player.GetMaxHealth()))
                Game.wait_for_input()
    
    def SetAllStats(self,NewStats,Class):
        self.Class = Class
        self.Stats = NewStats
    
    def ResetStats(self):
        self.Class = None
        self.Gold = 0
        self.Inventory.Game.Clear()
        self.Potions['HealthPotion'] = 5
        self.Equiped = {
            'Helmet' : None,
            'Chestplate' : None,
            'Leggins' : None,
            'LeftHand' : None,
            'RightHand' : None
        }
    
    def PrintStats(self):
        Game.Clear()
        print("Class: ",self.Class)
        print(self.GetHealth(),'/',self.GetMaxHealth(),' Health')
        print(self.GetAttack(),' Attack')
        print(self.GetDefence(),' Defence')
        print('Press any button to continue')
        Game.wait_for_input()
    
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
                    print("%s is not for your class : %s" % (self.name, player.Class))
                    Game.wait_for_input()
                    return
        if player.Equiped[self.EquipPlace] == None:
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
            print("You've used %s" % self.name)
        else:
            print("You've exchanged a %s for %s" % (player.Equiped[self.EquipPlace], self.name))
            player.Inventory.append(Item.FindItem(player.Equiped[self.EquipPlace]))
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
        player.ResetStatsFromEquipment()
        player.AddStatsFromEquipment()
        Game.wait_for_input()
    
    def Sell(self):
        if len(player.Inventory) <= 0: return
        for Item in range(len(player.Inventory)):
            if player.Inventory[Item] == self:
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
WarriorClass = CharacterClass('Worrior',70,30,20)
RangerClass = CharacterClass('Ranger',100,25,10)
MageClass = CharacterClass('Mage',50,40,5)
GodClass = CharacterClass('God',1000,1000,1000)
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
        print("Gold %s" % player.Gold)
        print("\nInventory")
        if not len(player.Inventory) <= 0:
            for x in player.Inventory:
                print(x.name)
        print("\nPotions")
        for x in player.Potions:
            print(x,"-",player.Potions[x])
        print("\nType the name of and item you want to use\nType 'Sell' before an Item to sell it\n0.Go back")
        answer = input()
        Game.Clear()
        if answer.lower().split(" ")[0] == "sell":
            ItemForSell = answer.split(" ",1)[1]
            if Item.FindItem(ItemForSell) != None:
                ItemPrice = Item.FindItem(ItemForSell).Price
                print("Do you want to sell %s for %s Gold" %(ItemForSell,ItemPrice))
                match input().lower():
                    case 'yes' | 'y':
                        Game.Clear()
                        player.SellItem(ItemForSell)
                        print("You just sold %s for %s Gold" %(ItemForSell,ItemPrice))
                        Game.wait_for_input()
                    case 'no' | 'n':
                        pass
        match answer:
            case '0':
                return 0
            case _:
                player.UsePotion(answer)
                player.UseItem(answer)

def ShowEquipment():
    while True:
        Game.Clear()
        print("Equipment")
        for x in player.Equiped:
            print(x,"-",player.Equiped[x])
        print("\nType the name of and item you want to use\n0.Go back")
        x = input()
        Game.Clear()
        match x:
            case '0':
                return 0
            case _:
                player.RemoveEquipment(x)

def ChooseCharacter():
    Game.Clear()
    while True:
        print('Choose your character!')
        for x in range(len(CharacterClass.Classes)):
            print(x+1,".",CharacterClass.Classes[x].Name,sep="")
        print("0.Menu")
        character = int(Game.get_input())
        Game.Clear()
        if character == 0:
            return 0
        elif character in range(len(CharacterClass.Classes)+1):
            player.SetAllStats(CharacterClass.Classes[character-1].Stats , CharacterClass.Classes[character-1].Name)
            return 1
        else:
            print("Character doesn't exist!")

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
        print("And recoverd %s Health" % HpRested)
        print("Current Health %s/%s" %(round(player.GetHealth()),player.GetMaxHealth()))
        Game.wait_for_input()
    elif rng in range(51,80):
        RandomEnemy = RollNextEnemy()
        print('Oh no you came across a ',RandomEnemy.name)
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
        print('You found an %s lying on the ground' % founditem.name)
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
        print("You're now fighting ",enemy.name)
        print(enemy.Stats['Health'],'/',enemy.Stats['MaxHealth']," Health")
        print(enemy.Stats['Attack']," Attack")
        print(enemy.Stats['Defence']," Defence\n")
        print("1.Attack\n2.inventory\n3.Show Stats\n0.Run Away")
        next_move = Game.get_input()
        Game.Clear()
        match next_move:
            case '1':
                print("You've dealt ",CalculateDamage(player.GetAttack(),enemy.Stats['Defence']),' damage ')
                enemy.Stats['Health'] -= CalculateDamage(player.GetAttack(),enemy.Stats['Defence'])
                print(enemy.name," Health ",enemy.Stats['Health'],'/',enemy.Stats['MaxHealth'])
                if enemy.Stats['Health'] <= 0:
                    print("You've killed ",enemy.name)
                    dropped = enemy.LootTable.Roll()
                    if not dropped == None:   
                        print("It dropped a %s" %dropped)
                    Game.wait_for_input()
                    return 0
                player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                print(enemy.name," dealt ",CalculateDamage(enemy.Stats['Attack'],player.GetDefence()),' damage')
                print("Player's Health ",player.Stats['Health'],'/',player.Stats['MaxHealth'])
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
                    print(enemy.name," dealt ",CalculateDamage(enemy.Stats['Attack'],player.GetDefence()),' damage')
                    Game.wait_for_input()
                    Game.Clear()
            case _:
                Game.Clear()

def CalculateDamage(Damage:int,Defence:int):
    reduction = 1+Defence/100
    result = Damage/reduction
    return int(result)

def Play():
    while True:
        if player.GetHealth() <= 0: return 0
        print('1.Next Turn\n2.Shop (WIP)\n3.Inventory \n4.Equipment \n5.Show Stats \n6.Save \n0.Menu')
        match Game.get_input():
            case '1':
                Game.Clear()
                AutoSave()
                NextTurn()
                Game.Clear()
            case '2':
                Game.Clear()
            case '3':
                ShowInventory()
                Game.Clear()
            case '4':
                ShowEquipment()
                Game.Clear()
            case '5':
                player.PrintStats()
                Game.Clear()
            case '6':
                Game.Clear()
                print('Name a save file')
                Save(input())
                Game.Clear()
            case '0':
                while True:
                    Game.Clear()
                    print("Do you want to save before quiting? Yes/No")
                    match input().lower():
                        case 'yes' | 'y':
                            Game.Clear()
                            print('Name a save file')
                            Save(input())
                            Game.Clear()
                            player.ResetStats()
                            return 0
                        case 'no' | 'n':
                            return 0
            case _:
                Game.Clear()

def GameNamePrint():
    print('____ ___  ____    ____ ____ _  _ ____ ',
          '|__/ |__] | __    | __ |__| |\/| |___ ',
          '|  \ |    |__]    |__] |  | |  | |___ ',
          '',
          '',sep="\n")

def Menu():
    Game.Clear()
    Debug()
    GameNamePrint()
    print("1.Play\n2.Load\n3.Your Saves\n4.Development Info\n0.Exit")
    match Game.get_input():
        case '0':
            sys.exit()
        case '1':
            if ChooseCharacter() != 0:
                CurrentSaveFileName = ""
                Game.Clear()
                Play()
        case '2':
            Game.Clear()
            print('Type the name of a save file')
            if not Load(input()) == 0:
                Play()
        case '3':
            Game.Clear()
            SavesMenu()
        case '4':
            Game.Clear()
            DeveloperInfoMenu()
        case _:
            Game.Clear()

def SavesMenu():
    saves = []
    for file in os.listdir(SaveFilePath):
        filename = os.fsdecode(file)
        if filename.endswith(".json"): 
            saves.append(file)
    while True:
        Game.Clear()
        print("Found %s save files" %len(saves))
        for x in saves:
            print(x.split(".")[0])
        print('\nType the name of a save file to load\n0.Menu')
        answer = input()
        match answer:
            case '0':
                return
            case _:
                Load(answer)
                if Play() == 0:
                    return
        
def AutoSave():
    if CurrentSaveFileName != "":
        Save(CurrentSaveFileName)

def Save(SaveName:str):
    Game.Clear()
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
        print("save file doesn't exist!")
        time.sleep(2)
        return 0
    if data['GameVersion'] != GameVersion:
        print("Save game version is diffrent form curent version\nLoad? Yes/No")
        answer = input().lower()
        if answer != "yes" or answer != "y": return 0
    
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
    while True:
        Game.Clear()
        print("Development info\n",
            "Game Roadmap:",
            "1.Add shops and currency",
            "2.Balance current gameplay",
            "3.Add more Items and Monsters",
            "4.Add Leveling system and exp gathering from fights",
            "5.Expand loot tables and refactor it's code\n",
            "Now i'm adding shops",
            'Press any button to continue',sep="\n")
        Game.wait_for_input()
        return



if __name__ == '__main__':
    Game.window("Rpg Game",55,15)
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