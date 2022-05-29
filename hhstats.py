from pprint import pprint
import time
from unittest import result
from xml.dom.minidom import Element
from selenium import webdriver
from pathlib import Path
import xml.etree.ElementTree as ET
import json
from typing import Optional, List


def main():

    BROWSER = webdriver.Chrome()

    REGIONS = (
        "amur_oblast",  # far_eastern_federal_district
        "jewish_autonomous_oblast",
        "zabaykalsky_krai",
        "kamchatka_krai",
        "magadan_oblast",
        "primorsky_krai",
        "buryatia",
        "sakha_republic",
        "sakhalin_oblast",
        "khabarovsk_krai",
        "chukotka",
        "kirov_oblast",  # volga_federal_district
        "nizhny_novgorod_oblast",
        "orenburg_oblast",
        "penza_oblast",
        "perm_krai",
        "bashkortostan",
        "mari_el_republic",
        "mordovia",
        "tatarstan",
        "samara_oblast",
        "saratov_oblast",
        "udmurtia",
        "ulyanovsk_oblast",
        "chuvash_republic",
        "arkhangelsk_oblast",  # northwestern_federal_district
        "vologodskaya_oblast",
        "kaliningrad_oblast",
        "leningrad_oblast",
        "murmansk_oblast",
        "nenets_autonomous_okrug",
        "novgorod_oblast",
        "pskov_oblast",
        "republic_of_karelia",
        "komi_republic",
        "kabardino_balkaria",  # north_caucasus_federal_district
        "karachay_cherkessia",
        "dagestan",
        "ingushetia",
        "north_ossetia_alania",
        "stavropol_krai",
        "chechnya",
        "altai_krai",  # siberian_federal_district
        "irkutsk_oblast",
        "kemerovo_oblast",
        "krasnoyarsk_krai",
        "novosibirsk_oblast",
        "omsk_oblast",
        "altai_republic",
        "tyva_republic",
        "khakassia",
        "tomsk_oblast",
        "kurgan_oblast",  # ural_federal_district
        "sverdlovsk_oblast",
        "tyumen_oblast",
        "khanty_mansi_ao_ugra",
        "chelybinsk_oblast",
        "yamalo_nenets_ao",
        "belgorod_oblast",  # central_federal_district
        "braynsk_oblast",
        "vladimir_oblast",
        "voronezh_oblast",
        "ivanovo_oblast",
        "kaluga_oblast",
        "kostroma_oblast",
        "kursk_oblast",
        "lipetsk_oblast",
        "moscow_oblast",
        "oryol_oblast",
        "ryazan_oblast",
        "smolensk_oblast",
        "tambov_oblast",
        "tver_oblast",
        "tula_oblast",
        "yaroslavl_oblast",
        "astrakhan_oblast",  # southern_federal_district
        "volgograd_oblast",
        "krasnodar_krai",
        "republic_of_adygea",
        "republic_of_kalmykia",
        "republic_of_crimea",
        "rostov_oblast"
    )

    result = {}

    LINK_TEMPLATE = "https://stats.hh.ru/{}#hhindex[type]=comparison&hhindex[profarea][]=all&hhindex[profarea][]=1&hhindex[profarea][]=8&hhindex[profarea][]=11&hhindex[active]=true&vacancies[type]=comparison&vacancies[profarea][]=all&vacancies[profarea][]=1&vacancies[profarea][]=8&vacancies[profarea][]=11&vacancies[active]=true&resumes[type]=comparison&resumes[profarea][]=all&resumes[profarea][]=1&resumes[profarea][]=8&resumes[profarea][]=11&resumes[active]=true"

    # https://stats.hh.ru/amur_oblast#hhindex[type]=comparison&hhindex[profarea][]=all&hhindex[profarea][]=1&hhindex[profarea][]=8&hhindex[profarea][]=11&hhindex[active]=true&vacancies[type]=comparison&vacancies[profarea][]=all&vacancies[profarea][]=1&vacancies[profarea][]=8&vacancies[profarea][]=11&vacancies[active]=true&resumes[type]=comparison&resumes[profarea][]=all&resumes[profarea][]=1&resumes[profarea][]=8&resumes[profarea][]=11&resumes[active]=true

    n = 0
    for region in REGIONS:
        print(n, '. ', n / len(REGIONS) * 100, '%', ' ', region, sep='')

        n += 1
        BROWSER.get(LINK_TEMPLATE.format(region))
        time.sleep(10)
        html_source = BROWSER.page_source
        separator = '<svg'
        ending = "/svg>"
        svgs = html_source.split(separator)[1:]
        svgs = [separator + s[:s.find(ending)] + ending for s in svgs]
        try:
            indexes_graphs = get_graphs_values_from_svg(svgs[2])
            vacancies_graphs = get_graphs_values_from_svg(svgs[4])
            resumes_graphs = get_graphs_values_from_svg(svgs[6])
        except IndexError as e:
            with open('result.json', 'w') as file:
                json.dump(result, file)
            print('ERROR!', e)
            return
        if len(indexes_graphs["all"]) != 13 or len(vacancies_graphs["all"]) != 13 or len(resumes_graphs["all"]) != 13 or len(indexes_graphs["it"]) != 13 or len(vacancies_graphs["it"]) != 13 or len(resumes_graphs["it"]) != 13 or len(indexes_graphs["security"]) != 13 or len(vacancies_graphs["security"]) != 13 or len(resumes_graphs["security"]) != 13 or len(indexes_graphs["arts"]) != 13 or len(vacancies_graphs["arts"]) != 13 or len(resumes_graphs["arts"]) != 13:
            with open('result.json', 'w') as file:
                json.dump(result, file)
            print('CHECKSUM FAILED!', len(indexes_graphs["all"]), len(vacancies_graphs["all"]), len(resumes_graphs["all"]), len(indexes_graphs["it"]), len(vacancies_graphs["it"]), len(resumes_graphs["it"]), len(indexes_graphs["security"]), len(vacancies_graphs["security"]), len(resumes_graphs["security"]), len(indexes_graphs["arts"]), len(vacancies_graphs["arts"]), len(resumes_graphs["arts"]))
            return
        result[region] = {
            "indexes": indexes_graphs,
            "vacancies": vacancies_graphs,
            "resumes": resumes_graphs
            }

        # pprint(indexes_graphs)
        # print('\n')
        # pprint(vacancies_graphs)
        # print('\n')
        # pprint(resumes_graphs)
        # print('______________\n')

    with open('result.json') as file:
        json.dump(result, file)
    BROWSER.close()

