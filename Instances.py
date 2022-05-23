import Engine, time, Main , random

class Item:

    ItemBase = []

    def __init__(self,Name:str,Price:int,Damage:int,Defence:int,MaxHealth:int,Speed:int,EquipPlace:str,ClassUse=[]):
        '''
        Creates an Item that has basic properties like:
        - Price = Ammount of gold that this item can be sold with
        - Damage = Boosts player damage
        - Defence = Boosts player defence
        - MaxHealth = Boosts player max health
        - EquipPlace = Defines where player can wear this item (If left blank it's not equpipable)
        - ClassUse = Defines which classes can use this item (If left blank every class can use it)
        '''
        self.name = Name
        self.Price = Price
        self.Damage = Damage
        self.Defence = Defence
        self.MaxHealth = MaxHealth
        self.Speed = Speed
        self.EquipPlace = EquipPlace
        self.ClassUse = ClassUse
        Item.ItemBase.append(self)
    
    def Use(self,player):
        SideText = Engine.Text("")
        if len(self.ClassUse) != 0:
            ClassesToCheck = len(self.ClassUse)
            for Class in self.ClassUse:
                if Class.Name == player.Class:
                    break
                ClassesToCheck -= 1
                if ClassesToCheck == 0:
                    SideText.append("%s is not for your class : %s" % (self.name, player.Class))
                    Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %Main.PANEL_COLOR))
                    Engine.Game.wait_for_input()
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
        Engine.layout['Side'].update(Engine.Panel(SideText,title="Inventory",style="%s" %Main.PANEL_COLOR))
        Engine.Game.wait_for_input()
    
    def ShowStats(self):
        ClassUse = ""
        if len(self.ClassUse) > 0:
            for x in self.ClassUse:
                if ClassUse == "": ClassUse += f"{x.Name} "
                else: ClassUse += f", {x.Name} "
        else: ClassUse = "All classes"

        text = Engine.Text(f"Name: {self.name}\nPrice: {self.Price} Gold\nEquip Place: {self.EquipPlace}\nClass use: {ClassUse}\n")
        text.append(f"Bonuses:\n Health = {self.MaxHealth}\n Damage = {self.Damage}\n Defence = {self.Defence}\n Speed = {self.Speed}")
        return text

    def FindItem(ItemName):
        if ItemName == None: return None
        for x in Item.ItemBase:
            if x.name == ItemName:
                return x
        return None

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

    def RollForItem(self,player):
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

