/*
  THE SHADOW ARCHIVE
  Main JavaScript
  --------------------------------
  Edit this file for case data,
  navigation, search, filters, map,
  timeline, and page interactions.
*/

const G=['#3a1013,#0a0808','#0d1a1c,#070808','#1c1608,#0a0808','#161022,#070608','#1d0d0d,#060505','#10161a,#070707','#1a1a1a,#050505'];
const C=[
{id:17,t:"The Dyatlov Pass Incident",c:"Russia",l:"Northern Urals, USSR",d:"February 1959",y:1959,k:"Historical Mysteries",s:"UNEXPLAINED",f:9,la:61.7,lo:59.4,
sum:"Nine experienced hikers left their tent in the dark, half-dressed, and died on a Ural slope.",
story:["In late January 1959 ten students and graduates of the Ural Polytechnic Institute, led by Igor Dyatlov, set out on a ski trek toward Otorten mountain. One member, Yuri Yudin, turned back ill on January 28 and became the only survivor.","On February 1 the nine remaining hikers camped on the slope of Kholat Syakhl. Their last photographs show them pitching the tent in poor light.","When no word came, searchers found the tent on February 26. It had been cut open from inside and was partly buried in snow. Footprints, apparently from people in socks or single shoes, led toward the treeline.","Over the following weeks the nine were found: five near the forest edge, some with severe cold exposure, and four in a ravine, three with major chest or skull injuries. The inquiry closed in May 1959, citing a 'compelling natural force'."],
tl:[["Jan 23","Group leaves Sverdlovsk by train"],["Jan 28","Yudin turns back with illness"],["Feb 1","Camp pitched on Kholat Syakhl"],["Feb 26","Search party finds the tent"],["Mar-May","Bodies recovered; inquiry closed"],["2019-20","Russian prosecutors reopen and conclude avalanche"]],
ppl:[["Igor Dyatlov, 23","Radio engineering student and expedition leader."],["Zinaida Kolmogorova, 22","Experienced hiker; found near the treeline."],["Semyon Zolotaryov, 37","Oldest member and a guide; found in the ravine."],["Yuri Yudin, 21","Turned back; survived and later spoke publicly on the case."]],
ev:[["Photograph","Final camp photos, developed from recovered cameras","Recovered film"],["Official report","1959 inquiry: 'compelling natural force'","Soviet inquiry"],["Physical","Tent slashed from inside","Search party testimony"],["Document","Autopsy findings on three ravine victims","Forensic records"]],
th:[["Slab avalanche","A delayed slab release hit the tent, forcing a night escape.","2021 study by Gaume and Puzrin modelled a slab release; 2020 prosecutor review agreed.","Gentle slope angle; no debris field was seen.",7],["Katabatic winds","Violent downslope winds drove the group out.","Strong winds are documented in the area.","Does not easily explain the injuries.",4],["Military testing","A secret weapon test caused panic.","Reports of radiation traces on some clothing; unusual lights claimed.","No documentary evidence; claims are disputed.",2],["Infrasound","Wind over the ridge produced terrifying infrasound.","Proposed physical mechanism.","Speculative; never demonstrated here.",2]],
kn:[["CONFIRMED","Nine hikers died in February 1959."],["CONFIRMED","The tent was cut open from inside."],["LIKELY","Cold exposure killed most of them."],["DISPUTED","Slab avalanche as the full cause."],["UNVERIFIED","Claims of military involvement."]],
un:["Why did they leave the tent unequipped?","What caused the chest and skull injuries?","Why were later accounts of radiation inconsistent?"],
im:"Inspired the 2013 film Devil's Pass, books, games, and decades of online debate.",src:["Soviet criminal case file, 1959","Gaume & Puzrin, Communications Earth & Environment (2021)","Russian Prosecutor General's Office statement (2020)"]
}
,
{id:23,t:"The Mothman",c:"USA",l:"Point Pleasant, West Virginia",d:"Nov 1966 - Dec 1967",y:1966,k:"Cryptids",s:"UNVERIFIED",f:7,la:38.84,lo:-82.14,
sum:"A winged, red-eyed figure seen around an old munitions site, then a bridge falls.",
story:["On November 15, 1966, two young couples reported a large winged creature with glowing red eyes near the abandoned TNT area outside Point Pleasant.","More sightings followed through 1967. Local newspapers covered them, and the name 'Mothman' was coined by the press.","On December 15, 1967 the Silver Bridge collapsed into the Ohio River, killing 46 people. Later writers tied the sightings to the disaster.","John Keel's 1975 book The Mothman Prophecies popularized the connection, mixing reporting with paranormal speculation."],
tl:[["Nov 15, 1966","First widely reported sighting"],["1967","Wave of local reports"],["Dec 15, 1967","Silver Bridge collapses"],["1975","Keel's book published"]],
ppl:[["Roger and Linda Scarberry","Among the couples in the first report."],["John Keel","Author and paranormal investigator."]],
ev:[["Newspaper","Local coverage of the November 1966 sightings","Regional press"],["Witness","Multiple independent sighting reports","Interviews"],["Official","Silver Bridge failure traced to an eyebar defect","Federal investigation"]],
th:[["Misidentified bird","Sandhill crane or large owl seen at night.","Fits red eye-shine and size claims.","Doesn't cover every account.",6],["Mass suggestion","Press attention fueled further reports.","Reports clustered after publicity.","Initial reports were independent.",5],["Omen","The creature foretold the collapse.","None beyond timing.","No causal link; the cause was a metal defect.",1]],
kn:[["CONFIRMED","Sighting reports were published in 1966-67."],["CONFIRMED","The Silver Bridge collapsed on Dec 15, 1967."],["DISPUTED","Any link between the two."],["LEGEND","Mothman as a warning."]],
un:["What did the first witnesses actually see?","Why did reports cease after the collapse?"],
im:"2002 film, annual Mothman Festival, and a statue in Point Pleasant.",src:["Point Pleasant Register, 1966-67","NTSB Silver Bridge report","Keel, The Mothman Prophecies (1975)"]
}
,
{id:31,t:"The Somerton Man",c:"Australia",l:"Adelaide, South Australia",d:"December 1948",y:1948,k:"Disappearances",s:"DOCUMENTED",f:6,la:-34.98,lo:138.5,
sum:"An unidentified man found dead on a beach, a scrap reading 'Tamam Shud' in his pocket.",
story:["On December 1, 1948 a well-dressed man was found dead on Somerton Beach. His clothing labels had been removed.","Months later police found a hidden pocket holding a scrap torn from a copy of the Rubaiyat of Omar Khayyam, printed with the words 'Tamam Shud'.","A book matching the scrap surfaced with a scribbled code and a phone number. The code was never conclusively solved.","In 2022 researchers announced DNA genealogy identifying him as Carl 'Charles' Webb, a Melbourne electrical engineer. How he died remains undetermined."],
tl:[["Dec 1, 1948","Body found on Somerton Beach"],["Jan 1949","Suitcase traced to Adelaide station"],["Jun 1949","Tamam Shud scrap found"],["2021-22","Exhumation and DNA identification announced"]],
ppl:[["Carl 'Charles' Webb","Identified in 2022 as the man."],["Professor Derek Abbott","University of Adelaide researcher who led the DNA effort."]],
ev:[["Document","The Tamam Shud scrap","South Australian police records"],["Cipher","Handwritten letters in the book","Police and cryptanalysts"],["Official","Coroner's inquest, cause undetermined","Inquest"]],
th:[["Poisoning","Suspected poison left no trace.","Organ findings suggested this to the pathologist.","Never proven.",5],["Cold War spy","A courier tied to espionage.","Era's tensions; the removed labels.","No documentary evidence.",2],["Personal tragedy","A private death.","Identification as Webb shifts focus here.","Motive and method unknown.",5]],
kn:[["CONFIRMED","Found Dec 1, 1948."],["LIKELY","Identified as Carl Webb."],["UNVERIFIED","Espionage links."]],
un:["How did he die?","What does the code mean?","Why was he in Adelaide?"],
im:"Subject of books, documentaries, and online research projects.",src:["South Australia police inquest records","University of Adelaide announcement (2022)"]
}
,
{id:41,t:"The Vanishing Hitchhiker",c:"Worldwide",l:"Roadsides, many regions",d:"Told since the 1800s",y:1830,k:"Folklore",s:"FOLKLORE",f:4,la:41.8,lo:-87.8,
sum:"A passenger picked up on a dark road disappears from the car, leaving a coat behind.",
story:["The tale is told on every continent: a driver offers a ride to a young woman or man. At the destination the seat is empty.","The driver visits the address and learns the passenger died years earlier, often on that road, on that date.","Folklorists record versions across centuries, long before cars, with carriages replacing them. Chicago's Resurrection Mary is the best-known American variant.","This is folklore, not a documented event."],
tl:[["1800s","Carriage versions recorded"],["1930s","Resurrection Mary reports begin"],["1981","Brunvand's study popularizes the type"]],
ppl:[["Resurrection Mary","Legendary figure; no confirmed identity."]],
ev:[["Folklore","Hundreds of collected variants","Folklore archives"]],
th:[["Cautionary tale","Teaches road safety and respect for the dead.","Universal themes.","Not provable.",6],["Cultural memory","Grief tied to roadside deaths.","Common roadside shrines.","Interpretive.",5]],
kn:[["LEGEND","Ghost passenger vanishes."],["CONFIRMED","The story type is documented worldwide."]],
un:["Why does the structure repeat across cultures?"],
im:"Appears in films, TV episodes, and countless campfire retellings.",src:["Brunvand, The Vanishing Hitchhiker (1981)"]
}
,
{id:52,t:"The Bell Witch",c:"USA",l:"Adams, Tennessee",d:"1817-1821",y:1817,k:"Ghost Stories",s:"FOLKLORE",f:7,la:36.58,lo:-87.06,
sum:"A farming family said to be tormented by an unseen presence with a voice.",
story:["Tradition holds that the Bell family of Robertson County was harassed from 1817 by raps, voices, and unseen touches.","John Bell reportedly died in December 1820 and the presence was blamed.","The earliest detailed account appeared in M.V. Ingram's 1894 book, decades later, which weakens it as evidence.","The story that Andrew Jackson visited is unverified."],
tl:[["1817","Alleged disturbances begin"],["Dec 1820","Death of John Bell"],["1894","Ingram publishes the account"]],
ppl:[["John Bell","Farmer at the center of the story."],["Betsy Bell","Daughter said to be the main target."]],
ev:[["Book","Ingram's Authentic History","Published 1894"]],
th:[["Folk embellishment","Rumor grew over generations.","Late written source.","Can't confirm events.",7],["Family conflict","Real troubles recast as haunting.","Plausible.","Speculative.",4]],
kn:[["CONFIRMED","John Bell existed."],["UNVERIFIED","Voices and attacks."],["LEGEND","The witch."]],
un:["What happened in the Bell household?"],
im:"Inspired the 2005 film An American Haunting and Tennessee tourism.",src:["Ingram, Authentic History of the Bell Witch (1894)"]
}
,
{id:61,t:"The Dancing Plague of 1518",c:"France",l:"Strasbourg",d:"July 1518",y:1518,k:"Historical Mysteries",s:"DOCUMENTED",f:6,la:48.58,lo:7.75,
sum:"Dozens, perhaps hundreds, danced for days without rest.",
story:["In July 1518 a woman known as Frau Troffea began dancing in a Strasbourg street and continued for days.","Within a week dozens joined her. Records suggest the number reached some hundreds at its height.","Authorities prescribed more dancing, built a stage, and hired musicians, a decision later seen as a mistake.","The outbreak faded in September."],
tl:[["Jul 1518","Troffea begins to dance"],["Late Jul","Dozens join"],["Aug","Council response"],["Sep","Outbreak ends"]],
ppl:[["Frau Troffea","Reported first dancer."]],
ev:[["Document","City council records","Strasbourg archives"],["Chronicle","Contemporary chronicles","Regional"]],
th:[["Mass psychogenic illness","Stress and belief spread the behavior.","Preferred by historians.","Hard to confirm.",8],["Ergot poisoning","Moldy grain caused hallucinations.","Rye diet.","Doesn't explain coordinated dancing.",2]],
kn:[["CONFIRMED","An outbreak occurred in 1518."],["LIKELY","Psychogenic cause."],["DISPUTED","Exact death toll."]],
un:["How many actually died?"],
im:"Subject of history books and documentaries.",src:["Waller, A Time to Dance, A Time to Die (2008)"]
}
,
{id:71,t:"The Hook Man",c:"USA",l:"Lovers' lanes",d:"1950s",y:1950,k:"Local Legends",s:"FOLKLORE",f:5,la:39.8,lo:-98.5,
sum:"A couple parked on a dark road hear a warning; a hook hangs from the car door.",
story:["A teen couple parks on a lovers' lane. The radio announces an escaped killer with a hook for a hand.","The girl insists they leave. At home they find a bloody hook caught on the door handle.","Folklorists trace the tale to the 1950s. A 1960 Dear Abby column printed a version.","No documented event is connected to it."],
tl:[["1950s","Tale circulates among teens"],["1960","Dear Abby letter"]],
ppl:[["The Hook Man","Archetype with no real identity."]],
ev:[["Folklore","Collected variants","Folklore archives"]],
th:[["Cautionary tale","Warns teens about isolated spots.","Fits the era.","Interpretive.",7]],
kn:[["LEGEND","The hook man."],["CONFIRMED","The tale circulated in the 1950s."]],
un:["Where did it originate?"],
im:"Slasher films and campfire stories.",src:["Brunvand, The Vanishing Hitchhiker (1981)"]
}
];
C.forEach((c,i)=>c.g=G[i%G.length]);
const $=s=>document.querySelector(s),app=$('#app'),CL=['DOCUMENTED','UNEXPLAINED','FOLKLORE','UNVERIFIED','FICTIONAL'];
const fear=n=>`<span class="fear" title="Fear ${n
}
/10">${Array.from({length:10
}
,(_,i)=>`<i class="${i<n?'on':''
}
"></i>`).join('')
}
</span>`;
const tag=s=>`<span class="tag ${s
}
">${s
}
</span>`;
const card=c=>`<a class="card" href="#/case/${c.id
}
">
<div class="img" style="--g:linear-gradient(160deg,${c.g.split(',')[0]
}
,${c.g.split(',')[1]
}
)" data-n="${String(c.id).padStart(3,'0')
}
"></div>
<div class="cb">
<div class="mono">CASE ${String(c.id).padStart(3,'0')
}
/ ${c.c
}
</div>
<h3>${c.t
}
</h3>
<div>${tag(c.s)
}
<span class="mono">${c.k
}
</span></div>${fear(c.f)
}
<p>${c.sum
}
</p>
<span class="open">OPEN CASE FILE</span></div></a>`;
function R(){
const [p,q]=location.hash.slice(2).split('?'),[pg,arg]=p.split('/'),qs=new URLSearchParams(q||'');
document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#/'+p));$('#nav').classList.remove('open');window.scrollTo(0,0);
({'':home,index:idx,case:cs,map:mp,timeline:tlp,evidence:evp,about:ab
}
[pg]||home)(arg,qs)
}
function home(){app.innerHTML=`<section class="hero">
<div class="sil"></div>
<h1>THE SHADOW ARCHIVE</h1>
<p>Some stories were never meant to be remembered.</p>
<div style="position:relative">
<a class="btn fill" href="#/index">EXPLORE THE ARCHIVE</a>
<button class="btn" onclick="rnd()">RANDOM CASE</button></div>
<div class="enter">ENTER IF YOU DARE &darr;</div></section>
<div class="wrap">
<h2 class="sec">Featured cases</h2>
<p class="sub">Each file is labelled by how much evidence stands behind it. Folklore is never presented as fact.</p>
<div class="grid">${C.map(card).join('')
}
</div>
<div id="rb" style="margin-top:4rem;text-align:center;border:1px solid var(--line);padding:3rem 1rem">
<h2 class="sec">Show me something I shouldn't know.</h2>
<button class="btn fill" onclick="rnd(1)">DRAW A FILE</button>
<div id="rout"></div></div></div>`
}
function rnd(inl){
const c=C[Math.floor(Math.random()*C.length)];if(!inl)return location.hash='#/case/'+c.id;$('#rout').innerHTML=`<div class="paper" style="max-width:480px;margin:2rem auto;text-align:left">
<div class="mono">CASE ${c.id
}
/ ${c.l
}
</div>
<h3>${c.t
}
</h3>${fear(c.f)
}
<p>${c.sum
}
</p>
<a class="btn fill" href="#/case/${c.id
}
" style="color:var(--ink)">OPEN THE FILE</a></div>`
}
function idx(_,qs){
const cats=[...new Set(C.map(c=>c.k))],cn=[...new Set(C.map(c=>c.c))];
app.innerHTML=`<div class="wrap">
<h2 class="sec">The Legend Index</h2>
<p class="sub">${C.length
}
fully developed files. Filter by classification, category, country, era and fear.</p>
<div class="bar">
<input id="fq" placeholder="Search the index" aria-label="Search index">
<select id="fk">
<option value="">All categories</option>${cats.map(x=>`<option>${x
}
</option>`)
}
</select>
<select id="fs">
<option value="">All classifications</option>${CL.map(x=>`<option ${qs.get('cls')===x?'selected':''
}
>${x
}
</option>`)
}
</select>
<select id="fc">
<option value="">All countries</option>${cn.map(x=>`<option>${x
}
</option>`)
}
</select>
<select id="fe">
<option value="">Any era</option>
<option value="0-1799">Before 1800</option>
<option value="1800-1949">1800-1949</option>
<option value="1950-2100">1950 onward</option></select>
<select id="ff">
<option value="0">Any fear level</option>
<option value="5">Fear 5+</option>
<option value="7">Fear 7+</option>
<option value="9">Fear 9+</option></select>
<select id="fo">
<option value="n">Newest</option>
<option value="o">Oldest</option>
<option value="m">Most mysterious</option>
<option value="d">Most disturbing</option></select></div>
<div id="ig" class="grid"></div></div>`;
const up=()=>{
const q=$('#fq').value.toLowerCase(),[a,b]=($('#fe').value||'0-9999').split('-').map(Number),o=$('#fo').value;
let r=C.filter(c=>(!q||hay(c).includes(q))&&(!$('#fk').value||c.k===$('#fk').value)&&(!$('#fs').value||c.s===$('#fs').value)&&(!$('#fc').value||c.c===$('#fc').value)&&c.y>=a&&c.y<=b&&c.f>=+$('#ff').value);
r.sort((x,y)=>o=='o'?x.y-y.y:o=='n'?y.y-x.y:o=='d'?y.f-x.f:(y.un.length+(y.s=='UNEXPLAINED'?9:0))-(x.un.length+(x.s=='UNEXPLAINED'?9:0)));
$('#ig').innerHTML=r.map(card).join('')||'<p class="sub">No files match. Clear a filter or try a different term.</p>'
}
;
document.querySelectorAll('.bar input,.bar select').forEach(e=>e.oninput=up);up()
}
const hay=c=>JSON.stringify([c.id,'case '+c.id,c.t,c.c,c.l,c.k,c.s,c.d,c.sum,c.ppl,c.story]).toLowerCase();
function cs(id){
const c=C.find(x=>x.id==id);if(!c)return idx();
app.innerHTML=`<div class="wrap cf">
<span class="stamp">CLASSIFIED FILE</span>
<div class="mono">CASE FILE ${String(c.id).padStart(3,'0')
}
</div>
<h1>${c.t
}
</h1>
<div class="meta mono">
<span>STATUS<b>${c.s
}
</b></span>
<span>LOCATION<b>${c.l
}
, ${c.c
}
</b></span>
<span>DATE<b>${c.d
}
</b></span>
<span>CLASS<b>${c.k
}
</b></span>
<span>FEAR LEVEL<b>${c.f
}
/10</b></span></div>
<div class="hero2" style="--g:linear-gradient(160deg,${c.g.split(',')[0]
}
,${c.g.split(',')[1]
}
)">
<span class="mono">${tag(c.s)
}
</span></div>
<h2>The case</h2>
<p class="story">${c.sum
}
${c.s=='FOLKLORE'||c.s=='UNVERIFIED'?'This file documents a legend or disputed account; the narrative below is tradition, not verified fact.':'This file rests on documented records.'
}
</p>
<h2>The story</h2>${c.story.map(p=>`<p class="story">${p
}
</p>`).join('')
}
<h2>The timeline</h2>
<div class="tl">${c.tl.map(t=>`<div>
<b>${t[0]
}
</b>${t[1]
}
</div>`).join('')
}
</div>
<h2>The people involved</h2>
<div class="grid">${c.ppl.map(p=>`<div class="paper" style="--r:${Math.random()*2-1
}
deg">
<div class="mono">PERSON</div>
<h3>${p[0]
}
</h3>
<p>${p[1]
}
</p></div>`).join('')
}
</div>
<h2>The location</h2>
<p class="story">
<b>${c.l
}
, ${c.c
}
.</b> Map reference ${c.la
}
, ${c.lo
}
. <a class="open" href="#/map?sel=${c.id
}
">View on the Haunted Map</a></p>
<h2>The evidence</h2>
<div class="grid">${c.ev.map(e=>`<div class="paper">
<div class="mono">${e[0].toUpperCase()
}
</div>
<h3>${e[1]
}
</h3>
<div class="mono">SOURCE: ${e[2]
}
</div></div>`).join('')
}
</div>
<h2>Theories</h2>
<div class="grid">${c.th.map((t,i)=>`<div class="card" style="cursor:default">
<div class="cb">
<div class="mono">THEORY 0${i+1
}
</div>
<h3>${t[0]
}
</h3>
<p>${t[1]
}
</p>
<p>
<b>Supports:</b> ${t[2]
}
</p>
<p>
<b>Problems:</b> ${t[3]
}
</p>
<div class="mono">CREDIBILITY ${t[4]
}
/10</div>
<div class="cred">
<i style="width:${t[4]*10
}
%"></i></div></div></div>`).join('')
}
</div>
<h2>What we know</h2>${c.kn.map(k=>`<div class="kn">
<span class="tag ${k[0]=='CONFIRMED'?'DOCUMENTED':k[0]=='LIKELY'?'UNEXPLAINED':k[0]=='DISPUTED'?'UNVERIFIED':k[0]=='LEGEND'?'FOLKLORE':'FICTIONAL'
}
">${k[0]
}
</span>${k[1]
}
</div>`).join('')
}
<h2>What we don't know</h2>
<ul class="pl">${c.un.map(u=>`<li>${u
}
</li>`).join('')
}
</ul>
<h2>Cultural impact</h2>
<p class="story">${c.im
}
</p>
<h2>Sources and references</h2>
<ul class="pl">${c.src.map(s=>`<li>${s
}
</li>`).join('')
}
</ul>
<p style="margin-top:3rem">
<a class="btn" href="#/index">BACK TO THE INDEX</a></p></div>`
}
function mp(_,qs){app.innerHTML=`<div class="wrap">
<h2 class="sec">The Haunted Map</h2>
<p class="sub">Select a pin to open the location panel.</p>
<div id="map" role="group" aria-label="World map">${C.map(c=>`<button class="pin" style="left:${(c.lo+180)/360*100
}
%;top:${(90-c.la)/180*100
}
%" data-id="${c.id
}
" aria-label="${c.l
}
"></button>`).join('')
}
</div>
<div id="panel" class="mono">Select a pin.</div></div>`;
const show=id=>{
const c=C.find(x=>x.id==id);$('#panel').innerHTML=`<h3 class="disp" style="font-size:1.8rem;color:var(--ink)">${c.l
}
</h3>
<p class="mono">${c.c
}
/ Legend count: 1 / Fear ${c.f
}
/10</p>
<p style="margin:.6rem 0;font-family:'Work Sans'">${c.sum
}
</p>
<a class="btn fill" href="#/case/${c.id
}
">OPEN CASE FILE</a>`
}
;
document.querySelectorAll('.pin').forEach(p=>p.onclick=()=>show(p.dataset.id));if(qs.get('sel'))show(qs.get('sel'))
}
function tlp(){
const E=[["1500s",0,1599],["1600s",1600,1699],["1700s",1700,1799],["1800s",1800,1899],["1900s",1900,1999],["2000s",2000,2099]];
app.innerHTML=`<div class="wrap">
<h2 class="sec">The Timeline of the Unknown</h2>
<p class="sub">Select an event to open its file. Folklore is placed by its earliest recorded telling.</p>${E.map(e=>{
const r=C.filter(c=>c.y>=e[1]&&c.y<=e[2]).sort((a,b)=>a.y-b.y);return r.length?`<div class="era disp">${e[0]
}
</div>${r.map(c=>`<a class="ev" href="#/case/${c.id
}
">
<b>${c.y
}
</b>
<span>${c.t
}
${tag(c.s)
}
</span></a>`).join('')
}
`:''
}
).join('')
}
</div>`
}
function evp(){app.innerHTML=`<div class="wrap">
<h2 class="sec">The Evidence Room</h2>
<p class="sub">Every item drawn from the case files. Select one to open its file.</p>
<div class="board">${C.flatMap(c=>c.ev.map(e=>[c,e])).map(([c,e],i)=>`<div class="paper" style="--r:${(i%5-2)*.8
}
deg" onclick="location.hash='#/case/${c.id
}
'">
<div class="mono">${e[0].toUpperCase()
}
/ ${c.s=='FOLKLORE'?'UNVERIFIED':'ARCHIVED'
}
</div>
<h3>${e[1]
}
</h3>
<div class="mono">${c.t
}
/ ${e[2]
}
</div></div>`).join('')
}
</div></div>`
}
function ab(){app.innerHTML=`<div class="wrap cf">
<h2 class="sec" style="margin-top:0">About the Archive</h2>
<p class="story" style="font:italic 1.5rem 'IM Fell DW Pica'">We document the stories that exist somewhere between fact, folklore, memory, and fear.</p>
<h2>Research methodology</h2>
<p class="story">Each file separates what primary sources show from what later tellers added. Dates and counts are taken from named sources.</p>
<h2>Evidence standards</h2>
<p class="story">Records, inquiries and peer-reviewed work outweigh books and testimony. Anything weaker is labelled.</p>
<h2>Classification system</h2>
<div class="grid">${[['DOCUMENTED','Historical evidence exists.'],['UNEXPLAINED','Evidence exists, but no universally accepted explanation.'],['FOLKLORE','Traditional cultural story or legend.'],['UNVERIFIED','Claims exist but evidence is weak or unavailable.'],['FICTIONAL','Known fictional creation.']].map(x=>`<div class="card" style="cursor:default">
<div class="cb">${tag(x[0])
}
<p>${x[1]
}
</p></div></div>`).join('')
}
</div>
<h2>Disclaimer</h2>
<p class="story">The Shadow Archive is a fictional organization. Entries summarise public history and folklore; classification does not imply verification.</p>
<h2>Contact</h2>
<p class="story">Submit a case: <span class="mono">files@shadowarchive.example</span></p></div>`
}
$('#fcat').innerHTML='<b class="mono">CATEGORIES</b>'+[...new Set(C.map(c=>c.k))].map(k=>`<a href="#/index">${k
}
</a>`).join('');
$('#burger').onclick=()=>$('#nav').classList.toggle('open');
const sr=$('#sr'),sq=$('#sq');$('#srch').onclick=()=>{sr.classList.add('on');sq.focus()
}
;$('#srx').onclick=()=>sr.classList.remove('on');
sq.oninput=()=>{
const q=sq.value.toLowerCase().trim();$('#sres').innerHTML=q?(C.filter(c=>hay(c).includes(q)).map(c=>card(c)).join('')||'<p class="sub">Nothing in the archive matches that.</p>'):''
}
;
$('#sres').onclick=()=>sr.classList.remove('on');
$('#sub').onclick=()=>{
const e=$('#em').value;$('#subm').textContent=/^\S+@\S+\.\S+$/.test(e)?'You are on the list, investigator.':'Enter a valid email address.'
}
;
document.onmousemove=e=>{$('#glow').style.left=e.clientX+'px';$('#glow').style.top=e.clientY+'px'
}
;
window.onhashchange=R;R();
setTimeout(()=>$('#lp').textContent='ACCESSING CLASSIFIED RECORDS...',1100);setTimeout(()=>$('#lp').textContent='WELCOME, INVESTIGATOR.',2200);
setTimeout(()=>{$('#load').style.opacity=0;setTimeout(()=>$('#load').remove(),1000)
}
,3000);
