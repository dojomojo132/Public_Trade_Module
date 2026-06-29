# -*- coding: utf-8 -*-
"""One-off patch: add ЧекиККМ and ФискальныеЧеки TCH to КассоваяСмена."""
from pathlib import Path


def attr_block(uid, name, syn, type_xml):
    return f"""\t\t\t\t<Attribute uuid="{uid}">
\t\t\t\t\t<Properties>
\t\t\t\t\t\t<Name>{name}</Name>
\t\t\t\t\t\t<Synonym>
\t\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t\t<v8:content>{syn}</v8:content>
\t\t\t\t\t\t\t</v8:item>
\t\t\t\t\t\t</Synonym>
\t\t\t\t\t\t<Comment/>
\t\t\t\t\t\t<Type>
{type_xml}
\t\t\t\t\t\t</Type>
\t\t\t\t\t\t<PasswordMode>false</PasswordMode>
\t\t\t\t\t\t<Format/>
\t\t\t\t\t\t<EditFormat/>
\t\t\t\t\t\t<ToolTip/>
\t\t\t\t\t\t<MarkNegatives>false</MarkNegatives>
\t\t\t\t\t\t<Mask/>
\t\t\t\t\t\t<MultiLine>false</MultiLine>
\t\t\t\t\t\t<ExtendedEdit>false</ExtendedEdit>
\t\t\t\t\t\t<MinValue xsi:nil="true"/>
\t\t\t\t\t\t<MaxValue xsi:nil="true"/>
\t\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
\t\t\t\t\t\t<ChoiceParameterLinks/>
\t\t\t\t\t\t<ChoiceParameters/>
\t\t\t\t\t\t<QuickChoice>Auto</QuickChoice>
\t\t\t\t\t\t<CreateOnInput>Auto</CreateOnInput>
\t\t\t\t\t\t<ChoiceForm/>
\t\t\t\t\t\t<LinkByType/>
\t\t\t\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
\t\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t\t\t<FullTextSearch>Use</FullTextSearch>
\t\t\t\t\t\t<DataHistory>Use</DataHistory>
\t\t\t\t\t</Properties>
\t\t\t\t</Attribute>"""


DECIMAL = (
    "\t\t\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>\n"
    "\t\t\t\t\t\t\t<v8:NumberQualifiers>\n"
    "\t\t\t\t\t\t\t\t<v8:Digits>15</v8:Digits>\n"
    "\t\t\t\t\t\t\t\t<v8:FractionDigits>2</v8:FractionDigits>\n"
    "\t\t\t\t\t\t\t\t<v8:AllowedSign>Any</v8:AllowedSign>\n"
    "\t\t\t\t\t\t\t</v8:NumberQualifiers>"
)
STRING50 = (
    "\t\t\t\t\t\t\t<v8:Type>xs:string</v8:Type>\n"
    "\t\t\t\t\t\t\t<v8:StringQualifiers>\n"
    "\t\t\t\t\t\t\t\t<v8:Length>50</v8:Length>\n"
    "\t\t\t\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>\n"
    "\t\t\t\t\t\t\t</v8:StringQualifiers>"
)


def ts_block(spec, name, syn):
    attrs = "\n".join(attr_block(u, n, s, t) for u, n, s, t in spec["attrs"])
    return f"""\t\t\t<TabularSection uuid="{spec['section']}">
\t\t\t\t<InternalInfo>
\t\t\t\t\t<xr:GeneratedType name="DocumentTabularSection.КассоваяСмена.{name}" category="TabularSection">
\t\t\t\t\t\t<xr:TypeId>{spec['type_section']}</xr:TypeId>
\t\t\t\t\t\t<xr:ValueId>{spec['val_section']}</xr:ValueId>
\t\t\t\t\t</xr:GeneratedType>
\t\t\t\t\t<xr:GeneratedType name="DocumentTabularSectionRow.КассоваяСмена.{name}" category="TabularSectionRow">
\t\t\t\t\t\t<xr:TypeId>{spec['type_row']}</xr:TypeId>
\t\t\t\t\t\t<xr:ValueId>{spec['val_row']}</xr:ValueId>
\t\t\t\t\t</xr:GeneratedType>
\t\t\t\t</InternalInfo>
\t\t\t\t<Properties>
\t\t\t\t\t<Name>{name}</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>{syn}</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<ToolTip/>
\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t<LineNumberLength>5</LineNumberLength>
\t\t\t\t</Properties>
\t\t\t\t<ChildObjects>
{attrs}
\t\t\t\t</ChildObjects>
\t\t\t</TabularSection>"""


