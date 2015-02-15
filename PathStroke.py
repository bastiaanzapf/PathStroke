
# Path stroking (aka Bezier Curve Offset), the easy way
#
# 1. Sort out trivial border cases (straight sections)
# 2. For every cubic spline A do:
# 2a. get three points on the parallel B to A by moving a certain distance
#     normal to the curve tangent
# 2b. get directions for the two endpoints
# 2c. put a spline C approximating B through the three points and two directions
# 2d. measure error between C and B
# 2e. if error is too large, split A in two parts and recurse to 2a
# 3. add join segments
#
# Some central ideas are found in this script by Simon Budig
#
# http://www.home.unix-ag.org/simon/sketch/pathstroke.py


