"""This example lets you dynamically create static walls and dynamic balls
"""
__docformat__ = "reStructuredText"

import pygame
from pygame.locals import *
from pygame.color import *
from pygame.display import *
from pygame.locals import *

import pymunk
from pymunk import Vec2d

import random

number_of_colors = 12

color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]


X,Y = 0,1
### Physics collision types
COLLTYPE_DEFAULT = 0
COLLTYPE_MOUSE = 1
COLLTYPE_BALL = 2
COLLTYPE_WALL = 3


def flipy(y):
    """Small hack to convert chipmunk physics to pygame coordinates"""
    return -y+600
def limit_velocity(body, gravity, damping, dt):
    max_velocity = 100
    pymunk.Body.update_velocity(body, gravity, damping, dt)
    l = body.velocity.length
    if l > max_velocity:
        scale = max_velocity / l
        body.velocity = body.velocity * scale

def mouse_coll_func(arbiter, space, data):
    """
    To do
    """
    # 마우스를 원에 올리면 동작하는 함수
    #s1,s2 = arbiter.shapes
    #s2.unsafe_set_radius(s2.radius + 0.15)
    return False
def collision_detection(arbiter, space, data):
    """
    To do
    """
    # 원 하고 원하고 충돌했을때 동작하는 함수
    # s1, s2가 그 원
    s1,s2 = arbiter.shapes
    if(s1.radius >= s2.radius):
        if(s2.radius > 0.2):
            s2.unsafe_set_radius(s2.radius - 0.1)
    else:
        if(s1.radius > 0.2):
            s1.unsafe_set_radius(s1.radius - 0.1)
    return True
def collision_detection_wall(arbiter, space, data):
    """
    To do
    """
    # 벽 하고 원하고 충돌했을때 동작하는 함수
    # s2가 그 원
    s1,s2 = arbiter.shapes
    if(s2.radius > 0.2):
        s2.unsafe_set_radius(s2.radius - 0.1)
    return True
def final_state():
    """
    To do
    """
    # 최종 단계에 대한 정의 - 최종 단계를 들어갔으면
    # return True

    return False
def main():

    pygame.init()

    screen = pygame.display.set_mode((600, 600),pygame.DOUBLEBUF )
    clock = pygame.time.Clock()
    running = True


    ### Physics stuff
    space = pymunk.Space()
    space.gravity = 0.0, 0.0

    ## initiating circles
    circles = []
    ## Balls
    balls = []

    ### Mouse
    mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    mouse_shape = pymunk.Circle(mouse_body, 3, (0,0))
    mouse_shape.collision_type = COLLTYPE_MOUSE
    space.add(mouse_shape)

    space.add_collision_handler(COLLTYPE_MOUSE, COLLTYPE_BALL).pre_solve=mouse_coll_func

    ### Static line
    line_point1 = None
    static_lines = []
    run_physics = True
    expanding = True
    x0 = 0
    y0 = 0
    x1 = 600
    y1 = 600
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    ## 벽 정
    for i in range(4):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment = pymunk.Segment(body, pts[i], pts[(i+1)%4], 20)
        segment.collision_type = COLLTYPE_WALL
        segment.elasticity = 0.999
        segment.friction = 1
        space.add(segment)
    space.add_collision_handler(COLLTYPE_WALL, COLLTYPE_BALL).pre_solve=collision_detection_wall
    while running:
        running = not final_state()
        expanding = not final_state()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                expanding = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
                expanding = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "balls_and_lines.png")
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                p = event.pos[X], flipy(event.pos[Y])
                body = pymunk.Body(100, 100)
                # 원의 초기 속도 정의
                # 모양 정의 (실제 생성되는 오브젝트)
                body.velocity_func = limit_velocity
                body.velocity = (random.uniform(-50,50),random.uniform(-50,50))
                body.position = p
                shape = pymunk.Circle(body, 10, (10,10))
                shape.elasticity = 0.999
                shape.friction = 1
                shape.collision_type = COLLTYPE_BALL
                space.add_collision_handler(COLLTYPE_BALL, COLLTYPE_BALL).pre_solve=collision_detection
                space.add(body, shape)
                circles.append(shape)

            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                if line_point1 is None:
                    line_point1 = Vec2d(event.pos[X], flipy(event.pos[Y]))
            elif event.type == MOUSEBUTTONUP and event.button == 3:
                if line_point1 is not None:

                    line_point2 = Vec2d(event.pos[X], flipy(event.pos[Y]))
                    body = pymunk.Body(body_type=pymunk.Body.STATIC)
                    shape= pymunk.Segment(body, line_point1, line_point2, 0.0)
                    shape.friction = 0.99
                    space.add(shape)
                    static_lines.append(shape)
                    line_point1 = None

            elif event.type == KEYDOWN and event.key == K_SPACE:
                run_physics = not run_physics
                expanding = not expanding

        p = pygame.mouse.get_pos()
        mouse_pos = Vec2d(p[X],flipy(p[Y]))
        mouse_body.position = mouse_pos


        if pygame.key.get_mods() & KMOD_SHIFT and pygame.mouse.get_pressed()[0]:
            body = pymunk.Body(10, 10)
            body.velocity = (100,100)
            body.position = mouse_pos
            shape = pymunk.Circle(body, 10, (1,1))
            shape.collision_type = COLLTYPE_BALL
            space.add(body, shape)
            circle.append(shape)

        ### Update physics
        if run_physics:
            dt = 1.0/60.0
            for x in range(1):
                space.step(dt)

        ### Draw stuff
        screen.fill(THECOLORS["white"])

        # Display some text
        font = pygame.font.Font(None, 16)
        text = """LMB: Create ball
Space: Pause physics simulation"""
        y = 5
        for line in text.splitlines():
            text = font.render(line, 1,THECOLORS["black"])
            screen.blit(text, (5,y))
            y += 10

        for i, circle in enumerate(circles):
            r = circle.radius
            v = circle.body.position
            # 원이 프레임당 얼마나 커지나
            # 0.05가 변수
            """
            To do
            """
            if(expanding):
                circle.unsafe_set_radius(r+0.05)
            rot = circle.body.rotation_vector
            p = int(v.x), int(flipy(v.y))
            p2 = Vec2d(rot.x, -rot.y) * r * 0.9

            pygame.draw.circle(screen, Color(color[i % 12]), p, int(r), 0)
            pygame.draw.line(screen, THECOLORS["black"], p, p+p2)

        if line_point1 is not None:
            p1 = line_point1.x, flipy(line_point1.y)
            p2 = mouse_pos.x, flipy(mouse_pos.y)
            pygame.draw.lines(screen, THECOLORS["black"], False, [p1,p2])

        for line in static_lines:
            body = line.body

            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            p1 = pv1.x, flipy(pv1.y)
            p2 = pv2.x, flipy(pv2.y)
            pygame.draw.lines(screen, THECOLORS["lightgray"], False, [p1,p2])

        ### Flip screen
        pygame.display.flip()
        clock.tick(1000)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))

if __name__ == '__main__':
    doprof = 0

    if not doprof:
        main()
    else:
        import cProfile, pstats

        prof = cProfile.run("main()", "profile.prof")
        stats = pstats.Stats("profile.prof")
        stats.strip_dirs()
        stats.sort_stats('cumulative', 'time', 'calls')
        stats.print_stats(30)
