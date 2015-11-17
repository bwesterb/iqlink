""" Finds all possible sollutions of the IQlink game.


        Bas Westerbaan
        <bas@westerbaan.name>  """

import json

from common import *

class Frame():
    def __init__(self, score,
                       pieces_todo,
                       board,
                       cells_touched,
                       pieces_score,
                       moves):
        self.score = score
        self.pieces_todo = pieces_todo
        self.board = board
        self.cells_touched = cells_touched
        self.pieces_score = pieces_score
        self.moves = moves
    def __cmp__(self, other):
        return cmp(self.score, other.score)
    def __repr__(self):
        return "<Frame score=%s #cells_touched=%s pieces_score=%s>" % (
                            self.score, len(self.cells_touched),
                            self.pieces_score)

def main():
    initial_board = {cell: SLOTS for cell in BOARD}
    initial_frame = Frame(score=0.0,
                          pieces_todo=tuple(PIECES),
                          board=initial_board,
                          cells_touched=frozenset(),
                          pieces_score=0.0,
                          moves=())
    stack = [initial_frame]
    # Calculate for each piece, its orbit
    orbits = {}
    for piece_name, piece in PIECES.iteritems():
        orbit = set()
        seen = set()
        for iso_name, iso in ISOMETRIES:
            transformed_piece = transform_piece(piece, iso)
            if transformed_piece in seen:
                continue
            seen.add(transformed_piece)
            orbit.add((iso_name, transformed_piece))
        orbits[piece_name] = orbit
    # Calculate for each piece, its score
    scores = {}
    for piece_name, piece in PIECES.iteritems():
        score = 0.0
        for b_dir, b_sl in piece:
            if b_sl == CLOSED_HOLE:
                score += 1.0
            else:
                score += .5
        scores[piece_name] = score
    N = 0
    N_found = 0
    while stack:
        N += 1
        f = stack.pop()
        if N % 1000 == 0:
            print N, N_found, len(f.pieces_todo), f.score, len(stack)
            lut = {}
            for f2 in stack:
                if not len(f2.moves) in lut:
                    lut[len(f2.moves)] = 0
                lut[len(f2.moves)] += 1
            import pprint
            pprint.pprint(lut)
        if not f.pieces_todo:
            N_found += 1
            print 'found one!'
            with open('results.jsons', 'a') as g:
                json.dump(f.moves, g)
                g.write('\n')
                g.flush()
            continue
        piece_name = f.pieces_todo[0]
        new_frames = []
        for iso_name, piece in orbits[piece_name]:
            for cell in BOARD:
                ok = True
                new_board = dict(f.board)
                new_cells_touched = f.cells_touched
                new_pieces_score = f.pieces_score + scores[piece_name]
                for d_bit, sl_bit in piece:
                    c_bit = move(cell, d_bit)
                    if c_bit not in BOARD:
                        ok = False
                        break
                    new_cells_touched |= frozenset([c_bit])
                    if new_board[c_bit] & sl_bit != sl_bit:
                        ok = False
                        break
                    new_board[c_bit] -= sl_bit
                if not ok:
                    continue
                new_moves = f.moves + ((piece_name, iso_name, cell),)
                new_score = new_pieces_score - len(new_cells_touched)
                if (sum([scores[p] for p in f.pieces_todo[1:]])
                       > len(BOARD) - len(new_cells_touched)):
                    continue
                new_frame = Frame(
                             score=new_score,
                             pieces_todo=f.pieces_todo[1:],
                             board=new_board,
                             moves=new_moves,
                             cells_touched=new_cells_touched,
                             pieces_score=new_pieces_score)
                new_frames.append(new_frame)
        new_frames.sort(key=lambda x: x.score)
        stack.extend(new_frames)

if __name__ == '__main__':
    main()
