import pygame

# --- 1. ALAPBEÁLLÍTÁSOK ---
pygame.init()
SZELESSEG, MAGASSAG = 800, 600
ablak = pygame.display.set_mode((SZELESSEG, MAGASSAG))
pygame.display.set_caption("Kocka Mario 2")
ora = pygame.time.Clock()
pygame.mixer.init()
pygame.mixer.music.load("8-Bit.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

# kép betöltése
background = pygame.image.load("bg3.png").convert()

# eredeti méret
bg_width = background.get_width()
bg_height = background.get_height()
# átméretezett háttér
background = pygame.transform.scale(background, (3072, 600))
scroll = 0
speed = 0.2

# --- SPRITEOK ---
sprite_sheet = pygame.image.load("sprite.png").convert_alpha()
portal_sheet = pygame.image.load("portalsprite.png").convert_alpha()
enemy_sheet = pygame.image.load("theeyeenemy.png").convert_alpha()
slingy_sheet = pygame.image.load("slingy_sam2.png").convert_alpha()
sarkany_sheet = pygame.image.load("sarkany.png").convert_alpha()
lazer_sprite = pygame.image.load("lazer.png").convert_alpha()
coin_sprite = pygame.image.load("coin.png").convert_alpha()
coin_sprite = pygame.transform.scale(coin_sprite,(40,40))

# Portál frame-ek
portal_frames = [
    portal_sheet.subsurface((0,0,16,16)),
    portal_sheet.subsurface((16,0,16,16))
]
portal_frame = 0
portal_timer = 0

# Színek
FEKETE, FEHER, EGSZINKEK = (0,0,0),(255,255,255),(135,206,235)
FOLD_ZOLD, MARIO_PIROS = (34,139,34),(255,50,50)
ARANY, CEL_KEK = (255,215,0),(0,0,255)

betutipus = pygame.font.SysFont("arial",24,bold=True)
nagy_betu = pygame.font.SysFont("arial",48,bold=True)

# --- 2. JÁTÉKOS OSZTÁLY ---
class Jatekos:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.seb_x = 0
        self.seb_y = 0
        self.gravitacio = 0.5
        self.ugras_ero = -15
        self.a_foldon_van = False
        self.frame = 0
        self.anim_timer = 0
        self.facing_left = False
        self.frames = [
            sprite_sheet.subsurface((0,0,16,16)),
            sprite_sheet.subsurface((16,0,16,16))
        ]
    def mozgatas(self, platformok):
        self.rect.x += self.seb_x
        for p in platformok:
            if self.rect.colliderect(p):
                if self.seb_x>0: self.rect.right=p.left
                if self.seb_x<0: self.rect.left=p.right
        self.seb_y += self.gravitacio
        self.rect.y += self.seb_y
        self.a_foldon_van = False
        for p in platformok:
            if self.rect.colliderect(p):
                if self.seb_y>0:
                    self.rect.bottom=p.top
                    self.seb_y=0
                    self.a_foldon_van=True
                elif self.seb_y<0:
                    self.rect.top=p.bottom
                    self.seb_y=0
        if self.seb_x!=0:
            self.anim_timer+=1
            if self.anim_timer>=30:
                self.frame=(self.frame+1)%2
                self.anim_timer=0
        self.facing_left = self.seb_x < 0
    def rajzol(self, felulet, kamera_x):
        rajz_x=self.rect.x-kamera_x
        rajz_y=self.rect.y
        sprite=self.frames[self.frame]
        if self.facing_left: sprite=pygame.transform.flip(sprite,True,False)
        sprite=pygame.transform.scale(sprite,(40,40))
        felulet.blit(sprite,(rajz_x,rajz_y))

# --- 2b. ENEMY OSZTÁLYOK ---
class Enemy:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,32,32)
        self.frame=0
        self.anim_timer=0
        self.facing_left=False
        self.frames=[enemy_sheet.subsurface((0,0,16,16)),enemy_sheet.subsurface((16,0,16,16))]
    def update(self,mario):
        self.anim_timer+=1
        if self.anim_timer>=15:
            self.frame=(self.frame+1)%2
            self.anim_timer=0
        self.facing_left=mario.rect.centerx<self.rect.centerx
    def rajzol(self,felulet,kamera_x):
        sprite=self.frames[self.frame]
        if self.facing_left: sprite=pygame.transform.flip(sprite,True,False)
        sprite=pygame.transform.scale(sprite,(40,40))
        felulet.blit(sprite,(self.rect.x-kamera_x,self.rect.y))

