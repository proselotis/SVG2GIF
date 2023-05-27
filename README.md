# SVG2GIF
After having a rather niche use case and struggling to find a python convertor for SVG to GIF [svg2pdf.py]() was written. It is documented that some of the most common open source libraries aren't covering this conversion yet (for good reasons). [reference](https://github.com/ImageMagick/ImageMagick/discussions/2391).


This script takes an SVG file, opens it in selenium using a firefox driver, screenshots the svg file in live action, then uses PIL to combine all the saved png's to a gif. There is some smoothing of the GIF by slowing the SVG file to take more screenshots during the animations. This can be improved upon. 

Although this framework seems inefficent, there isn't a clean way to "activate" or iterate through animations in an SVG, which is why popular frameworks haven't built a solution to this problem yet. 
