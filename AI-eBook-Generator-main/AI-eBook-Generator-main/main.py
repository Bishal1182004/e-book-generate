import cohere
import pdfkit
import markdown
import config
import os
import sys

# Get the absolute path of the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, 'templates')

co = cohere.Client(config.COHERE_API_KEY)

def generate_ebook(topic, chapters):
    prompt = f"Write an eBook about {topic} with {chapters} chapters. Each chapter should have a title and content. Format the output in Markdown."

    response = co.generate(
        model='command-r-plus',
        prompt=prompt,
        max_tokens=10000,  # Adjust the output as necessary based on expected length
        temperature=0.7,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE'
    )

    return str(response.generations[0].text).strip()

def save_markdown(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def markdown_to_html(markdown_content):
    html_content = markdown.markdown(markdown_content)
    return html_content

def embed_html_template(html_content, template_filename):
    # Read the selected template HTML file from the templates folder
    template_path = os.path.join(TEMPLATES_DIR, template_filename)
    with open(template_path, 'r', encoding='utf-8') as file:
        template = file.read()

    # Replace the placeholder with actual HTML content
    styled_html_content = template.replace('{{MARKDOWN_CONTENT}}', html_content)
    return styled_html_content

def convert_html_to_pdf(html_content, pdf_filename):
    try:
        # Configure wkhtmltopdf path based on OS
        if sys.platform == "win32":
            config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
        else:
            config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        
        # Convert HTML to PDF using pdfkit with configuration
        pdfkit.from_string(html_content, pdf_filename, configuration=config, options={"encoding": "UTF-8"})
    except OSError as e:
        print("Error: wkhtmltopdf is not installed or not found in the default location.")
        print("Please install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
        print("After installation, make sure it's available in the default location or update the path in the script.")
        sys.exit(1)

if __name__ == "__main__":
    topic = input("Enter the eBook topic: ")
    chapters = int(input("Enter the number of chapters: "))

    print("Available templates:")
    print("1. Classic")
    print("2. Modern")
    print("3. Minimalist")
    print("4. Elegant")
    print("5. Dark")

    template_choice = int(input("Choose a template (1-5): "))

    template_files = {
        1: 'classic.html',
        2: 'modern.html',
        3: 'minimalist.html',
        4: 'elegant.html',
        5: 'dark.html'
    }

    template_filename = template_files.get(template_choice, 'classic.html')

    print("Generating eBook content...")
    ebook_content = generate_ebook(topic, chapters)
    
    markdown_filename = topic.replace(" ", "-") + ".md"
    pdf_filename = topic.replace(" ", "-") + ".pdf"
    
    print(f"Saving eBook as Markdown ({markdown_filename})...")
    save_markdown(ebook_content, markdown_filename)
    
    print(f"Converting Markdown to HTML...")
    html_content = markdown_to_html(ebook_content)
    
    print(f"Embedding HTML content into HTML template ({template_filename})...")
    html_template_content = embed_html_template(html_content, template_filename)
    
    print(f"Converting HTML to PDF ({pdf_filename})...")
    convert_html_to_pdf(html_template_content, pdf_filename)
    
    print(f"eBook {pdf_filename} generation complete!")
