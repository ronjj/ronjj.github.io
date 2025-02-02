import os
from datetime import datetime
import re
import subprocess

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
        os.chdir('/Users/ronaldjabouin/Documents/Web Dev/personal-webiste-github')
        
        # Run git commands
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'added post: {title}'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("Successfully published changes to website")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
    except Exception as e:
        print(f"Error publishing changes: {e}")

def update_writing_page(title, slug):
    writing_path = "writing.html"
    try:
        with open(writing_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the media-content div
        media_content_start = content.find('<div class="media-content">')
        if media_content_start == -1:
            print("Warning: Could not find media-content div in writing.html")
            return
        
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
    except Exception as e:
        print(f"Error updating writing.html: {e}")

def create_blog_post():
    print("Welcome to the blog post generator!")
    
    # Get markdown file path first
    while True:
        markdown_path = input("Enter the path to your markdown file: ")
        content = read_markdown_file(markdown_path)
        if content is not None:
            break
    
    # Get default title from filename
    default_title = get_title_from_filename(markdown_path)
    title_input = input(f"Enter the post title (press Enter to use '{default_title}'): ")
    title = title_input if title_input.strip() else default_title
    
    # Get post subtitle
    subtitle = input("Enter the post subtitle: ")
    
    # Get date with validation
    while True:
        date_input = input("Enter the post date (MMMM DD, YYYY format, e.g. 'February 1, 2024') or press Enter for today's date: ")
        if not date_input:
            # Use current date if no input
            date_str = datetime.now().strftime("%B %d, %Y")
            break
        try:
            # Validate date format
            datetime.strptime(date_input, "%B %d, %Y")
            date_str = date_input
            break
        except ValueError:
            print("Invalid date format. Please use the format 'Month DD, YYYY'")
    
    # Create slug for filename
    slug = slugify(title)
    output_path = f"blog/{slug}.html"
    
    # HTML template
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base target="_blank">
    <link rel="stylesheet" href="../styles/styles.css">
    <title>{title} - Ronald Jabouin Jr</title>
    <link
    rel="stylesheet"
    href="https://cdn.locadapt.com/locadapt.min.css"
    />
    <script
    src="https://cdn.locadapt.com/locadapt.min.js"
    data-project-id="7b621cc3-43a2-4dd7-9fce-dca784360759"
    ></script>
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
</html>
'''
    
    # Create blog directory if it doesn't exist
    os.makedirs('blog', exist_ok=True)
    
    # Write the new blog post
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_template)
        print(f"\nSuccess! Blog post created at: {output_path}")
        
        # Update writing.html with the new post
        update_writing_page(title, slug)
        
        # Ask about publishing
        while True:
            publish = input("\nPublish changes to website? (y/n): ").lower()
            if publish in ['y', 'yes']:
                publish_changes(title)
                break
            elif publish in ['n', 'no']:
                print("Changes not published. You can publish them later using git.")
                break
            else:
                print("Please enter 'y' or 'n'")
                
    except Exception as e:
        print(f"Error creating blog post: {e}")

if __name__ == "__main__":
    create_blog_post()
