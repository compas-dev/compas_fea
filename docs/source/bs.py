import os
from bs4 import BeautifulSoup

for path, dirs, files in os.walk('/home/al/Dropbox/compas_fea/docs/'):
    for f in files:
        basename, ext = os.path.splitext(f)

        if ext == '.html':
            filepath = os.path.join(path, f)

            with open(filepath, 'r') as fp:
                soup = BeautifulSoup(fp.read(), 'html.parser')

                # change css links
                for link in soup.select('link'):
                    if 'rel' in link.attrs:
                        if link.attrs['rel'] == 'stylesheet':
                            if '_static' in link.attrs['href']:
                                href = link.attrs['href']
                                link.attrs['href'] = href.replace('_static', 'static')

                # change image referencing
                for img in soup.select('img'):
                    try:
                        alt = img.attrs['alt']
                        img.attrs['alt'] = alt.replace('_images', 'images')
                        src = img.attrs['src']
                        img.attrs['src'] = src.replace('_images', 'images')
                    except:
                        print(img.attrs)

            with open(filepath, 'w') as fp:
                fp.write(soup.prettify(formatter='html'))
