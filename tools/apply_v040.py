from pathlib import Path

backend = Path('questmath/app/backend/app/main.py')
s = backend.read_text(encoding='utf-8')
s = s.replace("app=FastAPI(title='MathQuest', version='0.3.1')", "app=FastAPI(title='MathQuest', version='0.4.0')")
s = s.replace("    status: Mapped[str] = mapped_column(String(20), default='in_progress')\n    questions:", "    status: Mapped[str] = mapped_column(String(20), default='in_progress')\n    selected_topic: Mapped[str] = mapped_column(String(40), default='mixed')\n    questions:")
s = s.replace("class AnswerIn(BaseModel): answer: Any; seconds: float = 0\n", "class AnswerIn(BaseModel): answer: Any; seconds: float = 0\nclass WorksheetCreateIn(BaseModel): topic: str = 'mixed'\n")
s = s.replace("            ('status', \"VARCHAR(20) DEFAULT 'in_progress'\")\n", "            ('status', \"VARCHAR(20) DEFAULT 'in_progress'\"),\n            ('selected_topic', \"VARCHAR(40) DEFAULT 'mixed'\")\n")
old = """@app.post('/api/worksheets/today')
def today_ws(u:User=Depends(current_user), s:Session=Depends(db)):
    if u.role!='student': raise HTTPException(403,'Student access required')
    existing=s.scalar(select(Worksheet).where(Worksheet.student_id==u.id,Worksheet.worksheet_date==date.today()))
    if existing: return worksheet_view(existing)
    st=student_settings(s,u.id); topics=json.loads(st.enabled_topics); levels=json.loads(st.manual_levels)
    rng=random.Random(f'{u.id}:{date.today().isoformat()}:{random.SystemRandom().randint(1,10**9)}')
    ws=Worksheet(student_id=u.id,worksheet_date=date.today(),total=st.question_count);s.add(ws);s.flush()
    w=weights(s,u.id,topics)
"""
new = """@app.post('/api/worksheets/today')
def today_ws(selection:WorksheetCreateIn, u:User=Depends(current_user), s:Session=Depends(db)):
    if u.role!='student': raise HTTPException(403,'Student access required')
    existing=s.scalar(select(Worksheet).where(Worksheet.student_id==u.id,Worksheet.worksheet_date==date.today()))
    if existing: return worksheet_view(existing)
    st=student_settings(s,u.id); enabled=json.loads(st.enabled_topics); levels=json.loads(st.manual_levels)
    selected=(selection.topic or 'mixed').lower()
    if selected!='mixed' and selected not in LEVEL4_STRANDS:
        raise HTTPException(400,'Unknown learning area')
    if selected!='mixed' and selected not in enabled:
        raise HTTPException(400,'This learning area is disabled by the parent')
    topics=enabled if selected=='mixed' else [selected]
    rng=random.Random(f'{u.id}:{date.today().isoformat()}:{selected}:{random.SystemRandom().randint(1,10**9)}')
    ws=Worksheet(student_id=u.id,worksheet_date=date.today(),total=st.question_count,selected_topic=selected);s.add(ws);s.flush()
    w=weights(s,u.id,topics)
"""
if old not in s:
    raise SystemExit('Worksheet creation block was not found')
s = s.replace(old, new)
s = s.replace("        'elapsed_seconds':ws.elapsed_seconds or 0,'status':ws.status or 'in_progress',\n", "        'elapsed_seconds':ws.elapsed_seconds or 0,'status':ws.status or 'in_progress',\n        'selected_topic':getattr(ws,'selected_topic','mixed') or 'mixed',\n")
backend.write_text(s, encoding='utf-8')

