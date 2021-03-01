from game_core import *
import math
import random

image_player = image( 'spaceship_own.png' )
image_shot = image( 'bullet_own.png' )
image_laser = image( 'laser.png' )
image_missile = image( 'homing_own.png' )
image_option = image( 'option.png' )
image_barrier = image( 'barrier.png' )
image_enemy00 = image( 'enemy00.png' )
image_enemy01 = image( 'enemy01.png' )
image_enemy02 = image( 'enemy02.png' )
image_enemy03 = image( 'enemy03.png' )
image_enemy04 = image( 'enemy04.png' )
image_shot_e = image( 'bullet_enemy.png' )
image_missile_e = image( 'homing_enemy.png' )
image_crash_own = image( 'crash_own.png' )
image_crash_enemy = image( 'crash_enemy.png' )

sound_shot = sound( 'shot.wav' )
sound_laser = sound( 'laser.wav' )
sound_missile = sound( 'missile.wav' )
sound_treasure = sound( 'treasure.wav' )
sound_crash_own = sound( 'crash_own.wav' )
sound_crash_enemy = sound( 'crash_enemy.wav' )


SW, SH = 1, 9/16
options = []


def shot( s ):
    s.x += s.vx
    s.y += s.vy

    if abs( s.x ) > SW+s.sx or abs( s.y ) > SH+s.sx:
        s.life = 0

def new_shot( x, y, v, dir, n, angle ):
    for i in range( n ):
        if n > 1:
            r = ( dir + angle / (n-1) * (i - (n-1) / 2) )
        else:
            r = dir
        
        rad = r * math.pi * 2

        vx = math.cos( rad ) * v
        vy = math.sin( rad ) * v

        create_object( shot, image_shot, 0.02, x, y, vx, vy, r=r )

def laser( l ):
    l.x += l.vx

    if l.parent:
        l.y = l.parent.y
    
    if abs( l.x ) > SW+l.sx or abs( l.y ) > SH+l.sx:
        l.life = 0


def homing_missile( h ):
    target = None
    target_d = float( 'inf' )

    for e in group( enemy ):
        d = math.dist( (h.x, h.y), (e.x, e.y) )

        if d < target_d:
            target, target_d = e, d
    
    vdir = math.atan2( h.vy, h.vx ) / math.pi / 2

    if target:
        tdir = math.atan2( target.y-h.y, target.x-h.x ) / math.pi / 2
        
        if vdir-tdir > 0.5:
            tdir += 1
        if tdir-vdir > 0.5:
            tdir -= 1
        
        vdir += ( tdir - vdir ) * 0.1
        v = math.dist( (h.vx, h.vy), (0,0) )
        rad = vdir * math.pi * 2
        h.vx = math.cos( rad ) * v
        h.vy = math.sin( rad ) * v
    
    h.x += h.vx
    h.y += h.vy
    h.r = vdir

    if h.time%2 == 0:
        create_object( homing_tail, image_missile, h.sx, h.x, h.y, r=h.r )
    
    h.time += 1

    if abs( h.x ) > SW+h.sx or abs( h.y ) > SH+h.sy:
        h.life = 0

def homing_tail( ht ):
    ht.sy *= 0.95

    if ht.sy < 0.01:
        ht.life = 0


def option( o ):
    o.time += 1

    o.sx = o.sy = 0.06 + math.sin( o.time * 0.2 ) * 0.01

    if o.tx[-1] != o.target.x or o.ty[-1] != o.target.y:
        o.tx.append( o.target.x )
        o.ty.append( o.target.y )
        o.x, o.y = o.tx[0], o.ty[0]
        del o.tx[0], o.ty[0]


def dropped_option( do ):
    do.x += do.vx
    do.y += do.vy


