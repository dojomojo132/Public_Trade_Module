"""Check CDI header format."""
f = open(r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml", "rb")
h = f.read(200)
f.close()
print(repr(h))
