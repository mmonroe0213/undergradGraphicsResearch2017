import bpy
import math
import bmesh

im = bpy.data.images.load("C:/Users/Michael/Documents/Research/src/images/difImageGrey2017_03_02_01_06_28.png")
imArray = [v for v in im.pixels]
w,h = im.size[0], im.size[1]
print(w, h)
bpy.data.images.remove(im, do_unlink = True)

# create new bmesh object
bme = bmesh.new()

# do modifications here
for v in range(h):
    for u in range(w):
        z = imArray[((v * w) + u) * 4] * 10
        bme.verts.new((u-w/2, v-h/2, z))

bme.verts.ensure_lookup_table()

for v0 in range(h-1):
    v1 = v0 + 1
    for u0 in range(w-1):
        u1 = u0 + 1
        
        i0 = v0 * w + u0
        i1 = v0 * w + u1
        i2 = v1 * w + u1
        i3 = v1 * w + u0
        
        bmf0 = bme.faces.new([bme.verts[i0],bme.verts[i1],bme.verts[i2],bme.verts[i3]])
 
# create mesh and object
# note: neither are linked to the scene, yet, so they won't show
# in the 3d view
me = bpy.data.meshes.new("MeshName")
ob = bpy.data.objects.new("ObjectName", me)
 
scn = bpy.context.scene # grab a reference to the scene
scn.objects.link(ob)    # link new object to scene
scn.objects.active = ob # make new object active
ob.select = True        # make new object selected (does not deselect
                        # other objects)
 
bme.to_mesh(me)         # push bmesh data into me

# to color vertices
# me.vertex_colors.new('Col')
# me.vertex_colors['Col'].data[0].color = Color((0,0,0))