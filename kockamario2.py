import pygame

# --- 1. ALAPBEÁLLÍTÁSOK ---
pygame.init()
SZELESSEG, MAGASSAG = 800, 600
ablak = pygame.display.set_mode((SZELESSEG, MAGASSAG))
pygame.display.set_caption("Kocka Mario 2")
ora = pygame.time.Clock()

# Spriteok betöltése
sprite_sheet = pygame.image.load("sprite.png").convert_alpha()
portal_sheet = pygame.image.load("portalsprite.png").convert_alpha()

# Portál frame-ek
portal_frames = [
    portal_sheet.subsurface((0, 0, 16, 16)),
    portal_sheet.subsurface((16, 0, 16, 16))
]

portal_frame = 0
portal_timer = 0

# Színek
FEKETE, FEHER, EGSZINKEK = (0, 0, 0), (255, 255, 255), (135, 206, 235)
FOLD_ZOLD, MARIO_PIROS = (34, 139, 34), (255, 50, 50)
ARANY, CEL_KEK = (255, 215, 0), (0, 0, 255)

betutipus = pygame.font.SysFont("arial", 24, bold=True)
nagy_betu = pygame.font.SysFont("arial", 48, bold=True)

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
            sprite_sheet.subsurface((0, 0, 16, 16)),
            sprite_sheet.subsurface((16, 0, 16, 16))
        ]

    def mozgatas(self, platformok):

        self.rect.x += self.seb_x
        for p in platformok:
            if self.rect.colliderect(p):
                if self.seb_x > 0: self.rect.right = p.left
                if self.seb_x < 0: self.rect.left = p.right

        self.seb_y += self.gravitacio
        self.rect.y += self.seb_y
        self.a_foldon_van = False
        
        for p in platformok:
            if self.rect.colliderect(p):
                if self.seb_y > 0:
                    self.rect.bottom = p.top
                    self.seb_y = 0
                    self.a_foldon_van = True
                elif self.seb_y < 0:
                    self.rect.top = p.bottom
                    self.seb_y = 0

        if self.seb_x != 0:
            self.anim_timer += 1

            if self.anim_timer >= 30:
                self.frame = (self.frame + 1) % 2
                self.anim_timer = 0

        if self.seb_x < 0:
            self.facing_left = True
        elif self.seb_x > 0:
            self.facing_left = False

    def rajzol(self, felulet, kamera_x):

        rajz_x = self.rect.x - kamera_x
        rajz_y = self.rect.y

        sprite = self.frames[self.frame]

        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)

        sprite = pygame.transform.scale(sprite, (40, 40))

        felulet.blit(sprite, (rajz_x, rajz_y))


# --- 3. PÁLYA BETÖLTŐ FÜGGVÉNY ---
def palya_betoltes(szint):
    platformok = []
    ermek = []
    
    if szint == 1:

        platformok = [
            pygame.Rect(0, 550, 1000, 50),
            pygame.Rect(1100, 550, 1000, 50),
            pygame.Rect(400, 450, 150, 20),
            pygame.Rect(700, 350, 150, 20),
            pygame.Rect(1300, 400, 200, 20),
            pygame.Rect(1600, 250, 100, 20)
        ]

        ermek = [
            pygame.Rect(450, 410, 20, 20),
            pygame.Rect(750, 310, 20, 20),
            pygame.Rect(1350, 360, 20, 20),
            pygame.Rect(1640, 210, 20, 20)
        ]

        celkapu = pygame.Rect(1900, 450, 50, 100)
        kezdo_pos = (50, 450)
        
    elif szint == 2:

        platformok = [
            pygame.Rect(0, 550, 400, 50),
            pygame.Rect(500, 450, 100, 20),
            pygame.Rect(700, 350, 100, 20),
            pygame.Rect(900, 250, 100, 20),
            pygame.Rect(1100, 400, 300, 20),
            pygame.Rect(1500, 550, 500, 50),
            pygame.Rect(1800, 450, 100, 20),
            pygame.Rect(2100, 300, 300, 20)
        ]

        ermek = [
            pygame.Rect(540, 410, 20, 20),
            pygame.Rect(740, 310, 20, 20),
            pygame.Rect(940, 210, 20, 20),
            pygame.Rect(1200, 360, 20, 20),
            pygame.Rect(2200, 260, 20, 20)
        ]

        celkapu = pygame.Rect(2300, 200, 50, 100)
        kezdo_pos = (50, 450)

    elif szint == 3:

        platformok = [
            pygame.Rect(0, 550, 400, 50),
            pygame.Rect(500, 450, 20, 20),
            pygame.Rect(700, 350, 5, 20),
            pygame.Rect(900, 250, 20, 20),
            pygame.Rect(1100, 400, 300, 20),
            pygame.Rect(1500, 550, 500, 50),
            pygame.Rect(1800, 450, 100, 20),
            pygame.Rect(2100, 300, 300, 20)
        ]

        ermek = [
            pygame.Rect(510, 410, 20, 20),
            pygame.Rect(701, 348, 20, 20),
            pygame.Rect(940, 260, 20, 20),
            pygame.Rect(1200, 360, 20, 20),
            pygame.Rect(2200, 260, 20, 20)
        ]

        celkapu = pygame.Rect(2300, 200, 50, 100)
        kezdo_pos = (50, 450)
        
    return platformok, ermek, celkapu, kezdo_pos


