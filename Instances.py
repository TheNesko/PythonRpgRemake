import Engine, random

class Item:

    ItemBase = []

    def __init__(self,Name:str,Price:int=10,Rarity='C'):
        
        self.name = Name
        self.Price = Price
        self.Rarity = Rarity.upper()
        Item.ItemBase.append(self)
    
    def UseItem(self,player,TargetItem):
        return Engine.Text("CAN'T USE THIS ITEM")

    def BuyItem(self,player,TargetItem):
        pass

    def SellItem(self,player,TargetItem):
        pass

    def ShowStats(self,PriceModifier=1):
        Rarity = 'Common'
        if self.Rarity == 'U': Rarity = 'Uncommon'
        elif self.Rarity == 'R': Rarity = 'Rare'
        text = Engine.Text(f"Name: {self.name}      Rarity: {Rarity}\nPrice: {round(self.Price*PriceModifier)} Gold")
        return text

    def FindItem(ItemName):
        if ItemName == None: return None
        for x in Item.ItemBase:
            if x.name == ItemName:
                return x
        return None

class Equipment(Item):

    EquipmentBase = []

    CommonEquipment = []
    UncommonEquipment = []
    RareEquipment = []
    LegendaryEquipment = []

    def __init__(self,Name:str,EquipPlace:str="Helmet",ClassUse=[],Price:int=10,Damage:int=0,
                Defence:int=0,MaxHealth:int=0,Speed:int=0,Rarity='C'):
        '''
        Creates an Item that has basic properties like:
        - EquipPlace = Defines where player can wear this item (If left blank it's not equpipable)
        - ClassUse = Defines which classes can use this item (If left blank every class can use it)
        - Price = Ammount of gold that this item can be sold with
        - Damage = Boosts player damage
        - Defence = Boosts player defence
        - MaxHealth = Boosts player max health
        '''
        super().__init__(Name, Price, Rarity)
        self.name = Name
        self.Price = Price
        self.Damage = Damage
        self.Defence = Defence
        self.MaxHealth = MaxHealth
        self.Speed = Speed
        self.EquipPlace = EquipPlace
        self.ClassUse = ClassUse
        self.Rarity = Rarity.upper()
        Item.ItemBase.append(self)
        Equipment.EquipmentBase.append(self)
        match self.Rarity:
            case 'C': Equipment.CommonEquipment.append(self)
            case 'U': Equipment.UncommonEquipment.append(self)
            case 'R': Equipment.RareEquipment.append(self)
            case 'L': Equipment.LegendaryEquipment.append(self)
    
    def UseItem(self,player,TargetItem):
        SideText = Engine.Text("")
        if len(self.ClassUse) != 0:
            ClassesToCheck = len(self.ClassUse)
            for Class in self.ClassUse:
                if Class.Name == player.Class:
                    break
                ClassesToCheck -= 1
                if ClassesToCheck == 0:
                    SideText.append("%s is not for your class : %s" % (self.name, player.Class))
                    return SideText
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
        return SideText

    def SellItem(self,player,TargetItem,PriceModifier=1):
        if len(player.Inventory) <= 0: return False
        for x in player.Inventory:
            if self == x:
                player.Inventory.remove(x)
                player.Gold += round(x.Price*PriceModifier)
                return True
        return False
    
    def BuyItem(self,player,TargetItem,PriceModifier=1):
        if player.Gold >= round(self.Price*PriceModifier):
            player.Gold -= round(self.Price*PriceModifier)
            player.Inventory.append(self)
            return True
        return False

    def ShowStats(self,PriceModifier=1):
        ClassUse = ""
        if len(self.ClassUse) > 0:
            for x in self.ClassUse:
                if ClassUse == "": ClassUse += f"{x.Name} "
                else: ClassUse += f", {x.Name} "
        else: ClassUse = "All classes"
        Rarity = 'Common'
        if self.Rarity == 'U': Rarity = 'Uncommon'
        elif self.Rarity == 'R': Rarity = 'Rare'

        text = Engine.Text(f"Name: {self.name}      Rarity: {Rarity}\nPrice: {round(self.Price*PriceModifier)} Gold\nEquip Place: {self.EquipPlace}\nClass use: {ClassUse}\nBonuses:\n")
        if self.MaxHealth != 0: text.append(f" Health = {self.MaxHealth}\n")
        if self.Damage != 0: text.append(f" Damage = {self.Damage}\n")
        if self.Defence != 0: text.append(f" Defence = {self.Defence}\n")
        if self.Speed != 0: text.append(f" Speed = {self.Speed}\n")
        return text

