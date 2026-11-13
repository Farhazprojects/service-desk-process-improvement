"""Build Tableau packaged workbooks (.twbx) from pandas DataFrames.

Tableau Public only opens workbooks whose data sources are extracts, so each
DataFrame is written to a .hyper extract with Tableau's Hyper API and the
workbook XML points at that file inside the package.
"""
import uuid
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr as q

import pandas as pd
from tableauhyperapi import (Connection, CreateMode, HyperProcess, Inserter, NULLABLE,
                             SqlType, TableDefinition, TableName, Telemetry)

SID = lambda: "<simple-id uuid='{%s}' />" % str(uuid.uuid4()).upper()
CARDS = ("<cards><edge name='left'><strip size='160'><card type='pages' /><card type='filters' />"
         "<card type='marks' /></strip></edge><edge name='top'><strip size='2147483647'>"
         "<card type='columns' /></strip><strip size='2147483647'><card type='rows' /></strip>"
         "<strip size='2147483647'><card type='title' /></strip></edge></cards>")
DER = {"none": "None", "sum": "Sum", "avg": "Avg", "cnt": "Count", "ctd": "CountD",
       "med": "Median", "usr": "User", "min": "Min", "max": "Max"}
FMT = {"pct": "p0.0%", "usd": 'c"$"#,##0;-"$"#,##0', "int": "n#,##0", "dec1": "n#,##0.0", "dec2": "n#,##0.00"}


def write_hyper(df, path, hp):
    cols = []
    for c in df.columns:
        k = str(df[c].dtype)
        t = (SqlType.big_int() if k.startswith("int") else SqlType.double() if k.startswith("float")
             else SqlType.date() if k == "object" and hasattr(df[c].dropna().iloc[0], "year") else SqlType.text())
        cols.append(TableDefinition.Column(c, t, NULLABLE))
    td = TableDefinition(TableName("Extract", "Extract"), cols)
    rows = [[None if v != v or v is None else (v.item() if hasattr(v, "item") else v) for v in r]
            for r in df.itertuples(index=False, name=None)]
    with Connection(hp.endpoint, str(path), CreateMode.CREATE_AND_REPLACE) as con:
        con.catalog.create_schema("Extract")
        con.catalog.create_table(td)
        with Inserter(con, td) as ins:
            ins.add_rows(rows)
            ins.execute()


class DS:
    """One data source: a DataFrame plus calculated fields."""

    def __init__(self, key, caption, df, dims=(), formats=None, captions=None, palette=None):
        self.palette = palette or {}
        self.key, self.name, self.caption, self.df = key, f"federated.{key}", caption, df
        self.cols = {}
        for c in df.columns:
            k = str(df[c].dtype)
            dt = "integer" if k.startswith("int") else "real" if k.startswith("float") else \
                 "date" if hasattr(df[c].dropna().iloc[0], "year") else "string"
            role = "dimension" if dt in ("string", "date") or c in dims else "measure"
            self.cols[c] = (dt, role, (captions or {}).get(c, c.replace("_", " ").capitalize()),
                            FMT.get((formats or {}).get(c)))
        self.calcs = {}

    def calc(self, cid, caption, formula, fmt=None, datatype="real", role="measure"):
        self.calcs[cid] = (datatype, role, caption, FMT.get(fmt), formula)
        return self

    def coldef(self, c):
        if c in self.cols:
            dt, role, cap, fm = self.cols[c]; body = " />"
        else:
            dt, role, cap, fm, f = self.calcs[c]
            body = f"><calculation class='tableau' formula={q(f)} /></column>"
        typ = "quantitative" if role == "measure" else "ordinal" if dt in ("integer", "date") else "nominal"
        fm = f" default-format={q(fm)}" if fm else ""
        return f"<column caption={q(cap)} datatype='{dt}'{fm} name={q('[' + c + ']')} role='{role}' type='{typ}'{body}"

    def xml(self):
        conn = f"hyper.{self.key}"
        return (f"<datasource caption={q(self.caption)} inline='true' name={q(self.name)} version='18.1'>"
                "<connection class='federated'><named-connections>"
                f"<named-connection caption={q(self.key)} name={q(conn)}>"
                "<connection access_mode='readonly' authentication='auth-none' author-locale='en_AU' class='hyper' "
                f"dbname='Data/Extracts/{self.key}.hyper' default-settings='yes' sslmode='' username='tableau_internal_user' />"
                "</named-connection></named-connections>"
                f"<relation connection={q(conn)} name='Extract' table='[Extract].[Extract]' type='table' />"
                "</connection><aliases enabled='yes' />"
                + "".join(self.coldef(c) for c in list(self.cols) + list(self.calcs)) + self._style() + "</datasource>")

    def _style(self):
        if not self.palette:
            return ""
        enc = ""
        for field, mp in self.palette.items():
            maps = "".join(f"<map to='{col}'><bucket>{escape(chr(34) + val + chr(34))}</bucket></map>" for val, col in mp.items())
            enc += f"<encoding attr='color' field={q('[none:' + field + ':nk]')} type='palette'>{maps}</encoding>"
        return f"<style><style-rule element='mark'>{enc}</style-rule></style>"


