import pymem
import time
from src.memory_adresses import *
from threading import Thread
import threading


class Wallhack:
    def __init__(self, pm=None, client=None):
        self.pm = pm
        self.client = client
        self.run_event = threading.Event()
        self.run_event.set()
        thread = Thread(target=self._wh, args=())
        thread.start()

    def _wh(self):
        player_team = int(pm.read_int(player + m_iTeamNum))
        while self.run_event.is_set():
            time.sleep(0.0001)
            for i in range(1, 32):  # entities 1-32 are reserved for players
                entity = self.pm.read_int(self.client + dwEntityList + i * 0x10)
                if entity:
                    is_ennemy = self.pm.read_int(entity + m_iTeamNum)
                    entity_glow = self.pm.read_int(entity + m_iGlowIndex)
                    if player_team != is_ennemy:  # wh only on ennemy team
                        self.pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(255))  # R 
                        self.pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(0))  # G
                        self.pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(0))  # B
                        self.pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(0.5))  # Alpha
                        self.pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1)


class Trigger:
    def __init__(self, pm=None, client=None):
        self.pm = pm
        self.client = client
        self.run_event = threading.Event()
        self.run_event.set()
        thread = Thread(target=self._trigger, args=())
        thread.start()

    def _trigger(self):
        player_team = int(pm.read_int(player + m_iTeamNum))
        while self.run_event.is_set():
            cr_entity = self.pm.read_int(player + m_iCrosshairId)
            if cr_entity > 0 and cr_entity <= 64:
                entity = self.pm.read_int(self.client + dwEntityList + (cr_entity -1) * 0x10)
                entity_team = self.pm.read_int(entity + m_iTeamNum)
                if player_team != entity_team:
                    self.pm.write_int(self.client + dwForceAttack, 5)
                    self.pm.write_int(self.client + dwForceAttack, 4)


if __name__ == "__main__":
    print("Loading...")
    pm = pymem.Pymem("csgo.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client_panorama.dll").lpBaseOfDll
    player = pm.read_int(client + dwLocalPlayer)
    glow_manager = pm.read_int(client + dwGlowObjectManager)
    try:
        trig = Trigger(pm, client)
        wh = Wallhack(pm, client)
        print("Running!")
    except KeyboardInterrupt:
        exit()