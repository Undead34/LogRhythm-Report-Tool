import chartify
from bokeh.resources import INLINE
from PIL import Image, ImageOps
from io import BytesIO
from bokeh.embed import file_html
import os


class Chart(chartify.Chart):
    def _figure_to_png(self):
        """Convert figure object to PNG
        Bokeh can only save figure objects as html.
        To convert to PNG the HTML file is opened in a headless browser.
        """
        driver = self._initialize_webdriver()

        # Save figure as HTML
        html = file_html(self.figure, resources=INLINE, title="")
        filename = os.path.realpath("./output/cache/chartify.html")

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding="utf-8") as fp:
            fp.write(html)

        # Open html file in the browser.
        file_url = "file:///" + filename
        driver.get(file_url)
        driver.execute_script("document.body.style.margin = '0px';")
        png = driver.get_screenshot_as_png()
        driver.quit()
        # Resize image if necessary.
        image = Image.open(BytesIO(png))
        target_dimensions = (self.style.plot_width, self.style.plot_height)
        if image.size != target_dimensions:
            image = image.resize(target_dimensions, resample=ImageOps.LANCZOS)
        return image