def _inst(spec, ds, compute=None):
    d, col, tp = spec.split(":")[:3]
    typ = {"qk": "quantitative", "nk": "nominal", "ok": "ordinal"}[tp]
    tc = ""
    if compute:
        tc = f"<table-calc ordering-field={q(f'[{ds.name}].[{compute}]')} ordering-type='Field' />"
    return (f"<column-instance column={q('[' + col + ']')} derivation='{DER[d]}' name={q('[' + spec + ']')} "
            f"pivot='key' type='{typ}'>{tc}</column-instance>")


def sheet(ds, name, rows=(), cols=(), mark="Automatic", color=None, text=None, lod=(), filters=(),
          sort=None, title=None, big=None, compute=None, refline=None, label=False, mark_color=None):
    """compute: {instance_spec: field_spec} for table calculations.
    big: instance to show as a large KPI number. refline: (instance, value, label)."""
    used = list(rows) + list(cols) + [x for x in (color, text, big) if x] + list(lod) + [f[0] for f in filters]
    if sort:
        used.append(sort[1])
    if label and not text:
        text = [x for x in list(cols) + list(rows) if x.endswith(':qk')][-1]
    used = list(dict.fromkeys(used + ([text] if text else [])))
    ref = lambda s: f"[{ds.name}].[{s}]"
    compute = compute or {}
    for v in compute.values():
        if v not in used:
            used.append(v)
    names = list(dict.fromkeys(s.split(":")[1] for s in used))
    # A calculation that uses another calculation needs both declared.
    for c in list(names):
        if c in ds.calcs:
            for other in ds.calcs:
                if f"[{other}]" in ds.calcs[c][4] and other not in names:
                    names.append(other)
    deps = "".join(ds.coldef(c) for c in names) + "".join(_inst(s, ds, compute.get(s)) for s in used)
    pdep, pds = "", ""
    used_params = [p for p in PARAM_COLS if any(f"[Parameters].[{p}]" in ds.calcs[c][4] for c in names if c in ds.calcs)]
    if used_params:
        pds = "<datasource name='Parameters' />"
        pdep = ("<datasource-dependencies datasource='Parameters'>" + "".join(PARAM_COLS[p] for p in used_params)
                + "</datasource-dependencies>")
    fx = ""
    for spec, members in filters:
        mem = "".join(f"<groupfilter function='member' level={q('[' + spec + ']')} member={q(chr(34) + m + chr(34))} />"
                      for m in members)
        if len(members) > 1:
            mem = f"<groupfilter function='union' user:ui-enumeration='inclusive' user:ui-marker='enumerate'>{mem}</groupfilter>"
        else:
            mem = mem.replace(" />", " user:ui-enumeration='inclusive' user:ui-marker='enumerate' />")
        fx += f"<filter class='categorical' column={q(ref(spec))}>{mem}</filter>"
    srt = f"<computed-sort column={q(ref(sort[0]))} direction='{sort[2]}' using={q(ref(sort[1]))} />" if sort else ""
    enc = ""
    if color: enc += f"<color column={q(ref(color))} />"
    if text or big: enc += f"<text column={q(ref(text or big))} />"
    for l in lod: enc += f"<lod column={q(ref(l))} />"
    enc = f"<encodings>{enc}</encodings>" if enc else ""
    cl = ""
    if big:
        cl = (f"<customized-label><formatted-text><run bold='true' fontsize='20'>{escape('<' + ref(big) + '>')}</run>"
              "</formatted-text></customized-label>")
        mark = "Text"
    st = ""
    rules = []
    if (text and mark != "Text"):
        rules.append("<format attr='mark-labels-show' value='true' />")
    if mark_color:
        rules.append(f"<format attr='mark-color' value='{mark_color}' />")
    if big:
        st = ("<style><style-rule element='cell'><format attr='font-size' value='22' /><format attr='font-weight' value='bold' />"
              "<format attr='text-align' value='center' /><format attr='vertical-align' value='center' /></style-rule></style>")
    elif rules:
        st = f"<style><style-rule element='mark'>{''.join(rules)}</style-rule></style>"
    rl = ""
    if refline:
        rl = (f"<reference-line axis-column={q(ref(refline[0]))} enable-instant-analytics='true' formula='constant' "
              f"id='refline{uuid.uuid4().hex[:6]}' label={q(refline[2])} label-type='custom' scope='per-table' value='{refline[1]}' "
              f"value-column={q(ref(refline[0]))} z-order='1' />")
    ttl = (f"<layout-options><title><formatted-text><run bold='true' fontsize='11'>{escape(title or name)}</run>"
           "</formatted-text></title></layout-options>")
    shelf = lambda xs: " / ".join(ref(x) for x in xs)
    return name, f"""<worksheet name={q(name)}>{ttl}
<table><view><datasources><datasource caption={q(ds.caption)} name={q(ds.name)} />{pds}</datasources>
<datasource-dependencies datasource={q(ds.name)}>{deps}</datasource-dependencies>{pdep}
{fx}{srt}<aggregation value='true' /></view><style />
<panes><pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view>
<mark class='{mark}' />{enc}{rl}{cl}{st}</pane></panes>
<rows>{shelf(rows)}</rows><cols>{shelf(cols)}</cols></table>{SID()}</worksheet>"""