def barrier( b ):
    if b.life == 3:
        b.x = b.parent.x + 0.13
    elif b.life == 2:
        b.x = b.parent.x + 0.12
    else:
        b.x = b.parent.x + 0.11
    
    b.y = b.parent.y

    for e in group( enemy, bullet_enemy, homing_missile_enemy ):
        d = math.dist( (b.x, b.y), (e.x, e.y) )

        if d < b.sx * 1.5:
            e.life = 0
            b.life -= 1
            b.sx *= 0.6
            b.sy *= 0.6


def enemy( e ):
    e.x += e.vx
    e.y += e.vy
    e.r += [ 0.03, 0.03, 0, 0.06, 0 ][ e.state ]

    for w in group( shot, laser, homing_missile ):
        d = math.dist( (w.x, w.y), (e.x, e.y) )
        if d < e.sx * 2:
            e.life -= w.life
            w.life = 0
    
    if e.life <= 0:
        sound_crash_enemy.play()
        new_crash( e.x, e.y, 0.01, 20, 0.95, image_crash_enemy )
        score( 1 )
    
    if abs( e.x ) > SW+e.sx or abs( e.y ) > SH+e.sy:
        e.life = 0
    
    if e.state == 0 and random.random() < 0.02:
        new_aim( e.x, e.y, 0.01 )
    
    if e.state == 1 and random.random() < 0.06:
        new_dir( e.x, e.y, 0.01, random.random() )
    
    if e.state == 2 and random.random() < 0.004:
        for p in group( player ):
            dir = math.atan2( p.y-e.y, p.x-e.x ) / math.pi / 2
            new_nway( e.x, e.y, 0.01, dir, 5, 0.1 )
    
    if e.state == 3 and random.random() < 0.003:
        new_circle( e.x, e.y, 0.01, random.random(), 20 )
    
    if e.state == 4 and random.random() < 0.01:
        create_object( homing_missile_enemy, image_missile_e, 0.05, e.x, e.y, -0.01, 0 )



def bullet_enemy( b ):
    b.x += b.vx
    b.y += b.vy
    b.r += 0.01

    if abs( b.x ) > SW+b.sx or abs( b.y ) > SH+b.sy:
        b.life = 0


def homing_missile_enemy( b ):
    vdir = math.atan2( b.vy, b.vx ) / math.pi / 2

    for p in group( player ):
        pdir = math.atan2( p.y-b.y, p.x-b.x ) / math.pi / 2
        if vdir-pdir > 0.5:
            pdir += 1
        if pdir-vdir > 0.5:
            pdir -= 1
        
        d = math.dist( (b.x, b.y), (p.x, p.y) )
        vdir += (pdir-vdir) * min( 0.05, d*0.1 )
        v = math.dist( (b.vx, b.vy), (0, 0) )
        rad = vdir * math.pi * 2
        b.vx = math.cos( rad ) * v
        b.vy = math.sin( rad ) * v
    
    b.x += b.vx
    b.y += b.vy
    b.r = vdir

    for w in group( shot, laser, homing_missile ):
        d = math.dist( (w.x, w.y), (b.x, b.y) )
        if d < b.sx:
            b.life = 0
    
    if abs( b.x ) > SW+b.sx or abs( b.y ) > SH+b.sy:
        b.life = 0
        

def new_aim( x, y, v ):
    for p in group( player ):
        d = math.dist( (x,y), (p.x, p.y) )
        if d:
            vx = (p.x - x) / d*v
            vy = (p.y - y) / d*v
            create_object( bullet_enemy, image_shot_e, 0.03, x, y, vx, vy )


def new_dir( x, y, v, dir ):
    rad = dir * math.pi * 2
    vx = math.cos( rad ) * v
    vy = math.sin( rad ) * v
    create_object( bullet_enemy, image_shot_e, 0.03, x, y, vx, vy )


def new_nway( x, y, v, dir, n, angle ):
    if n > 1:
        for i in range( n ):
            new_dir( x, y, v, dir+angle/(n-1) * (i-(n-1)/2) )


