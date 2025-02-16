import os
from datetime import datetime
import re
import subprocess
import shutil

# Constants for directories
TO_PUBLISH_DIR = "/Users/ronaldjabouin/Documents/Reading and Learning/Blog Writing/to-publish"
PUBLISHED_DIR = "/Users/ronaldjabouin/Documents/Reading and Learning/Blog Writing/2025"
WEBSITE_DIR = "/Users/ronaldjabouin/Documents/Web Dev/personal-webiste-github"

def slugify(title):
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    return slug

def get_title_from_filename(file_path):
    # Get the filename without extension and path
    filename = os.path.splitext(os.path.basename(file_path))[0]
    # Replace hyphens and underscores with spaces
    title = filename.replace('-', ' ').replace('_', ' ')
    # Capitalize words
    return ' '.join(word.capitalize() for word in title.split())

def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Could not find markdown file at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return None

def publish_changes(title):
    try:
        # Change to the correct directory
        os.chdir(WEBSITE_DIR)
        
        # Run git commands
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'added post: {title}'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("Successfully published changes to website")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        return False
    except Exception as e:
        print(f"Error publishing changes: {e}")
        return False

def update_writing_page(title, slug):
    writing_path = "writing.html"
    try:
        with open(writing_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the media-content div
        media_content_start = content.find('<div class="media-content">')
        if media_content_start == -1:
            print("Warning: Could not find media-content div in writing.html")
            return False
        
        # Create new post HTML
        new_post_html = f'''            <div class="post">
                <h4><a href="blog/{slug}.html" target="_self">{title}</a></h4>
            </div>
'''
        
        # Insert the new post at the start of media-content
        insert_position = media_content_start + len('<div class="media-content">\n')
        updated_content = content[:insert_position] + new_post_html + content[insert_position:]
        
        # Write the updated content back to the file
        with open(writing_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print("Successfully updated writing.html with the new post")
        return True
    except Exception as e:
        print(f"Error updating writing.html: {e}")
        return False

def move_to_published(markdown_path):
    try:
        # Create the published directory if it doesn't exist
        os.makedirs(PUBLISHED_DIR, exist_ok=True)
        
        # Move the file
        filename = os.path.basename(markdown_path)
        new_path = os.path.join(PUBLISHED_DIR, filename)
        shutil.move(markdown_path, new_path)
        print(f"Moved {filename} to published directory")
        return True
    except Exception as e:
        print(f"Error moving file to published directory: {e}")
        return False

def process_single_post(markdown_path):
    # Get default title from filename
    default_title = get_title_from_filename(markdown_path)
    title_input = input(f"Enter the post title (press Enter to use '{default_title}'): ")
    title = title_input if title_input.strip() else default_title
    
    # Get post subtitle
    subtitle = input("Enter the post subtitle: ")
    
    # Default to current date
    date_str = datetime.now().strftime("%B %d, %Y")
    date_input = input(f"Enter the post date (press Enter to use today's date: '{date_str}'): ")
    
    # If user provided a date, validate and use it
    if date_input.strip():
        while True:
            try:
                # Validate date format
                datetime.strptime(date_input, "%B %d, %Y")
                date_str = date_input
                break
            except ValueError:
                print("Invalid date format. Please use the format 'Month DD, YYYY'")
                date_input = input(f"Enter the post date (press Enter to use today's date: '{date_str}'): ")
                if not date_input.strip():
                    break
    
    content = read_markdown_file(markdown_path)
    if content is None:
        return False
    
    # Create slug for filename
    slug = slugify(title)
    output_path = f"blog/{slug}.html"
    
    # HTML template
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-X3S4QFM8BT"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-X3S4QFM8BT');
    </script>
    <base target="_blank">
    <link rel="stylesheet" href="../styles/styles.css">
    <title>{title} - Ronald Jabouin Jr</title>
    <link rel="stylesheet" href="https://cdn.locadapt.com/locadapt.min.css"/>
    <script src="https://cdn.locadapt.com/locadapt.min.js" data-project-id="7b621cc3-43a2-4dd7-9fce-dca784360759"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500&display=swap" rel="stylesheet">
    <script type="module" src="https://md-block.verou.me/md-block.js"></script>
</head>

<body>
    <div class="main-content">
        <h1>{title}</h1>
        <p class="date">{date_str}</p>
        <p class="subtitle">{subtitle}</p>
        
        <div class="blog-content">
            <md-block>
{content}
            </md-block>
        </div>

        <div class="links">
            <a href="../writing.html" target="_self">Back to Writing</a>
            <a href="../index.html" target="_self">Back to Home</a>
        </div>
    </div>
</body>
</html>'''
    
    # Create blog directory if it doesn't exist
    os.makedirs('blog', exist_ok=True)
    
    # Write the new blog post
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_template)
        print(f"\nSuccess! Blog post created at: {output_path}")
        
        # Update writing.html with the new post
        if not update_writing_page(title, slug):
            return False
            
        return True
    except Exception as e:
        print(f"Error creating blog post: {e}")
        return False

def create_blog_posts():
    print("Welcome to the blog post generator!")
    
    # Check for markdown files in the to-publish directory
    markdown_files = [f for f in os.listdir(TO_PUBLISH_DIR) if f.endswith('.md')]
    
    if not markdown_files:
        print(f"No markdown files found in {TO_PUBLISH_DIR}")
        return
    
    # Change to website directory for file operations
    os.chdir(WEBSITE_DIR)
    
    if len(markdown_files) == 1:
        # Process single file
        print(f"Found one blog post: {markdown_files[0]}")
        file_path = os.path.join(TO_PUBLISH_DIR, markdown_files[0])
        if process_single_post(file_path):
            if input("\nPublish changes to website? (y/n): ").lower() in ['y', 'yes']:
                if publish_changes(get_title_from_filename(file_path)):
                    move_to_published(file_path)
    else:
        # Multiple files found
        print("\nFound multiple blog posts:")
        for i, file in enumerate(markdown_files, 1):
            print(f"{i}. {file}")
        print("a. All posts")
        
        while True:
            choice = input("\nEnter the number(s) of posts to publish (comma-separated) or 'a' for all: ").lower()
            if choice == 'a':
                indices = range(len(markdown_files))
                break
            try:
                indices = [int(i.strip()) - 1 for i in choice.split(',')]
                if all(0 <= i < len(markdown_files) for i in indices):
                    break
                print("Invalid selection. Please enter valid numbers.")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas or 'a'.")
        
        # Process selected files
        success = True
        for i in indices:
            file_path = os.path.join(TO_PUBLISH_DIR, markdown_files[i])
            print(f"\nProcessing: {markdown_files[i]}")
            if process_single_post(file_path):
                if success:  # Only move file if all operations succeeded
                    move_to_published(file_path)
            else:
                success = False
        
        if success and input("\nPublish all changes to website? (y/n): ").lower() in ['y', 'yes']:
            publish_changes("multiple posts")

if __name__ == "__main__":
    create_blog_posts()