class Potion(Item):

    PotionBase = []

    def __init__(self, Name: str, Price: int = 10, HealingPower:int=1, Stackable:bool = True, Rarity='C'):
        super().__init__(Name, Price, Rarity)
        Potion.PotionBase.append(self)
        self.HealingPower = HealingPower
        self.Stackable = Stackable
        self.StackedPotions = 1

    def UseItem(self,player,TargetItem):
        text = Engine.Text()
        if player.GetHealth() < player.GetMaxHealth():
            TargetItem.StackedPotions -= 1
            if TargetItem.StackedPotions < 1: player.Potions.remove(TargetItem)
            HealthBefore = round(player.GetHealth())
            Heal = round(player.GetMaxHealth() * self.HealingPower)
            player.SetHealth(player.GetHealth() + Heal)
            HealthAfter = round(player.GetHealth())
            HealValue = HealthAfter - HealthBefore
            text.append("You've used a Health Potion\n")
            text.append("It healed you for %s \n" %HealValue)
            text.append("Current health %s/%s \n" %(round(player.GetHealth()),player.GetMaxHealth()))
        else: text.append("You already have full hp")
        return text

    def SellItem(self,player,TargetItem,PriceModifier=1):
        if len(player.Potions) <= 0: return False
        for x in player.Potions:
            if TargetItem == x:
                TargetItem.StackedPotions -= 1
                if TargetItem.StackedPotions <= 0: player.Potions.remove(TargetItem)
                player.Gold += round(x.Price*PriceModifier)
                return True
        return False
    
    def BuyItem(self,player,TargetItem,PriceModifier=1):
        if player.Gold >= round(TargetItem.Price*PriceModifier):
            player.Gold -= round(TargetItem.Price*PriceModifier)
            if len(player.Potions) > 0:
                for potion in player.Potions:
                    if potion == TargetItem:
                        potion.StackedPotions += 1
                        return True
            player.Potions.append(TargetItem)
            return True
        return False

    def ShowStats(self,PriceModifier=1):
        text = Engine.Text(f"Name: {self.name}\nPrice: {round(self.Price*PriceModifier)} Gold\n")
        text.append(f"{self.name} heal {round(self.HealingPower*100)}% of player's max health")
        return text

class LootTable:

    CommonChance = range(0,700)           # 70%
    UncommonChance = range(700,950)       # 25%
    RareChance = range(950,995)           # 4.5%
    LegendaryChance = range(950,1000)     # 0.5%

    def __init__(self,LootDropChance:int=60):
        self.CommonLoot = []
        self.UncommonLoot = []
        self.RareLoot = []
        self.LegendaryLoot = []
        self.LootDropChance = LootDropChance

    def addLoot(self,Item,Weight:int):
        self.Drop = {
            'Item': Item,
            'Weight' : Weight
        }
        match Item.Rarity:
            case 'C': self.CommonLoot.append(self.Drop)
            case 'U': self.UncommonLoot.append(self.Drop)
            case 'R': self.RareLoot.append(self.Drop)
            case 'L': self.LegendaryLoot.append(self.Drop)

    def RollForItem(self,player):
        Loot = []
        AllWeights = 0
        Dropped = None
        Previous = None
        RolledLoot = []

        if not random.randrange(0,100) in range(0,self.LootDropChance): return None

        LootRarity = random.randrange(0,1000)
        if LootRarity in LootTable.CommonChance: RolledLoot = self.CommonLoot
        elif LootRarity in LootTable.UncommonChance: RolledLoot = self.UncommonLoot
        elif LootRarity in LootTable.RareChance: RolledLoot = self.RareLoot
        elif LootRarity in LootTable.LegendaryChance: RolledLoot = self.LegendaryLoot

        if len(RolledLoot) < 1: return None
        for x in RolledLoot:
            LootItem = {
                'Item': None,
                'MinChance': 0,
                'MaxChance': 0
            }
            AllWeights += x['Weight']
            LootItem['Item'] = x['Item']
            if Previous == None:
                LootItem['MinChance'] = 1
                LootItem['MaxChance'] = x['Weight']
            else:
                LootItem['MinChance'] = (Previous['MaxChance'] + 1)
                LootItem['MaxChance'] = (Previous['MaxChance'] + x['Weight'])
            Loot.append(LootItem)
            Previous = LootItem
        rng = random.randrange(1,AllWeights)
        for x in Loot:
            if rng <= x['MaxChance'] and rng >= x['MinChance']:
                if x['Item'] != None:
                    Dropped = x
        if Dropped != None:
            player.Inventory.append(Dropped['Item'])
        if Dropped == None:
            return None
        return Dropped['Item'].name

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

