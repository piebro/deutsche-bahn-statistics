import re
import sys

from bs4 import BeautifulSoup


def get_tag_and_question(file_path):
    with open(file_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        h1 = soup.find("h1")
        question = h1.text.replace("\n", "") if h1 else None
        tag = h1.get("id") if h1 else None
    return tag, question


def update_main_index(order):
    with open("questions/index.html", encoding="utf-8") as file:
        content = file.read()

    questions = []
    for folder in order:
        tag, question = get_tag_and_question(f"questions/{folder}/index.html")
        if question:
            questions.append((folder, tag, question))

    new_content = ""
    for folder, tag, question in questions:
        new_content += f'        <a href="{folder}" class="question-card">\n'
        new_content += f"            <h4>{tag}</h4>\n"
        new_content += f"            <p>{question}</p>\n"
        new_content += "        </a>\n"

    pattern = r"(?s)<!-- generated with scripts/generate_html_links\.py -->.*?<!-- end of generated links -->"
    updated_content = re.sub(
        pattern,
        f"<!-- generated with scripts/generate_html_links.py -->\n{new_content}            <!-- end of generated links-->",
        content,
    )

    with open("questions/index.html", "w", encoding="utf-8") as file:
        file.write(updated_content)


def update_question_page(folder, prev_folder, next_folder, start_date, end_date):
    file_path = f"questions/{folder}/index.html"
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    # Add header content
    header_content = '    <header class="header">\n'
    header_content += '        <div class="left-nav">\n'
    if prev_folder:
        header_content += f'            <a href="../{prev_folder}">←</a>\n'
    header_content += '            <a href="..">alle Fragen</a>\n'
    if next_folder:
        header_content += f'            <a href="../{next_folder}">→</a>\n'
    header_content += '        </div>\n'
    header_content += '        <nav>\n'
    header_content += '            <a href="../about.html">About</a>\n'
    header_content += '            <a href="https://github.com/piebro/deutsche-bahn-statistics">Code</a>\n'
    header_content += '            <a href="https://github.com/piebro/deutsche-bahn-data">Daten</a>\n'
    header_content += '            <a href="https://piebro.github.io/">andere Projekte</a>\n'
    header_content += '        </nav>\n'
    header_content += '    </header>\n'

    # Update header section
    header_pattern = r"(?s)<!-- header generated with scripts/generate_html_links\.py -->.*?<!-- end of generated header-->"
    content = re.sub(
        header_pattern,
        f"<!-- header generated with scripts/generate_html_links.py -->\n{header_content}    <!-- end of generated header-->",
        content,
    )

    # Updated footer content with new date format
    footer_content = "    <p>\n"
    footer_content += f'        Quelle: <a href="https://github.com/piebro/deutsche-bahn-statistics/blob/main/questions/{folder}/calculations.py">Berechnet</a>\n'
    footer_content += '        auf Basis von\n'
    footer_content += '        <a href="https://github.com/piebro/deutsche-bahn-data">gesammelten Daten</a>\n'
    footer_content += f'        von der Deutschen Bahn vom {start_date} bis {end_date}.\n\n'
    footer_content += '        <nav class="question-nav">\n'
    if prev_folder:
        footer_content += f'            <a href="../{prev_folder}" class="prev-question">Vorherige Frage</a>\n'
    if next_folder:
        _, next_question = get_tag_and_question(f"questions/{next_folder}/index.html")
        footer_content += f'            <a href="../{next_folder}" class="next-question">{next_question}</a>\n'
    footer_content += "        </nav>\n"
    footer_content += "    </p>\n"

    # Update navigation section
    footer_pattern = r"(?s)<!-- footer generated with scripts/generate_html_links\.py -->.*?<!-- end of generated footer -->"
    content = re.sub(
        footer_pattern,
        f"<!-- footer generated with scripts/generate_html_links.py -->\n{footer_content}    <!-- end of generated footer -->",
        content,
    )
    print(file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def main(order, start_date, end_date):
    update_main_index(order)
    for i, folder in enumerate(order):
        prev_folder = order[i - 1] if i > 0 else None
        next_folder = order[i + 1] if i < len(order) - 1 else None
        update_question_page(folder, prev_folder, next_folder, start_date, end_date)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scripts/generate_html_links.py START_DATE END_DATE 'folder1,folder2,folder3,...'")
        sys.exit(1)
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    order = sys.argv[3].split(",")
    main(order, start_date, end_date)
