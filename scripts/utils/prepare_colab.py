import zipfile
import os

def zip_project(output_filename):
    print(f"📦 Zipping project to {output_filename}...")
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add requirements.txt
        if os.path.exists('requirements.txt'):
            zipf.write('requirements.txt')
            print(" - Added requirements.txt")
            
        # 2. Add src/
        for root, dirs, files in os.walk('src'):
            for file in files:
                if "__pycache__" in root: continue
                file_path = os.path.join(root, file)
                zipf.write(file_path)
                print(f" - Added {file_path}")

        # 3. Add data/
        for root, dirs, files in os.walk('data'):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path)
                print(f" - Added {file_path}")

    print(f"✅ Created {output_filename}")

if __name__ == "__main__":
    zip_project('project.zip')
