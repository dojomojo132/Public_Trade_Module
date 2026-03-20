import uuid, os

base = r'D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors'
src = os.path.join(base, 'Вчсн_КассаПанель', 'Вчсн_КассаПанель.xml')
dst = os.path.join(base, 'Вчсн_КассаПанель.xml')

with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

type_id = str(uuid.uuid4())
value_id = str(uuid.uuid4())
mgr_type_id = str(uuid.uuid4())
mgr_value_id = str(uuid.uuid4())

internal_info = (
    '        <InternalInfo>\n'
    '            <xr:GeneratedType name="DataProcessorObject.Вчсн_КассаПанель" category="Object">\n'
    f'                <xr:TypeId>{type_id}</xr:TypeId>\n'
    f'                <xr:ValueId>{value_id}</xr:ValueId>\n'
    '            </xr:GeneratedType>\n'
    '            <xr:GeneratedType name="DataProcessorManager.Вчсн_КассаПанель" category="Manager">\n'
    f'                <xr:TypeId>{mgr_type_id}</xr:TypeId>\n'
    f'                <xr:ValueId>{mgr_value_id}</xr:ValueId>\n'
    '            </xr:GeneratedType>\n'
    '        </InternalInfo>\n'
    '        '
)

new_content = content.replace('        <Properties>', internal_info + '<Properties>')

with open(dst, 'w', encoding='utf-8') as f:
    f.write(new_content)

os.remove(src)
print('OK')
print('src:', src)
print('dst:', dst)
