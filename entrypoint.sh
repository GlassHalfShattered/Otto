#!/bin/bash
mkdir -p /app/config/db ./config/images
# Initialize Exorcists.db
if [ ! -f ./config/db/Exorcists.db ]; then
    touch ./config/db/Exorcists.db
    sqlite3 ./config/db/Exorcists.db "CREATE TABLE IF NOT EXISTS Exorcists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT DEFAULT '0',
    XID TEXT DEFAULT '0',
    Agenda TEXT DEFAULT '0',           
    Blastphemy TEXT DEFAULT '0',
    Image TEXT DEFAULT '0',
    Player TEXT DEFAULT '0',
    Status TEXT DEFAULT '0',           
    Sex TEXT DEFAULT '0',              
    Height TEXT DEFAULT '0',           
    Weight TEXT DEFAULT '0',           
    Hair TEXT DEFAULT '0',             
    Eyes TEXT DEFAULT '0',             
    Force TEXT DEFAULT '0',            
    Conditioning TEXT DEFAULT '0',     
    Covert TEXT DEFAULT '0',           
    Interfacing TEXT DEFAULT '0',      
    Investigation TEXT DEFAULT '0',
    Surveillance TEXT DEFAULT '0',     
    Negotiation TEXT DEFAULT '0',      
    Authority TEXT DEFAULT '0',      
    Connection TEXT DEFAULT '0',  
    Improvements TEXT DEFAULT '0',
    Stress TEXT DEFAULT '0',
    Injuries TEXT DEFAULT '0',
    Afflictions TEXT DEFAULT '0',   
    Divine_Agony TEXT DEFAULT '0',
    XP TEXT DEFAULT '0',
    Advancements TEXT DEFAULT '0',       
    Cat_Rating TEXT DEFAULT '0',       
    Psyche TEXT DEFAULT '0',
    Burst TEXT DEFAULT '0',
    Kit_Points TEXT DEFAULT '0',
    Agenda_Items TEXT DEFAULT '0',    
    Agenda_Abilities TEXT DEFAULT '0',
    Observed_Power0 TEXT DEFAULT '0',
    Observed_Power1 TEXT DEFAULT '0', 
    Observed_Power2 TEXT DEFAULT '0', 
    Observed_Power3 TEXT DEFAULT '0', 
    Observed_Power4 TEXT DEFAULT '0', 
    CID TEXT DEFAULT '0',             
    Sin TEXT DEFAULT '0',              
    Sin_Marks TEXT DEFAULT 'None',
    Scrip TEXT DEFAULT '0',         
    Coordination TEXT DEFAULT '0', 
    HOOK1 TEXT DEFAULT '0',
    HOOK2 TEXT DEFAULT '0',
    HOOK3 TEXT DEFAULT '0',
    ADD_BLSPH TEXT DEFAULT '0',
    Kit_Items TEXT DEFAULT 'N/A',
    HOOK1_NAME TEXT DEFAULT 'Hook 1',
    HOOK2_NAME TEXT DEFAULT 'Hook 2',
    HOOK3_NAME TEXT DEFAULT 'Hook 3',
    Kit_Mod TEXT DEFAULT '0',
    Total_Sin_Marks TEXT DEFAULT '0',
    Passives TEXT DEFAULT '0',
    Visitation TEXT DEFAULT '0',
    Living_Quarters TEXT DEFAULT '0',
    Private_Room TEXT DEFAULT '0',
    Relaxed_Grooming TEXT DEFAULT '0',
    Improved_Meals TEXT DEFAULT '0',
    Indulgences TEXT DEFAULT '0',
    Leave_Of_Absence TEXT DEFAULT '0',
    Silver TEXT DEFAULT '0',
    Inj_mod TEXT DEFAULT '0',
    Stress_Mod TEXT DEFAULT '0',
    Sin_Mod TEXT DEFAULT '0',
    Q1 TEXT DEFAULT '0',
    Q2 TEXT DEFAULT '0',
    Q3 TEXT DEFAULT '0',
    Q4 TEXT DEFAULT '0',
    Q5 TEXT DEFAULT '0'
    );"
fi
# Initialize level.db
if [ ! -f ./config/db/level.db ]; then
    touch ./config/db/level.db
    sqlite3 ./config/db/level.db "CREATE TABLE IF NOT EXISTS Users 
    (Guild_id INTEGER, 
    User_id INTEGER, 
    Level INTEGER, 
    Xp INTEGER, 
    Level_Up_XP INTEGER, 
    Username TEXT, 
    Number_Of_Messages INTEGER, 
    PRIMARY KEY (Guild_id, User_id))"

fi
 #Initialize groove_grove.db
if [ ! -f ./config/db/groove_grove.db ]; then
    touch ./config/db/groove_grove.db
    sqlite3 ./config/db/groove_grove.db "CREATE TABLE IF NOT EXISTS Nominations (
    id INTEGER PRIMARY KEY,
    Username TEXT NOT NULL,
    Nomination TEXT NOT NULL,
    Date INTEGER NOT NULL,
    Link TEXT NOT NULL,
    UserID TEXT NOT NULL,
    Artist TEXT
    );" || { echo "Error creating Nominations table"; exit 1; }
    echo "groove_grove.db initialized successfully"
fi
# Initialize polymarket.db
if [ ! -f ./config/db/polymarket.db ]; then
    touch ./config/db/polymarket.db
    sqlite3 ./config/db/polymarket.db "CREATE TABLE IF NOT EXISTS Transactions (
        Id INTEGER PRIMARY KEY,
        Date TEXT NOT NULL,
        Shares_Purchased REAL NOT NULL,
        Event TEXT NOT NULL,
        Resolve_Date TEXT NOT NULL,
        User_id TEXT NOT NULL,
        BetterBucks_Spent REAL NOT NULL,
        BetterBucks_Before REAL NOT NULL,
        BetterBucks_After REAL NOT NULL,
        Question TEXT NOT NULL,
        Answer TEXT NOT NULL,
        Resolved TEXT DEFAULT 'NO',
        Win TEXT
    );" || { echo "Error creating Transactions table"; exit 1; }
    sqlite3 ./config/db/polymarket.db "CREATE TABLE IF NOT EXISTS Users (
        Id INTEGER PRIMARY KEY,
        BetterBucks REAL NOT NULL,
        Guild_id TEXT NOT NULL,
        User_id TEXT NOT NULL,
        User_Name TEXT
    );" || { echo "Error creating Users table"; exit 1; }
    echo "polymarket.db initialized successfully"
fi
exec python3 /app/main.py