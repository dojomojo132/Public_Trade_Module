# -*- coding: utf-8 -*-
"""Extract .cfe extension file to XML using 1C Designer command line."""
import os, sys, pathlib, subprocess, time

PRRO_DIR = pathlib.Path(r"D:\Git\Public_Trade_Module\PRRO")
OUT_DIR = PRRO_DIR / "_extracted"

def find_1cv8():
    v8_dir = pathlib.Path(r"C:\Program Files\1cv8")
    if v8_dir.exists():
        versions = sorted(
            [d for d in v8_dir.iterdir() if d.is_dir() and d.name[0].isdigit()],
            key=lambda d: d.name, reverse=True
        )
        for v in versions:
            candidate = v / "bin" / "1cv8.exe"
            if candidate.exists():
                return str(candidate)
    raise FileNotFoundError("1cv8.exe not found")

def main():
    # Find .cfe file
    cfe_files = [f for f in os.listdir(PRRO_DIR) if f.endswith('.cfe')]
    if not cfe_files:
        print("No .cfe files found")
        return
    
    cfe_path = PRRO_DIR / cfe_files[0]
    print(f"CFE: {cfe_files[0]}")
    
    v8exe = find_1cv8()
    print(f"1cv8: {v8exe}")
    
    # Create output directory
    OUT_DIR.mkdir(exist_ok=True)
    
    # Use 1C Designer to dump CFE to XML
    # /DumpCfg exports configuration, but for extensions we need /DumpConfigToFiles
    # Actually for .cfe we need a temp infobase
    
    # Simpler approach: use 1C to create temp IB, load extension, dump to XML
    # But even simpler: .cfe can be unpacked with /DumpConfigToFiles if loaded via extension
    
    # Actually the simplest approach is to use the platform's ability to work with .cf/.cfe directly
    # via /ConfigurationFileDecompile (available in modern versions)
    
    IB = r"D:\Confiq\Public Trade Module"
    USER = "Админ"
    EXT = "TempVchasno"
    
    def run_1c(tag, extra_args, timeout=120):
        log = PRRO_DIR / f"_log_{tag}.txt"
        args = [v8exe, "DESIGNER", "/F", IB, "/N", USER,
                *extra_args, "/DisableStartupDialogs", "/DisableStartupMessages",
                "/Out", str(log)]
        print(f"\n[{tag}] {' '.join(extra_args)}")
        t0 = time.time()
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        print(f"  Exit: {r.returncode} ({time.time()-t0:.1f}s)")
        if log.exists():
            for enc in ("utf-8-sig", "utf-8", "cp1251"):
                try:
                    txt = log.read_text(encoding=enc)
                    if txt.strip():
                        print(f"  Log: {txt[:500]}")
                    break
                except: continue
        return r.returncode
    
    # Step 1: Load .cfe into IB as extension
    rc = run_1c("load", ["/LoadCfg", str(cfe_path), "-Extension", EXT, "-AllowUnresolvedRefs"])
    
    if rc != 0:
        print("Load failed, aborting")
        return
    
    # Step 2: Dump extension to XML files
    run_1c("dump", ["/DumpConfigToFiles", str(OUT_DIR), "-Extension", EXT])
    
    # List extracted files
    if OUT_DIR.exists():
        for root, dirs, files in os.walk(OUT_DIR):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, OUT_DIR)
                size = os.path.getsize(full)
                print(f"  {rel} ({size} bytes)")
    
    # Cleanup: unload the temp extension from IB
    print("\nCleaning up temp extension from IB...")
    cleanup_args = [
        v8exe, "DESIGNER",
        "/F", r"D:\Confiq\Public Trade Module",
        "/N", "Админ",
        "/ManageCfgExtensions", "-Delete", "-Extension", "TempVchasno",
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", str(PRRO_DIR / "_cleanup_log.txt"),
    ]
    try:
        subprocess.run(cleanup_args, capture_output=True, text=True, timeout=60)
        print("Cleanup done")
    except:
        print("Cleanup skipped")

if __name__ == '__main__':
    main()
