"""Original Hakiland Display drawings. No source-font outlines or raster tracing.

Geometry is authored in font units, then written to the shared SVG canvas.
Run with .venv/bin/python examples/build_wedge.py [--controls].
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from fontTools.agl import UV2AGL
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

from font_maker.models import KerningPair, VerticalMetrics
from font_maker.preview import compose_preview_svg, shape_font, svg_to_png
from font_maker.service import FontMakerService

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'wedge'
REFERENCE = Path('/var/folders/61/r756smb95_16p68hfyzwypq40000gn/T/codex-clipboard-9b9d5222-0485-40e2-b46a-a99d6d1fe063.png')
G: dict[str, tuple[int, str]] = {}


def poly(*pts):
    return 'M' + ' L'.join(f'{x:g},{y:g}' for x, y in pts) + ' Z '


def rect(x, y, w, h):
    return poly((x,y), (x,y+h), (x+w,y+h), (x+w,y))


def transform(d, sx=1, sy=1, dx=0, dy=0):
    pen = SVGPathPen(None)
    parse_path(d, TransformPen(pen, (sx,0,0,sy,dx,dy)))
    return pen.getCommands() + ' '


def reverse(d):
    pen=SVGPathPen(None)
    parse_path(d,ReverseContourPen(pen))
    return pen.getCommands()+' '


def oval(cx, cy, rx, ry, hole=False):
    k = .55228475
    d = (f'M {cx} {cy+ry} C {cx+rx*k} {cy+ry} {cx+rx} {cy+ry*k} {cx+rx} {cy} '
         f'C {cx+rx} {cy-ry*k} {cx+rx*k} {cy-ry} {cx} {cy-ry} '
         f'C {cx-rx*k} {cy-ry} {cx-rx} {cy-ry*k} {cx-rx} {cy} '
         f'C {cx-rx} {cy+ry*k} {cx-rx*k} {cy+ry} {cx} {cy+ry} Z ')
    return transform(d, sx=-1, dx=2*cx) if hole else d


def diamond(x, y, r=39):
    return poly((x,y+r),(x+r,y),(x,y-r),(x-r,y))


def foot(x, w=116, y=0, s=54, depth=54):
    return poly((x-s,y),(x,y+depth),(x+w,y+depth),(x+w+s,y))


def crown(x, w=116, y=700, s=54, depth=54):
    return poly((x-s,y),(x+w+s,y),(x+w,y-depth),(x,y-depth))


def stem(x=90, w=116, top=700, bottom=0):
    return rect(x,bottom,w,top-bottom)+foot(x,w,bottom)+crown(x,w,top)


def lstem(x=82, w=106, top=470, bottom=0):
    return poly((x-56,top-44),(x+w,top+10),(x+w,bottom+54),(x+w+54,bottom),
                (x-54,bottom),(x,bottom+54),(x,top-100))


def parallel_x(top, left, right, thick, thin, cross, serif):
    """Two exact parallelograms; paired cuts are 45 degrees, with flush joins."""
    yhi,ylo=top-serif,serif
    travel=yhi-ylo
    descend=2/3
    ascend=.8
    a=left; b=right
    c=a+travel*descend; d=b-travel*ascend
    return (poly((a,yhi),(a+thick,yhi),(c+thick,ylo),(c,ylo))+
            poly((b,yhi),(b+thin,yhi),(d+thin,ylo),(d,ylo))+
            crown(a,thick,top,serif,serif)+crown(b,thin,top,serif,serif)+
            foot(c,thick,0,serif,serif)+foot(d,thin,0,serif,serif))


def add(ch, width, *paths):
    G[ch] = (width, ''.join(paths))


def draw():
    # Controls: 700 cap, 470 x-height; 116/106 stems, 20–24 hairlines.
    add('H',730,stem(),stem(524),rect(190,330,350,24))
    add('O',730,oval(365,350,318,362),oval(365,350,182,340,True))
    add('Q',770,G['O'][1],
        'M 334 166 C 391 159 414 104 468 59 L 616 -89 L 738 -49 L 657 -130 L 576 -103 L 416 57 C 380 95 361 127 334 147 Z ')
    add('I',304,stem(94))
    add('A',740,
        poly((28,0),(65,64),(355,724),(657,67),(724,0),(431,0),(503,66),(430,247),(184,247),(106,62),(166,0)),
        poly((194,271),(421,271),(311,548)))
    add('V',738,poly((28,700),(238,700),(200,662),(404,152),(604,652),(556,700),(690,700),(636,646),(372,-14),(346,-14),(82,646)))
    add('W',1020,poly((23,700),(252,700),(191,651),(351,157),(476,550),(445,651),(391,700),(610,700),(555,651),(719,155),(891,651),(838,700),(963,700),(924,647),(689,-14),(661,-14),(491,507),(323,-14),(294,-14),(74,649)))
    add('X',728,parallel_x(700,110,588,105,29,0,50))
    add('Y',706,poly((24,700),(266,700),(205,652),(402,350),(546,652),(496,700),(666,700),(581,652),(421,321),(421,49),(475,0),(251,0),(305,49),(305,307),(82,652)))
    add('N',768,poly((40,700),(213,700),(641,184),(641,652),(587,700),(720,700),(665,652),(665,0),(640,0),(118,623),(118,48),(172,0),(40,0),(94,48),(94,650)))
    add('M',890,stem(94,24),stem(682,116),
        poly((78,700),(213,700),(468,163),(441,4),(415,4)),
        poly((441,4),(416,44),(707,700),(735,700)))
    add('L',633,poly((36,700),(260,700),(206,653),(206,24),(475,24),(611,173),(570,0),(36,0),(90,49),(90,653)))
    add('T',690,stem(287),poly((38,700),(652,700),(667,513),(531,675),(159,675),(23,513)))
    add('E',654,poly((36,700),(596,700),(613,540),(486,676),(206,676),(206,358),(426,358),(475,442),(475,250),(426,334),(206,334),(206,24),(474,24),(621,169),(581,0),(36,0),(90,49),(90,653)))
    add('F',607,poly((36,700),(572,700),(588,531),(464,676),(206,676),(206,361),(411,361),(462,444),(462,252),(411,337),(206,337),(206,49),(260,0),(36,0),(90,49),(90,653)))
    add('P',650,stem(),
        'M 197 700 L 347 700 C 534 700 604 624 604 510 C 604 385 480 330 337 330 L 197 330 L 197 353 L 328 353 C 432 353 468 417 468 515 C 468 611 428 677 329 677 L 197 677 Z ')
    add('R',724,G['P'][1],
        'M 274 348 L 393 348 C 438 348 459 324 483 282 L 611 73 C 633 38 658 14 703 0 L 511 0 L 335 300 C 320 324 306 325 274 325 Z ')
    add('B',670,stem(),
        'M 198 700 L 357 700 C 532 700 594 634 594 538 C 594 450 529 397 417 374 C 572 358 635 287 635 187 C 635 61 520 0 347 0 L 196 0 L 196 23 L 326 23 C 442 23 495 75 495 190 C 495 299 451 362 338 362 L 196 362 L 196 385 L 320 385 C 416 385 461 435 461 535 C 461 627 423 677 328 677 L 198 677 Z ')
    add('D',736,stem(),
        'M 194 700 L 350 700 C 558 700 690 589 690 350 C 690 111 558 0 350 0 L 194 0 L 194 24 L 329 24 C 481 24 551 127 551 350 C 551 573 481 676 329 676 L 194 676 Z ')
    add('C',717,
        'M 647 644 L 562 530 L 502 662 C 464 680 427 690 380 690 C 250 690 183 533 183 350 C 183 133 266 14 392 14 C 489 14 568 62 651 159 L 657 151 C 590 40 511 -12 375 -12 C 171 -12 46 146 46 350 C 46 559 181 712 385 712 C 484 712 570 686 647 644 Z ')
    add('G',754,
        'M 665 679 L 665 490 L 505 666 C 472 680 426 690 383 690 C 249 690 183 535 183 350 C 183 143 257 12 392 12 C 455 12 501 29 532 61 L 532 288 L 431 350 L 727 350 L 650 288 L 650 72 C 563 20 477 -12 370 -12 C 173 -12 46 146 46 350 C 46 565 184 712 385 712 C 506 712 566 679 665 679 Z ')
    add('J',463,crown(247),
        'M 247 669 L 363 669 L 363 133 C 363 29 306 -31 226 -72 L 140 -5 C 208 -6 247 33 247 117 Z ')
    add('K',725,stem(),poly((197,310),(588,649),(541,700),(697,700),(622,648),(435,486),(644,45),(705,0),(471,0),(523,44),(336,400),(197,278)))
    add('S',613,
        'M 526 670 L 526 488 L 411 656 C 380 678 351 690 309 690 C 225 690 174 644 174 580 C 174 514 221 479 327 431 L 393 401 C 505 350 568 290 568 187 C 568 62 475 -12 316 -12 C 215 -12 133 17 66 42 L 66 237 L 174 61 C 213 28 258 11 311 11 C 408 11 459 58 459 130 C 459 199 411 235 312 280 L 241 313 C 129 364 70 428 70 532 C 70 645 168 712 307 712 C 394 712 465 689 526 670 Z ')
    add('U',746,crown(92),crown(617,25),
        'M 92 668 L 208 668 L 208 218 C 208 95 269 27 376 27 C 519 27 617 112 617 250 L 617 669 L 642 669 L 642 238 C 642 77 535 -12 365 -12 C 185 -12 92 65 92 218 Z ')
    add('Z',663,poly((50,700),(621,700),(621,677),(181,24),(456,24),(619,203),(588,0),(34,0),(34,23),(473,676),(204,676),(59,516)))
    # Lowercase bowls and stem/shoulder construction.
    add('o',558,oval(279,235,239,247),oval(279,235,126,225,True))
    add('n',586,lstem(),
        'M 179 359 C 236 444 292 482 364 482 C 445 482 502 439 502 349 L 502 42 L 556 0 L 343 0 L 397 42 L 397 345 C 397 410 370 439 329 439 C 279 439 221 404 179 339 Z ')
    add('h',586,lstem(top=760),G['n'][1][len(lstem()):])
    add('m',858,lstem(),
        'M 179 359 C 236 444 281 482 344 482 C 415 482 453 443 468 387 C 520 449 565 482 634 482 C 717 482 774 439 774 349 L 774 42 L 828 0 L 615 0 L 669 42 L 669 345 C 669 410 642 439 601 439 C 555 439 504 405 477 371 L 477 42 L 531 0 L 318 0 L 372 42 L 372 345 C 372 410 345 439 309 439 C 266 439 217 404 179 339 Z ')
    add('l',274,lstem(top=760))
    add('i',274,lstem(),diamond(135,608,39))
    add('j',286,
        'M 36 435 L 197 480 L 197 -73 C 197 -148 148 -197 78 -230 L 9 -169 C 57 -176 91 -131 91 -76 L 91 394 Z ',diamond(144,608,39))
    add('r',438,lstem(),
        'M 178 340 C 225 420 262 459 318 488 L 404 402 L 326 324 L 259 391 C 235 407 210 368 178 315 Z ')
    add('b',582,lstem(top=760),
        'M 179 411 C 224 457 270 482 330 482 C 457 482 540 383 540 244 C 540 98 442 -12 304 -12 C 247 -12 206 4 163 26 L 177 49 C 210 26 243 12 279 12 C 371 12 427 97 427 239 C 427 372 383 445 302 445 C 254 445 215 425 179 388 Z ')
    add('d',582,lstem(x=392,top=760),reverse(transform(G['b'][1][len(lstem(top=760)):],sx=-1,dx=580)))
    add('p',582,lstem(bottom=-220),G['b'][1][len(lstem(top=760)):])
    add('q',582,lstem(x=392,bottom=-220),reverse(transform(G['b'][1][len(lstem(top=760)):],sx=-1,dx=580)))
    add('a',562,
        'M 408 45 C 351 5 297 -12 239 -12 C 117 -12 43 32 43 118 C 43 230 166 264 398 332 L 398 374 C 398 436 368 459 320 459 C 259 459 228 430 222 402 L 222 343 C 187 318 167 334 114 385 C 170 449 241 482 329 482 C 438 482 504 433 504 351 L 504 49 L 553 49 L 444 -16 Z M 398 310 C 208 252 158 211 158 137 C 158 73 194 43 253 43 C 304 43 356 67 398 107 Z ')
    # Unified bowl/stem contours eliminate swelling from overlapping foot wedges.
    right_bowl = ('C 356 8 310 -12 258 -12 C 124 -12 40 89 40 235 '
                  'C 40 381 136 482 270 482 C 318 482 360 461 392 430 ')
    right_counter = ('M 392 390 C 360 434 325 458 281 458 C 198 458 153 375 153 235 '
                     'C 153 95 198 12 281 12 C 325 12 360 36 392 80 Z ')
    add('d',582,'M 336 716 L 498 770 L 498 54 L 552 0 L 392 0 L 392 48 '+right_bowl+'L 392 660 Z ',right_counter)
    add('q',582,'M 336 426 L 498 480 L 498 -166 L 552 -220 L 338 -220 L 392 -166 L 392 48 '+right_bowl+'L 392 370 Z ',right_counter)
    left_counter=reverse(transform(right_counter,sx=-1,dx=580))
    left_bowl=('C 220 461 262 482 310 482 C 444 482 540 381 540 235 '
               'C 540 89 456 -12 322 -12 C 270 -12 224 8 188 48 ')
    add('b',582,'M 26 716 L 188 770 L 188 430 '+left_bowl+'L 188 0 L 28 0 L 82 54 L 82 660 Z ',left_counter)
    add('p',582,'M 26 426 L 188 480 L 188 430 '+left_bowl+'L 188 -166 L 242 -220 L 28 -220 L 82 -166 L 82 370 Z ',left_counter)
    add('a',562,
        'M 398 69 C 354 18 304 -12 246 -12 C 127 -12 58 40 58 132 C 58 244 185 277 398 344 L 398 378 C 398 434 368 458 320 458 C 270 458 235 432 222 404 L 222 344 L 192 328 L 114 386 C 170 449 241 482 329 482 C 438 482 504 433 504 351 L 504 54 L 553 54 L 446 -16 Z '
        'M 398 319 L 250 263 C 193 238 170 197 170 139 C 170 59 208 14 267 14 C 314 14 359 48 398 105 Z ')
    add('c',506,
        'M 464 422 L 386 323 L 333 442 C 316 454 297 460 274 460 C 189 460 151 362 151 240 C 151 98 210 27 292 27 C 358 27 406 53 466 109 L 473 99 C 421 24 358 -12 268 -12 C 129 -12 38 90 38 235 C 38 381 135 482 278 482 C 354 482 414 460 464 422 Z ')
    add('e',531,
        'M 151 278 L 379 278 C 379 392 342 460 279 460 C 207 460 155 380 151 278 Z M 151 254 C 151 103 209 27 298 27 C 367 27 426 59 483 107 L 490 98 C 429 22 356 -12 270 -12 C 129 -12 38 90 38 235 C 38 382 141 482 282 482 C 407 482 489 404 489 254 Z ')
    add('f',363,
        'M 89 445 L 32 445 L 32 470 L 89 470 L 89 543 C 89 697 167 770 274 770 C 323 770 357 754 382 731 L 326 646 L 274 739 C 266 745 255 748 244 748 C 210 748 195 707 195 624 L 195 470 L 326 470 L 326 445 L 195 445 L 195 42 L 258 0 L 34 0 L 89 42 Z ')
    add('g',558,
        oval(274,319,218,163),oval(274,319,103,143,True),
        poly((338,462),(448,572),(448,462)),
        'M 162 185 L 185 172 C 139 146 136 115 166 100 C 185 90 228 91 291 91 L 351 91 C 477 91 526 36 526 -51 C 526 -161 420 -223 264 -223 C 119 -223 39 -181 39 -114 C 39 -62 77 -26 151 5 L 168 -7 C 125 -39 116 -67 116 -105 C 116 -166 171 -202 265 -202 C 366 -202 418 -160 418 -103 C 418 -44 383 -17 287 -17 L 199 -17 C 95 -17 49 18 65 77 C 76 118 110 154 162 185 Z ')
    add('u',588,
        'M 26 434 L 187 480 L 187 132 C 187 67 213 39 256 39 C 307 39 359 74 402 117 L 402 392 L 347 434 L 508 480 L 508 48 L 559 48 L 402 -10 L 402 92 C 345 22 288 -12 219 -12 C 136 -12 81 32 81 121 L 81 393 Z ')
    add('t',370,
        'M 89 470 L 89 532 L 195 638 L 195 470 L 323 470 L 323 445 L 195 445 L 195 99 C 195 54 215 33 247 33 C 275 33 305 51 332 76 L 342 64 C 299 14 255 -12 201 -12 C 126 -12 89 30 89 108 L 89 445 L 29 445 L 29 470 Z ')
    add('k',562,lstem(top=760),poly((179,216),(401,430),(355,470),(471,470),(437,430),(332,329),(484,35),(527,0),(305,0),(355,35),(249,249),(179,184)))
    add('v',530,poly((33,470),(215,470),(177,432),(299,127),(421,432),(383,470),(488,470),(450,432),(272,-13),(249,-13),(71,432)))
    add('w',766,poly((23,470),(216,470),(164,433),(272,122),(348,346),(315,433),(267,470),(459,470),(410,433),(520,120),(658,433),(610,470),(729,470),(687,433),(501,-13),(477,-13),(365,303),(255,-13),(231,-13),(66,433)))
    add('x',531,parallel_x(470,76,398,106,26,0,38))
    add('y',531,G['v'][1],
        'M 267 48 L 290 27 L 226 -128 C 197 -199 161 -229 121 -229 C 85 -229 53 -209 28 -188 L 92 -112 L 143 -166 C 162 -180 183 -164 201 -122 Z ')
    add('z',492,poly((48,470),(453,470),(453,450),(159,23),(321,23),(453,146),(435,0),(30,0),(30,21),(325,447),(168,447),(48,336)))
    add('s',458,
        'M 384 449 L 384 314 L 299 438 C 276 453 256 460 226 460 C 166 460 131 431 131 389 C 131 349 164 326 237 293 L 277 275 C 367 235 414 193 414 124 C 414 40 338 -12 225 -12 C 153 -12 94 8 46 28 L 46 170 L 127 49 C 158 24 186 10 227 10 C 290 10 325 42 325 84 C 325 124 291 148 224 178 L 174 201 C 88 240 48 281 48 351 C 48 435 121 482 228 482 C 289 482 341 466 384 449 Z ')
    # Proportional lining figures with the same vertical contrast.
    add('0',580,oval(290,350,247,362),oval(290,350,126,340,True))
    add('1',378,poly((46,601),(260,712),(260,48),(326,0),(79,0),(146,48),(146,608)))
    add('2',559,
        'M 52 555 C 73 656 161 712 280 712 C 407 712 503 646 503 542 C 503 432 415 366 306 264 L 135 106 L 371 106 L 505 214 L 464 0 L 44 0 L 44 23 L 240 254 C 335 368 384 447 384 545 C 384 635 350 690 279 690 C 224 690 184 651 184 598 L 211 540 L 135 473 Z ')
    add('3',552,
        'M 61 700 L 503 700 L 503 679 L 284 403 C 434 415 515 326 515 206 C 515 79 414 -12 268 -12 C 167 -12 93 20 39 73 L 99 181 L 173 53 C 197 22 224 10 262 10 C 346 10 389 91 389 200 C 389 314 342 371 251 371 L 204 365 L 196 382 L 376 595 L 158 595 L 56 522 Z ')
    add('4',582,
        poly((346,712),(460,712),(460,238),(542,238),(542,208),(460,208),(460,43),(514,0),(292,0),(346,43),(346,208),(32,208),(32,232)),
        poly((65,238),(346,238),(346,661)))
    add('5',549,
        'M 99 700 L 515 700 L 472 594 L 119 594 L 101 411 C 150 437 205 449 259 449 C 416 449 510 356 510 223 C 510 81 405 -12 262 -12 C 167 -12 93 18 43 63 L 99 178 L 169 55 C 195 25 224 10 260 10 C 339 10 386 81 386 208 C 386 327 332 396 239 396 C 184 396 136 384 74 352 L 60 364 Z ')
    add('6',570,
        'M 490 705 L 494 688 C 311 644 193 520 174 365 C 211 408 264 429 321 429 C 446 429 529 342 529 217 C 529 80 430 -12 287 -12 C 132 -12 42 100 42 280 C 42 482 207 655 490 705 Z M 166 274 C 166 104 204 10 289 10 C 365 10 409 84 409 214 C 409 328 372 395 300 395 C 244 395 194 362 171 315 C 168 302 166 287 166 274 Z ')
    add('7',546,poly((39,700),(511,700),(511,677),(276,0),(136,0),(412,591),(135,591),(36,492)))
    add('8',572,
        'M 288 712 C 415 712 502 649 502 553 C 502 475 450 422 376 383 C 474 328 531 268 531 187 C 531 66 427 -12 283 -12 C 135 -12 43 62 43 169 C 43 257 95 315 181 359 C 98 410 60 466 60 548 C 60 647 156 712 288 712 Z M 307 422 C 373 468 405 507 405 558 C 405 634 358 690 283 690 C 211 690 165 645 165 586 C 165 519 213 477 307 422 Z M 205 337 C 149 292 127 244 127 179 C 127 80 180 10 287 10 C 373 10 423 61 423 124 C 423 205 362 258 205 337 Z ')
    add('9',570,transform(G['6'][1],sx=-1,sy=-1,dx=570,dy=700))
    # Punctuation dots echo the small diamond tittles, at an optical size.
    dot=diamond(100,39,39)
    comma='M 100 78 L 142 38 C 142 -26 112 -79 49 -115 L 39 -103 C 86 -64 99 -31 100 -2 L 61 38 Z '
    add('.',200,dot);add(',',200,comma)
    add(':',218,transform(dot,dx=9),transform(dot,dx=9,dy=322))
    add(';',218,transform(comma,dx=9),transform(dot,dx=9,dy=322))
    add('!',253,poly((65,655),(78,700),(175,700),(188,655),(137,171),(116,171)),diamond(126,39,39))
    add('?',496,
        'M 50 572 C 65 664 146 712 255 712 C 369 712 450 652 450 555 C 450 470 396 432 319 376 C 257 331 247 283 247 174 L 222 174 C 215 316 228 374 279 431 C 321 479 337 512 337 563 C 337 639 302 690 244 690 C 192 690 163 654 163 603 L 193 548 L 126 489 Z ',diamond(235,39,39))
    add('-',338,rect(47,243,244,45))
    add('–',570,rect(42,243,486,39));add('—',1000,rect(44,243,912,39))
    add('_',554,rect(22,-120,510,31));add('…',600,dot,transform(dot,dx=200),transform(dot,dx=400))
    add('•',330,diamond(165,272,75))
    single=poly((57,700),(150,700),(124,489),(83,489))
    add("'",207,single);add('"',378,single,transform(single,dx=171))
    rightquote=transform(comma,dy=622)
    leftquote=transform(rightquote,sx=-1,sy=-1,dx=202,dy=1210)
    add('’',209,rightquote);add('‘',209,leftquote)
    add('”',380,rightquote,transform(rightquote,dx=171));add('“',380,leftquote,transform(leftquote,dx=171))
    add('/',439,poly((35,-64),(66,-64),(410,741),(379,741)))
    add('\\',439,transform(G['/'][1],sx=-1,dx=439))
    add('|',214,rect(91,-155,32,916))
    add('(',353,
        'M 310 761 L 320 746 C 198 623 169 482 169 300 C 169 118 198 -24 320 -145 L 310 -160 C 139 -62 54 80 54 300 C 54 520 139 662 310 761 Z ')
    add(')',353,transform(G['('][1],sx=-1,dx=353))
    add('[',334,poly((81,-150),(81,750),(296,750),(296,725),(173,725),(173,-125),(296,-125),(296,-150)))
    add(']',334,transform(G['['][1],sx=-1,dx=334))
    add('{',395,
        'M 345 752 L 345 729 C 231 729 216 701 216 615 L 216 454 C 216 362 188 325 99 301 C 188 277 216 240 216 148 L 216 -13 C 216 -99 231 -127 345 -127 L 345 -150 C 152 -150 114 -121 114 -11 L 114 150 C 114 244 101 277 40 289 L 40 313 C 101 325 114 358 114 452 L 114 613 C 114 723 152 752 345 752 Z ')
    add('}',395,transform(G['{'][1],sx=-1,dx=395))
    add('+',582,rect(54,290,474,36),rect(273,72,36,473))
    add('=',582,rect(54,385,474,35),rect(54,195,474,35))
    add('<',582,poly((531,551),(531,513),(109,301),(531,89),(531,51),(51,291),(51,311)))
    add('>',582,transform(G['<'][1],sx=-1,dx=582))
    add('^',510,poly((48,463),(231,706),(279,706),(462,463),(434,463),(255,626),(76,463)))
    add('`',300,poly((59,739),(151,739),(248,565),(224,553)))
    add('~',588,
        'M 45 264 C 82 362 127 382 180 382 C 249 382 337 292 407 292 C 450 292 485 313 531 362 L 545 352 C 507 251 461 232 409 232 C 340 232 248 322 180 322 C 137 322 102 301 59 254 Z ')
    add('#',620,poly((198,705),(231,705),(121,-5),(88,-5)),poly((467,705),(500,705),(390,-5),(357,-5)),rect(55,439,515,51),rect(24,218,515,51))
    add('$',613,G['S'][1],rect(290,-99,27,885))
    add('%',766,oval(180,535,130,177),oval(180,535,64,156,True),oval(586,164,130,177),oval(586,164,64,156,True),poly((109,-18),(140,-18),(658,718),(627,718)))
    star=''
    import math
    for angle in range(0,360,72):
        t=math.radians(angle)
        pen=SVGPathPen(None)
        parse_path(poly((-17,22),(-41,159),(41,159),(17,22)),TransformPen(pen,(math.cos(t),math.sin(t),-math.sin(t),math.cos(t),231,522)))
        star+=pen.getCommands()
    add('*',462,star)
    add('&',760,
        'M 365 455 C 466 520 514 557 514 619 C 514 677 459 712 382 712 C 271 712 208 651 208 569 C 208 510 239 461 281 407 C 130 343 54 270 54 166 C 54 54 146 -12 280 -12 C 387 -12 477 33 549 107 L 635 0 L 753 0 L 617 166 C 660 235 687 298 708 359 L 751 398 L 573 398 L 671 348 C 650 291 627 242 599 197 Z M 346 479 C 299 537 275 579 275 621 C 275 663 308 690 352 690 C 395 690 422 663 422 623 C 422 570 397 533 346 479 Z M 298 386 L 531 129 C 474 69 411 35 339 35 C 243 35 178 102 178 199 C 178 281 219 343 298 386 Z ')
    add('@',866,
        'M 753 112 C 663 30 565 -12 441 -12 C 198 -12 40 130 40 348 C 40 565 215 712 462 712 C 680 712 827 587 827 405 C 827 251 734 161 628 161 C 577 161 543 182 533 221 C 496 181 454 160 405 160 C 309 160 250 230 250 340 C 250 474 340 571 448 571 C 490 571 526 553 549 516 L 558 558 L 657 558 L 606 297 C 593 228 598 191 637 191 C 714 191 790 268 790 405 C 790 563 667 685 462 685 C 249 685 134 540 134 348 C 134 153 251 17 443 17 C 558 17 653 58 738 131 Z M 366 332 C 366 246 390 206 434 206 C 490 206 532 284 543 378 C 555 473 516 540 471 540 C 408 540 366 444 366 332 Z ')


def write_sources(chars):
    source = OUT / 'drawings'
    source.mkdir(exist_ok=True)
    spacing_path=OUT/'spacing-refinement.json'
    spacing=json.loads(spacing_path.read_text()) if spacing_path.exists() else {}
    items=[]
    for ch in chars:
        width, path = G[ch]
        refined=OUT/'refined'/f'glyph-U{ord(ch):04X}.svg'
        # Convert authoring coordinates to the canonical y-down SVG canvas.
        path = transform(path, sy=-1, dy=800) if path else ''
        f = source / f'glyph-U{ord(ch):04X}.svg'
        f.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1040" data-fontmaker-baseline-y="800"><g id="glyph" fill="#000">' + (f'<path d="{path}"/>' if path else '') + '</g></svg>')
        item=dict(name=UV2AGL.get(ord(ch), f'uni{ord(ch):04X}'),svg_path=str(refined if refined.exists() else f),codepoints=[f'U+{ord(ch):04X}'],advance_width=spacing.get('advance_overrides',{}).get(ch,width))
        if ch in spacing.get('left_side_bearing_overrides',{}):
            item['left_side_bearing']=spacing['left_side_bearing_overrides'][ch]
        items.append(item)
    return items


def run(controls=False):
    draw()
    add(' ',255,'')
    service=FontMakerService()
    if (OUT/'font.yaml').exists():
        info=service.open_project(str(OUT))
    else:
        info=service.create_project(str(OUT),'Hakiland Display',metrics=VerticalMetrics(ascender=800,cap_height=700,x_height=470,descender=-240,line_gap=70),reference_image=str(REFERENCE),version='0.100')
    pid,rev=info['project_id'],info['revision']
    chars=list('HOnoAVQiljaprg ') if controls else sorted(G,key=ord)
    imported=service.upsert_glyphs(pid,rev,write_sources(chars))
    if not controls:
        pairs={}
        def kern(left,right,value):
            for l in left:
                for r in right:
                    pairs[l+r]=value
        kern('A','VWY',-60);kern('A','T',-48);kern('A','COQ',-20)
        kern('VW','A',-55);kern('Y','A',-72);kern('T','A',-55)
        kern('L','TVWY',-65);kern('F','A',-44);kern('P','A',-42)
        kern('T','acegos',-55);kern('T','ru',-35);kern('T','y',-25)
        kern('V','acegos',-42);kern('W','acegos',-30);kern('Y','acegos',-65)
        kern('Y','ru',-40);kern('F','aceo',-25)
        kern('r','aceo',-18);kern('r','.,',-25)
        kern('vwy','.,',-35);kern('k','eo',-12)
        kern('TVWY','.,',-60);kern('A','vwy',-25)
        kern('“‘','A',-35);kern('PFT','.,',-50)
        spacing_path=OUT/'spacing-refinement.json'
        if spacing_path.exists():
            pairs.update(json.loads(spacing_path.read_text()).get('kerning_overrides',{}))
        rules=[KerningPair(left=UV2AGL.get(ord(k[0]),f'uni{ord(k[0]):04X}'),right=UV2AGL.get(ord(k[1]),f'uni{ord(k[1]):04X}'),value=v) for k,v in pairs.items()]
        old=service._store_project(pid)[1].kerning.pairs
        service.set_kerning(pid,imported.revision,remove_pairs=[(pair.left,pair.right) for pair in old],upsert_pairs=rules)
    built=service.build(pid,['ttf','otf','woff2'])
    (OUT/'build-report.json').write_text(json.dumps(built,indent=2))
    print(json.dumps({'revision':built['revision'],'glyphs':len(chars),'diagnostics':built['diagnostics'],'artifacts':built['artifacts']},indent=2))
    font=OUT/built['artifacts'][0]['path']
    project=service._store_project(pid)[1]
    proofs=OUT/'proofs';proofs.mkdir(exist_ok=True)
    texts={'controls':'HHOH no noon AV Qilj aarg'} if controls else {
        'headline':'Angular grace', 'caps-one':'ABCDEFGHIJKLM', 'caps-two':'NOPQRSTUVWXYZ',
        'lower-one':'abcdefghijklm', 'lower-two':'nopqrstuvwxyz',
        'detail':'AaRrGg QO', 'words':'Quiet geometry. Sharp by nature.',
        'rhythm':'minimum noon parallel rare', 'pairs':'AV AW AY To Ta Ty Va Vo Ya Yo',
        'figures':'0123456789 & ?!',
        'punctuation':'12:30; a,b. “Quiet!” (g) $25.00',
        'symbols':'@ # % & * + = / \\ < > [ ] { }',
        'refinements':'Qg QO QUEUE gag gig',
    }
    for name,text in texts.items():
        shaped=shape_font(font,text,{'kern':True,'liga':False})
        svg=compose_preview_svg(font,project,shaped,font_size=96,guides=False)
        (proofs/f'{name}.svg').write_bytes(svg)
        (proofs/f'{name}.png').write_bytes(svg_to_png(svg,pixel_scale=3))
    for name,text in {'small':'Quiet geometry. Angular grace. 0123456789', 'small-controls':'minimum nixn njn aadd bbppqq HHOH'}.items():
        shaped=shape_font(font,text,{'kern':True,'liga':False})
        svg=compose_preview_svg(font,project,shaped,font_size=24,guides=False)
        (proofs/f'{name}.svg').write_bytes(svg)
        (proofs/f'{name}.png').write_bytes(svg_to_png(svg,pixel_scale=1))
    (OUT/'design.json').write_text(json.dumps({'family':project.font.family_name,'scope':'103-character Latin display prototype','provenance':'Original project-specific Bézier drawings guided by user-supplied concept artwork. No existing font outlines or bitmap tracing.','reference_traits':['high vertical contrast','triangular wedge serifs','double-storey a and g','diamond dots','unbracketed sharp terminals'],'user_refinements':['g ear is one triangle without a separate bar','Q tail has parallel diagonal edges and a faceted finish','parallel construction: vertical stem families, horizontal crossbars, 45-degree serif cuts, exact parallelograms for X/x, parallel V/v diagonals','a lower bowl and b/d/p/q joins redrawn as clean unified contours'], 'metrics':{'upm':1000,'cap':700,'x_height':470,'ascenders':770,'descenders':[-220,-230],'cap_stem':116,'lower_stem':106,'hairline':[20,24],'round_overshoot':12},'revision':built['revision']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true')
    run(parser.parse_args().controls)