StrongHealthPotion = Potion('Strong Health Potion', Price=15, HealingPower=1)
RegularHealthPotion = Potion('Regular Health Potion', Price=10, HealingPower=0.5)
WeekHealthPotion = Potion('Week Health Potion', Price=5, HealingPower=0.25)


#---Leather---
LeatherHelmet = Equipment('Leather Helmet', 'Helmet', Price=10, Defence=2, Speed=5)
LeatherChestplate = Equipment('Leather Chestplate', 'Chestplate', Price=15, Defence=5, MaxHealth=5)
LeatherLeggins = Equipment('Leather Leggins', 'Leggins', Price=10, Defence=3, Speed=3)
LeatherGloves = Equipment('Leather Gloves', 'LeftHand', Price=10, Defence=1, Speed=2)
#----Fur----
FurHelmet = Equipment('Fur Helmet', 'Helmet', [RangerClass],Price=20, Defence=3, Speed=6, Rarity='U')
FurChestplate = Equipment('Fur Chestplate', 'Chestplate', [RangerClass], Price=35, Defence=7, MaxHealth=5, Speed=5, Rarity='U')
FurLeggins = Equipment('Fur Leggins', 'Leggins', [RangerClass], Price=25, Defence=3, Speed=5, Rarity='U')
FurGloves = Equipment('Fur Gloves', 'LeftHand', [RangerClass], Price=20, Defence=2, Speed=3, Rarity='U')
#---Iron---
IronHelmet = Equipment('Iron Helmet', 'Helmet', [WarriorClass], Price=30, Defence=5, Speed=-2,Rarity='U')
IronChestplate = Equipment('Iron Chestplate', 'Chestplate', [WarriorClass], Price=100, Defence=-5, MaxHealth=10, Speed=3, Rarity='R')
IronLeggins = Equipment('Iron Leggins', 'Leggins', [WarriorClass], Price=40, Defence=7, Speed=-7, Rarity='U')
IronShield = Equipment('Iron Shield', 'LeftHand', [WarriorClass], Price=150, Defence=10, Speed=-5, Rarity='R')
IronSword = Equipment('Iron Sword', 'RightHand', [WarriorClass], Price=50, Damage=12, Rarity='U')
IronDagger = Equipment('Iron Dagger', 'RightHand', [RangerClass,MageClass], Price=15, Damage= 5)
#---Wooden---
WoodenShield = Equipment('Wooden Shield', 'LeftHand', [WarriorClass], Price=20, Defence=5, Speed=-3)
WoodenSword = Equipment('Wooden Sword', 'RightHand', [WarriorClass], Price=25, Damage=8)
WoodenBow = Equipment('Wooden Bow', 'RightHand', [RangerClass], Price=50, Damage=7, Speed=3)
Crossbow = Equipment('Wooden Crossbow', 'RightHand', [RangerClass], Price=50, Damage=10, Rarity='U')
#---Magic---
WizardHat = Equipment('Wizard Hat', 'Helmet', [MageClass], Price=45, Defence=5, Speed=7,Rarity='U')
StudentCape = Equipment('Student Cape', 'Chestplate', [MageClass], Price=25, Defence=7, Speed=5)
MonkRobe = Equipment('Monk Robe', 'Chestplate', [MageClass], Price=80, Defence=10, MaxHealth=15, Rarity='R')
BegginersWand = Equipment('Begginers Wand', 'RightHand', [MageClass], Price=20, Damage=7)
WizardStaff = Equipment('Wizard Staff', 'RightHand', [MageClass], Price=100, Damage=15, Rarity='R')
SpellBook = Equipment('Spell Book', 'LeftHand', [MageClass], Price=30, Damage=5)
MagicTome = Equipment('Magic Tome', 'LeftHand', [MageClass], Price=70, Damage=7, Defence=5, Rarity='U')
MagicOrb = Equipment('Magic Orb', 'LeftHand', [MageClass], Price=140, Damage=12, Defence=5, Speed=5, Rarity='R')
#---Other---
Chainmail = Equipment('Chainmail', 'Chestplate', Price=35, Defence=7, MaxHealth=5, Speed=5, Rarity='U')
NeskoGlasses = Equipment("Nesko's Glasses", "Helmet", Price=420, Defence=6, MaxHealth=9, Speed=69,Rarity='L')

