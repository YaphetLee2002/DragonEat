import random
import sys
import time
import math
import pygame
from pygame.locals import *

FPS = 60  # 游戏帧数
WINWIDTH = 1000  # 宽度
WINHEIGHT = 800  # 高度
HALF_WINWIDTH = int(WINWIDTH / 2)   # 屏幕半宽度
HALF_WINHEIGHT = int(WINHEIGHT / 2)  # 屏幕半高度

GRASSCOLOR = (252, 232, 236)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90  # 镜头追踪，就是镜头最大的偏移量
MOVERATE = 9  # 速度
BOUNCERATE = 6  # 弹跳速率
BOUNCEHEIGHT = 30  # 跳跃高度
STARTSIZE = 25  # 初始尺寸
WINSIZE = 300  # 获胜尺寸
INVULNTIME = 2  # 无敌时间
GAMEOVERTIME = 3  # 重生时间
MAXHEALTH = 10  # 生命值

NUMGRASS = 80  # 有多草
NUMdragonS = 30  # 有多少龙
dragonMINSPEED = 3  # 最慢速度

dragonMAXSPEED = 7  # 最快速度
DIRCHANGEFREQ = 2  # 每帧方向变化百分比
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_DRAGON_IMG, R_DRAGON_IMG, L_DRAGONSELF_IMG, R_DRAGONSELF_IMG, GRASSIMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('dragon Eat dragon')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # 加载图片文件
    L_DRAGON_IMG = pygame.image.load('dragon.png')
    R_DRAGON_IMG = pygame.transform.flip(L_DRAGON_IMG, True, False)
    L_DRAGONSELF_IMG = pygame.image.load('dragon-self.png')
    R_DRAGONSELF_IMG = pygame.transform.flip(L_DRAGONSELF_IMG, True, False)
    GRASSIMAGES = []

    # 播放背景音乐
    file = r'T-Pain _ Ne-Yo - Turn All the Lights On (Explicit).mp3'
    pygame.mixer.init()
    track = pygame.mixer.music.load(file)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1, 0)

    for i in range(1, 5):  # 生草
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))

    while True:  # 重开
        runGame()