# --- 4. JÁTÉK VÁLTOZÓI ---
aktualis_palya = 1
max_palya = 3
pontszam = 0
kamera_x = 0

platformok, ermek, celkapu, kezdo_pos = palya_betoltes(aktualis_palya)
mario = Jatekos(kezdo_pos[0], kezdo_pos[1])

# --- 5. FŐ JÁTÉKCIKLUS ---
futo = True
jatek_vege = False

while futo:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            futo = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and mario.a_foldon_van and not jatek_vege:
                mario.seb_y = mario.ugras_ero

    if not jatek_vege:

        gombok = pygame.key.get_pressed()

        mario.seb_x = 0

        if gombok[pygame.K_LEFT]:
            mario.seb_x = -6

        if gombok[pygame.K_RIGHT]:
            mario.seb_x = 6

        mario.mozgatas(platformok)

        kamera_x = mario.rect.x - (SZELESSEG // 2)

        if kamera_x < 0:
            kamera_x = 0

        if mario.rect.top > MAGASSAG:
            mario.rect.x, mario.rect.y = kezdo_pos
            mario.seb_y = 0
            pontszam = max(0, pontszam - 2)

        for erme in ermek[:]:
            if mario.rect.colliderect(erme):
                ermek.remove(erme)
                pontszam += 1

        if mario.rect.colliderect(celkapu):
            aktualis_palya += 1

            if aktualis_palya > max_palya:
                jatek_vege = True
            else:
                platformok, ermek, celkapu, kezdo_pos = palya_betoltes(aktualis_palya)
                mario.rect.x, mario.rect.y = kezdo_pos
                mario.seb_y = 0

    # --- PORTÁL ANIMÁCIÓ ---
    portal_timer += 1
    if portal_timer >= 30:
        portal_frame = (portal_frame + 1) % 2
        portal_timer = 0

    # --- RAJZOLÁS ---
    ablak.fill(EGSZINKEK)

    for p in platformok:
        rajz_rect = pygame.Rect(p.x - kamera_x, p.y, p.width, p.height)
        pygame.draw.rect(ablak, FOLD_ZOLD, rajz_rect)
        pygame.draw.rect(ablak, FEKETE, rajz_rect, 2)

    for erme in ermek:
        rajz_rect = pygame.Rect(erme.x - kamera_x, erme.y, erme.width, erme.height)
        pygame.draw.ellipse(ablak, ARANY, rajz_rect)

    # PORTÁL RAJZOLÁS
    cel_rajz = pygame.Rect(celkapu.x - kamera_x, celkapu.y, celkapu.width, celkapu.height)

    portal_sprite = portal_frames[portal_frame]
    portal_sprite = pygame.transform.scale(portal_sprite, (50, 100))

    ablak.blit(portal_sprite, (cel_rajz.x, cel_rajz.y))

    mario.rajzol(ablak, kamera_x)

    szint_szoveg = betutipus.render(f"Pálya: {aktualis_palya}/{max_palya}", True, FEKETE)
    pont_szoveg = betutipus.render(f"Érmék: {pontszam}", True, FEKETE)

    ablak.blit(szint_szoveg, (10, 10))
    ablak.blit(pont_szoveg, (10, 40))

    if jatek_vege:
        vege_szoveg = nagy_betu.render("MINDEN PÁLYA TELJESÍTVE!", True, MARIO_PIROS)
        ablak.blit(vege_szoveg, (SZELESSEG//2 - vege_szoveg.get_width()//2, MAGASSAG//2))

    pygame.display.flip()
    ora.tick(60)

pygame.quit()