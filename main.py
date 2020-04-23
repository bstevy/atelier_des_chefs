import io
import os
import re

import requests
import unidecode
from bs4 import BeautifulSoup
from tqdm import tqdm

recette_id_re = re.compile(r"lienImprimerRecette\((\d+)\)")
not_word = re.compile(r"\W")

base_url = "https://www.atelierdeschefs.fr/fr/cours-en-ligne/{id_recette}"
print_url = "https://www.atelierdeschefs.fr/fr/recette/imprimerrecette/id/{id_print}"

for id_recette in tqdm(range(1748)):

    response = requests.get(base_url.format(id_recette=id_recette))
    html_content = response.content

    try:
        html_content_utf8 = html_content.decode("utf8")
    except:
        continue

    rez = [
        id_print
        for id_print in recette_id_re.findall(html_content_utf8)
        if id_print != "0"
    ]

    for id_print in rez:
        a = id_recette
        response = requests.get(print_url.format(id_print=id_print))
        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup.select("script"):
            script.decompose()

        title = unidecode.unidecode(soup.select("h1")[0].get_text())
        new_title = "_".join([not_word.sub("", i) for i in title.split()])

        with io.open(
            os.path.join(".", "recettes", "{}.html".format(new_title)),
            "w",
            encoding="utf-8",
        ) as out_file:
            out_file.write(str(soup))


working_dir = os.path.join(".", "recettes",)
for old_name in os.listdir(working_dir):
    new_name = old_name.replace("Recette_de_", "")
    os.rename(
        os.path.join(working_dir, old_name), os.path.join(working_dir, new_name),
    )
