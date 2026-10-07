"""Reproduce the frozen-universe selection and comparison figures."""
from pathlib import Path
import json
import hashlib
import os
import tempfile
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'fe5108-matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / 'artifacts/inputs'
RESULTS = ROOT / 'artifacts/results'
FIGURES = ROOT / 'artifacts/figures'



def centrality_scores(vectors):
    """Mean cosine distance to every OTHER member; no eligibility filtering here."""
    x = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(x, axis=1)
    if len(x) < 2 or not np.isfinite(x).all() or np.any(norms == 0):
        raise ValueError('Need at least two finite nonzero vectors.')
    x = x / norms[:, None]
    distance = np.clip(1 - x @ x.T, 0, 2)
    np.fill_diagonal(distance, 0)
    return distance.sum(axis=1) / (len(x) - 1)


def select_representatives(ranked):
    """Largest formation cap among complete-history members; no centrality cutoff."""
    valid = ranked.loc[ranked.eligible_108 & ranked.identity_match & ranked.market_cap_usd_raw.gt(0)]
    candidates = valid.sort_values(['cluster_label','market_cap_usd_raw','cik'], ascending=[True,False,True]).groupby('cluster_label', sort=True).head(1).copy()
    candidates['retained'] = True
    return candidates


def verify_filing_timing():
    d = pd.read_csv(INPUTS / 'filing_timing_2024.csv', dtype={'cik': str})
    available = pd.to_datetime(d.available_after, utc=True)
    formation = pd.to_datetime(d.formation_at, utc=True)
    if len(d) != 1910 or d.cik.duplicated().any() or available.isna().any() or not available.le(formation).all():
        raise ValueError('Formation filing timing validation failed.')
    return {'issuers': len(d), 'latest_available_after': str(available.max()),
            'availability_rule': 'SEC acceptance timestamp plus one calendar day',
            'scope': 'Filing eligibility at formation only; not a point-in-time 2017-2025 investment universe.'}


def build_selection():
    labels = pd.read_parquet(INPUTS / 'tfidf_umap_leiden_assignments.parquet')
    a = labels[labels.formation.eq('2024-12-31')]
    partitions = {int(seed): g.set_index('cik').sort_index() for seed, g in a.groupby('seed')}
    seed_scores = []
    for seed, p in partitions.items():
        scores = []
        for other, q in partitions.items():
            if other == seed:
                continue
            if not p.index.equals(q.index):
                raise ValueError('Seed cohorts differ.')
            scores.append(adjusted_rand_score(p.cluster_label, q.cluster_label))
        seed_scores.append({'seed': seed, 'mean_ari_with_other_seeds': np.mean(scores)})
    seed_table = pd.DataFrame(seed_scores).sort_values(['mean_ari_with_other_seeds','seed'], ascending=[False,True])
    seed = int(seed_table.iloc[0].seed)
    if seed != 20260831:
        raise ValueError('Frozen representative seed changed.')
    a = partitions[seed].reset_index()
    metadata = pd.read_csv(INPUTS / 'company_metadata_and_coverage_2024.csv', dtype={'cik':str})
    d = a.merge(metadata, on=['cik','ticker','security_id','accession'], validate='one_to_one')
    if len(d) != 1910:
        raise ValueError('Incomplete metadata join.')
    z = np.load(INPUTS / 'tfidf_fused_vectors_2024_seed20260831.npz', allow_pickle=False)
    vectors = dict(zip(z['tickers'], z['vectors']))
    if set(vectors) != set(d.ticker):
        raise ValueError('Vector alignment failure.')
    pieces = []
    for _, g in d.groupby('cluster_label'):
        g = g.copy()
        g['mean_within_cosine_distance'] = centrality_scores(np.stack([vectors[t] for t in g.ticker]))
        g = g.sort_values(['mean_within_cosine_distance','cik'])
        g['centrality_rank'] = np.arange(1, len(g)+1)
        pieces.append(g)
    ranked = pd.concat(pieces, ignore_index=True)
    caps = pd.read_csv(INPUTS / 'formation_market_caps_2024.csv', dtype={'cik': str,'returned_cik': str})
    assert len(caps)==1910 and caps.security_id.is_unique and caps.formation.eq('2024-12-31').all()
    ranked = ranked.merge(caps[['security_id','market_cap_usd_raw','identity_match','quality_flags']], on='security_id', validate='one_to_one')
    assert ranked.identity_match.all() and ranked.market_cap_usd_raw.gt(0).all()
    ranked = ranked.sort_values(['cluster_label','market_cap_usd_raw','cik'],ascending=[True,False,True])
    ranked['market_cap_rank'] = ranked.groupby('cluster_label').cumcount()+1
    candidates = select_representatives(ranked)
    selected = candidates[candidates.retained].sort_values('cluster_label')
    if len(candidates) != 30 or len(selected) != 30 or not selected.complete_months.eq(108).all():
        raise ValueError('Frozen universe did not reproduce.')
    ranked.to_csv(RESULTS / 'all_company_rankings_2024.csv', index=False)
    candidates.to_csv(RESULTS / 'candidates_30.csv', index=False)
    selected.to_csv(RESULTS / 'selected_universe.csv', index=False)
    seed_table.to_csv(RESULTS / 'representative_seed.csv', index=False)
    (RESULTS / 'selected_tickers.json').write_text(json.dumps(selected.ticker.tolist(), indent=2)+'\n')
    return ranked, selected


