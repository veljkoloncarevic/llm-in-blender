import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create bookshelf frame
def create_box_frame():
    # Create a thin cube for frame elements
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    frame = bpy.context.active_object
    frame.scale = (0.05, 0.05, 2.5)  # Thin vertical post
    bpy.ops.object.transform_apply(scale=True)
    
    # Create frame collection
    bpy.ops.object.select_all(action='DESELECT')
    frame.select_set(True)
    bpy.context.view_layer.objects.active = frame
    
    # Left post
    left_post = frame.copy()
    left_post.data = frame.data.copy()
    left_post.location = (-1.5, 0, 0)
    bpy.context.collection.objects.link(left_post)
    
    # Right post
    right_post = frame.copy()
    right_post.data = frame.data.copy()
    right_post.location = (1.5, 0, 0)
    bpy.context.collection.objects.link(right_post)
    
    # Top frame
    top_frame = frame.copy()
    top_frame.data = frame.data.copy()
    top_frame.scale = (3.1, 0.05, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    top_frame.location = (0, 0, 1.25)
    bpy.context.collection.objects.link(top_frame)
    
    # Bottom frame
    bottom_frame = frame.copy()
    bottom_frame.data = frame.data.copy()
    bottom_frame.scale = (3.1, 0.05, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    bottom_frame.location = (0, 0, -1.25)
    bpy.context.collection.objects.link(bottom_frame)
    
    # Back frame
    back_frame = frame.copy()
    back_frame.data = frame.data.copy()
    back_frame.scale = (3.1, 0.05, 2.5)
    bpy.ops.object.transform_apply(scale=True)
    back_frame.location = (0, -0.975, 0)
    bpy.context.collection.objects.link(back_frame)
    
    return frame, [left_post, right_post, top_frame, bottom_frame, back_frame]

frame, frame_parts = create_box_frame()

# Create shelf
def create_shelf():
    bpy.ops.mesh.primitive_cube_add(size=1)
    shelf = bpy.context.active_object
    shelf.scale = (3, 0.05, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    return shelf

# Create book with array modifier
def create_books_on_shelf(shelf_y_pos):
    # Create single book
    bpy.ops.mesh.primitive_cube_add(size=1)
    book = bpy.context.active_object
    book.scale = (0.08, 0.15, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    book.location = (-1.3, shelf_y_pos, 0)
    
    # Add array modifier for books
    array_mod = book.modifiers.new(name="BookArray", type='ARRAY')
    array_mod.count = 12
    array_mod.relative = True
    array_mod.use_relative_offset = True
    array_mod.relative_offset_displace = (0.22, 0, 0)
    
    return book

# Add shelves and books
shelves = []
shelf_heights = [0.5, 0, -0.5]

for height in shelf_heights:
    # Add shelf
    shelf = create_shelf()
    shelf.location = (0, 0, height)
    shelves.append(shelf)
    
    # Add books on shelf
    books = create_books_on_shelf(0)
    books.location = (-1.3, 0, height + 0.15)

# Apply modifiers to reduce face count
bpy.ops.object.select_all(action='DESELECT')
for book in bpy.context.scene.objects:
    if book.type == 'MESH' and book.modifiers:
        book.select_set(True)
        bpy.context.view_layer.objects.active = book
        bpy.ops.object.modifier_apply(modifier=book.modifiers[0].name)
        book.select_set(False)

# Join frame parts into single object for efficiency
bpy.ops.object.select_all(action='DESELECT')
frame.select_set(True)
for part in frame_parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = frame
bpy.ops.object.join()

# Select all and view
bpy.ops.object.select_all(action='SELECT')
bpy.ops.view3d.view_all()
