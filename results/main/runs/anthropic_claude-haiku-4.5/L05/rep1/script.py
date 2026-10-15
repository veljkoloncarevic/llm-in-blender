import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create bookshelf frame using thin cubes
def create_cube(location, scale, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    return obj

# Frame dimensions
frame_width = 12
frame_height = 10
frame_depth = 2

# Create left side frame
left_frame = create_cube(Vector((-frame_width/2 - 0.2, frame_height/2, 0)), 
                         Vector((0.4, frame_height, frame_depth)), "LeftFrame")

# Create right side frame
right_frame = create_cube(Vector((frame_width/2 + 0.2, frame_height/2, 0)), 
                          Vector((0.4, frame_height, frame_depth)), "RightFrame")

# Create top frame
top_frame = create_cube(Vector((0, frame_height + 0.2, 0)), 
                        Vector((frame_width, 0.4, frame_depth)), "TopFrame")

# Create bottom frame
bottom_frame = create_cube(Vector((0, -0.2, 0)), 
                           Vector((frame_width, 0.4, frame_depth)), "BottomFrame")

# Create shelves at three heights
shelf_positions = [2.5, 5.0, 7.5]
shelves = []
for i, y_pos in enumerate(shelf_positions):
    shelf = create_cube(Vector((0, y_pos, 0)), 
                       Vector((frame_width - 0.8, 0.3, frame_depth)), 
                       f"Shelf{i+1}")
    shelves.append(shelf)

# Create a single book shape (thin tall box)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
book_template = bpy.context.active_object
book_template.name = "BookTemplate"
book_template.scale = Vector((0.3, 1.8, 0.15))  # Thin, tall book shape

# Apply array modifier to create row of books
array_mod = book_template.modifiers.new(name="ArrayBooks", type='ARRAY')
array_mod.count = 12
array_mod.relative = True
array_mod.use_relative_offset = True
array_mod.relative_offset_displace = (0.35, 0, 0)  # Space between books

# Create instances of books on each shelf
for i, shelf in enumerate(shelves):
    # Duplicate the book template for each shelf
    bpy.context.view_layer.objects.active = book_template
    book_template.select_set(True)
    bpy.ops.object.duplicate()
    book_row = bpy.context.active_object
    book_row.name = f"Books_Shelf{i+1}"
    
    # Position book row on shelf
    book_row.location = Vector((-5, shelf_positions[i], 0.2))

# Hide the template book
book_template.hide_set(True)
book_template.hide_render = True

# Apply modifiers and join objects for optimization
all_objects = [left_frame, right_frame, top_frame, bottom_frame] + shelves

# Select all frame and shelf objects
for obj in all_objects:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

# Apply transforms
for obj in bpy.context.selected_objects:
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Join frame and shelves into one object
if all_objects:
    bpy.context.view_layer.objects.active = all_objects[0]
    bpy.ops.object.join()

# Apply array modifiers on book rows
for obj in bpy.context.scene.objects:
    if obj.name.startswith("Books_Shelf"):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        # Apply the array modifier
        for mod in obj.modifiers:
            if mod.type == 'ARRAY':
                bpy.ops.object.modifier_apply(modifier=mod.name)

print("Bookshelf scene created successfully!")
