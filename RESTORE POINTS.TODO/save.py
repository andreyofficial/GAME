# FULL RESTORED VERSION (SAVE 3 COMPLETE + FIXED)

import pygame, os, re, math, sys, random
pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BASE = "/home/a/Desktop/GAME"
font = pygame.font.SysFont("Arial", 14)

fullscreen = False
game_state = "game"
menu_state = "main"
code_input = ""

# =============================
# STATS
# =============================
player_hp = 100
player_mana = 100
MAX_MANA = 100
MANA_REGEN = 0.25

DMG = {
    "MELEE":5,"FIREBALL":15,"LIGHTNING":20,
    "DARK":18,"SPARK":10,"RAIN":25,"NOVA":30,"ENEMY":10
}

MANA_COST = {"1":10,"2":15,"3":12,"4":8,"5":25,"6":30}

PLAYER_SPEED = 4.5
ROLL_SPEED = 12

# =============================
# PLAYER
# =============================
player = pygame.Rect(400,300,240,160)
state="idle"
frame=0
locked=False
facing_left=False

# =============================
# ENEMY
# =============================
enemy = pygame.Rect(900,400,120,120)
enemy_hp = 100
enemy_alive = True
enemy_cd = 0
ATTACK_RANGE = 90

# =============================
# COOLDOWNS
# =============================
cd = {"melee":0,"dash":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0}
cd_max = {"1":60,"2":80,"3":70,"4":40,"5":120,"6":150}

# =============================
# FX
# =============================
particles=[]
damage_texts=[]
shake=0

class Particle:
    def __init__(self,x,y,color):
        self.x=x; self.y=y
        self.vx=random.uniform(-2,2)
        self.vy=random.uniform(-2,2)
        self.life=30
        self.color=color
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.life-=1
    def draw(self,off):
        if self.life>0:
            pygame.draw.circle(screen,self.color,(int(self.x+off[0]),int(self.y+off[1])),2)

def spawn_particles(pos,color,count=10):
    for _ in range(count):
        particles.append(Particle(pos[0],pos[1],color))

class DamageText:
    def __init__(self,x,y,val):
        self.x=x; self.y=y; self.val=val; self.life=40
    def update(self):
        self.y-=1; self.life-=1
    def draw(self,off):
        img = font.render(str(self.val),True,(255,200,50))
        screen.blit(img,(self.x+off[0],self.y+off[1]))

# =============================
# HELPERS
# =============================
def safe(anim,f):
    return anim[int(f)%len(anim)] if anim else pygame.Surface((1,1),pygame.SRCALPHA)

def load_anim(pattern,size):
    out=[]
    for root,_,files in os.walk(BASE):
        for file in files:
            if re.match(pattern,file):
                out.append(os.path.join(root,file))
    return [pygame.transform.scale(pygame.image.load(p),(size,size)) for p in sorted(out)]

# =============================
# MAGIC
# =============================
fireball=load_anim(r"Fire-bomb\d+\.png",64)
lightning=load_anim(r"Lightning\d+\.png",96)
dark=load_anim(r"Dark-Bolt\d+\.png",64)
spark=load_anim(r"spark\d+\.png",48)

class Projectile:
    def __init__(self,pos,target,frames,damage,speed=10):
        self.x,self.y=pos
        dx,dy=target[0]-pos[0],target[1]-pos[1]
        dist=max(1,math.hypot(dx,dy))
        self.vx,self.vy=dx/dist*speed,dy/dist*speed
        self.frames=frames
        self.frame=0
        self.damage=damage
        self.hit=False
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.frame+=0.4
    def draw(self,off):
        img=safe(self.frames,self.frame)
        screen.blit(img,img.get_rect(center=(self.x+off[0],self.y+off[1])))
    def rect(self):
        return pygame.Rect(self.x-20,self.y-20,40,40)

projectiles=[]

