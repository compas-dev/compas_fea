from __future__ import print_function

import os
from bs4 import BeautifulSoup

for path, dirs, files in os.walk('../'):
    for f in files:
        basename, ext = os.path.splitext(f)

        if ext == '.html':
            filepath = os.path.join(path, f)

            with open(filepath, 'r') as fp:
                soup = BeautifulSoup(fp.read(), 'html.parser')

                # change css links
                for link in soup.select('link'):
                    # print(link.attrs)
                    if 'rel' in link.attrs:
                        if link.attrs['rel'][0] == 'stylesheet':
                            href = link.attrs['href']
                            link.attrs['href'] = href.replace('_static', 'static')

                # change script links
                for script in soup.select('script'):
                    if 'src' in script.attrs:
                        src = script.attrs['src']
                        script.attrs['src'] = src.replace('_static', 'static')

                # change image referencing
                for img in soup.select('img'):
                    if 'alt' in img.attrs:
                        alt = img.attrs['alt']
                        img.attrs['alt'] = alt.replace('_images', 'images')
                    src = img.attrs['src']
                    img.attrs['src'] = src.replace('_images', 'images')

            with open(filepath, 'w') as fp:
                fp.write(soup.prettify(formatter='html'))