class SlingySam:
    def __init__(self,platform,seb=2):
        self.platform=platform
        self.rect=pygame.Rect(platform.left,platform.top-16,48,32)
        self.seb=seb
        self.frame=0
        self.anim_timer=0
        self.facing_left=False
        self.frames=[slingy_sheet.subsurface((0,0,96,32)),slingy_sheet.subsurface((96,0,96,32))]
    def update(self):
        self.anim_timer+=1
        if self.anim_timer>=15:
            self.frame=(self.frame+1)%2
            self.anim_timer=0
        self.rect.x+=self.seb
        if self.rect.left<=self.platform.left:
            self.rect.left=self.platform.left
            self.seb=abs(self.seb)
        elif self.rect.right>=self.platform.right:
            self.rect.right=self.platform.right
            self.seb=-abs(self.seb)
        self.facing_left=self.seb<0
    def rajzol(self,felulet,kamera_x):
        sprite=self.frames[self.frame]
        if self.facing_left: sprite=pygame.transform.flip(sprite,True,False)
        sprite=pygame.transform.scale(sprite,(48,16))
        felulet.blit(sprite,(self.rect.x-kamera_x,self.rect.y))

# --- 2c. SÁRKÁNY ---
class Sarkany:
    def __init__(self,y,seb=2):
        self.y=y
        self.seb=seb
        self.rect=pygame.Rect(0,y,96,96)
        self.frames_nem_los=[sarkany_sheet.subsurface((0,0,96,96)),sarkany_sheet.subsurface((96,0,96,96))]
        self.frame_los=sarkany_sheet.subsurface((192,0,96,96))
        self.frame=0
        self.anim_timer=0
        self.los=False
        self.laser_timer=0
        self.laser_period=3000
        self.lazer=None
        self.facing_left=False
    def update(self,dt,mario):
        # Követi a játékost vízszintben
        if self.rect.centerx<mario.rect.centerx:
            self.rect.x+=self.seb
            self.facing_left=False
        elif self.rect.centerx>mario.rect.centerx:
            self.rect.x-=self.seb
            self.facing_left=True
        if self.rect.left<0: self.rect.left=0
        if self.rect.right>3000: self.rect.right=3000
        # 3mp váltás
        self.laser_timer+=dt
        if self.laser_timer>=self.laser_period:
            self.los=not self.los
            self.laser_timer=0
        # Ha lő, frissíti a lézer pozícióját a sárkánnyal
        if self.los:
            self.lazer=pygame.Rect(self.rect.centerx-8,0,16,96*15)
        else:
            self.anim_timer+=dt
            if self.anim_timer>=250:
                self.frame=(self.frame+1)%2
                self.anim_timer=0
            self.lazer=None
    def rajzol(self,felulet,kamera_x):
        sprite=self.frame_los if self.los else self.frames_nem_los[self.frame]
        if self.facing_left: sprite=pygame.transform.flip(sprite,True,False)
        sprite=pygame.transform.scale(sprite,(96,96))
        felulet.blit(sprite,(self.rect.x-kamera_x,self.y))
        if self.los and self.lazer:
            lazer_img=pygame.transform.scale(lazer_sprite,(16,96*15))
            felulet.blit(lazer_img,(self.lazer.x-kamera_x,self.lazer.y))

