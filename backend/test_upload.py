import os
import shutil

def collect_all_borders(upload_parts_dir='backend/upload_parts', border_dir='backend/upload_parts/border'):
    """
    Collect all border.png files from each subfolder in upload_parts_dir and copy them to border_dir.
    The copied files are renamed to avoid overwriting, using the subfolder name as a prefix.
    """
    if not os.path.exists(border_dir):
        os.makedirs(border_dir)

    for folder in os.listdir(upload_parts_dir):
        folder_path = os.path.join(upload_parts_dir, folder)
        if os.path.isdir(folder_path) and folder.endswith('_parts'):
            border_path = os.path.join(folder_path, 'border.png')
            if os.path.exists(border_path):
                # Rename to avoid overwriting: <folder>_border.png
                dest_filename = f"{folder}_border.png"
                dest_path = os.path.join(border_dir, dest_filename)
                shutil.copy2(border_path, dest_path)
                print(f"Copied {border_path} to {dest_path}")
            else:
                print(f"No border.png in {folder_path}")

if __name__ == "__main__":
    collect_all_borders()
