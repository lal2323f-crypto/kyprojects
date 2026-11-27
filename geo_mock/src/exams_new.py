from bank import N, A
from bank3 import X
N.update(X); A.update(X)
from bank2 import I, M, F, W, MAPC, MAPK
def lead(title, paras, src, extra=()):
    return dict(kind='lead', title=title, paras=[[src[k] for k in p] for p in paras], extra=list(extra))
def q(title, items, fig=None): return dict(kind='q', title=title, subs=items, fig=fig)
def mp(items): return dict(kind='map', title='次の地図Ⅰ・地図Ⅱは北欧とその周辺を示したものである。これら', subs=items, fig='<div class="figrow">' + MAPC.replace('class="fig"', 'class="fig" style="flex:1"') + MAPK.replace('class="fig"', 'class="fig" style="flex:1"') + '</div>')
EXAMS = {}
EXAMS[1] = dict(no='①', note='北欧の地形・気候、北欧の地図、アフリカの地形・気候・資源', sections=[
 q('北欧とアフリカの自然環境', [I[k] for k in ['i_d', 'i_et', 'i_south7', 'i_byakuya', 'i_6do', 'i_tate', 'i_aurora', 'i_hokuo_kikou', 'i_africa_kikou']]),
 lead('北欧の地形と気候', [['n_kyoku', 'n_tate', 'n_kokki', 'x_nadaraka', 'n_ice', 'x_kazan', 'n_jut'], ['n_hyoga', 'n_mori', 'n_fjord', 'x_yase'], ['n_danryu', 'n_dfb', 'n_dfc', 'x_pulp', 'n_et']], N, [F['ph_sami'], W['w_mugi'], W['w_partner']]),
 mp([M[k] for k in ['mA', 'mBC', 'mDE', 'ka', 'ku', 'ko', 'nato_not1', 'nato23', 'nato24', 'nato32', 'mapA_plate', 'mE']] + [W['w_cph']]),
 lead('アフリカの地形と気候', [['a54', 'a_region', 'x_nairobi', 'a_antei', 'a_table', 'a_rift', 'a_kili', 'a_lake'], ['a_ankoku', 'a_atlas', 'a_drake', 'a_copper', 'x_tetsudo', 'a_sahara', 'x_kigo'], ['a_taisho', 'a_squall', 'a_amazon', 'a_latosol', 'a_yakihata', 'a_savanna', 'a_kanryu', 'a_cs']], A, [W['w_gyao'] if False else W['w_1960']]),
 q('北欧とアフリカの資料', [F[k] for k in ['diamond', 'diamond_r', 'cg_dfb', 'cg_cs', 'ph_sapeur', 'cacao', 'cg_af', 'cof_x', 'cof_yz', 'coffee', 'nclim2']] + [W['w_sahel']]),
])
EXAMS[2] = dict(no='②', note='北欧の生活文化・産業、北欧の地図、アフリカの文化・農業・工業・国境', sections=[
 q('北欧とアフリカの自然環境', [I[k] for k in ['i_et', 'i_antei', 'i_shinki', 'i_cs', 'i_steppe', 'i_south7', 'i_aurora', 'i_hokuo_kikou']]),
 lead('北欧の生活文化と産業', [['n5', 'x_hikari', 'x_design', 'n_sami', 'x_kyosei', 'n_fika', 'n_hygge', 'n_spice'], ['n_sauna', 'n_geshi', 'n_prot', 'x_ikea'], ['n_kiruna', 'n_chrome', 'n_rin', 'n_volvo', 'n_clean', 'n_salmon']], N, [W['w_tax']]),
 mp([M[k] for k in ['mB', 'mC', 'mD', 'ki', 'ke', 'kpos_hel', 'nato_not2', 'eu_not', 'mapD_pen', 'mapE_suomi']] + [W['w_reyk']]),
 lead('アフリカの文化と産業', [['a_minzoku', 'a_swahili', 'a_sapeur', 'a_rel', 'a_anim', 'x_kouyougo'], ['a_yakihata', 'x_savanna', 'a_plant', 'a_medit', 'a_mono', 'a_seizo', 'a_cashless', 'a_iyaku'], ['a_1960', 'a_44', 'x_kokkyo', 'a_tobihi', 'a_rwanda']], A, [W['w_fair']]),
 q('北欧とアフリカの資料', [F[k] for k in ['coffee', 'tea', 'gold', 'copper', 'cg_af', 'nclim1', 'ph_fjord']] + [W['w_kanryu']]),
])
EXAMS[3] = dict(no='③', note='北欧の気候・社会・NATO（時事）、北欧の地図、アフリカの自然・課題', sections=[
 q('北欧とアフリカの自然環境', [I[k] for k in ['i_d', 'i_et', 'i_tate', 'i_6do', 'i_cs', 'i_af', 'i_steppe', 'i_aurora']]),
 lead('北欧の気候と社会', [['n_hyoga', 'n_mori', 'n_danryu', 'n_et', 'n_byakuya'], ['n_salmon', 'n_tax', 'n_gender'], ['n_nato', 'x_nato', 'n_neutral', 'n_trade', 'n_baltic']], N, [F['ph_sami'], W['w_geshi']]),
 mp([M[k] for k in ['mA', 'mB', 'mE', 'ka', 'ki', 'ku', 'kpos_cph', 'nato_not3', 'nato23', 'nato24']] + [W['w_hel']]),
 lead('アフリカの自然と課題', [['x_choco', 'x_mono', 'x_wana'], ['a_leap', 'x_mpesa', 'x_hanbai', 'a_fair'], ['x_funso', 'x_rwanda', 'a_rwanda'], ['x_jinko', 'a_jinko', 'x_saimu', 'a_debt', 'a_slum', 'a_sahel', 'a_malaria']], A, [W['w_victoria']]),
 q('北欧とアフリカの資料', [F[k] for k in ['diamond', 'ph_table', 'ph_sapeur', 'cg_cs', 'nclim2', 'cof_yz', 'domino']] + [W['w_hokkai']]),
])
EXAMS[4] = dict(no='④', note='北欧の地形・文化・産業、北欧の地図、アフリカの地形・気候・文化', sections=[
 q('北欧とアフリカの自然環境', [I[k] for k in ['i_d', 'i_byakuya', 'i_kyokuken', 'i_6do', 'i_south7', 'i_tate', 'i_aurora', 'i_africa_kikou', 'i_et']]),
 lead('北欧の地形と生活', [['n5', 'n_tate', 'n_kokki', 'n_jut', 'n_mori'], ['n_kochi', 'n_dfc', 'n_et'], ['n_yule', 'n_prot', 'n_hygge', 'x_fika', 'x_sauna'], ['n_chrome', 'x_yoshoku', 'n_clean']], N, [W['w_geshi']]),
 mp([M[k] for k in ['mBC', 'mDE', 'mA', 'ko', 'ke', 'kpos_sto', 'nato_not1', 'nato32', 'eu_not', 'mapB_fjord', 'nato23']] + [W['w_oslo']]),
 lead('アフリカの地形・気候と文化', [['a_antei', 'x_rare', 'a_table', 'a_rift', 'a_kili', 'x_mannen', 'a_lake', 'a_copper'], ['a_taisho', 'a_squall', 'a_latosol', 'a_savanna', 'a_steppe', 'x_joshou', 'a_cs'], ['a_minzoku', 'a_swahili', 'x_swahili', 'a_rel', 'a_anim', 'a_plant', 'a_medit']], A, [W['w_sahel']]),
 q('北欧とアフリカの資料', [F[k] for k in ['tea', 'coffee', 'gold', 'diamond_r', 'cg_dfb', 'ph_sami', 'ph_sapeur', 'cof_x', 'cg_cs', 'nclim2']] + [W['w_1960'], W['w_fair']]),
])
EXAMS[5] = dict(no='⑤', note='総仕上げ：北欧とアフリカの地誌全体、北欧の地図（国・首都・NATO）', sections=[
 q('北欧とアフリカの自然環境', [I[k] for k in ['i_d', 'i_et', 'i_antei', 'i_byakuya', 'i_hokuo_kikou']]),
 lead('北欧の地誌', [['n_kyoku', 'n_ice', 'n_hyoga', 'n_fjord'], ['n_dfb', 'n_dfc'], ['x_design', 'n_sami', 'n_fika', 'n_geshi'], ['n_kiruna', 'n_rin', 'n_volvo', 'x_ikea', 'x_suiryoku'], ['n_tax', 'n_nato']], N, [W['w_hokkai'], W['w_partner']]),
 mp([M[k] for k in ['mA', 'mB', 'mC', 'mD', 'mE', 'ka', 'ki', 'ku', 'kpos_cph', 'nato_not2', 'nato23', 'nato24']] + [W['w_hel']]),
 lead('アフリカの地誌', [['a54', 'a_region', 'a_ankoku', 'a_atlas', 'a_drake', 'a_sahara'], ['a_amazon', 'a_latosol', 'a_kanryu', 'a_cs'], ['a_sapeur', 'a_rel', 'x_kouyougo', 'a_yakihata', 'x_olive', 'a_mono'], ['x_kokkyo', 'a_debt', 'a_slum', 'a_sahel', 'a_jinko']], A, []),
 q('北欧とアフリカの資料', [F[k] for k in ['cacao', 'tea', 'copper', 'diamond', 'cg_dfb', 'ph_table', 'cof_x', 'domino']] + [W['w_victoria']]),
])
