import re

from bs4 import BeautifulSoup, Tag

from article import Article, Section


# Parse a given html_doc and create an Article with the given title and date.
def parse_html(title, date, html_doc: str) -> Article:
    article = Article(title, date, [])
    soup = BeautifulSoup(html_doc, "html.parser")

    soup = soup.find(_is_main_body)

    if soup is None:
        raise ValueError("Couldn't find main body")

    _delete_sponsored_content(soup)
    _delete_styles_and_scripts(soup)

    # Add newlines to the end of <p> tags to make their inner content string
    # representations look like paragraphs.
    for p in soup.find_all("p"):
        p.append("\n\n")

    # There were 3 kinds of section headers, we need to try each one to see which matches.
    section_heading_finders = [
        _is_section_heading_table,
        _is_section_heading_h2,
        _is_section_heading_h3,
    ]
    for section_heading_finder in section_heading_finders:
        is_section_heading = section_heading_finder
        elem = soup.find(is_section_heading)
        if elem is not None:
            break
    else:
        raise ValueError("Can't find section heading")

    while elem is not None:
        if isinstance(elem, Tag):
            if is_section_heading(elem):
                section_title = _clean_text(elem.get_text(separator="", strip=True))
                article.sections.append(Section(section_title, ""))
            else:
                text = elem.get_text()
                text = _clean_text(text)
                article.sections[-1].body += text
        elem = elem.next_sibling
    return article


def _is_main_body(tag: Tag):
    return "class" in tag.attrs and (
        "body-component__content" in tag.attrs["class"]
        or "body-component" in tag.attrs["class"]
        or "body-copy" in tag.attrs["class"]
        or ("inner" in tag.attrs["class"] and "contents" in tag.attrs["class"])
    )


def _delete_sponsored_content(soup: BeautifulSoup):
    sponsored_content = soup.find(class_="sponsored-content")
    if sponsored_content:
        sponsored_content.decompose()


def _delete_styles_and_scripts(soup: BeautifulSoup):
    for style in soup.find_all("style"):
        style.decompose()
    for script in soup.find_all("script"):
        script.decompose()


def _is_section_heading_h2(tag: Tag) -> bool:
    return tag.name == "h2"


def _is_section_heading_h3(tag: Tag) -> bool:
    return tag.name == "h3"


def _is_section_heading_table(tag: Tag) -> bool:
    return (
        tag.name == "table"
        and "class" in tag.attrs
        and tag.attrs["class"] == ["header"]
    )

# Apply any "universal" text corrections/cleanups.
def _clean_text(s: str) -> str:
    return re.sub(" +", " ", s)