def runGame():

    # 设置游戏开始时的各个变量
    invulnerableMode = False
    invulnerableStartTime = 0
    gameOverMode = False
    gameOverStartTime = 0
    winMode = False

    eat_sound = pygame.mixer.Sound("eat.wav")
    eat_sound.set_volume(1.0)

    # 设置游戏界面文本
    gameOverSurf = BASICFONT.render(
        'What a scary BIT evil dragon!', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You are the BIT evil dragon!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press R to restart)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # 镜头位置
    camerax = 0
    cameray = 0

    grassObjs = []    # 存放地上的草
    dragonObjs = []  # 存放NPC

    # 存放玩家
    playerObj = {'surface': pygame.transform.scale(L_DRAGONSELF_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce': 0,
                 'health': MAXHEALTH}

    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False

    # 初始状态生草
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True:  # 游戏开始
        # 检查无敌时间是否到期
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # 移动NPC
        for sObj in dragonObjs:
            # 实现NPC的移动和跳跃
            sObj['x'] += sObj['movex']  # 横向移动
            sObj['y'] += sObj['movey']  # 纵向移动
            sObj['bounce'] += 1  # 跳跃
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0  # reset bounce amount

            # 随机改变方向
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()  # 随机的速度，大于0朝右，小于0朝左
                sObj['movey'] = getRandomVelocity()  # 随机的速度，大于0朝上，小于0朝下
                if sObj['movex'] > 0:  # 朝右走
                    sObj['surface'] = pygame.transform.scale(
                        R_DRAGON_IMG, (sObj['width'], sObj['height']))  # 使用朝右的贴图并缩放
                else:  # 朝左走，总之不会停
                    sObj['surface'] = pygame.transform.scale(
                        L_DRAGON_IMG, (sObj['width'], sObj['height']))  # 使用朝左的贴图并缩放

        # 界面以外的都去掉
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(dragonObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, dragonObjs[i]):
                del dragonObjs[i]

        # 移走镜头以后继续添加新的NPC和地上的草
        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray)) 
        while len(dragonObjs) < NUMdragonS:
            # 生成新NPC
            sq = {}
            if playerObj['size'] < 150:
                generalSize = random.randint(playerObj['size'] // 4, playerObj['size'])
                multiplier = random.randint(1, 2)
            else:
                generalSize = random.randint(25, 50)
                multiplier = random.randint(3, 5)
            sq['width'] = (generalSize + random.randint(0, 10)) * multiplier
            sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
            sq['x'], sq['y'] = getRandomOffCameraPos(
                camerax, cameray, sq['width'], sq['height'])
            sq['movex'] = getRandomVelocity()
            sq['movey'] = getRandomVelocity()
            if sq['movex'] < 0:  # 朝左
                sq['surface'] = pygame.transform.scale(
                    L_DRAGON_IMG, (sq['width'], sq['height']))
            else:  # 朝右
                sq['surface'] = pygame.transform.scale(
                    R_DRAGON_IMG, (sq['width'], sq['height']))
            sq['bounce'] = 0
            sq['bouncerate'] = random.randint(10, 18)
            sq['bounceheight'] = random.randint(10, 50)
            dragonObjs.append(sq)

        # 调整镜头位置
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)  # 玩家横向位置
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)  # 玩家纵向位置
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # 绘制背景
        DISPLAYSURF.fill(GRASSCOLOR)

        # 随机生成镜头范围内的草
        for gObj in grassObjs:
            gRect = pygame.Rect((gObj['x'] - camerax,
                                 gObj['y'] - cameray,
                                 gObj['width'],
                                 gObj['height']))
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        # 绘制NPC
        for sObj in dragonObjs:
            sObj['rect'] = pygame.Rect((sObj['x'] - camerax,
                                        sObj['y'] - cameray - getBounceAmount(
                sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                sObj['width'],
                sObj['height']))
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])

        # 绘制玩家的龙
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect((playerObj['x'] - camerax,
                                             playerObj['y'] - cameray - getBounceAmount(
                playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                playerObj['size'],
                playerObj['size']))
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])

        # 绘制血条
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT:  # 使用朝左的贴图
                        playerObj['surface'] = pygame.transform.scale(
                            L_DRAGONSELF_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT:  # 使用朝右的贴图
                        playerObj['surface'] = pygame.transform.scale(
                            R_DRAGONSELF_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif winMode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # 在游戏中移动玩家的龙
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0  # reset bounce amount

            # 碰撞检查
            for i in range(len(dragonObjs)-1, -1, -1):
                sqObj = dragonObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):

                    if sqObj['width'] * sqObj['height'] <= playerObj['size']**2:
                        # 玩家大，吃掉
                        playerObj['size'] += int((sqObj['width']
                                                 * sqObj['height'])**0.18) + 1
                        eat_sound.play()  # 吃掉的音效
                        del dragonObjs[i]  # 清除NPC

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(
                                L_DRAGONSELF_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(
                                R_DRAGONSELF_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:  # 玩家已经足够大了
                            winMode = True  # 触发获胜机制

                    elif not invulnerableMode:
                        # 玩家不够大
                        invulnerableMode = True  # 开启无敌模式
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:  # 玩家血条空了
                            gameOverMode = True  # 触发失败机制
                            gameOverStartTime = time.time()
        else:
            # g游戏已经结束，展示结束界面
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return

        # 检查是否获胜
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# 绘制血条
def drawHealthMeter(currentHealth):
    for i in range(currentHealth):  # 绘制红色血条
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 +
                         (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):  # 绘制血条边框
        pygame.draw.rect(DISPLAYSURF, WHITE,
                         (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)

def terminate():
    pygame.quit()
    sys.exit()

def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # 返回要根据反弹偏移的像素数
    return int(math.sin((math.pi / float(bounceRate)) * currentBounce) * bounceHeight)

# 获得一个随机速度
def getRandomVelocity():
    speed = random.randint(dragonMINSPEED, dragonMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed

def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # 使用随机坐标创建一个 Rect 对象并使用 colliderect()确保右边缘不在相机视图中。
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y

def makeNewGrass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(
        camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))
    return gr

def isOutsideActiveArea(camerax, cameray, obj):
    # 如果camerax和cameray超出窗口边缘超过半个窗口长度，返回False。
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(
        boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)

if __name__ == '__main__':
    main()