def new_circle( x, y, v, dir, n ):
    new_nway( x, y, v, dir, n, 1-1/n )


def crash( c ):
    c.x += c.vx
    c.y += c.vy
    c.r += 0.02
    c.sx *= c.vs
    c.sy *= c.vs

    if c.sx < 0.01:
        c.life = 0

def new_crash( x, y, v, n, vs, img ):
    for i in range( n ):
        rad = i / n * math.pi * 2
        vx = math.cos( rad ) * v
        vy = math.sin( rad ) * v
        create_object( crash, img, 0.04, x, y, vx, vy, vs=vs )


def player( p ):
    global options
    
    v = 0.02

    if key( LEFT ):
        p.x -= v
    if key( RIGHT ):
        p.x += v
    if key( UP ):
        p.y += v
    if key( DOWN ):
        p.y -= v
    
    p.x = max( -SW+p.sx, min( SW-p.sx, p.x ) )
    p.y = max( -SH, min( SH, p.y ) )

    for e in group( enemy, bullet_enemy, homing_missile_enemy, dropped_option ):
        d = math.dist( (p.x, p.y), (e.x, e.y) )
        if d < e.sx:
            if hasattr( e, 'isOption' ) and e.isOption and len( options ) < 3:
                sound_treasure.play()
                e.life = 0
                options.append( create_object( option, image_option, 0.06, -0.9, 0 ) )
                parent = p

                for o in options:
                    o.target = parent
                    o.tx = [ parent.x ] * 10
                    o.ty = [ parent.y ] * 10
                    parent = o

            elif not hasattr( e, 'isOption' ):
                sound_crash_own.play()
                new_crash( p.x, p.y, 0.01, 20, 0.98, image_crash_own )
                p.life = 0
                options = []

                for ob in group( option, barrier ):
                    ob.life = 0
                
                for l in group( laser ):
                    l.parent = None

    p.time -= 1

    if key( Z ) and p.time <= 0:
        sound_shot.play()
        for o in group( player, option ):
            new_shot( o.x, o.y, 0.05, 0, 3, 0.04 )
        
        p.time = 5
    
    elif key( X ):
        sound_laser.play()
        for o in group( player, option ):
            create_object( laser, image_laser, 0.05, o.x, o.y, 0.07, parent=o )
    
    elif key( C ) and p.time <= 0:
        sound_missile.play()
        for o in group( player, option ):
            create_object( homing_missile, image_missile, 0.08, o.x, o.y, 0.03, life=10 )
            p.time = 30
    

def stage( s ):

    if random.random() < 0.01 + 0.0005 * score():
        size = 0.08
        x = SW+size
        y = random.uniform( -SH+size, SH-size )
        enemy_type = random.randrange( 5 )
    
        if enemy_type == 0:
            enemy_life = 30
            enemy_image = image_enemy00
        elif enemy_type == 1:
            enemy_life = 40
            enemy_image = image_enemy01
        elif enemy_type == 2:
            enemy_life = 50
            enemy_image = image_enemy02
        elif enemy_type == 3:
            enemy_life = 60
            enemy_image = image_enemy03
        elif enemy_type == 4:
            enemy_life = 70
            enemy_image = image_enemy04
        
        create_object( enemy, enemy_image, size, x, y, -0.005, life=enemy_life, state=enemy_type )


    if random.random() < 0.001 and len( options ) < 3:
        size = 0.06
        create_object( dropped_option, image_option, size, SW+size, random.uniform( -SH+size, SH-size ), -0.005, isOption=True )

    

def start():
    global options
    options = []

    score()

    p = create_object( player, image_player, 0.15, -0.9, 0 )

    create_object( barrier, image_barrier, 0.10, -0.8, 0, parent=p, life=3 )

    create_object( stage )




run( start, 1280, 720, (0.1, 0.1, 0.2), False, (1, 1, 1) )
