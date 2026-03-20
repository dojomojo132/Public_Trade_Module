# -*- coding: utf-8 -*-
"""Parse 1C v8 container (.cfe/.cf/.epf) and extract files."""
import os, sys, struct, zlib, re

PRRO_DIR = r"D:\Git\Public_Trade_Module\PRRO"
OUT_DIR = os.path.join(PRRO_DIR, "_extracted")

def read_v8_file(filepath):
    """Read 1C v8 container file."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return data

def parse_block_header(data, offset):
    """Parse a v8 block header at given offset.
    Format: \r\n{hex_doc_size} {hex_page_size} {hex_next_page}\r\n
    or starts with ff ff ff 7f as container header.
    """
    if offset + 4 > len(data):
        return None
    
    magic = struct.unpack_from('<I', data, offset)[0]
    if magic == 0x7fffffff:
        # Container header
        # ff ff ff 7f + 4 bytes block_size + 4 bytes ??? + 4 bytes ???
        block_size = struct.unpack_from('<I', data, offset + 4)[0]
        return {'type': 'container', 'block_size': block_size, 'header_size': 16}
    
    return None

def inflate_data(data):
    """Try to decompress deflate data."""
    try:
        return zlib.decompress(data, -15)  # raw deflate
    except:
        try:
            return zlib.decompress(data)  # zlib format
        except:
            return None

def parse_toc_line(line):
    """Parse TOC line: 'XXXXXXXX YYYYYYYY ZZZZZZZZ'"""
    parts = line.strip().split()
    if len(parts) >= 3:
        try:
            return {
                'doc_size': int(parts[0], 16),
                'page_size': int(parts[1], 16),
                'next_page': int(parts[2], 16)
            }
        except ValueError:
            return None
    return None

def extract_v8_container(data):
    """Extract files from v8 container format."""
    results = []
    
    # Skip container header (16 bytes: magic + block_size + 8 reserved)
    if len(data) < 16:
        return results
    
    magic = struct.unpack_from('<I', data, 0)[0]
    if magic != 0x7fffffff:
        print(f"Not a v8 container (magic: {magic:#x})")
        return results
    
    block_size = struct.unpack_from('<I', data, 4)[0]
    print(f"Container block_size: {block_size}")
    
    # After the 16-byte header, there's a TOC (table of contents)
    # TOC format: \r\n followed by lines of "offset size next\r\n"
    pos = 16
    
    # Read TOC - it starts with \r\n
    if data[pos:pos+2] != b'\r\n':
        print(f"Expected \\r\\n at offset {pos}, got {data[pos:pos+2].hex()}")
        # Try scanning for TOC pattern
    
    # Parse TOC entries
    toc_entries = []
    toc_text = b""
    
    # Read until we find non-TOC data
    while pos < len(data):
        if data[pos:pos+2] == b'\r\n':
            pos += 2
            # Read a line until next \r\n
            end = data.find(b'\r\n', pos)
            if end == -1:
                break
            line = data[pos:end].decode('ascii', errors='replace')
            entry = parse_toc_line(line)
            if entry:
                toc_entries.append(entry)
                pos = end
            else:
                break
        else:
            break
    
    print(f"Found {len(toc_entries)} TOC entries")
    
    # Now extract pages based on TOC
    for i, entry in enumerate(toc_entries):
        page_offset = entry['doc_size']  # This is actually the offset
        page_size = entry['page_size']
        
        if page_offset + page_size > len(data):
            print(f"  Entry {i}: offset {page_offset} + size {page_size} exceeds file ({len(data)})")
            continue
        
        page_data = data[page_offset:page_offset + page_size]
        
        # Try to decompress
        decompressed = inflate_data(page_data)
        if decompressed:
            results.append({
                'index': i,
                'offset': page_offset,
                'compressed_size': page_size,
                'data': decompressed,
                'decompressed_size': len(decompressed)
            })
            print(f"  Entry {i}: offset={page_offset:#x} size={page_size} -> decompressed {len(decompressed)} bytes")
        else:
            results.append({
                'index': i,
                'offset': page_offset,
                'compressed_size': page_size,
                'data': page_data,
                'decompressed_size': len(page_data)
            })
            print(f"  Entry {i}: offset={page_offset:#x} size={page_size} (raw, not compressed)")
    
    return results

def try_brute_force_deflate(data):
    """Scan entire binary for deflate streams and try to decompress."""
    results = []
    pos = 0
    
    while pos < len(data) - 2:
        # Look for common deflate stream starts
        # deflate with default compression typically starts with 0x78 0x9C or 0x78 0x01 or 0x78 0xDA
        if data[pos] == 0x78 and data[pos+1] in (0x01, 0x5E, 0x9C, 0xDA):
            try:
                decompressed = zlib.decompress(data[pos:pos+min(500000, len(data)-pos)])
                if len(decompressed) > 50:  # Skip tiny fragments
                    results.append({
                        'offset': pos,
                        'data': decompressed,
                        'size': len(decompressed)
                    })
                    pos += 100  # Skip ahead
                    continue
            except:
                pass
        pos += 1
    
    return results

def save_results(results, out_dir):
    """Save extracted data to files."""
    os.makedirs(out_dir, exist_ok=True)
    
    for i, result in enumerate(results):
        data = result['data']
        
        # Try to determine file type
        ext = '.bin'
        if data[:5] == b'<?xml':
            ext = '.xml'
        elif b'\xd0\x9f\xd1\x80\xd0\xbe\xd1\x86\xd0\xb5\xd0\xb4\xd1\x83\xd1\x80\xd0\xb0' in data[:500]:
            ext = '.bsl'  # Contains "Процедура"
        elif b'\xd0\xa4\xd1\x83\xd0\xbd\xd0\xba\xd1\x86\xd0\xb8\xd1\x8f' in data[:500]:
            ext = '.bsl'  # Contains "Функция"
        elif b'Procedure' in data[:500] or b'Function' in data[:500]:
            ext = '.bsl'
        elif data[:1] == b'{':
            ext = '.txt'  # 1C metadata descriptor
        
        offset = result.get('offset', i)
        fname = os.path.join(out_dir, f"chunk_{i:03d}_off{offset:#x}{ext}")
        with open(fname, 'wb') as f:
            f.write(data)
        
        # Print preview
        preview = data[:200].decode('utf-8', errors='replace')
        print(f"\n--- chunk_{i:03d}{ext} ({len(data)} bytes) ---")
        print(preview[:300])

def main():
    cfe_files = [f for f in os.listdir(PRRO_DIR) if f.endswith('.cfe')]
    if not cfe_files:
        print("No .cfe files found")
        return
    
    cfe_path = os.path.join(PRRO_DIR, cfe_files[0])
    print(f"Parsing: {cfe_files[0]}")
    print(f"Size: {os.path.getsize(cfe_path)} bytes\n")
    
    data = read_v8_file(cfe_path)
    
    # Method 1: Try structured parsing
    print("=== Method 1: Structured TOC parsing ===")
    pages = extract_v8_container(data)
    
    # Method 2: Brute force deflate scanning
    print("\n=== Method 2: Brute-force deflate scanning ===")
    deflated = try_brute_force_deflate(data)
    print(f"Found {len(deflated)} deflate streams")
    
    # Use whichever method found more
    if len(deflated) > len(pages):
        print(f"\nUsing brute-force results ({len(deflated)} streams)")
        save_results(deflated, OUT_DIR)
    elif pages:
        print(f"\nUsing structured results ({len(pages)} pages)")
        save_results(pages, OUT_DIR)
    else:
        print("\nNo data extracted by either method")
        # Dump raw for manual inspection
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, 'raw.bin'), 'wb') as f:
            f.write(data)
        print("Raw binary saved")

if __name__ == '__main__':
    main()
