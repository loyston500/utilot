from cmd import cmd
import argutils; from argutils import ArgParse

from io import BytesIO
import PIL
from PIL import Image
from PIL import ImageOps
from PIL.ImageFilter import (
   BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE,
   EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN
)

filters = {
    "BLUR": BLUR,
    "CONTOUR": CONTOUR,
    "DETAIL": DETAIL,
    "EDGE_ENHANCE": EDGE_ENHANCE,
    "EDGE_ENHANCE_MORE": EDGE_ENHANCE_MORE,
    "EMBOSS": EMBOSS,
    "FIND_EDGES": FIND_EDGES,
    "SMOOTH": SMOOTH,
    "SMOOTH_MORE": SMOOTH_MORE,
    "SHARPEN": SHARPEN,
}

@cmd.new()
@ArgParse.wrap(
    ArgParse()
        .add_argument(names=['r', 'rotate'], greedy=True)
        .add_argument(names=['c', 'crop'], greedy=True)
        .add_argument(names=['t', 'transpose'], greedy=True)
        .add_argument(names=['s', 'size'], greedy=True)
        .add_argument(names=['f', 'filter'], greedy=True)
        .add_argument(names=['E', 'encoder'], greedy=True)
        .add_argument(names=['i', 'invert'], greedy=False)
        #.add_argument(names=[''])
        
        .test()
)
async def img(snd, ctx, piped, args):
    '''
    whatis: an image editing tool that uses pillow lib internally
    man:
        usage: '{name} {{options}}'
        props:
            - PIPED [image data 1] {{image data 2}} ...
        description: |
            An image editing tool that uses pillow lib internally
            
            -r --rotate [DEGREES] Rotates the image
            -c --crop   [LEFT:UPPER:RIGHT:LOWER] Crops the image
            
            -s --size   [OPTION]
                SIZE          Resizes the image by the given percentage
                HEIGHTxWIDTH  Resizes the image by the given height and width percentage    
            
            -t --transpose [OPTION1:OPTION2...]
                FLIPH     Flips the image horizontally
                FLIPV     Flips the image vertically
                ROTAT90   Rtoates the image by 90 degrees
                ROTAT180  Rtoates the image by 180 degrees
                ROTAT270  Rtoates the image by 270 degrees
                
            -f --filter [OPTION1:OPTION2...]
                Supported filters below:
                    BLUR
                    CONTOUR
                    DETAIL
                    EDGE_ENHANCE
                    EDGE_ENHANCE_MORE
                    EMBOSS
                    FIND_EDGES
                    SMOOTH
                    SMOOTH_MORE
                    SHARPEN
                    
            -i --invert  Invertes the given image
                
    '''
    
    kwargs, args = args.parse()
    
    encoder = kwargs.encoder or 'PNG'
    
    if piped and piped._out:
        imgbytes = piped._out[0]
    else:
        snd.sendout('no content provided')
        snd.exitcode(1)
        return
    
    try:
        image = Image.open(BytesIO(imgbytes))
    except:
        snd.sendout('bad image data')
        snd.exitcode(1)
        return 
    
    if 'rotate' in kwargs:
        try:
            v = int(kwargs.rotate)
            if v < 0 or v > 360:
                raise ValueError
        except ValueError:
            snd.senderr('rotate value must be an integer value in between 0 and 360')
            snd.exitcode(1)
            return 
        
        image = image.rotate(v)
        
    if 'crop' in kwargs:
        try:
            a, b, c, d = [int(v) for v in kwargs.crop.split(':')]
        except (ValueError, IndexError):
            snd.senderr('crop values must be integers value and should be in the form left:upper:right:lower')
            snd.exitcode(1)
            return 
        
        try:
            image = image.crop((a, b, c, d))
        except Exception as err:
            raise err
        
    if 'transpose' in kwargs:
        opts = set(kwargs.transpose.split(':'))
        
        for opt in opts:
            if opt == 'FLIPH':
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif opt == 'FLIPV':
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            elif opt == 'ROTATE90':
                image = image.transpose(Image.ROTATE_90)
            elif opt == 'ROTATE180':
                image = image.transpose(Image.ROTATE_180)
            elif opt == 'ROTATE270':
                image = image.transpose(Image.ROTATE_270)
                
    if 'size' in kwargs:
        s = kwargs.size.split('X')
        
        if len(s) == 1:
            try:
                s = int(s[0])
            except:
                snd.senderr('size must be a single integer or two integers in the form HEIGHTxWIDTH')
                snd.exitcode(1)
                return
            
            if s > 100 or s < 0:
                snd.senderr('size must be greater than 0 and lesser 100')
                snd.exitcode(1)
                return 
            
            image = image.resize((round(image.size[0] * (s / 100)), round(image.size[1] * (s / 100))))
            
        elif len(s) == 2:
            try:
                h, w = int(s[0]), int(s[1])
            except:
                snd.senderr('size must be a single integer or two integers in the form heightXwidth')
                snd.exitcode(0)
                return
            
            if h > 100 or h < 0 or w > 100 or w < 0:
                snd.senderr('height and width must be greater than 0 and lesser 100')
                snd.exitcode(1)
                return 
            
            
            image = image.resize((round(image.size[0] * (h / 100)), round(image.size[1] * (w / 100))))
            
            
    if 'filter' in kwargs:
        fltr_strs = (kwargs.filter.split(':'))
        
        for fltr in fltr_strs:
            if fltr in filters:
                image = image.filter(filters[fltr])
                
            else:
                snd.senderr(f'bad filter {fltr}')
                snd.exitcode(0)
                return
            
            
    if 'invert' in kwargs:
        image = ImageOps.invert(image)
        
               
        
    
    save = BytesIO()
    image.save(save, format=encoder)
    
    snd.sendout(save.getvalue())
        
    
            
    