frontend = Path('questmath/app/frontend/src/main.tsx')
s = frontend.read_text(encoding='utf-8')
s = s.replace("const VERSION = '0.3.1';", "const VERSION = '0.4.0';")
s = s.replace("  current_question_id:number|null; current_phase:'main'|'skipped'; elapsed_seconds:number; status:string;\n", "  current_question_id:number|null; current_phase:'main'|'skipped'; elapsed_seconds:number; status:string; selected_topic:string;\n")
s = s.replace("  const[working,setWorking]=useState(false);\n", "  const[working,setWorking]=useState(false);\n  const[choosing,setChoosing]=useState(false);\n")
s = s.replace("  if(summary)return <Result data={summary} back={()=>{setSummary(null);load()}}/>;\n", "  if(summary)return <Result data={summary} back={()=>{setSummary(null);load()}}/>;\n  if(choosing&&!worksheet)return <QuestCategoryPicker cancel={()=>setChoosing(false)} start={async topic=>{const next=await req('/worksheets/today',{method:'POST',body:JSON.stringify({topic})});setWorksheet(next);setChoosing(false);setWorking(true)}}/>;\n")
s = s.replace("      <button className=\"primary\" disabled={!!worksheet?.completed_at} onClick={async()=>{\n        const next=worksheet||await req('/worksheets/today',{method:'POST'});setWorksheet(next);setWorking(true)\n      }}>", "      <button className=\"primary\" disabled={!!worksheet?.completed_at} onClick={()=>{\n        if(worksheet){setWorking(true)}else{setChoosing(true)}\n      }}>")
insert = '''
const QUEST_CATEGORIES=[
  {id:'measurement',icon:'📏',name:'Measurement',description:'Length, area, perimeter, time, temperature and angles'},
  {id:'algebra',icon:'🧩',name:'Algebra',description:'Unknown values, patterns and number facts'},
  {id:'probability',icon:'🎲',name:'Probability',description:'Chance, likelihood and repeated experiments'},
  {id:'number',icon:'🔢',name:'Number',description:'Place value, fractions, operations, money and estimation'},
  {id:'space',icon:'⬡',name:'Space',description:'Shapes, grids, symmetry and position'},
  {id:'statistics',icon:'📊',name:'Statistics',description:'Data, graphs, surveys and investigations'},
  {id:'mixed',icon:'✨',name:'Mixed Adventure',description:'A balanced quest across all learning areas'}
];

function QuestCategoryPicker({start,cancel}:{start:(topic:string)=>Promise<void>;cancel:()=>void}){
  const[selected,setSelected]=useState('mixed');
  const[busy,setBusy]=useState(false);
  return <main className="category-page"><section className="category-card">
    <p className="eyebrow">CHOOSE TODAY’S QUEST</p><h1>What would you like to practise?</h1><p>Pick one Victorian Curriculum learning area, or choose a mixed adventure.</p>
    <div className="category-grid">{QUEST_CATEGORIES.map(c=><button type="button" key={c.id} className={'category-option '+(selected===c.id?'selected':'')} onClick={()=>setSelected(c.id)}><span>{c.icon}</span><b>{c.name}</b><small>{c.description}</small></button>)}</div>
    <div className="category-actions"><button onClick={cancel}>Back</button><button className="primary" disabled={busy} onClick={async()=>{setBusy(true);try{await start(selected)}finally{setBusy(false)}}}><Play size={20}/>{busy?'Building your quest…':'Start this quest'}</button></div>
  </section></main>;
}
'''
marker = 'function Metric({icon,label,value}:any)'
if marker not in s:
    raise SystemExit('Frontend insertion marker was not found')
s = s.replace(marker, insert + '\n' + marker)
frontend.write_text(s, encoding='utf-8')

styles = Path('questmath/app/frontend/src/styles.css')
styles.write_text(styles.read_text(encoding='utf-8') + '''
.category-page{min-height:100vh;background:radial-gradient(circle at top,#eeeaff,#f7f8ff 55%);padding:32px 18px;display:grid;place-items:center}.category-card{width:min(1050px,100%);background:white;border:1px solid #e4e6f2;border-radius:30px;padding:clamp(24px,5vw,48px);box-shadow:0 24px 80px #4b438822;text-align:center}.category-card h1{font-size:clamp(30px,5vw,48px);margin:8px 0}.category-card>p:not(.eyebrow){color:#737b91;margin-bottom:28px}.category-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;text-align:left}.category-option{display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;column-gap:13px;align-items:center;padding:20px;border:2px solid #e7e8f2;background:#fafaff}.category-option>span{grid-row:1/3;font-size:34px}.category-option>b{font-size:18px}.category-option>small{font-weight:600;color:#777f93;line-height:1.3}.category-option.selected{border-color:#6c5ce7;background:#f0edff;box-shadow:0 8px 22px #6c5ce722}.category-actions{display:flex;justify-content:flex-end;gap:12px;margin-top:28px}.worksheet-top>span{text-transform:capitalize}@media(max-width:800px){.category-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.category-grid{grid-template-columns:1fr}.category-actions{display:grid;grid-template-columns:1fr}.category-actions button{width:100%}}
''', encoding='utf-8')

config = Path('questmath/config.yaml')
config.write_text(config.read_text(encoding='utf-8').replace('version: "0.3.1"', 'version: "0.4.0"'), encoding='utf-8')

changelog = Path('questmath/CHANGELOG.md')
changelog.write_text('''# MathQuest 0.4.0

- Added a student learning-area selector before a new daily worksheet begins.
- Added focused worksheets for Measurement, Algebra, Probability, Number, Space and Statistics.
- Added a Mixed Adventure option spanning all enabled Level 4 strands.
- Stored the selected learning area with each worksheet for future reporting.
- Preserved parent topic controls, adaptive difficulty and resume behaviour.

''' + changelog.read_text(encoding='utf-8'), encoding='utf-8')
