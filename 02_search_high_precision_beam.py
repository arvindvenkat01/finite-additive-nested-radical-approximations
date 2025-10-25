# MIT License
# Copyright (c) 2025 Arvind N. Venkat
# Permission is hereby granted, free of charge...

# Colab-ready: finite nested radical search for pi, e, phi
# !pip install mpmath numba  # numba not required; mpmath for high precision

from mpmath import mp
import csv

# --- Precision (raise to 200–300 for deeper/wider searches) ---
mp.dps = 150  # working decimal precision for evaluation and scoring

# --- Target constants ---
def target_const(name):
    nm = name.lower()
    if nm == 'pi':
        return +mp.pi
    if nm == 'e':
        return +mp.e
    if nm in ('phi','φ'):
        return (1 + mp.sqrt(5)) / 2
    raise ValueError('Unknown target name: ' + name)

# --- Evaluate R_k(a1,...,ak) = sqrt(a1 + sqrt(a2 + ... + sqrt(ak))) ---
def eval_nested_mp(coeffs):
    v = mp.mpf('0')
    for a in reversed(coeffs):
        v = mp.sqrt(v + a)
    return v

# --- Matched-digit counter at current mp.dps ---
def matched_digits(x, y):
    sx = mp.nstr(x, mp.dps)
    sy = mp.nstr(y, mp.dps)
    c = 0
    for chx, chy in zip(sx, sy):
        if chx != chy:
            break
        if chx.isdigit():
            c += 1
    return c

# --- Backward-squaring beam search ---
# y1 = t^2 - a1 >= 0, y2 = y1^2 - a2 >= 0, ..., ak = round(y_{k-1}^2)
def search_backward_beam(t, depth, offsets, beam=30, a_min=0, a_max=None):
    assert len(offsets) == depth - 1
    # State = (coeffs_list, y_value_mp, score)
    level_states = [ ([], +t, mp.inf) ]
    for lvl in range(1, depth):
        window = int(offsets[lvl-1])
        next_states = []
        for coeffs, y, _ in level_states:
            base = int(mp.floor(y*y))
            start = max(a_min, base - window)
            end = base + window
            for a in range(start, end+1):
                if a_max is not None and a > a_max:
                    break
                y_next = y*y - a
                if y_next < 0:
                    break
                # Provisional completion via greedy ak for scoring
                ak = int(mp.nint(y_next*y_next))
                full = coeffs + [a, ak] if lvl == depth-1 else coeffs + [a]
                val = eval_nested_mp(full)
                err = abs(val - t)
                if lvl == depth-1:
                    next_states.append((full[:-1] + [ak], y_next, err))
                else:
                    next_states.append((coeffs + [a], y_next, err))
        next_states.sort(key=lambda s: s[2])
        level_states = next_states[:beam]
    # Best complete tuple
    best = min(level_states, key=lambda s: s[2])
    coeffs, _, _ = best
    approx = eval_nested_mp(coeffs)
    abs_err = abs(approx - t)
    return coeffs, approx, abs_err

# --- Batch runner with CSV output ---
def run_suite(names=('pi','e','phi'), depths=(3,4,5,6),
              offset_schedules=None, beam=30, mp_digits=150,
              csvfile='nested_beam_results.csv'):
    if offset_schedules is None:
        offset_schedules = {3:[40,60], 4:[40,60,80], 5:[40,60,80,100], 6:[40,60,80,100,120]}
    mp.dps = mp_digits
    rows = []
    for nm in names:
        t = target_const(nm)
        for d in depths:
            offs = offset_schedules[d]
            coeffs, approx, err = search_backward_beam(t, d, offs, beam=beam)
            md = matched_digits(approx, t)
            rows.append({'target': nm, 'depth': d,
                         'coeffs': ' '.join(map(str, coeffs)),
                         'approx': mp.nstr(approx, 60),
                         'abs_error': mp.nstr(err, 20),
                         'matched_digits': str(md),
                         'mp_dps': str(mp.dps)})
            print(nm, d, coeffs, 'err=', err, 'matched_digits=', md)
    with open(csvfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['target','depth','coeffs','approx','abs_error','matched_digits','mp_dps'])
        writer.writeheader()
        writer.writerows(rows)
    print('Wrote', csvfile)
    return rows, csvfile

# Example run (adjust as desired):
# rows, fname = run_suite(names=('pi','e','phi'), depths=(3,4,5,6), beam=30, mp_digits=200)

"""
######################### OUTPUT #########################
pi 3 [1, 44, 1202] err= 0.00000009496882140855246708226537032772204181847493096084112260448370285141062065108868590367152860235876356378997528650132611840953192758349934300670429436669712642590921720252487793124875416091003213247011 matched_digits= 7
pi 4 [3, 44, 2, 67] err= 0.00000017004457116873774449526761688863410077165483313932844078431993738173690001959204902068651635839128194376700228100575061817863271574453310898521296190563042224514808243097008217931929442431643610398771 matched_digits= 7
pi 5 [0, 92, 26, 3, 58] err= 0.000000059818421137117843152481222599568515073184774872763190221238359307937949155983359353291039090462830654672709575012652767821226333152021180517642148724211533906383344986755325072776163060846565296195 matched_digits= 7
pi 6 [0, 92, 26, 7, 0, 171] err= 0.000000014244448308423326395391453823851954494059071583194092284226538326572473661632124595628841399844672550542238996644037752084777753957120281020416377605159789285305545948944191505517109089779868974080617 matched_digits= 8
e 3 [0, 10, 1989] err= 0.00000069961771239100452731423189349813293811825912446623246803712407802150366236719114817942078261547981917193720464181830473037289097212476695717962597735477594126327213086781336123734282060420199562004102 matched_digits= 6
e 4 [0, 48, 33, 111] err= 0.000000065923111129909828843148218254586864560530682166425809463896873681312475509068337879037320944281524060055365581914042966007555047319244702009319599090828250299771401061508509874660748119007247828890828 matched_digits= 8
e 5 [0, 49, 29, 1, 20] err= 0.000000026781905877027353226114570319705227155386610793607536225168709726713219314553543013609760809066543745169947471788556723333772342801600683704243537939083542480104942674120257282432430454964023321978825 matched_digits= 8
e 6 [0, 49, 29, 2, 3, 82] err= 0.000000038516939424907854722820625922168336647216000616923012452516277433100841619790033361086275661138036487821414212596129516673420992174771526176908201350709520697629822137078201498464772556242968568266788 matched_digits= 7
phi 3 [0, 0, 47] err= 0.000091624018126766739957636566174495250429060131422318939739050693322004401085570758459152454421087359351825996557956865959242557318275785014394255967465022018498129903957296727022344939429088111434522089 matched_digits= 4
phi 4 [0, 0, 0, 2207] err= 0.000000020761710348286718616497161209305670554049120405616588389557264955081723555124685114021955749435793829713559933327113593923607236376095080197548711652181606562228586221790733503206755639515354717535051 matched_digits= 6
phi 5 [0, 0, 40, 27, 471] err= 0.000000027334574704366792910564673479749794664103321642492143384817665647504673694376157709370271594886347728263572315711637705681710397291992171757100985192660964727572809345094565813813366218006971963963252 matched_digits= 6
phi 6 [0, 1, 29, 26, 0, 10] err= 0.0000000026438165810915738245726541662881575523947729815206656307830701062985812055272561584441763143816286336676288960492538243800768718040551743994127596515030282670098596900735932855020171762958486882602645 matched_digits= 8
#Wrote nested_beam_results.csv
"""