# --- 3. PÁLYA BETÖLTŐ ---
def palya_betoltes(szint):
    platformok=[]
    ermek=[]
    enemyk=[]
    enemyk_vegleges = []
    sarkanyok = []
    if szint==1:
        platformok=[pygame.Rect(0,550,1000,50),
                    pygame.Rect(1100,550,1000,50),
                    pygame.Rect(400,450,150,20),
                    pygame.Rect(700,350,150,20),
                    pygame.Rect(1300,400,200,20),
                    pygame.Rect(1600,250,100,20)]
        ermek=[pygame.Rect(450,410,20,20),
               pygame.Rect(750,310,20,20),
               pygame.Rect(1350,360,20,20),
               pygame.Rect(1640,210,20,20)]
        enemyk=[Enemy(600,500),
                Enemy(1400,300),
                Enemy(1600,210),
                Enemy(1100,500)]
        enemyk_vegleges = [SlingySam(platformok[3],seb=3)]
        sarkanyok = [Sarkany(y=50,seb=3)]
        celkapu=pygame.Rect(1900,450,50,100)
        kezdo_pos=(50,450)
    elif szint==2:
        platformok=[pygame.Rect(0,550,400,50),
                    pygame.Rect(500,450,100,20),
                    pygame.Rect(700,350,100,20),
                    pygame.Rect(900,250,100,20),
                    pygame.Rect(1100,400,300,20),
                    pygame.Rect(1500,550,500,50),
                    pygame.Rect(1800,450,100,20),
                    pygame.Rect(2100,300,300,20)]
        ermek=[pygame.Rect(540,410,20,20),
               pygame.Rect(740,310,20,20),
               pygame.Rect(940,210,20,20),
               pygame.Rect(1200,360,20,20),
               pygame.Rect(2200,260,20,20)]
        enemyk=[Enemy(600,300)]
        enemyk_vegleges = [SlingySam(platformok[5],seb=2)]
        celkapu=pygame.Rect(2300,200,50,100)
        kezdo_pos=(50,450)
    elif szint==3:
        platformok=[pygame.Rect(0,550,400,50),
                    pygame.Rect(500,450,20,20),
                    pygame.Rect(700,350,5,20),
                    pygame.Rect(900,250,20,20),
                    pygame.Rect(1100,400,300,20),
                    pygame.Rect(1500,550,500,50),
                    pygame.Rect(1800,450,100,20),
                    pygame.Rect(2100,300,300,20)]
        ermek=[pygame.Rect(510,410,20,20),
               pygame.Rect(699,345,20,20),
               pygame.Rect(910,200,20,20),
               pygame.Rect(1200,300,20,20),
               pygame.Rect(2200,260,20,20)]
        sarkanyok = [Sarkany(y=40,seb=4)]
        enemyk=[Enemy(600,300)]
        enemyk_vegleges = [SlingySam(platformok[4],seb=2)]
        celkapu=pygame.Rect(2300,200,50,100)
        kezdo_pos=(50,450)

    elif szint == 4:
        platformok = [
            pygame.Rect(0, 550, 100, 50),
            pygame.Rect(300, 450, 40, 20),
            pygame.Rect(50, 330, 40, 20),
            pygame.Rect(350, 230, 40, 20),
            pygame.Rect(950, 400, 300, 20),
            pygame.Rect(1500, 300, 500, 50),
            pygame.Rect(1800, 250, 100, 20),
            pygame.Rect(2100, 200, 100, 20),
            pygame.Rect(2500, 180, 100, 20),
            pygame.Rect(2750, 350, 100, 20),
            pygame.Rect(3000, 400, 300, 20)


        ]
        ermek = [
            pygame.Rect(320, 410, 20, 20),
            pygame.Rect(70, 300, 20, 20),
            pygame.Rect(937, 240, 20, 20),
            pygame.Rect(50, 500, 20, 20),
            pygame.Rect(2150, 130, 20, 20)
        ]
        enemyk = [
            Enemy(800, 350),
            Enemy(2550, 20),
            Enemy(3000, 300),
            Enemy(1700, 310),
        ]
        enemyk_vegleges = [
            SlingySam(platformok[4],seb=3),
            SlingySam(platformok[5],seb=3),
            SlingySam(platformok[10],seb=3)
        ]
        sarkanyok = [Sarkany(y=15,seb=3)]
                           
        celkapu = pygame.Rect(3250, 300, 50, 100)
        kezdo_pos = (50, 450)
    elif szint == 5:
        platformok = [
            pygame.Rect(0, 550, 500, 50),
            pygame.Rect(2000, 550, 300, 20),
            pygame.Rect(2000, 350, 20, 200),
            pygame.Rect(1300, 550, 500, 20)
        ]
        enemyk = [
            Enemy(800,500 ),
            Enemy(850,500),
            Enemy(900,500),
            Enemy(950,450),
            Enemy(1000,450),
            Enemy(1050,450),
            Enemy(1150,500),
            Enemy(1200,450),
            Enemy(1800,450)
        ]
        enemyk_vegleges = [SlingySam(platformok[3],seb=3),
                           SlingySam(platformok[3],seb=4),
                           SlingySam(platformok[3],seb=5)]
        sarkanyok = [Sarkany(y=40,seb=3)]
        celkapu = pygame.Rect(2250, 450, 50, 100)
        kezdo_pos = (50, 450)
    elif szint == 6:
        platformok = [
            pygame.Rect(0, 550, 500, 50),
        ]
        enemyk = [
            Enemy(800,500 ),
            Enemy(1075,500),
            Enemy(1350,500),
            Enemy(1625,500),
            Enemy(1900,500),
            Enemy(2175,500),
            Enemy(2450,500),
           
        ]                     
        celkapu = pygame.Rect(2725, 450, 50, 100)
        kezdo_pos = (50, 450)
    elif szint == 7:
        platformok = [
            pygame.Rect(0, 550, 200, 50),
            pygame.Rect(577, 550, 475, 50)
        ]

        celkapu = pygame.Rect(1000, 450, 50, 100)
        kezdo_pos = (50, 450)
    elif szint == 8:
        platformok = [
            pygame.Rect(0, 550, 300, 50),
            pygame.Rect(1150, 0, 50, 450)
        ]
        enemyk = [
            Enemy(500,500),
            Enemy(600,400),
            Enemy(700,300),
            Enemy(950,300),
            Enemy(950,200),
            Enemy(950,175),
            Enemy(950,150),
            Enemy(1100,500),
            Enemy(1200,500),
            Enemy(1400,400),
            Enemy(1625,300),
            Enemy(1900,500),
            Enemy(2000,500),
            Enemy(2100,500),
            Enemy(2200,500),
            Enemy(2300,500),
            Enemy(2400,500),
            Enemy(2500,500),
            Enemy(2600,500)
        ]
        celkapu = pygame.Rect(2725, 450, 50, 100)
        kezdo_pos = (50, 450)
    eredeti_ermek=[pygame.Rect(e.x,e.y,e.width,e.height) for e in ermek]
    return platformok,ermek,enemyk,enemyk_vegleges,sarkanyok,celkapu,kezdo_pos,eredeti_ermek
     
    

