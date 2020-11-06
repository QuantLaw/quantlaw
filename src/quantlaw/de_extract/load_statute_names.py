import json
import os
import re
import shutil
import zipfile

import lxml.etree
import requests

from quantlaw.de_extract.stemming import stem_law_name


def load_law_names(date, path):
    r = requests.get(
        f"https://github.com/QuantLaw/gesetze-im-internet/archive/{date}.zip",
        stream=True,
    )
    assert r.status_code == 200
    with open(path + ".zip", "wb") as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    law_names = {}

    with zipfile.ZipFile(path + ".zip") as zip_file:
        for member_info in sorted(zip_file.namelist()):
            if member_info.endswith(".xml"):
                with zip_file.open(member_info) as member_file:
                    node = lxml.etree.parse(member_file)
                first_norm_nodes = node.xpath("(//norm)[1]")
                if not first_norm_nodes:
                    continue
                abk_nodes = first_norm_nodes[0].xpath(".//jurabk | //amtabk")
                if not abk_nodes:
                    continue
                abk = (
                    lxml.etree.tostring(abk_nodes[0], method="text", encoding="utf8")
                    .decode("utf8")
                    .strip()
                )
                abk_stem = re.sub(r"[^a-z0-9\-]", "_", abk.lower())

                law_names[stem_law_name(abk)] = abk_stem

                heading_nodes = first_norm_nodes[0].xpath(
                    ".//jurabk | //amtabk | " ".//langue | .//kurzue"
                )
                for heading_node in heading_nodes:
                    text = (
                        lxml.etree.tostring(
                            heading_node, method="text", encoding="utf8"
                        )
                        .decode("utf8")
                        .strip()
                    )
                    text = stem_law_name(text)
                    law_names[text] = abk_stem

    with open(path, "w", encoding="utf8") as f:
        json.dump(law_names, f, ensure_ascii=False, indent=0)

    os.remove(path + ".zip")
