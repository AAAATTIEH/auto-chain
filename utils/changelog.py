# Specify the path to your Markdown file
markdown_file_path = 'changelog.md'

# Open the Markdown file and read its content into a string
with open(markdown_file_path, 'r', encoding='utf-8') as file:
    changelog_markdown = file.read()