# =============================
# LOAD ANIMS
# =============================
def load_knight(name):
    for root,_,files in os.walk(BASE):
        for f in files:
            if f.endswith(name):
                sheet=pygame.image.load(os.path.join(root,f)).convert_alpha()
                frames=[]
                for i in range(sheet.get_width()//120):
                    fr=pygame.Surface((120,80),pygame.SRCALPHA)
                    fr.blit(sheet,(0,0),(i*120,0,120,80))
                    fr=pygame.transform.scale(fr,(240,160))
                    frames.append(fr)
                return frames
    return []

idle=load_knight("_Idle.png")
run_anim=load_knight("_Run.png")
attack_anim=load_knight("_Attack.png")
roll_anim=load_knight("_Roll.png")

blob=[]
for root,_,files in os.walk(BASE):
    for f in files:
        if f=="blob.png":
            sheet=pygame.image.load(os.path.join(root,f)).convert_alpha()
            fw=sheet.get_width()//5
            fh=sheet.get_height()//3
            for y in range(3):
                for x in range(5):
                    fr=pygame.Surface((fw,fh),pygame.SRCALPHA)
                    fr.blit(sheet,(0,0),(x*fw,y*fh,fw,fh))
                    fr=pygame.transform.scale(fr,(fw*3,fh*3))
                    blob.append(fr)

# =============================
# UI
# =============================
def draw_bar(x,y,w,h,val,maxv,color,off):
    pygame.draw.rect(screen,(40,40,40),(x+off[0],y+off[1],w,h))
    pygame.draw.rect(screen,color,(x+off[0],y+off[1],w*(val/maxv),h))

# =============================
# LOOP
# =============================
while True:

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                game_state="pause" if game_state=="game" else "game"

        if game_state!="game":
            continue

        # MELEE
        if e.type==pygame.MOUSEBUTTONDOWN:
            if e.button==1 and cd["melee"]<=0 and not locked:
                state="attack"; frame=0; locked=True
                cd["melee"]=30
                print("MELEE(5)")
                if player.colliderect(enemy):
                    enemy_hp-=DMG["MELEE"]
                    damage_texts.append(DamageText(enemy.x,enemy.y,5))

        # DASH
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_SPACE and cd["dash"]<=0:
                state="roll"; frame=0
                cd["dash"]=60

        # MAGIC (WITH COOLDOWN)
        if e.type==pygame.KEYDOWN:
            mx,my=pygame.mouse.get_pos()

            def cast(k,frames,dmg,target=None):
                global player_mana
                if cd[k]>0 or player_mana<MANA_COST[k]: return
                tgt=target if target else (mx,my)
                projectiles.append(Projectile(player.center,tgt,frames,dmg))
                cd[k]=cd_max[k]
                player_mana-=MANA_COST[k]
                print(f"{k}({dmg})")

            if e.key==pygame.K_1: cast("1",fireball,DMG["FIREBALL"])
            if e.key==pygame.K_2: cast("2",lightning,DMG["LIGHTNING"])
            if e.key==pygame.K_3: cast("3",dark,DMG["DARK"])
            if e.key==pygame.K_4: cast("4",spark,DMG["SPARK"])
            if e.key==pygame.K_5: cast("5",fireball,DMG["RAIN"])
            if e.key==pygame.K_6: cast("6",lightning,DMG["NOVA"],enemy.center)

    # UPDATE
    if game_state=="game":

        player_mana=min(MAX_MANA,player_mana+MANA_REGEN)

        keys=pygame.key.get_pressed()

        if not locked and state!="roll":
            if keys[pygame.K_a]: player.x-=PLAYER_SPEED; facing_left=True
            if keys[pygame.K_d]: player.x+=PLAYER_SPEED; facing_left=False
            if keys[pygame.K_w]: player.y-=PLAYER_SPEED
            if keys[pygame.K_s]: player.y+=PLAYER_SPEED

        if state=="attack":
            frame+=0.4
            if frame>=len(attack_anim):
                state="idle"; frame=0; locked=False

        elif state=="roll":
            frame+=0.5
            player.x += -ROLL_SPEED if facing_left else ROLL_SPEED
            if frame>=len(roll_anim):
                state="idle"; frame=0

        else:
            frame+=0.25

        # ENEMY AI
        if enemy_alive:
            dx=player.centerx-enemy.centerx
            dy=player.centery-enemy.centery
            dist=max(1,math.hypot(dx,dy))

            if dist>ATTACK_RANGE:
                enemy.x+=int(dx/dist*2)
                enemy.y+=int(dy/dist*2)

            if dist<=ATTACK_RANGE and enemy_cd<=0:
                player_hp-=DMG["ENEMY"]
                shake=5
                enemy_cd=90

        enemy_cd=max(0,enemy_cd-1)

        # PROJECTILES
        for p in projectiles:
            p.update()
            if not p.hit and p.rect().colliderect(enemy):
                enemy_hp-=p.damage
                damage_texts.append(DamageText(enemy.x,enemy.y,p.damage))
                p.hit=True

        projectiles=[p for p in projectiles if not p.hit]

        # DEATH
        if enemy_hp<=0: enemy_alive=False

        for k in cd: cd[k]=max(0,cd[k]-1)

        for dt in damage_texts: dt.update()
        damage_texts=[dt for dt in damage_texts if dt.life>0]

        shake=max(0,shake-0.3)

    # DRAW
    offset=(int(random.uniform(-shake,shake)),int(random.uniform(-shake,shake)))
    screen.fill((20,20,20))

    img=safe(run_anim,frame)
    if state=="attack": img=safe(attack_anim,frame)
    if state=="roll": img=safe(roll_anim,frame)
    if facing_left: img=pygame.transform.flip(img,True,False)
    screen.blit(img,(player.x+offset[0],player.y+offset[1]))

    if enemy_alive:
        screen.blit(blob[int(frame)%len(blob)],(enemy.x+offset[0],enemy.y+offset[1]))
        draw_bar(enemy.x,enemy.y-10,80,5,enemy_hp,100,(255,50,50),offset)

    for p in projectiles: p.draw(offset)
    for dt in damage_texts: dt.draw(offset)

    draw_bar(player.x,player.y-12,90,6,player_hp,100,(255,60,60),offset)
    draw_bar(player.x,player.y-5,90,5,player_mana,MAX_MANA,(50,150,255),offset)

    pygame.display.update()
    clock.tick(60)