def verify_daily(root, ranked):
    """Optional local-only replay of strict monthly coverage, without uploading returns."""
    import pyarrow.parquet as pq
    chunks = []
    paths = sorted(Path(root).glob('data/**/returns.parquet'))
    if len(paths) != 9:
        raise ValueError('Expected nine annual return files under --daily-root/data.')
    for p in paths:
        a = pq.ParquetFile(p).read(columns=['date','security_id','window','return']).to_pandas()
        a = a[a.window.eq('evaluation')].copy()
        a['month'] = pd.to_datetime(a.date).dt.to_period('M')
        expected = a.groupby('month').date.nunique()
        a = a[a.security_id.isin(ranked.security_id)]
        if a.duplicated(['security_id','date']).any():
            raise ValueError('Duplicate daily observations.')
        a['finite'] = np.isfinite(a['return'])
        g = a.groupby(['security_id','month']).agg(n=('date','nunique'),valid=('finite','sum'))
        g['expected'] = g.index.get_level_values('month').map(expected)
        g['complete'] = g.n.eq(g.expected) & g.valid.eq(g.expected)
        chunks.append(g.reset_index())
    g = pd.concat(chunks)
    if g.duplicated(['security_id','month']).any():
        raise ValueError('Overlapping annual evaluation windows.')
    wide = g.pivot(index='security_id', columns='month', values='complete').reindex(
        columns=pd.period_range('2017-01','2025-12',freq='M')).fillna(False).astype(bool)
    counts = wide.sum(axis=1)
    actual = ranked.security_id.map(counts).fillna(0).astype(int)
    if not np.array_equal(actual.to_numpy(), ranked.complete_months.to_numpy()):
        raise ValueError('Local raw-panel coverage differs from frozen coverage.')
    return {'annual_files': len(paths), 'companies_checked': len(ranked), 'coverage_matches': True}


