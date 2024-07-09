from reportlab.platypus import Image, Spacer, Paragraph, PageBreak
from src.themes.theme import Theme, ParagraphStyles
from reportlab.lib.units import cm

class Cover():
    def __init__(self, title: str, enterprise_logo: str, client_logo: str, text: str, footer: str, theme: 'Theme') -> None:
        self.title = title
        self.enterprise_logo = enterprise_logo
        self.client_logo = client_logo
        self.text = text
        self.footer = footer
        self.theme = theme

    def render(self):
        get_style = self.theme.get_style
        text_styles = ParagraphStyles

        elements = []

        # Add the enterprise logo
        enterprise_logo = Image(self.enterprise_logo, width=3.67 * cm, height=3.12 * cm, hAlign="CENTER")
        elements.append(enterprise_logo)
        elements.append(Spacer(0, 4 * cm))

        # Add the title
        title_paragraph = Paragraph(self.title, get_style(text_styles.TITLE_1))
        elements.append(title_paragraph)
        elements.append(Spacer(0, 3 * cm))

        # Add the client logo
        client_logo = Image(self.client_logo, width=10.37 * cm, height=2.46 * cm, hAlign="CENTER")
        elements.append(client_logo)
        elements.append(Spacer(0, 3 * cm))

        # Add the text
        text_paragraph = Paragraph(self.text, get_style(text_styles.TEXT_NORMAL))
        elements.append(text_paragraph)

        # Calculate the used height
        used_height = 0
        for element in elements:
            if isinstance(element, Spacer):
                used_height += element.height
            else:
                _, element_height = element.wrap(self.theme.page_width - self.theme.leftMargin - self.theme.rightMargin, self.theme.page_height)
                used_height += element_height + element.getSpaceAfter()

        # Calculate the remaining space to push the footer to the bottom
        remaining_space = self.theme.page_height - used_height - self.theme.bottomMargin - self.theme.topMargin  # Adjust for top and bottom margins

        if remaining_space > 2 * cm:  # Ensure space for footer height
            elements.append(Spacer(0, remaining_space - 2 * cm))  # Adjust for footer height

        # Add the footer
        footer_paragraph = Paragraph(self.footer, get_style(text_styles.TEXT_ITALIC))
        elements.append(footer_paragraph)

        # Ensure the footer is placed correctly
        if remaining_space <= 2 * cm:
            # If not enough space, add a new page and then the footer
            elements.append(PageBreak())
            elements.append(Spacer(0, self.theme.page_height - self.theme.bottomMargin - 2 * cm))  # Adjust for the new page's footer placement
            elements.append(footer_paragraph)
        
        return elements
