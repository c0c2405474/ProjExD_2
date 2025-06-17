import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA={ #移動量辞書
    pg.K_UP:(0,-5),
    pg.K_DOWN:(0,+5),
    pg.K_LEFT:(-5,0),
    pg.K_RIGHT:(+5,0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool,bool]:
    """
    引数：こうかとんRectまたはばくだんRect 
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True  # 初期値:画面の中
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate  # 横方向、縦方向の画面内判定を返す  


def gameover(screen: pg.Surface) -> None:
    cryk_img =pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)  # 泣いてるこうかとん
    cryk_rct = cryk_img.get_rect()
    cryk_rct.center = 757, 261
    cryk_img2 =pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)  # 泣いてるこうかとん2匹目
    cryk_rct2 = cryk_img2.get_rect()
    cryk_rct2.center = 357, 261
    gameover_img = pg.Surface((1100, 650))  # 空のsurfaceをつくる
    pg.draw.rect(gameover_img, (0,0,0), (1100,650,1100,650))  # 暗い画面をつくる
    gameover_img.set_alpha((128))  
    gameover_rct=gameover_img.get_rect()  # 暗い画面のRectを取得
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("GAMEOVER",True, (255, 255, 255))
    screen.blit(gameover_img, gameover_rct)
    screen.blit(cryk_img, cryk_rct)
    screen.blit(cryk_img2, cryk_rct2)
    screen.blit(txt, [400, 250])
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    関数内で加速度の段階と画像の拡大のリストの作成
    戻り値→二つのリストをタプルにしたもの
    """
    bb_lst = []
    sbb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0,0,0))
        bb_lst.append(bb_img)
    return sbb_accs, bb_lst


def load_kk_images() -> dict[tuple[int, int], pg.Surface]:  # こうかとんの画像を読み込む
    img_base = pg.image.load("fig/3.png")  # こうかとんの画像を読み込む
    img_base = pg.transform.rotozoom(img_base, 0, 0.9)  # 画像のサイズを縮小する
    himg_base =pg.transform.flip(img_base,True,False)
    himg_base2 =pg.transform.flip(img_base,False,True)
    himg_base3=pg.transform.flip(img_base,True,True)
    kk_imgs = {
        (0, 0): img_base,  # 静止画像
        (0, -5): pg.transform.rotozoom(himg_base2, -90, 0.9),  # 上方向
        (0, 5): pg.transform.rotozoom(himg_base2, 90, 0.9),  # 下方向
        (-5, 0): pg.transform.rotozoom(himg_base3, 180, 0.9),  # 左方向
        (5, 0): pg.transform.rotozoom(himg_base2, -180, 0.9),  # 右方向
        (-5, -5): pg.transform.rotozoom(img_base, -45, 0.9),  # 左上方向
        (-5, 5): pg.transform.rotozoom(img_base, 45, 0.9),  # 左下方向
        (5, -5): pg.transform.rotozoom(himg_base, 45, 0.9),  # 右上方向
        (5, 5): pg.transform.rotozoom(himg_base, -45, 0.9),  # 右下方向
    }
    return kk_imgs

  # 移動量から画像を取得
def get_kk_img(sum_mv: tuple[int, int], kk_imgs: dict[tuple[int, int], pg.Surface]) -> pg.Surface:
    """
    移動量の合計値タプルに対応する向きの画像Surfaceを返す
    """
    return kk_imgs.get(tuple(sum_mv), kk_imgs[(0, 0)])

def calc_orientation(org: pg.Rect, dst: pg.Rect,current_xy: tuple[float, float]) -> tuple[float, float]:
    # current_xy=[]
    x=dst.centerx-org.centerx
    y=dst.centery-org.centery
    n=(x**2+y**2)**(1/2)
    if n<300:
        return current_xy
    return x/n*(50**(1/2)),y/n*(50**(1/2))


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_imgs = load_kk_images()  # ★ 画像読み込み
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20))  # 空のsurfaceをつくる
    pg.draw.circle(bb_img,(255,0,0),(10,10),10)  # 赤い円を描く
    bb_img.set_colorkey((0,0,0))
    bb_rct=bb_img.get_rect()  # 爆弾Rectを取得
    bb_rct.centerx = random.randint(0,WIDTH)  # 横座標の乱数
    bb_rct.centery = random.randint(0,HEIGHT)  # 縦座標の乱数
    vx,vy=+5,+5  # 爆弾の移動速度
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):  # こうかとんRectと爆弾Rectの衝突判定 
            gameover(screen)
            # display.update()
            return
        bb_accs, bb_imgs = init_bb_imgs()
        bb_img = bb_imgs[min(tmr//500, 9)]   
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0]+=mv[0]
                sum_mv[1]+=mv[1]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True,True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])  # 移動をなかったことにする      
        kk_img = get_kk_img(tuple(sum_mv), kk_imgs) 
        screen.blit(kk_img, kk_rct)
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx = vx*bb_accs[min(tmr//500, 9)]
        avy= vy*bb_accs[min(tmr//500, 9)]
        bb_rct.width=bb_img.get_rect().width
        bb_rct.height=bb_img.get_rect().height
        bb_rct.move_ip(avx,avy)  # 爆弾の移動
        yoko,tate= check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出ていたら
            vx*=-1 
        if not tate:  # 縦方向にはみ出ていたら
            vy*=-1    
        screen.blit(bb_img, bb_rct)
        
        # bb_img = bb_imgs[min(tmr//500, 9)]
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()