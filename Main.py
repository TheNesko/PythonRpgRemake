import time, sys, os, random, json, msvcrt

#---------
GameVersion= "0.0.1"
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
            item = FindItem(ItemName)
        except:
            print('Item not found')
            msvcrt.getch()
            return
        if not player.Equiped[item.EquipPlace] == None:
            player.Equiped[item.EquipPlace] = None
            player.Inventory.append(item)
            print("You've taken off a %s" % item.name)
        else:
            print("You don't have that item equiped")
        msvcrt.getch()

    def UsePotion(self,Name:str):
        match Name:
            case 'HealthPotion':
                if self.Potions[Name] <= 0:
                    print("You don't have any Health Potions")
                    msvcrt.getch()
                    return
                self.Potions[Name] -= 1
                player.SetHealth(player.GetHealth() + 10)
                print("You've used a Health Potion")
                msvcrt.getch()
    
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
        if not self.Equiped['Helmet'] == None:
            item = FindItem(self.Equiped['Helmet'])
            self.EquipmentMaxHealth += item.MaxHealth
            self.EquipmentAttack += item.Damage
            self.EquipmentDefence += item.Defence
        if not self.Equiped['Chestplate'] == None:
            item = FindItem(self.Equiped['Chestplate'])
            self.EquipmentMaxHealth += item.MaxHealth
            self.EquipmentAttack += item.Damage
            self.EquipmentDefence += item.Defence
        if not self.Equiped['Leggins'] == None:
            item = FindItem(self.Equiped['Leggins'])
            self.EquipmentMaxHealth += item.MaxHealth
            self.EquipmentAttack += item.Damage
            self.EquipmentDefence += item.Defence
        if not self.Equiped['LeftHand'] == None:
            item = FindItem(self.Equiped['LeftHand'])
            self.EquipmentMaxHealth += item.MaxHealth
            self.EquipmentAttack += item.Damage
            self.EquipmentDefence += item.Defence
        if not self.Equiped['RightHand'] == None:
            item = FindItem(self.Equiped['RightHand'])
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

player = Player()

class CharacterClass:
    def __init__(self,Name,MHP,AD,DF):
        self.Name = Name
        self.Stats = {
            'Health' : MHP,
            'MaxHealth' : MHP,
            'Attack' : AD,
            'Defence' : DF
        }

WarriorClass = CharacterClass('Worrior',100,30,50)
RangerClass = CharacterClass('Ranger',70,20,40)
MageClass = CharacterClass('Mage',50,60,10)

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
                if not x['Item'] == None:
                    self.Dropped = x
        if not self.Dropped == None:
            player.Inventory.append(self.Dropped['Item'])
        # for x in self.Loot:
        #     if x["Item"] != None:
        #         print(x['Item'].name,x)
        # print(rng)
        if self.Dropped == None:
            return None
        return self.Dropped['Item'].name

class Item:
    def __init__(self,Name:str,Damage:int,Defence:int,MaxHealth:int,EquipPlace:str):
        self.name = Name
        self.Damage = Damage
        self.Defence = Defence
        self.MaxHealth = MaxHealth
        self.EquipPlace = EquipPlace
    
    def Use(self):
        if player.Equiped[self.EquipPlace] == None:
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
            print("You've used %s" % self.name)
        else:
            print("You've exchanged a %s for %s" % (player.Equiped[self.EquipPlace], self.name))
            player.Inventory.append(FindItem(player.Equiped[self.EquipPlace]))
            player.Equiped[self.EquipPlace] = self.name
            player.Inventory.remove(self)
        player.ResetStatsFromEquipment()
        player.AddStatsFromEquipment()
        msvcrt.getch()

Helmet = 'Helmet'
Chestplate = 'Chestplate'
Leggins = 'Leggins'
LeftHand = 'LeftHand'
RightHand = 'RightHand'

WoddenSword = Item('Wodden Sword',10,0,0,RightHand)
IronSword = Item('Iron Sword',20,0,0,RightHand)
Chestplate = Item('Chestplate',0,30,10,Chestplate)

ItemBase = []
ItemBase.append(WoddenSword)
ItemBase.append(IronSword)
ItemBase.append(Chestplate)

def FindItem(ItemName):
    for x in ItemBase:
        if x.name == ItemName:
            return x
    return None

class Monster:
    def __init__(self,Name:str,MHP,AD,DF,LootTable:LootTable):
        self.name = Name
        self.Stats = {
            'Health' : MHP,
            'MaxHealth' : MHP,
            'Attack' : AD,
            'Defence' : DF
        }
        self.LootTable = LootTable
    
    def SetMaxHealth(self):
        self.Stats['Health'] = self.Stats['MaxHealth']

#----Zombie----
ZombieLoot = LootTable()
ZombieLoot.addLoot(WoddenSword,8)
ZombieLoot.addLoot(IronSword,3)
ZombieLoot.addLoot(Chestplate,5)
ZombieLoot.addLoot(None,20)
Zombie = Monster('Zombie',40,10,20,ZombieLoot)
#----Skeleton----
Skeleton = Monster('Skeleton',25,20,10,ZombieLoot)


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
            '''
            if player.Equiped[x] == None:
                print(x,"-",player.Equiped[x])
            else:
                print(x,"-",player.Equiped[x])
            '''
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
        print('Choose your character!\n1.Worrior\n2.Ranger\n3.Mage\n0.Menu')
        character = int(msvcrt.getch())
        Clear()
        match character:
            case 1:
                player.SetAllStats(WarriorClass.Stats,WarriorClass.Name)
                break
            case 2:
                player.SetAllStats(RangerClass.Stats,RangerClass.Name)
                break
            case 3:
                player.SetAllStats(MageClass.Stats,MageClass.Name)
                break
            case 0:
                return 0
            case _:
                print("Character doesn't exist!")

