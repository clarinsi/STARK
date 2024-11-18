import yaml
import json

# get yaml from https://github.com/UniversalDependencies/docs-automation/blob/master/codes_and_flags.yaml
with open("codes_and_flags.yaml", "r") as stream:
    try:
        codes_and_flags = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open("grew_corpus_names.txt", "r") as f:
    corpus_names = [fname[:-6] for fname in f.readlines()]
    # try:
    #     codes_and_flags = yaml.safe_load(stream)
    # except yaml.YAMLError as exc:
    #     print(exc)

code_mapper = {}
for lname, val in codes_and_flags.items():
    lcode = val['lcode']
    code_mapper[lname] = lcode

json_dict = {}
for cname in corpus_names:
    lang_corp = cname[3:].split('-')
    lang = lang_corp[0].replace('_', ' ')
    corp = lang_corp[1]
    if code_mapper[lang] not in json_dict:
        json_dict[code_mapper[lang]] = {}
    json_dict[code_mapper[lang]][corp.lower()] = cname

with open("../stark/resources/codes_mapper.json", "w") as outfile:
    json.dump(json_dict, outfile, indent=4)