def get_coordinates_from_path_tag(root: Element, xml_path_from_root):
    coordinates = root
    try:
        for i in range(len(xml_path_from_root)):
            coordinates = coordinates[xml_path_from_root[i]]
    except IndexError as e:
        return []
    coordinates = coordinates.attrib['d']
    # M 31 127 (move point to coordinates X,Y) L 570 88 (from current point draw line to X,Y)
    coordinates = coordinates.split()
    coordinates = list(filter(lambda x: x != 'M' and x != 'L', coordinates))
    coordinates = [float(c) if '%' not in c else float(c[:-1]) for c in coordinates]  # make float and remove percent if necessary
    coordinates = list(zip(coordinates[::2], coordinates[1::2]))
    coordinates.sort()  # so that coordinates always corespond the months
    return coordinates

def get_graphs_values_from_svg(svg: str):

    all_xml_path = (1, 0, 4, 1)
    it_xml_path = (1, 0, 6, 0)
    security_xml_path = (1, 0, 7, 0)
    arts_xml_path = (1, 0, 9, 0)
    borders_xml_path = (1, 0, 3)

    root = ET.fromstring(svg)

    min_value = root[1][0][15][0][0][0].text  # min_value_path
    max_value = root[1][0][15][-1][0][0].text  # max_value_path
    min_value = float(min_value) if '%' not in min_value else float(min_value[:-1])
    max_value = float(max_value) if '%' not in max_value else float(max_value[:-1])

    all_coordinates = get_coordinates_from_path_tag(root, all_xml_path)
    it_coordinates = get_coordinates_from_path_tag(root, it_xml_path)
    security_coordinates = get_coordinates_from_path_tag(root, security_xml_path)
    arts_coordinates = get_coordinates_from_path_tag(root, arts_xml_path)
    borders_coordinates = get_coordinates_from_path_tag(root, borders_xml_path)

    axisX = [p[0] for p in all_coordinates]

    lower_border_Y = borders_coordinates[0][1]
    upper_border_Y = borders_coordinates[-1][1]

    # print(lower_border_Y)
    # print(upper_border_Y)
    # print(min_value)
    # print(max_value)

    # system of linear equations

    k = (max_value - min_value) / (lower_border_Y - upper_border_Y)
    b = -k * upper_border_Y + min_value

    all_coordinates = {c[0]: c[1] for c in all_coordinates}
    it_coordinates = {c[0]: c[1] for c in it_coordinates}
    security_coordinates = {c[0]: c[1] for c in security_coordinates}
    arts_coordinates = {c[0]: c[1] for c in arts_coordinates}

    return {
        "all": [all_coordinates[x] * k + b if x in all_coordinates else None for x in axisX],
        "it": [it_coordinates[x] * k + b if x in it_coordinates else None for x in axisX],
        "security": [security_coordinates[x] * k + b if x in security_coordinates else None for x in axisX],
        "arts": [arts_coordinates[x] * k + b if x in arts_coordinates else None for x in axisX]
        }


if __name__ == "__main__":
    main()
