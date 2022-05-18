import time, sys, os, random, json
from Engine import Game

#---------
GameVersion= "0.0.2"
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
        self.Inventory = []
        self.Potions = {
            'HealthPotion' : 0
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
    
    def RemoveEquipment(self,ItemName):
        try:
            item = Item.FindItem(ItemName)
        except:
            print('Item not found')
            Game.wait_for_input()
            return
        if player.Equiped[item.EquipPlace] != None:
            player.Equiped[item.EquipPlace] = None
            player.Inventory.append(item)
            print("You've taken off a %s" % item.name)
        else:
            print("You don't have that item equiped")
        Game.wait_for_input()

    def UsePotion(self,Name:str):
        match Name:
            case 'HealthPotion':
                if self.Potions[Name] <= 0:
                    print("You don't have any Health Potions")
                    Game.wait_for_input()
                    return
                self.Potions[Name] -= 1
                player.SetHealth(player.GetHealth() + 10)
                print("You've used a Health Potion")
                Game.wait_for_input()
    
    def SetAllStats(self,NewStats,Class):
        self.Class = Class
        self.Stats = NewStats
    
    def ResetStats(self):
        self.Class = None
        self.Inventory.clear()
        self.Potions['HealthPotion'] = 0
        self.Equiped = {
            'Helmet' : None,
            'Chestplate' : None,
            'Leggins' : None,
            'LeftHand' : None,
            'RightHand' : None
        }
    
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

    def __init__(self,Name:str,Damage:int,Defence:int,MaxHealth:int,EquipPlace:str):
        self.name = Name
        self.Damage = Damage
        self.Defence = Defence
        self.MaxHealth = MaxHealth
        self.EquipPlace = EquipPlace
        Item.ItemBase.append(self)
    
    def Use(self):
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
WarriorClass = CharacterClass('Worrior',70,30,50)
RangerClass = CharacterClass('Ranger',100,25,40)
MageClass = CharacterClass('Mage',50,40,10)
GodClass = CharacterClass('God',1000,1000,1000)
#----Items-----

Helmet = 'Helmet'
Chestplate = 'Chestplate'
Leggins = 'Leggins'
LeftHand = 'LeftHand'
RightHand = 'RightHand'

#---Helmet---
LeatherHelmet = Item('Leather Helmet',0,5,0,Helmet)
#---Chestplate---
Chainmail = Item('Chainmail',0,10,5,Chestplate)
IronChestplate = Item('Iron Chestplate',0,30,10,Chestplate)
#---Leggins---
IronLeggins = Item('Iron Leggins',0,10,0,Leggins)
#---LeftHand---
WoodenShield = Item('Wooden Shield',-5,10,0,LeftHand)
#---RightHand---
WoodenSword = Item('Wooden Sword',5,0,0,RightHand)
IronSword = Item('Iron Sword',20,0,0,RightHand)

#----Zombie----
ZombieLoot = LootTable()
ZombieLoot.addLoot(WoodenSword,8)
ZombieLoot.addLoot(WoodenShield,5)
ZombieLoot.addLoot(IronSword,2)
ZombieLoot.addLoot(None,50)
Zombie = Monster('Zombie',40,10,20,ZombieLoot)
#----Skeleton----
SkeletonLoot = LootTable()
SkeletonLoot.addLoot(Chainmail,5)
SkeletonLoot.addLoot(LeatherHelmet,10)
SkeletonLoot.addLoot(None,100)
Skeleton = Monster('Skeleton',25,20,10,SkeletonLoot)
#-----Ghost-----
GhostLoot = LootTable()
GhostLoot.addLoot(None,100)
Ghost = Monster('Ghost',10,1,500,GhostLoot)


#===========================

def ShowInventory():
    while True:
        Clear()
        print("Inventory")
        if not len(player.Inventory) <= 0:
            for x in player.Inventory:
                print(x.name)
        print("\nPotions")
        for x in player.Potions:
            print(x,"-",player.Potions[x])
        print("\nType the name of and item you want to use\n0.Go back")
        x = input()
        Clear()
        match x:
            case '0':
                return 0
            case _:
                player.UsePotion(x)
                player.UseItem(x)

def ShowEquipment():
    while True:
        Clear()
        print("Equipment")
        for x in player.Equiped:
            print(x,"-",player.Equiped[x])
        print("\nType the name of and item you want to use\n0.Go back")
        x = input()
        Clear()
        match x:
            case '0':
                return 0
            case _:
                player.RemoveEquipment(x)

def Clear():
    os.system('cls')

def ChooseCharacter():
    Clear()
    while True:
        print('Choose your character!')
        for x in range(len(CharacterClass.Classes)):
            print(x+1,".",CharacterClass.Classes[x].Name,sep="")
        print("0.Menu")
        character = int(Game.get_input())
        Clear()
        if character == 0:
            return 0
        elif character in range(len(CharacterClass.Classes)+1):
            player.SetAllStats(CharacterClass.Classes[character-1].Stats , CharacterClass.Classes[character-1].Name)
            return 1
        else:
            print("Character doesn't exist!")

def PrintStats():
    Clear()
    print("Class: ",player.Class)
    print(player.GetHealth(),'/',player.GetMaxHealth(),' Health')
    print(player.GetAttack(),' Attack')
    print(player.GetDefence(),' Defence')
    print('Press any button to continue')
    Game.wait_for_input()

def RollNextEnemy() -> Monster:
    value = random.randint(0,len(Monster.MonsterBase)-1)
    return Monster.MonsterBase[value]

def NextTurn():
    rng = random.randint(0,100)
    if rng in range(0,1):
        print('Lucky you! Nothing happend')
        Game.wait_for_input()
    elif rng in range(2,50):
        print('You found a place to rest')
        ProcentHealthRested = random.randint(5,25)/100
        HpRested = player.GetMaxHealth() * ProcentHealthRested
        player.SetHealth(player.GetHealth()+HpRested)
        print("And recoverd ",HpRested," Health")
        print("Current Health ",player.GetHealth(),"/",player.GetMaxHealth())
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
    Clear()
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
        Clear()
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
                Clear()
            case '2':
                ShowInventory()
                Clear()
            case '3':
                PrintStats()
                Clear()
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
                    Clear()
            case _:
                Clear()

def CalculateDamage(Damage:int,Defence:int):
    reduction = 1+Defence/100
    result = Damage/reduction
    return int(result)

def Play():
    while True:
        if player.GetHealth() <= 0: return 0
        print('1.Next Turn\n2.Inventory \n3.Equipment \n4.Show Stats \n5.Save \n0.Menu')
        match Game.get_input():
            case '1':
                Clear()
                NextTurn()
                Clear()
            case '2':
                ShowInventory()
                Clear()
            case '3':
                ShowEquipment()
                Clear()
            case '4':
                PrintStats()
                Clear()
            case '5':
                Clear()
                print('Name a save file')
                Save(input())
                Clear()
            case '0':
                while True:
                    Clear()
                    print("Do you want to save before quiting? Yes/No")
                    match input().lower():
                        case 'yes' | 'y':
                            Clear()
                            print('Name a save file')
                            Save(input())
                            Clear()
                            player.ResetStats()
                            return 0
                        case 'no' | 'n':
                            return 0
            case _:
                Clear()

def GameNamePrint():
    print('____ ___  ____    ____ ____ _  _ ____ ',
          '|__/ |__] | __    | __ |__| |\/| |___ ',
          '|  \ |    |__]    |__] |  | |  | |___ ',
          '',
          '',sep="\n")

def Menu():
    Clear()
    Debug()
    GameNamePrint()
    print("1.Play\n2.Load\n3.Your Saves\n4.Development Info\n0.Exit")
    match Game.get_input():
        case '0':
            sys.exit()
        case '1':
            if ChooseCharacter() != 0:
                Clear()
                Play()
        case '2':
            Clear()
            print('Type the name of a save file')
            if not Load(input()) == 0:
                Play()
        case '3':
            Clear()
            SavesMenu()
        case '4':
            Clear()
            DeveloperInfoMenu()
        case _:
            Clear()

def SavesMenu():
    saves = []
    for file in os.listdir(SaveFilePath):
        filename = os.fsdecode(file)
        if filename.endswith(".json"): 
            saves.append(file)
    while True:
        Clear()
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
        
def Save(SaveName:str):
    Clear()
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

def Load(SaveName:str):
    Clear()
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
        Clear()
        print("Development info\n\nGame Roadmap:\n1.Add shops and currency")
        print("2.Balance current gameplay\n3.Add more Items and Monsters")
        print("4.Add Leveling system and exp gathering from fights")
        print("5.Expand loot tables and refactor it's code\n")
        print("currently I'm cleaning up some nasty code\n")
        print('Press any button to continue')
        Game.wait_for_input()
        return



if __name__ == '__main__':
    os.system('mode con: cols=55 lines=15')
    os.system("title " + "Rpg Game")
    while True:
        Menu()


'''
---------------------------------------------
Ideas:
1. Evade chance (not to get damaged for monsters and classes)
---------------------------------------------
TO DO:
1.shop
2.Coins
3.Add Coins To loot table
4.Add EXP and LEVELS to player and Monsters
5.Add more Items
6.Add more Monsters
7.Balance the game
---------------------------------------------
'''