#--LOOT-TABLES-
#----Common----
CommonLootTable = LootTable()
CommonLootTable.addLoot(LeatherHelmet,4)
CommonLootTable.addLoot(LeatherChestplate,2)
CommonLootTable.addLoot(LeatherLeggins,4)
CommonLootTable.addLoot(LeatherGloves,4)
CommonLootTable.addLoot(WoodenShield,3)
CommonLootTable.addLoot(WoodenSword,2)
CommonLootTable.addLoot(WoodenBow,2)
CommonLootTable.addLoot(IronDagger,1)
#--Uncommon--
UncommonLootTable = LootTable(70)
UncommonLootTable.addLoot(IronHelmet,4)
UncommonLootTable.addLoot(IronChestplate,2)
UncommonLootTable.addLoot(IronLeggins,4)
UncommonLootTable.addLoot(IronShield,4)
UncommonLootTable.addLoot(IronSword,3)
UncommonLootTable.addLoot(BegginersWand,2)
UncommonLootTable.addLoot(WizardHat,2)
UncommonLootTable.addLoot(MagicTome,1)
#----Rare----
RareLootTable = LootTable(80)
RareLootTable.addLoot(IronChestplate,2)
RareLootTable.addLoot(IronSword,3)
RareLootTable.addLoot(BegginersWand,2)
RareLootTable.addLoot(Crossbow,3)
RareLootTable.addLoot(StudentCape,2)
RareLootTable.addLoot(MagicOrb,1)




#----Zombie----
ZombieLoot = LootTable()
ZombieLoot.addLoot(WoodenSword,10)
ZombieLoot.addLoot(WoodenShield,9)
ZombieLoot.addLoot(IronSword,4)
ZombieLoot.addLoot(IronDagger,7)
ZombieLoot.addLoot(IronShield,3)
ZombieLoot.addLoot(Chainmail,8)
#----Warewolf----
WarewolfLoot = LootTable()
WarewolfLoot.addLoot(IronHelmet,5)
WarewolfLoot.addLoot(IronChestplate,2)
WarewolfLoot.addLoot(IronLeggins,4)
WarewolfLoot.addLoot(IronDagger,6)
WarewolfLoot.addLoot(IronSword,3)
#----Skeleton----
SkeletonLoot = LootTable()
SkeletonLoot.addLoot(Chainmail,10)
SkeletonLoot.addLoot(LeatherHelmet,9)
SkeletonLoot.addLoot(LeatherLeggins,5)
SkeletonLoot.addLoot(LeatherGloves,7)
SkeletonLoot.addLoot(LeatherChestplate,4)
SkeletonLoot.addLoot(WoodenBow,8)
#-----Ghost-----
GhostLoot = LootTable()
GhostLoot.addLoot(BegginersWand,5)
GhostLoot.addLoot(WizardHat,5)
GhostLoot.addLoot(StudentCape,4)
GhostLoot.addLoot(MagicTome,8)
#-----Thief-----
ThiefLoot = LootTable()
ThiefLoot.addLoot(LeatherHelmet,6)
ThiefLoot.addLoot(LeatherChestplate,4)
ThiefLoot.addLoot(LeatherLeggins,5)
ThiefLoot.addLoot(LeatherGloves,7)
ThiefLoot.addLoot(IronDagger,3)
#-----Wraith-----
WraithLoot = LootTable()
WraithLoot.addLoot(BegginersWand,9)
WraithLoot.addLoot(StudentCape,4)
WraithLoot.addLoot(MagicTome,8)
WraithLoot.addLoot(MagicOrb,3)

Zombie = Monster('Zombie', 60, 15, 20, 10, ZombieLoot)
Warewolf = Monster("Warewolf", 50, 20, 20, 20, WarewolfLoot)
Skeleton = Monster('Skeleton', 45, 10, 10, 30, SkeletonLoot)
Ghost = Monster('Ghost', 15, 5, 500, 0, GhostLoot)
Thief = Monster('Thief', 25, 10, 5, 80, ThiefLoot)
Wraith = Monster('Wraith', 100, 15, 5, 30, WraithLoot)

Wolf = Monster('Wolf', 20, 10, 10, 60, CommonLootTable)
Bear = Monster('Bear', 50, 20, 30, 5, CommonLootTable)
Bandit = Monster('Bandit', 60, 25, 40, 5, UncommonLootTable)
Troll = Monster('Troll', 120, 15, 50, 0, RareLootTable)
Demon = Monster('Demon', 100, 15, 50, 25, RareLootTable)