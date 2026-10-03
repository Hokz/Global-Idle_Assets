#!/usr/bin/env python3
"""Build Global Idle's searchable reference catalog from an extracted client tree.

Input is development-reference material. Output is metadata only.
Unknown source fields are retained/ignored conservatively, never guessed into gameplay semantics.
"""
from __future__ import annotations
import argparse, bisect, hashlib, json, re
from collections import Counter
from pathlib import Path

KIND={1:"object",2:"outfit",3:"effect",4:"missile"}

def sha256(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def read_varint(data: bytes, i: int):
    v=s=0
    while True:
        b=data[i]; i+=1; v|=(b&127)<<s
        if b<128:return v,i
        s+=7
        if s>70: raise ValueError("invalid varint")

def wire_fields(data: bytes):
    i=0
    while i<len(data):
        key,i=read_varint(data,i); field=key>>3; wt=key&7
        if wt==0: value,i=read_varint(data,i)
        elif wt==1: value=data[i:i+8]; i+=8
        elif wt==2:
            n,i=read_varint(data,i); value=data[i:i+n]; i+=n
        elif wt==5: value=data[i:i+4]; i+=4
        else: raise ValueError(f"unsupported wire type {wt} at field {field}")
        yield field,wt,value

def one_varint(fields, num, default=None):
    for f,w,v in fields:
        if f==num and w==0:return v
    return default

def parse_catalog_content(path: Path):
    rows=json.loads(path.read_text(encoding="utf-8"))
    sprite=[r for r in rows if r.get("type")=="sprite"]
    sprite.sort(key=lambda r:int(r["firstspriteid"]))
    starts=[int(r["firstspriteid"]) for r in sprite]
    return rows,sprite,starts

def sheet_for(sprite_id:int, sprite, starts):
    j=bisect.bisect_right(starts,sprite_id)-1
    if j<0:return None
    r=sprite[j]
    if sprite_id>int(r["lastspriteid"]):return None
    return {
      "file":r["file"],"spriteType":r.get("spritetype"),
      "firstSpriteId":r["firstspriteid"],"lastSpriteId":r["lastspriteid"],
      "area":r.get("area")
    }

def parse_sprite_info(blob: bytes, sprite, starts):
    fs=list(wire_fields(blob))
    vals={n:[v for f,w,v in fs if f==n and w==0] for n in range(1,9)}
    ids=vals[5]
    return {
      "patternWidth": vals[1][0] if vals[1] else None,
      "patternHeight": vals[2][0] if vals[2] else None,
      "patternDepth": vals[3][0] if vals[3] else None,
      "layers": vals[4][0] if vals[4] else None,
      "spriteIds": ids,
      "boundingSquare": vals[7][0] if vals[7] else None,
      "sourceSheets": [sheet_for(x,sprite,starts) for x in ids],
      "hasAnimationMetadata": any(f==6 for f,_,_ in fs),
      "boundingBoxCount": sum(1 for f,w,_ in fs if f==9 and w==2)
    }

def parse_appearances(path: Path, sprite, starts):
    top=list(wire_fields(path.read_bytes()))
    result=[]
    counts=Counter()
    for tf,tw,msg in top:
        if tf not in KIND or tw!=2: continue
        af=list(wire_fields(msg)); aid=one_varint(af,1)
        name=None
        for f,w,v in af:
            if f==4 and w==2:
                try:name=v.decode("utf-8")
                except UnicodeDecodeError:name=None
                break
        groups=[]
        for f,w,g in af:
            if f!=2 or w!=2:continue
            gf=list(wire_fields(g)); info=None
            for sf,sw,sv in gf:
                if sf==3 and sw==2: info=parse_sprite_info(sv,sprite,starts); break
            groups.append({
              "sourceCategory":one_varint(gf,1),
              "frameGroupId":one_varint(gf,2),
              "spriteInfo":info
            })
        result.append({
          "appearanceClass":KIND[tf],"appearanceId":aid,"name":name,
          "frameGroups":groups,
          "flagsPayloadPresent":any(f==3 and w==2 for f,w,_ in af)
        })
        counts[KIND[tf]]+=1
    return result,dict(counts)

MM=re.compile(r"Minimap_(Color|WaypointCost)_(-?\d+)_(-?\d+)_(-?\d+)\.png$",re.I)
def minimap_index(root:Path):
    out=[]
    for p in sorted((root/"minimap").glob("*.png")):
        m=MM.match(p.name)
        if not m:continue
        out.append({"kind":m.group(1),"x":int(m.group(2)),"y":int(m.group(3)),"z":int(m.group(4)),"file":p.name})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("--out",type=Path,default=Path("indexes/generated"))
    ap.add_argument("--hash-files",action="store_true")
    a=ap.parse_args(); root=a.source.resolve(); out=a.out; out.mkdir(parents=True,exist_ok=True)

    cat_path=root/"assets"/"catalog-content.json"
    rows,sprite,starts=parse_catalog_content(cat_path)
    app_path=next((root/"assets").glob("appearances-*.dat"))
    appearances,counts=parse_appearances(app_path,sprite,starts)
    mini=minimap_index(root)

    inv=[]
    category_counts=Counter(); ext_counts=Counter(); total=0
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        rel=p.relative_to(root).as_posix(); size=p.stat().st_size; total+=size
        top=rel.split("/",1)[0]; category_counts[top]+=1; ext_counts[p.suffix.lower() or "<none>"]+=1
        rec={"path":rel,"bytes":size}
        if a.hash_files:rec["sha256"]=sha256(p)
        inv.append(rec)

    (out/"appearances.json").write_text(json.dumps(appearances,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    (out/"sprite-sheets.json").write_text(json.dumps(sprite,separators=(",",":")),encoding="utf-8")
    (out/"minimap-sectors.json").write_text(json.dumps(mini,separators=(",",":")),encoding="utf-8")
    (out/"source-files.json").write_text(json.dumps(inv,separators=(",",":")),encoding="utf-8")
    summary={
      "schemaVersion":1,"appearanceCounts":counts,"spriteSheetCount":len(sprite),
      "minimapSectorFiles":len(mini),"sourceFileCount":len(inv),"sourceBytes":total,
      "topLevelCounts":dict(category_counts),"extensionCounts":dict(ext_counts)
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
