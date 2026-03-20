"""Исправляет VRD файл публикации /ptm — убирает испорченный Usr, оставляет правильный путь к ИБ."""
vrd_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
vrd_content += '<point xmlns="http://v8.1c.ru/8.2/virtual-resource-system"\n'
vrd_content += '       xmlns:xs="http://www.w3.org/2001/XMLSchema"\n'
vrd_content += '       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
vrd_content += '       base="/ptm"\n'
vrd_content += '       ib="File=&quot;D:\\Confiq\\Public Trade Module&quot;;">\n'
vrd_content += '    <ws pointEnableCommon="true"/>\n'
vrd_content += '    <httpServices publishByDefault="true"\n'
vrd_content += '                  publishExtensionsByDefault="true"/>\n'
vrd_content += '    <standardOdata enable="false"\n'
vrd_content += '                   reuseSessions="autouse"\n'
vrd_content += '                   sessionMaxAge="20"\n'
vrd_content += '                   poolSize="10"\n'
vrd_content += '                   poolTimeout="5"/>\n'
vrd_content += '    <analytics enable="true"\n'
vrd_content += '               sessionMaxAge="1200"\n'
vrd_content += '               poolSize="500"\n'
vrd_content += '               poolTimeout="5"/>\n'
vrd_content += '</point>\n'

path = r'C:\Server\Apache24\htdocs\ptm\default.vrd'
with open(path, 'w', encoding='utf-8') as f:
    f.write(vrd_content)
print(f'VRD updated: {path}')
print('Content:')
print(vrd_content)
