import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create bookshelf frame using thin cubes
def create_cube(name, location, scale):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    return obj

# Bookshelf dimensions
shelf_width = 10
shelf_depth = 0.3
frame_thickness = 0.15
shelf_height = 0.8
total_height = 2.5

# Create left side frame
left_frame = create_cube("LeftFrame", Vector((-shelf_width/2 - frame_thickness/2, 0, total_height/2)), 
                         Vector((frame_thickness, shelf_depth, total_height)))

# Create right side frame
right_frame = create_cube("RightFrame", Vector((shelf_width/2 + frame_thickness/2, 0, total_height/2)), 
                          Vector((frame_thickness, shelf_depth, total_height)))

# Create back frame
back_frame = create_cube("BackFrame", Vector((0, -shelf_depth/2 - frame_thickness/2, total_height/2)), 
                         Vector((shelf_width + 2*frame_thickness, frame_thickness, total_height)))

# Create top frame
top_frame = create_cube("TopFrame", Vector((0, 0, total_height - frame_thickness/2)), 
                        Vector((shelf_width + 2*frame_thickness, shelf_depth + 2*frame_thickness, frame_thickness)))

# Create bottom frame
bottom_frame = create_cube("BottomFrame", Vector((0, 0, frame_thickness/2)), 
                           Vector((shelf_width + 2*frame_thickness, shelf_depth + 2*frame_thickness, frame_thickness)))

# Create three shelves
shelf_positions = [0.8, 1.6, 2.4]
for i, z_pos in enumerate(shelf_positions):
    shelf = create_cube(f"Shelf{i}", Vector((0, 0, z_pos)), 
                       Vector((shelf_width, shelf_depth, frame_thickness)))

# Create a single book model
book_width = 0.4
book_height = 0.7
book_depth = 0.1

bpy.ops.mesh.primitive_cube_add(size=1, location=Vector((-shelf_width/2 + book_width, 0, 0)))
book_template = bpy.context.active_object
book_template.name = "Book"
book_template.scale = Vector((book_width, book_depth, book_height))

# Apply scale to make it permanent
bpy.context.view_layer.objects.active = book_template
bpy.ops.object.transform_apply(scale=True)

# Add Array modifier to create row of books
array_mod = book_template.modifiers.new(name="ArrayBooks", type='ARRAY')
array_mod.count = 11
array_mod.relative = True
array_mod.use_relative_offset = True
array_mod.relative_offset_displace = (book_width * 2.2, 0, 0)

# Duplicate book rows for each shelf
for i, z_pos in enumerate(shelf_positions):
    if i == 0:
        continue
    
    # Duplicate the book with array modifier
    bpy.context.view_layer.objects.active = book_template
    book_template.select_set(True)
    bpy.ops.object.duplicate()
    book_copy = bpy.context.active_object
    book_copy.name = f"BookRow{i}"
    book_copy.location.z = z_pos

# Position first book row on first shelf
book_template.location.z = shelf_positions[0]

# Join all frame pieces into one object for efficiency
bpy.context.view_layer.objects.active = left_frame
left_frame.select_set(True)
right_frame.select_set(True)
back_frame.select_set(True)
top_frame.select_set(True)
bottom_frame.select_set(True)

for i in range(3):
    bpy.data.objects[f"Shelf{i}"].select_set(True)

bpy.ops.object.join()
frame_obj = bpy.context.active_object
frame_obj.name = "Bookshelf"

# Deselect all
bpy.ops.object.select_all(action='DESELECT')