_z = [20]
def _zid():
    _z[0] += 1
    return _z[0]


def dashboard(name, title, grid, params=(), w=1300, h=820, subtitle=""):
    """grid: (sheet name, x, y, w, h) in pixels. params: (param name, x, y, w, h)."""
    sx, sy = 100000 / w, 100000 / h
    box = lambda x, y, ww, hh: f"h='{int(hh * sy)}' w='{int(ww * sx)}' x='{int(x * sx)}' y='{int(y * sy)}'"
    z = [f"<zone h='100000' id='{_zid()}' type-v2='layout-basic' w='100000' x='0' y='0'>",
         f"<zone {box(0, 0, w, 56)} id='{_zid()}' type-v2='title' />"]
    for sn, x, y, ww, hh in grid:
        z.append(f"<zone {box(x, y, ww, hh)} id='{_zid()}' name={q(sn)}><zone-style>"
                 "<format attr='border-color' value='#d9d9d9' /><format attr='border-style' value='solid' />"
                 "<format attr='border-width' value='1' /><format attr='margin' value='4' /></zone-style></zone>")
    for pn, x, y, ww, hh in params:
        z.append(f"<zone {box(x, y, ww, hh)} id='{_zid()}' mode='slider' param={q('[Parameters].[' + pn + ']')} type-v2='paramctrl' />")
    z.append("</zone>")
    run2 = f"<run fontsize='10' fontcolor='#666666'>{escape(chr(10) + subtitle)}</run>" if subtitle else ""
    xml = (f"<dashboard name={q(name)}><layout-options><title><formatted-text><run bold='true' fontsize='16'>"
           f"{escape(title)}</run>{run2}</formatted-text></title></layout-options><style />"
           f"<size maxheight='{h}' maxwidth='{w}' minheight='{h}' minwidth='{w}' sizing-mode='fixed' />"
           f"<datasources /><zones>{''.join(z)}</zones>{SID()}</dashboard>")
    return name, xml, [g[0] for g in grid]