# --- 4. JÁTÉK VÁLTOZÓI ---
aktualis_palya=1
max_palya=7
pontszam=0
halalok = 0  # Death Tracker
kamera_x=0

platformok,ermek,enemyk,enemyk_vegleges,sarkanyok,celkapu,kezdo_pos,eredeti_ermek=palya_betoltes(aktualis_palya)
mario=Jatekos(kezdo_pos[0],kezdo_pos[1])

# sárkány inicializálás
# sarkany=Sarkany(y=50,seb=3)

# --- 5. FŐ CICLUS ---
futo=True
jatek_vege=False
while futo:
    dt=ora.tick(60)
    for event in pygame.event.get():
        if event.type==pygame.QUIT: futo=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_UP and mario.a_foldon_van and not jatek_vege:
                mario.seb_y=mario.ugras_ero
    if not jatek_vege:
        gombok=pygame.key.get_pressed()
        mario.seb_x=0
        if gombok[pygame.K_LEFT]: mario.seb_x=-6
        if gombok[pygame.K_RIGHT]: mario.seb_x=6

        mario.mozgatas(platformok)
        kamera_x=max(0,mario.rect.x-(SZELESSEG//2))

        if mario.rect.top>MAGASSAG:
            mario.rect.x,mario.rect.y=kezdo_pos
            mario.seb_y=0
            pontszam=max(0,pontszam-2)
            halalok += 1  # ide írjuk a növelést
            platformok,_,enemyk,enemyk_vegleges,_,_,_,_ = palya_betoltes(aktualis_palya)
            

        for erme in ermek[:]:
            if mario.rect.colliderect(erme):
                ermek.remove(erme)
                pontszam+=1

        if mario.rect.colliderect(celkapu):
            aktualis_palya+=1
            if aktualis_palya>max_palya: jatek_vege=True
            else:
                platformok,ermek,enemyk,enemyk_vegleges,sarkanyok,celkapu,kezdo_pos,eredeti_ermek=palya_betoltes(aktualis_palya)
                mario.rect.x,mario.rect.y=kezdo_pos
                mario.seb_y=0

        for e in enemyk:
            if isinstance(e,Enemy): e.update(mario)
            else: e.update()
            if mario.rect.colliderect(e.rect):

                # ha felülről ugrik rá
                if mario.seb_y > 0 and mario.rect.bottom >= e.rect.top - mario.seb_y:
                    enemyk.remove(e)
                    if pygame.key.get_pressed()[pygame.K_UP]:
                        mario.seb_y = -12   # nagyobb visszapattanás
                    else:
                        mario.seb_y = -5 # kisebb visszapattanas

                # ha nem felülről (pl oldalról)
                else:
                    mario.rect.x, mario.rect.y = kezdo_pos
                    mario.seb_y = 0
                    halalok += 1  # ide is írjuk a növelést
                    platformok,_,enemyk,enemyk_vegleges,_,_,_,_ = palya_betoltes(aktualis_palya)

        for e in enemyk_vegleges:
            if isinstance(e,Enemy): e.update(mario)
            else: e.update()
            if mario.rect.colliderect(e.rect):
                mario.rect.x, mario.rect.y = kezdo_pos
                mario.seb_y = 0
                halalok += 1  # <<< hozzáadva
                platformok,_,enemyk,enemyk_vegleges,_,_,_,_ = palya_betoltes(aktualis_palya)

        for e in sarkanyok:
            if isinstance(e,Enemy): e.update(dt,mario)
            else: e.update(dt,mario)
            if mario.rect.colliderect(e.rect):

                # ha felülről ugrik rá
                if mario.seb_y > 0 and mario.rect.bottom >= e.rect.top - mario.seb_y:
                    sarkanyok.remove(e)
                    if pygame.key.get_pressed()[pygame.K_UP]:
                        mario.seb_y = -12   # nagyobb visszapattanás
                    else:
                        mario.seb_y = -4 # kisebb visszapattanas

                # ha nem felülről (pl oldalról)
                else:
                    mario.rect.x, mario.rect.y = kezdo_pos
                    mario.seb_y = 0
                    halalok += 1  # ide is írjuk a növelést
                    platformok,_,enemyk,enemyk_vegleges,_,_,_,_ = palya_betoltes(aktualis_palya)
                   
        for e in sarkanyok:
#            if isinstance(e,Enemy): e.update(dt,mario)
#            else: e.update(dt,mario)
            if e.los and e.lazer and mario.rect.colliderect(e.lazer):
                mario.rect.x,mario.rect.y=kezdo_pos
                mario.seb_y=0
                halalok += 1  # <<< hozzáadva
                platformok,_,enemyk,enemyk_vegleges,_,_,_,_ = palya_betoltes(aktualis_palya)
            
            '''   
        # sárkány update
        sarkany.update(dt,mario)
        if sarkany.los and sarkany.lazer and mario.rect.colliderect(sarkany.lazer):
            mario.rect.x,mario.rect.y=kezdo_pos
            mario.seb_y=0
            halalok += 1  # <<< hozzáadva
            platformok,_,enemyk,enemyk_vegleges,_,_,_,_ = palya_betoltes(aktualis_palya)
            '''
        portal_timer+=1
        if portal_timer>=30:
            portal_frame=(portal_frame+1)%2
            portal_timer=0

    # --- RAJZOLÁS ---
    # ablak.fill(EGSZINKEK)
        # háttér mozgatása
    scroll -= speed

    # ha a kép véget ér → újrakezd
    if abs(scroll) > bg_width * 3:
        scroll = 0

    # háttér kirajzolása (többször egymás után)
    for i in range(2):
        ablak.blit(background, (scroll + i * bg_width * 3 - kamera_x, 0))

    for p in platformok:
        rajz_rect=pygame.Rect(p.x-kamera_x,p.y,p.width,p.height)
        pygame.draw.rect(ablak,FOLD_ZOLD,rajz_rect)
        pygame.draw.rect(ablak,FEKETE,rajz_rect,2)
    for erme in ermek:
        rajz_x = erme.x - kamera_x
        rajz_y = erme.y
        coin = pygame.transform.scale(coin_sprite,(20,20))
        ablak.blit(coin_sprite,(rajz_x,rajz_y))
    for e in enemyk:
        e.rajzol(ablak,kamera_x)
    for e in enemyk_vegleges:
        e.rajzol(ablak,kamera_x)
    for e in sarkanyok:
        e.rajzol(ablak,kamera_x)
    cel_rajz=pygame.Rect(celkapu.x-kamera_x,celkapu.y,celkapu.width,celkapu.height)
    portal_sprite=pygame.transform.scale(portal_frames[portal_frame],(50,100))
    ablak.blit(portal_sprite,(cel_rajz.x,cel_rajz.y))
#    sarkany.rajzol(ablak,kamera_x)
    mario.rajzol(ablak,kamera_x)
    szint_szoveg=betutipus.render(f"Pálya: {aktualis_palya}/{max_palya}",True,FEKETE)
    pont_szoveg=betutipus.render(f"Érmék: {pontszam}",True,FEKETE)
    halal_szoveg = betutipus.render(f"Halálok: {halalok}", True, FEKETE)
    ablak.blit(szint_szoveg,(10,10))
    ablak.blit(pont_szoveg,(10,40))
    ablak.blit(halal_szoveg, (10, 70))  # érmék alatt jelenik meg
    if jatek_vege:
        vege_szoveg=nagy_betu.render("MINDEN PÁLYA TELJESÍTVE!",True,MARIO_PIROS)
        ablak.blit(vege_szoveg,(SZELESSEG//2-vege_szoveg.get_width()//2,MAGASSAG//2))
    pygame.display.flip()
    

pygame.quit()