def PrintStats():
    Clear()
    print(player.GetHealth(),'/',player.GetMaxHealth(),' Health')
    print(player.GetAttack(),' Attack')
    print(player.GetDefence(),' Defence')
    print('Press any button to continue')
    msvcrt.getch()

def NextTurn():
    rng = random.randint(0,10)
    match rng:
        case 0 | 3 | 2 | 7:
            print('Lucky u nothing happend')
            msvcrt.getch()
        case 1 | 9 | 10:
            print('Oh no you came across a Zombie')
            msvcrt.getch()
            Fight(Zombie)
        case 5:
            player.Potions['HealthPotion'] += 1
            print('Wow! you found a Healing potion\nYou now have %s' % player.Potions['HealthPotion'])
            msvcrt.getch()
        case 4 | 6:
            print('Spooky scary skeleton!')
            msvcrt.getch()
            Fight(Skeleton)
        case 8:
            rngItem = random.randint(0,len(ItemBase)-1)
            founditem = ItemBase[rngItem]
            player.Inventory.append(founditem)
            print('You found an %s lying on the ground' % founditem.name)
            msvcrt.getch()
    
def Fight(Monster:Monster):
    Clear()
    enemy = Monster
    enemy.SetMaxHealth()
    while True:
        if player.GetHealth() <= 0:
            print("You died!")
            msvcrt.getch()
            return 0
        print("You're now fighting ",enemy.name)
        print(enemy.Stats['Health'],'/',enemy.Stats['MaxHealth']," Health")
        print(enemy.Stats['Attack']," Attack")
        print(enemy.Stats['Defence']," Defence\n")
        print("1.Attack\n2.inventory\n3.Show Stats\n0.Run Away")
        NextMove = int(msvcrt.getch())
        Clear()
        match NextMove:
            case 1:
                enemy.Stats['Health'] -= CalculateDamage(player.GetAttack(),enemy.Stats['Defence'])
                if enemy.Stats['Health'] <= 0:
                    print("You've killed ",enemy.name)
                    dropped = enemy.LootTable.Roll()
                    if not dropped == None:   
                        print("It dropped a %s" %dropped)
                    msvcrt.getch()
                    return 0
                print("You dealt ",CalculateDamage(player.GetAttack(),enemy.Stats['Defence']),' damage')
                player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                print(enemy.name," dealt ",CalculateDamage(enemy.Stats['Attack'],player.GetDefence()),' damage')
                msvcrt.getch()
                Clear()
            case 2:
                ShowInventory()
                Clear()
            case 3:
                PrintStats()
                Clear()
            case 0:
                x = random.randint(0,1)
                if x == 0:
                    print('You escaped safely')
                    msvcrt.getch()
                    return 0
                else:
                    print('You failled to escape')
                    player.SetHealth(player.GetHealth()-CalculateDamage(enemy.Stats['Attack'],player.GetDefence()))
                    print(enemy.name," dealt ",CalculateDamage(enemy.Stats['Attack'],player.GetDefence()),' damage')
                    msvcrt.getch()
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
        answer = int(msvcrt.getch())
        match answer:
            case 1:
                Clear()
                NextTurn()
                Clear()
            case 2:
                ShowInventory()
                Clear()
            case 3:
                ShowEquipment()
                Clear()
            case 4:
                PrintStats()
                Clear()
            case 5:
                Clear()
                print('Name a save file')
                Save(input())
                Clear()
            case 0:
                while True:
                    Clear()
                    print("Do you want to save before quiting? Yes/No")
                    match input():
                        case 'Yes':
                            Clear()
                            print('Name a save file')
                            Save(input())
                            Clear()
                            player.ResetStats()
                            return 0
                        case 'No':
                            return 0
            case _:
                Clear()

def Menu():
    Clear()
    Debug()
    print("Super EPIC game\n1.Play\n2.Load\n3.Your Saves\n4.Development Info\n0.Exit")
    answer = int(msvcrt.getch())
    match answer:
        case 0:
            sys.exit()
        case 1:
            if ChooseCharacter() == 0: return 0
            Clear()
            Play()
        case 2:
            Clear()
            print('Type the name of a save file')
            if not Load(input()) == 0:
                Play()
        case 3:
            Clear()
            SavesMenu()
        case 4:
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
        if not input() == "yes":
            return 0
    player.SetAllStats(data['Player'],data['PlayerClass'])
    player.Potions = data['Inventory']['Potions']
    player.Equiped = data['Inventory']['Equiped']
    for x in data['Inventory']['Items']:
        for y in ItemBase:
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
        msvcrt.getch()
        return

while True:
    Menu()
    


'''
---------------------------------------------
IMPORTANTE YES!
separate the code to thir own files
basicly own class gets it's own file or smth idk
ex. Monster class is in Monsters.py file and contains
Monster data base with every monster for eazy acces
same with Items and add some utils like 
Get_Input() insted of int(msvcrt.getch())
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