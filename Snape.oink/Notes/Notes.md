# Notes

## Canvas

1. Canvas is an HTML element it has 2 attributes only, width & height, with default values 300px & 150px respectively.
2. When no styling rules are applied to the canvas it will initially be fully transparent.
3. Fallback content is content inside the \<canvas> element Browsers, by default, will ignore the content inside the container, rendering the canvas normally unless \<canvas> isn't supported.
4. \<canvas> element has a method called getContext(), used to obtain the rendering context and its drawing functions. getContext() takes one parameter, the type of context, like 2D, webgl, etc.
5. Specifying "2d" to get a CanvasRenderingContext2D.
6. Canvas grid or coordinate space, The origin of this grid is positioned in the top left corner at coordinate (0,0). All elements are placed relative to this origin.
7. Unlike SVG, \<canvas> only supports two primitive shapes: rectangles and paths (lists of points connected by lines). All other shapes must be created by combining one or more paths. Luckily, we have an assortment of path drawing functions which make it possible to compose very complex shapes.

   - Rectangle, there are three functions that draw rectangles on the canvas:  
    Here, (x,y) are the coordinates of top-left corner of rectangle from origin.
     - fillRect(x, y, width, height)  
       Draws a filled rectangle.
     - strokeRect(x, y, width, height)  
       Draws a rectangular outline.
     - clearRect(x, y, width, height)  
       Clears the specified rectangular area, making it fully transparent.  