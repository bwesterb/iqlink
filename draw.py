import cairo
import json
import math

from common import *

DIR_TO_ANGLE = {
        R: 0,
        DR: math.pi/3.0,
        DL: 2*math.pi/3.0,
        L: 3*math.pi/3.0,
        UL: 4*math.pi/3.0,
        UR: 5*math.pi/3.0 }

# height of equilateral triangle
YFAC = math.sqrt(3)*.5

PIECE_TO_RGB = {
            'red-vee': (1,0,0),
            'purple-vee': (.5,0,.5),
            'purple-line': (.5,0,.5),
            'pink-vee': (1,.5,.8),
            'yellow-vee': (1,1,0),
            'blue-vee': (0,.5,.6),
            'blue-triangle': (0,0,.8),
            'lime-line': (.5,1,0),
            'green-line': (0,.9,.8),
            'green-triangle': (0,.6,0),
            'orange-triangle': (1,.5,0),
            'red-triangle': (1,0,0),
        }

# transforms a coordinate on the board (see common.py) to a coordinate
# on the picture.
def coord(x, y):
    if y <= 1:
        x -= 1
    if y % 2 == 1:
        x += .5
    x += .5
    y += .5
    return (x, y*YFAC)

def create_svg(filename, moves):
    WIDTH = 650
    HEIGHT = int(400*YFAC)
    with open(filename, 'w') as g:
        surface = cairo.SVGSurface(g, WIDTH+10, HEIGHT+10)
        ctx = cairo.Context(surface)
        ctx.translate(5,5)
        ctx.scale(WIDTH/6.5, HEIGHT/4.0/YFAC)
        draw(ctx, moves)
        surface.finish()

def draw(ctx, moves):
    ctx.set_line_width(0.05)
    # draw each piece
    for piece_name, iso_name, position in moves:
        # rotate (trasform/flip) piece
        transformed_piece = transform_piece(PIECES[piece_name],
                                    ISOS_BY_NAME[iso_name])
        # find color
        ctx.set_source_rgb(*PIECE_TO_RGB[piece_name])
        # coordinates of center
        ccx, ccy = coord(*position)
        # Draw each bit of each piece.  The drawing is a bit ad-hoc: we use
        # knowledge of the pieces not encoded in PIECES.
        # First record the corner-case the center is a dot
        center_is_dot = False
        for slot, bit in transformed_piece:
            if slot == C and C in bit:
                center_is_dot = True
        for slot, bit in transformed_piece:
            bit_position = move(position, slot)
            cx, cy = coord(*bit_position)
            ctx.set_line_width(0.12)
            if C in bit:
                # must be a dot
                ctx.arc(cx, cy, 0.22, 0, 2*math.pi)
                ctx.fill()
                if slot != C:
                    angle = DIR_TO_ANGLE[slot] + math.pi
                    ox, oy = .4*math.cos(angle), .4*math.sin(angle)
                    ctx.move_to(cx, cy)
                    ctx.line_to(cx+ox, cy+oy)
                    ctx.stroke()
            else:
                # not a dot: draw the arcs
                for dr, angle in DIR_TO_ANGLE.iteritems():
                    if dr not in bit:
                        continue
                    ctx.arc(cx, cy, 0.4, angle-math.pi/6.0,
                                    angle+math.pi/6.0)
                    ctx.stroke()
            # connect to center
            if slot != C:
                angle = DIR_TO_ANGLE[slot] + math.pi
                ox, oy = .4*math.cos(angle), .4*math.sin(angle)
                ctx.move_to(cx+ox, cy+oy)
                ctx.line_to(ccx-ox, ccy-oy)
                ctx.stroke()
            if slot != C and center_is_dot:
                angle = DIR_TO_ANGLE[slot] + math.pi
                ox, oy = .4*math.cos(angle), .4*math.sin(angle)
                ctx.move_to(ccx-ox, ccy-oy)
                ctx.line_to(ccx, ccy)
                ctx.stroke()




def main():
    with open('results.jsons') as f:
        for i, line in enumerate(f):
            moves = json.loads(line[:-1])
            print 'drawing', i
            create_svg('solutions/%s.svg' % i, moves)

if __name__ == '__main__':
    main()
