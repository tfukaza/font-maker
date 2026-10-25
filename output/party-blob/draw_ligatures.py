"""Original Party Blob ligature drawings, using the accepted glyph template.
The supplied font's own components are design material; AI pixels are never traced.
"""
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.svgLib.path import parse_path
import yaml
OUT=Path(__file__).resolve().parent
BASE=OUT/'font'
manifest=yaml.safe_load((BASE/'font.yaml').read_text())
ns={'s':'http://www.w3.org/2000/svg'}
def component(name):
 root=ET.parse(BASE/manifest['glyphs'][name]['source']).getroot()
 return ' '.join(p.attrib['d'] for p in root.findall('.//s:g[@id="glyph"]//s:path',ns))
def move(path,dx=0,dy=0):
 pen=SVGPathPen(None);parse_path(path,TransformPen(pen,(1,0,0,1,dx,dy)));return pen.getCommands()
def hole(path):
 pen=SVGPathPen(None);parse_path(path,ReverseContourPen(pen));return pen.getCommands()
D={}
# ec is one redrawn outer sweep; the e counter remains a true separate counter.
D['e_c']=(805,'''M121 558 C83 559 77 586 108 604 C170 647 263 650 331 629 C395 609 423 553 445 497 C480 409 550 354 632 365 C698 357 750 385 761 427 C777 499 705 521 645 487 C594 458 545 462 509 496 C472 530 465 578 498 607 C543 647 631 630 693 637 C756 644 782 686 766 744 C748 811 669 829 579 813 C505 800 456 766 414 725 C379 786 314 827 231 814 C104 798 23 716 19 604 C16 471 104 369 235 365 C343 362 424 411 425 481 C427 550 362 575 281 576 C218 577 174 556 121 558 Z'''+hole('''M108 465 C121 426 178 412 217 425 C251 436 257 472 236 491 C212 513 163 512 132 500 C112 492 101 483 108 465 Z'''))
# The i hook rises into the n entry; dot and n's familiar swollen shoulder survive.
D['i_n']=(650,'''M65 403 C101 374 172 377 176 418 C181 459 125 492 105 546 C80 609 87 688 117 710 C148 733 177 714 194 672 C220 610 215 532 224 476 C230 408 267 369 332 365 C430 360 515 412 530 486 C546 573 529 657 579 731 C597 757 620 771 629 785 C639 807 587 817 553 792 C491 746 478 653 433 578 C399 522 330 512 293 558 C258 604 265 674 244 724 C216 784 176 818 118 810 C42 800 37 721 39 650 C41 557 22 440 65 403 Z''' + component('i')[component('i').index('M50'):])
# Re-carved n exit makes room beneath a without welding the two contours.
D['n_a']=(855,'''M29 787 C10 775 53 749 65 714 C95 635 82 549 61 490 C35 417 69 369 152 365 C250 360 335 412 350 486 C364 573 343 650 378 716 C395 747 423 766 428 782 C434 799 394 800 370 780 C311 728 298 653 253 578 C219 522 150 512 113 558 C78 604 98 710 84 758 C76 790 45 799 29 787 Z'''+move(component('a'),385))
# A curved seam is cut into the first o's right side; each o retains its own counter.
D['o_o']=(865,component('o')+move(''' M604 365 C718 353 814 432 824 546 C837 686 751 804 617 815 C498 824 412 780 415 713 C417 674 458 617 464 560 C472 478 483 378 604 365 Z''',20)+move(hole('''M104 562 C102 489 148 433 210 432 C275 431 307 479 300 550 C292 619 249 664 189 661 C133 658 106 619 104 562 Z'''),405))
# r's terminal rolls downward below the lifted, shortened left t crossbar.
r='''M18 781 C15 761 51 709 66 659 C89 581 107 497 173 431 C228 377 283 389 313 416 C336 440 334 469 309 483 C282 500 263 459 221 481 C147 519 137 597 126 669 C117 731 108 784 73 799 C45 811 21 801 18 781 Z'''
t='''M154 208 C186 184 217 203 207 248 C195 300 166 354 158 411 C196 400 252 392 279 410 C313 433 289 459 256 457 C224 455 184 437 154 448 C132 541 117 644 151 684 C185 724 241 697 286 649 C270 755 204 821 135 811 C53 799 69 690 82 600 C90 543 99 492 106 451 C70 432 31 412 -10 399 C-42 391 -43 366 -12 368 C32 371 73 398 111 416 C118 326 115 238 154 208 Z'''
D['r_t']=(660,r+move(t,340))
template=(BASE/'glyph-template.svg').read_text()
dest=OUT/'ligature-drawings';dest.mkdir(exist_ok=True)
items=[]
for name,(advance,path) in D.items():
 file=dest/(name+'.svg')
 file.write_text(template.replace('<g id="glyph" fill="#000000"></g>',f'<g id="glyph" fill="#000000"><path d="{path}"/></g>'))
 items.append({'name':name,'svg_path':str(file),'codepoints':[],'advance_width':advance})
(OUT/'creative-glyphs.json').write_text(json.dumps(items,indent=2))
print('Drew',list(D))