def main():
    base = Path(r"D:\Git\Public_Trade_Module\Конфигурация\Documents\КассоваяСмена.xml")
    text = base.read_text(encoding="utf-8-sig")

    if "TabularSection" not in text:
        ts_cheki = {
            "section": "8f3a7b2e-c4d5-4e6f-9a1b-3c5d7e9f0a2b",
            "type_section": "f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "val_section": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "type_row": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "val_row": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",
            "attrs": [
                ("a2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d", "Касса", "Касса", "\t\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.Кассы</v8:Type>"),
                ("a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d", "ЧекККМ", "Чек ККМ", "\t\t\t\t\t\t\t<v8:Type>cfg:DocumentRef.ЧекККМ</v8:Type>"),
                ("a4b5c6d7-e8f9-4a0b-1c2d-3e4f5a6b7c8d", "Сумма", "Сумма", DECIMAL),
                ("a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d", "СуммаСкидки", "Сумма скидки", DECIMAL),
            ],
        }
        ts_fisk = {
            "section": "b1c2d3e4-f5a6-4b7c-8d9e-2a3b4c5d6e7f",
            "type_section": "d4e5f6a7-b8c9-4d0e-1f23-4a5b6c7d8e9f",
            "val_section": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",
            "type_row": "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c",
            "val_row": "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d",
            "attrs": [
                ("c8d9e0f1-a2b3-4c4d-5e6f-7a8b9c0d1e2f", "ВидОперации", "Вид операции", "\t\t\t\t\t\t\t<v8:Type>cfg:EnumRef.ВидыОперацийФискальногоЧека</v8:Type>"),
                ("b2c3d4e5-f6a7-4b8c-9d0e-3a4b5c6d7e8f", "ФОП", "ФОП", "\t\t\t\t\t\t\t<v8:Type>cfg:CatalogRef.ФОП</v8:Type>"),
                ("b3c4d5e6-f7a8-4b9c-0d1e-4a5b6c7d8e9f", "ФискальныйНомер", "Фискальный номер", STRING50),
                ("b4c5d6e7-f8a9-4b0c-1d2e-5a6b7c8d9e0f", "Сумма", "Сумма", DECIMAL),
                ("b5c6d7e8-f9a0-4b1c-2d3e-6a7b8c9d0e1f", "ФискальныйЧек", "Фискальный чек", "\t\t\t\t\t\t\t<v8:Type>cfg:DocumentRef.ФискальныйЧек</v8:Type>"),
            ],
        }
        insert = "\n" + ts_block(ts_cheki, "ЧекиККМ", "Чеки ККМ") + "\n" + ts_block(ts_fisk, "ФискальныеЧеки", "Фискальные чеки") + "\n\t\t\t"
        text = text.replace("\t\t\t<Form>ФормаДокумента</Form>", insert + "<Form>ФормаДокумента</Form>")
        base.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
        print("КассоваяСмена.xml updated")
    else:
        print("КассоваяСмена.xml already has TCH")

    cdi = Path(r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml")
    cdi_text = cdi.read_text(encoding="utf-8-sig")
    if "TabularSection.ЧекиККМ" not in cdi_text:
        old = (
            '\t\t\t<Metadata name="Document.КассоваяСмена.Attribute.Касса" id="ce733a7f-7b7c-45f5-a290-a0cf6c2990e0"/>\n'
            "\t\t</Metadata>"
        )
        new = (
            '\t\t\t<Metadata name="Document.КассоваяСмена.Attribute.Касса" id="ce733a7f-7b7c-45f5-a290-a0cf6c2990e0"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ЧекиККМ" id="8f3a7b2e-c4d5-4e6f-9a1b-3c5d7e9f0a2b"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ЧекиККМ.Attribute.Касса" id="a2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ЧекиККМ.Attribute.ЧекККМ" id="a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ЧекиККМ.Attribute.Сумма" id="a4b5c6d7-e8f9-4a0b-1c2d-3e4f5a6b7c8d"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ЧекиККМ.Attribute.СуммаСкидки" id="a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ФискальныеЧеки" id="b1c2d3e4-f5a6-4b7c-8d9e-2a3b4c5d6e7f"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ФискальныеЧеки.Attribute.ВидОперации" id="c8d9e0f1-a2b3-4c4d-5e6f-7a8b9c0d1e2f"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ФискальныеЧеки.Attribute.ФОП" id="b2c3d4e5-f6a7-4b8c-9d0e-3a4b5c6d7e8f"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ФискальныеЧеки.Attribute.ФискальныйНомер" id="b3c4d5e6-f7a8-4b9c-0d1e-4a5b6c7d8e9f"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ФискальныеЧеки.Attribute.Сумма" id="b4c5d6e7-f8a9-4b0c-1d2e-5a6b7c8d9e0f"/>\n'
            '\t\t\t<Metadata name="Document.КассоваяСмена.TabularSection.ФискальныеЧеки.Attribute.ФискальныйЧек" id="b5c6d7e8-f9a0-4b1c-2d3e-6a7b8c9d0e1f"/>\n'
            "\t\t</Metadata>"
        )
        cdi_text = cdi_text.replace(old, new)
        cdi.write_bytes(b"\xef\xbb\xbf" + cdi_text.encode("utf-8"))
        print("ConfigDumpInfo.xml updated")
    else:
        print("ConfigDumpInfo already has TCH")


if __name__ == "__main__":
    main()