class Monster:

    MonsterBase = []

    def __init__(self,Name:str,MaxHealth:int,Attack:int,Defence:int,Speed:int,LootTable=None):
        self.name = Name
        self.Stats = {
            'Health' : MaxHealth,
            'MaxHealth' : MaxHealth,
            'Attack' : Attack,
            'Defence' : Defence,
            'Speed' : Speed
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
    
    @staticmethod
    def RollNextEnemy():
        value = random.randint(0,len(Monster.MonsterBase)-1)
        return Monster.MonsterBase[value]

class CharacterClass:

    Classes = []

    def __init__(self,Name:str=10,MaxHealth:int=10,Attack:int=10,Defence:int=10,Speed:int=10):
        self.Name = Name
        self.Stats = {
            'Health' : MaxHealth,
            'MaxHealth' : MaxHealth,
            'Attack' : Attack,
            'Defence' : Defence,
            'Speed' : Speed
        }
        CharacterClass.Classes.append(self)

WarriorClass = CharacterClass('Warrior', 80, 30, 40, 20)
RangerClass = CharacterClass('Ranger', 60, 25, 20, 50)
MageClass = CharacterClass('Mage', 60, 40, 10, 30)
TitanClass = CharacterClass('Titan', 1000, 1000, 1000, 100)

#---Leather---
LeatherHelmet = Item('Leather Helmet', 15, 0, 5, 0, 5, 'Helmet')
LeatherChestplate = Item('Leather Chestplate', 25, 0, 7, 5, 7, 'Chestplate')
LeatherLeggins = Item('Leather Leggins', 15, 0, 5, 0, 5, 'Leggins')
LeatherGloves = Item('Leather Gloves', 15, 0, 5, 0, 3, 'LeftHand')
#---Iron---
IronHelmet = Item('Iron Helmet', 50, 0, 5, 5, 0, 'Helmet', [WarriorClass])
IronChestplate = Item('Iron Chestplate', 100, 0, 30, 10, -5, 'Chestplate', [WarriorClass])
IronLeggins = Item('Iron Leggins', 50, 0, 10, 0, -2, 'Leggins', [WarriorClass])
IronShield = Item('Iron Shield', 70, -5, 20, 0, -10, 'LeftHand', [WarriorClass])
IronSword = Item('Iron Sword', 40, 10, 0, 0, -5, 'RightHand', [WarriorClass])
IronDagger = Item('Iron Dagger', 25, 7, 0, 0, 2, 'RightHand', [RangerClass,MageClass])
#---Wooden---
WoodenShield = Item('Wooden Shield', 15, -3, 10, 0, -5, 'LeftHand', [WarriorClass])
WoodenSword = Item('Wooden Sword', 15, 5, 0, 0, 0, 'RightHand', [WarriorClass])
WoodenBow = Item('Wooden Bow', 20, 10, 0, 0, 3, 'RightHand', [RangerClass])
#---Magic---
BegginersWand = Item('Begginers Wand', 45, 10, 0, 0, 5, 'RightHand', [MageClass])
StudentCape = Item('Student Cape', 100, 5, 5, 5, 10, 'Chestplate', [MageClass])
WizardHat = Item('Wizard Hat', 75, 5, 5, 0, 4, 'Helmet', [MageClass])
MagicTome = Item('Magic Tome', 50, 10, 0, 0, 5, 'LeftHand', [MageClass])
MagicOrb = Item('Magic Orb', 120, 20, 0, 0, 0, 'LeftHand', [MageClass])
#---Other---
Chainmail = Item('Chainmail', 35, 0, 10, 5, -5, 'Chestplate', [RangerClass,WarriorClass])


#----Zombie----
ZombieLoot = LootTable()
ZombieLoot.addLoot(WoodenSword,10)
ZombieLoot.addLoot(WoodenShield,9)
ZombieLoot.addLoot(IronSword,4)
ZombieLoot.addLoot(IronDagger,7)
ZombieLoot.addLoot(IronShield,4)
ZombieLoot.addLoot(Chainmail,8)
ZombieLoot.addLoot(None,100)
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
#----Skeleton----
SkeletonLoot = LootTable()
SkeletonLoot.addLoot(Chainmail,10)
SkeletonLoot.addLoot(LeatherHelmet,9)
SkeletonLoot.addLoot(LeatherLeggins,5)
SkeletonLoot.addLoot(LeatherGloves,7)
SkeletonLoot.addLoot(LeatherChestplate,4)
SkeletonLoot.addLoot(WoodenBow,8)
SkeletonLoot.addLoot(None,100)
#-----Ghost-----
GhostLoot = LootTable()
GhostLoot.addLoot(BegginersWand,5)
GhostLoot.addLoot(WizardHat,9)
GhostLoot.addLoot(StudentCape,10)
GhostLoot.addLoot(MagicTome,8)
GhostLoot.addLoot(None,100)
#-----Thief-----
ThiefLoot = LootTable()
ThiefLoot.addLoot(LeatherHelmet,6)
ThiefLoot.addLoot(LeatherChestplate,4)
ThiefLoot.addLoot(LeatherLeggins,5)
ThiefLoot.addLoot(LeatherGloves,7)
ThiefLoot.addLoot(IronDagger,3)
ThiefLoot.addLoot(None,100)
#-----Wraith-----
WraithLoot = LootTable()
WraithLoot.addLoot(BegginersWand,9)
WraithLoot.addLoot(StudentCape,7)
WraithLoot.addLoot(MagicTome,8)
WraithLoot.addLoot(MagicOrb,5)
WraithLoot.addLoot(None,100)

Zombie = Monster('Zombie', 60, 15, 20, 10, ZombieLoot)
Warewolf = Monster("Warewolf", 50, 20, 20, 20, WarewolfLoot)
Skeleton = Monster('Skeleton', 45, 10, 10, 30, SkeletonLoot)
Ghost = Monster('Ghost', 15, 5, 500, 0, GhostLoot)
Thief = Monster('Thief', 25, 10, 5, 80, ThiefLoot)
Wraith = Monster('Wraith', 100, 15, 5, 30, WraithLoot)