def save(fig, name):
    fig.savefig(FIGURES / f'{name}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)


def figures():
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
    d = pd.read_csv(INPUTS / 'section_comparison_2024.csv')
    fig, axes = plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    enc = ['TF-IDF/SVD','E5','Nomic'];x=np.arange(3)
    for ax, metric, title in zip(axes,['rho_gap','chi10_empirical_gap'],['Pearson correlation gap','Empirical lower-tail chi(0.10) gap']):
        for shift, arm, color in [(-.18,'Item 1A','#94a3b8'),(.18,'Four sections','#2563eb')]:
            vals=d[d.text_arm.eq(arm)].set_index('representation').loc[enc,metric]
            ax.bar(x+shift,vals,width=.34,label=arm,color=color)
        ax.set_xticks(x,enc);ax.set_title(title);ax.set_ylabel('Within minus across');ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Multi-section gains depend on the representation\nEnd-2024 formation / 2025 evaluation; KMeans, 48 groups')
    save(fig,'01_single_vs_multi_section')
    k=pd.read_csv(INPUTS / 'kmeans48_multiyear.csv');l=pd.read_csv(INPUTS / 'leiden_multiyear.csv')
    styles=[('Lexical: Original + KMeans48','TF-IDF/SVD: original','#1d4ed8','-'),('Lexical: UMAP3 + KMeans48','TF-IDF/SVD: UMAP3','#06b6d4','-'),('E5: UMAP3 + KMeans48','E5: UMAP3','#d97706','-'),('Nomic: UMAP3 + KMeans48','Nomic: UMAP3','#8b5cf6','-'),('FF48','FF48','#111827','--'),('Historical returns (48)','Historical returns: 48','#6b7280',':')]
    fig,axes=plt.subplots(1,2,figsize=(12,5.1),layout='constrained')
    for ax,metric,title in zip(axes,['rho','chi10_empirical'],['Pearson gap','Empirical lower-tail chi(0.10) gap']):
        for method,label,color,ls in styles:
            q=k[k.method.eq(method)&k.metric.eq(metric)].sort_values('evaluation_year');ax.plot(q.evaluation_year,q.gap,marker='o',markersize=3,label=label,color=color,linestyle=ls)
        ax.set_title(title);ax.set_xlabel('Evaluation year');ax.set_ylabel('Within minus across');ax.grid(alpha=.2)
    axes[1].legend(fontsize=8,loc='upper left',frameon=False)
    fig.suptitle('Matched 48-group comparisons: lexical features outperform FF48\nFive-seed means; historical control unavailable for 2019')
    save(fig,'02_matched48_multiyear')
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for model,label,color in [('tfidf-svd','TF-IDF/SVD','#1d4ed8'),('e5','E5','#d97706'),('nomic','Nomic','#8b5cf6')]:
        q=l[l.model.eq(model)&l.route.eq('umap')].sort_values('evaluation_year')
        axes[0].plot(q.evaluation_year,q.gap,marker='o',label=label+' + UMAP3 + Leiden',color=color)
        axes[1].plot(q.evaluation_year,(q.groups_min+q.groups_max)/2,marker='o',color=color,label=label)
        axes[1].fill_between(q.evaluation_year,q.groups_min,q.groups_max,color=color,alpha=.13)
    q=l[l.model.eq('tfidf-svd')&l.route.eq('original')].sort_values('evaluation_year');axes[0].plot(q.evaluation_year,q.gap,color='#06b6d4',marker='.',label='TF-IDF/SVD + direct Leiden')
    for name,color,ls in [('FF48','#111827','--'),('Historical returns (48)','#6b7280',':')]:
        q=k[k.method.eq(name)&k.metric.eq('rho')].sort_values('evaluation_year');axes[0].plot(q.evaluation_year,q.gap,color=color,linestyle=ls,label=name)
    axes[0].set_ylabel('Pearson within-minus-across gap');axes[0].legend(fontsize=7.5,frameon=False)
    axes[1].set_ylabel('Native Leiden groups: midpoint and seed range');axes[1].legend(frameon=False,fontsize=8)
    for ax in axes:ax.set_xlabel('Evaluation year');ax.grid(alpha=.2)
    fig.suptitle('TF-IDF/SVD + UMAP3 leads the nine Leiden routes in all seven years\nNative group counts differ; this is not a matched-count superiority test')
    save(fig,'03_native_leiden_multiyear')
    stats=[]
    for metric in ['rho','chi10_empirical']:
        p=k[k.metric.eq(metric)].pivot(index='formation',columns='method',values='gap')
        for method in ['Lexical: Original + KMeans48','Lexical: UMAP3 + KMeans48']:
            for control in ['FF48','Historical returns (48)']:
                ok=p[control].notna()&p[method].notna();stats.append({'comparison':method+' vs '+control,'metric':metric,'wins':int((p.loc[ok,method]>p.loc[ok,control]).sum()),'comparable_years':int(ok.sum())})
    target=l[l.model.eq('tfidf-svd')&l.route.eq('umap')].set_index('formation').gap
    p=k[k.metric.eq('rho')].pivot(index='formation',columns='method',values='gap')
    for control in ['FF48','Historical returns (48)']:
        ok=p[control].notna();stats.append({'comparison':'TF-IDF/SVD + UMAP3 + Leiden vs '+control,'metric':'rho','wins':int((target.loc[p.index[ok]]>p.loc[ok,control]).sum()),'comparable_years':int(ok.sum())})
    pd.DataFrame(stats).to_csv(RESULTS/'comparison_win_counts.csv',index=False)


def run(daily_root=None):
    RESULTS.mkdir(exist_ok=True);FIGURES.mkdir(exist_ok=True)
    provenance=json.loads((INPUTS/'provenance.json').read_text())
    for name, expected in provenance['derived_inputs'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(f'Input checksum mismatch: {name}')
    timing=verify_filing_timing();ranked,selected=build_selection();figures()
    report={'selected_assets':len(selected),'monthly_observations_per_asset':108,'filing_timing':timing,'daily_replay':'Not requested; using frozen coverage artifact.'}
    if daily_root:
        report['daily_replay']=verify_daily(daily_root,ranked)
    (RESULTS/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Reproduced 30 selected assets, three comparison figures and filing-timing checks.')
