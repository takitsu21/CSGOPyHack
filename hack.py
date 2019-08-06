# !/usr/bin/python
# coding:utf8
import pymem
import time
import keyboard
from threading import Thread
import threading
import json
import datetime
import logging
import sys
import os
import requests


offset_update = "https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json"

def is_updated(offsets, local_offsets):
    print("Checking for updates...")
    r = requests.get(offsets)
    timestamp = json.loads(r.content)
    return local_offsets["timestamp"] == timestamp["timestamp"]

def _update(offsets):
    print("Downloading...")
    r = requests.get(offsets)
    if r.status_code == 200:
        with open("src/offsets.json", "w+", encoding="utf8") as f:
            f.write(r.text)
        print("offsets downloaded!\n")
    else:
        print(f"ERROR {r.status_code} ON DOWNLOAD")

try:
    with open("src/offsets.json", "r", encoding="utf8") as f:
        offsets = json.loads(str(''.join(f.readlines())))
except Exception as e:
    print(f"{type(e).__name__} : {type(e)}")
    _update(offset_update)
    with open("src/offsets.json", "r", encoding="utf8") as f:
        offsets = json.loads(str(''.join(f.readlines())))

QUIT = False
netvars = offsets["netvars"]
signatures = offsets["signatures"]

m_iTeamNum = netvars["m_iTeamNum"]
m_iGlowIndex = netvars["m_iGlowIndex"]
dwEntityList = signatures["dwEntityList"]
dwForceAttack = signatures["dwForceAttack"]
m_iCrosshairId = netvars["m_iCrosshairId"]
dwLocalPlayer = signatures["dwLocalPlayer"]
dwGlowObjectManager = signatures["dwGlowObjectManager"]
m_flFlashMaxAlpha = netvars["m_flFlashMaxAlpha"]


def last_update(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return f"{date.day}/{date.month}/{date.year}"

class AimLock(threading.Thread):
    def __init__(self):
        super (AimLock, self).__init__ ()
        print("Aimlock enabled... press ² to use it")
    
    def lock(self):
        pass

class AntiFlash(threading.Thread):
    def __init__(self):
        super (AntiFlash, self).__init__ ()
        print("Antiflash enabled...")

    def run(self):
        while not QUIT:
            flashed = pm.read_int(player + m_flFlashMaxAlpha)
            if flashed > 0:
                pm.write_int(player + m_flFlashMaxAlpha, 0)

class Wallhack(threading.Thread):
    def __init__(self):
        super (Wallhack, self).__init__ ()
        self.rgb = (255,0,0)
        print("Wallhack enabled...")

    def run(self):
        global player_id, entity_id
        glow_manager = pm.read_int(client + dwGlowObjectManager)

        while not QUIT:
            for i in range(1,10): # for competitive otherwise should be range(1, 32)

                entity = pm.read_int(client + dwEntityList + i * 0x10)
                if entity:
                    player_id = int(pm.read_int(player + m_iTeamNum))
                    entity_id = pm.read_int(entity + m_iTeamNum)
                    entity_glow = pm.read_int(entity + m_iGlowIndex)
                    if is_ennemy(player_id, entity_id):  # wh only on ennemy team
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(self.rgb[0]))
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(self.rgb[1]))
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(self.rgb[2]))
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(0.5))  # Alpha
                        pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1)

class Trigger(threading.Thread):
    def __init__(self):
        super (Trigger, self).__init__ ()
        print("Trigger enabled... press ALT to use it")

    def run(self):
        while not QUIT:
            if keyboard.is_pressed("ALT"):
                # player_id = pm.read_int(player + m_iTeamNum)
                on_crossh = pm.read_int(player + m_iCrosshairId)
                if on_crossh > 0: # if a player is on the crosshair
                    # entity = pm.read_int(client + dwEntityList + (player_entity_id - 1) * 0x10)
                    # entity_id = pm.read_int(entity + m_iTeamNum)
                    if is_ennemy(player_id, entity_id):
                        pm.write_int(client + dwForceAttack, 5)
                        pm.write_int(client + dwForceAttack, 4)

def is_ennemy(_player_id, _ennemy_id):
    return _player_id != _ennemy_id

def check_update(old_offset, checker):
    if is_updated(checker, old_offset):
        print("offsets are up to date")
    else: _update(checker)

if __name__ == "__main__":
    pm = pymem.Pymem("csgo.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client_panorama.dll").lpBaseOfDll
    os.system("cls")

    player = pm.read_int(client + dwLocalPlayer)
    check_update(offsets, offset_update)
    input("Press any key to start the script...")
    trig = Trigger()
    wh = Wallhack()
    fl = AntiFlash()
    trig.start()
    wh.start()
    fl.start()
    print("Running!")
    input("Press any key to interrupt the program...")
    QUIT = True
    trig.join()
    wh.join()
    fl.join()
