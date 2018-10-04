import json
import re

class Division:
    def __init__(self, d_name, d_code):
        self.d_name = d_name
        self.d_code = d_code

    def getDivision(self):
        return self.d_name, self.d_code


class Group(Division):
    def __init__(self, d_name, d_code, g_name, g_code):
        Division.__init__(self, d_name, d_code)
        self.g_name = g_name
        self.g_code = g_code

    def getGroup(self):
        return self.g_name, self.g_code


class Field(Group):
    def __init__(self, d_name, d_code, g_name, g_code, f_name, f_code):
        Group.__init__(self, d_name, d_code, g_name, g_code)
        self.f_name = f_name
        self.f_code = f_code

    def getField(self):
        return self.f_name, self.f_code


class ForCode:
    def __init__(self):
        with open('tag_file.json', 'r') as f:
            tag_json = f.read()
            tag_dict = json.loads(tag_json)
        divisions = tag_dict.keys()
        groups_lookup = []
        fields_lookup = []
        for groups in divisions:
            group = tag_dict[groups].keys()
            groups_lookup += group
            for fields in group:
                fields_lookup += tag_dict[groups][fields]

        self.divsion_lookup = divisions
        self.group_lookup = groups_lookup
        self.fields_lookup = fields_lookup
        self.tag_dict = tag_dict

    def search(self, term, level):
        def lookUp(term, lookup):
            for item in lookup:
                if term in item:
                    return item

        if level == 'field':
            for field in self.fields_lookup:
                field = field.split(' ', 1)
                if re.match(re.escape(field[1]), term, re.I):
                    f_code = field[0][:6] # 6 digit code
                    g_code = field[0][:4] # 4 digit code
                    d_code = field[0][:2] # 2 digit code
                    field = lookUp(f_code, self.fields_lookup)
                    group = lookUp(g_code, self.group_lookup)
                    division = lookUp(d_code, self.divsion_lookup)
                    field = field.split(' ', 1)
                    group = group.split(' ', 2)
                    division = division.split(' ', 2)
                    field_instance = Field(division[2], d_code, group[2], g_code, field[1], f_code)
                    return field_instance
        elif level == 'group':
            for group in self.group_lookup:
                group = group.split(' ', 2)
                if re.match(re.escape(group[2]), term, re.I):
                    g_code = group[1][:4]
                    d_code = group[1][:2]
                    group = lookUp(g_code, self.group_lookup)
                    division = lookUp(d_code, self.divsion_lookup)
                    group = group.split(' ', 2)
                    division = division.split(' ', 2)
                    group_instance = Group(division[2], d_code, group[2], g_code)
                    return group_instance
        elif level == 'division':
            for division in self.divsion_lookup:
                division = division.split(' ', 2)
                if re.match(re.escape(division[2]), term, re.I):
                    d_code = division[1]
                    division_instance = Division(division[2], d_code)
                    return division_instance

'''
bio = Division('BIOLOGICAL SCIENCES', '01')
bioinfor = Group('BIOLOGICAL SCIENCES', '01', 'Bioinformatics', '010101')

print bioinfor.getGroup()
print bioinfor.getDivision()
'''