PARAM_COLS = {}
def parameters(plist):
    """plist: (name, caption, datatype, value, min, max, step, format key)"""
    cols = ""
    for n, cap, dt, val, lo, hi, step, fm in plist:
        f = f" default-format={q(FMT[fm])}" if fm else ""
        PARAM_COLS[n] = (f"<column caption={q(cap)} datatype='{dt}'{f} name={q('[' + n + ']')} param-domain-type='range' "
                         f"role='measure' type='quantitative' value='{val}'><calculation class='tableau' formula='{val}' />"
                         f"<range granularity='{step}' max='{hi}' min='{lo}' /></column>")
        cols += PARAM_COLS[n]
    return f"<datasource hasconnection='false' inline='true' name='Parameters' version='18.1'><aliases enabled='yes' />{cols}</datasource>"


def declare_parameters(plist):
    parameters(plist)
    return plist


def actions_xml(acts):
    """acts: (caption, dashboard, source sheet)"""
    out = ""
    for i, (cap, dash, src) in enumerate(acts, 1):
        out += (f"<action caption={q(cap)} name='[Action{i}]'><activation auto-clear='true' type='on-select' />"
                f"<source dashboard={q(dash)} type='sheet' worksheet={q(src)} />"
                f"<command command='tsc:tsl-filter'><param name='exclude' value={q(src)} />"
                f"<param name='special-fields' value='all' /><param name='target' value={q(dash)} /></command></action>")
    return f"<actions>{out}</actions>" if out else ""


def build(path, dss, sheets, dashes, params=None, acts=()):
    path = Path(path)
    win = "".join(f"<window class='worksheet' hidden='true' name={q(n)}>{CARDS}{SID()}</window>" for n, _ in sheets)
    for i, (dn, _, used) in enumerate(dashes):
        vp = "".join(f"<viewpoint name={q(u)}><zoom type='entire-view' /></viewpoint>" for u in used)
        win += (f"<window class='dashboard'{' maximized=' + chr(39) + 'true' + chr(39) if i == 0 else ''} name={q(dn)}>"
                f"<viewpoints>{vp}</viewpoints><active id='-1' />{SID()}</window>")
    twb = f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook original-version='18.1' source-build='2026.2.0 (20262.26.0528.2205)' source-platform='mac' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
<document-format-change-manifest><SheetIdentifierTracking /><SortTagCleanup /><WindowsPersistSimpleIdentifiers /></document-format-change-manifest>
<preferences />
<datasources>{parameters(params) if params else ''}{''.join(d.xml() for d in dss)}</datasources>
{actions_xml(acts)}
<worksheets>{''.join(x for _, x in sheets)}</worksheets>
<dashboards>{''.join(x for _, x, _ in dashes)}</dashboards>
<windows>{win}</windows>
</workbook>"""
    tmp = path.parent / "_build"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / (path.stem + ".twb")).write_text(twb)
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        for d in dss:
            write_hyper(d.df, tmp / f"{d.key}.hyper", hp)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(tmp / (path.stem + ".twb"), path.stem + ".twb")
        for d in dss:
            z.write(tmp / f"{d.key}.hyper", f"Data/Extracts/{d.key}.hyper")
    return tmp / (path.stem + ".twb")
