import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.cwd();
const input = path.join(root, "data", "processed", "clean_sakhalin_1890_ru_v3_20260712.csv");
const outputDir = path.join(root, "outputs", "translation_review_20260716");
const outputPath = path.join(outputDir, "sakhalin_1890_english_translation_options.xlsx");

function parseCsv(text) {
  const rows=[]; let row=[], cell="", q=false;
  for(let i=0;i<text.length;i++){ const c=text[i];
    if(q){ if(c==='"' && text[i+1]==='"'){cell+='"';i++;} else if(c==='"')q=false; else cell+=c; }
    else if(c==='"')q=true; else if(c===','){row.push(cell);cell="";} else if(c==='\n'){row.push(cell.replace(/\r$/, ""));rows.push(row);row=[];cell="";} else cell+=c;
  }
  if(cell.length||row.length){row.push(cell);rows.push(row);} return rows;
}
const matrix=parseCsv((await fs.readFile(input,"utf8")).replace(/^\uFEFF/,""));
const headers=matrix[0], data=matrix.slice(1).filter(r=>r.length>1);
const idx=Object.fromEntries(headers.map((h,i)=>[h,i]));
const counts=(field)=>{const m=new Map(); for(const r of data){const v=r[idx[field]]??"";m.set(v,(m.get(v)||0)+1);} return [...m].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],"ru"));};

const fieldRows = [
 ["person_id","Person ID","Person identifier","Person ID","Keep unchanged","Identifier; never translate"],
 ["source_position_id","Source-position ID","Source location identifier","Source-position ID","Keep unchanged","Identifier; never translate"],
 ["district_code","District code","District identifier","District code","Keep unchanged","Code; never translate"],
 ["district","District","Administrative district","District name","Translate/transliterate","Use historical district form"],
 ["settlement_order","Settlement order","Settlement sequence","Settlement order","Keep unchanged","Numeric source ordering"],
 ["settlement","Settlement","Locality","Settlement/post","Transliterate","Retain historical place identity; translate generic type only"],
 ["person_order_in_settlement","Person order within settlement","Person sequence in locality","Local person number","Keep unchanged","Integer"],
 ["page_number","Source page","Printed-book page","Page number","Keep unchanged","Integer"],
 ["household_id","Household ID","Household identifier","Household ID","Keep unchanged","Identifier"],
 ["household_type","Household type","Dwelling/institution type","Household setting","Translate","Controlled category"],
 ["household_details","Household details","Dwelling details","Household description","Translate selectively","Free text; retain Russian beside English"],
 ["legal_status","Detailed legal/social status","Recorded legal status","Source legal status","Translate with review","Detailed historical wording"],
 ["legal_status_norm","Legal-status category","Analytical legal status","Normalized legal status","Translate via lookup","Recommended key analytical field"],
 ["name_raw","Name (Russian)","Recorded personal name","Original name","Transliterate","Never translate personal names"],
 ["name_alias","Name alias (Russian)","Alternative/former name","Alias","Transliterate","Never translate personal names"],
 ["sex","Sex","Recorded/derived sex","Sex category","Translate via lookup","Use sex, not gender, because dataset records a binary historical demographic variable"],
 ["sex_evidence","Sex-classification evidence","Evidence for sex derivation","Sex evidence","Translate controlled phrases","Provenance field"],
 ["family_status","Household/family role","Recorded household relationship","Source household role","Translate with review","Not marital status"],
 ["family_status_norm","Household-role category","Analytical household relationship","Normalized household role","Translate via lookup","Use household role to avoid confusion with marriage_status"],
 ["age","Age (years)","Age in completed years","Age","Keep numeric","Infant detail remains in comments"],
 ["religion","Religious confession","Confession/religion","Religion","Translate via lookup","Confession is historically more exact"],
 ["origin_place","Place of origin","Administrative origin","Origin","Translate/transliterate","Translate unit; use established English toponym"],
 ["arrival_year","Year of arrival","Arrival year","Year arrived","Keep numeric","Integer year"],
 ["occupation","Occupation/activity","Recorded occupation","Occupation","Translate with review","Free-text vocabulary; later dedicated lookup"],
 ["literacy","Literacy","Literacy/education level","Literacy status","Translate via lookup","Controlled category"],
 ["marriage_status","Marital situation","Recorded marital status/location","Marriage status","Translate via lookup","Location of spouse/marriage is semantically important"],
 ["allowance_status","Receiving state allowance","Government allowance indicator","Allowance status","Boolean label","TRUE means allowance recorded"],
 ["illness","Recorded illness/condition","Recorded health condition","Illness","Translate with medical-historical review","Free text"],
 ["illness_norm","Health-condition category","Analytical illness/condition","Normalized illness","Translate via lookup","Avoid modern diagnosis where source is descriptive"],
 ["comments","Comments (Russian)","Source/reviewer comments","Notes","Translate selectively","Retain Russian beside English"],
 ["notes_raw","Archival reference","Raw archival note","Source note","Keep unchanged","Archival sigla and numbers are identifiers"],
];

const direct = {
 "Александровский":["Alexandrovsk District","Alexandrovsky District","District of Alexandrovsk"], "Тымовский":["Tymovsk District","Tymovsky District","District of Tymovsk"], "Корсаковский":["Korsakovsk District","Korsakovsky District","District of Korsakovsk"],
 "Частное":["Private household","Private dwelling","Householder's dwelling"], "Казарма":["Barracks","Barrack building","Barracks accommodation"], "Дом":["House","Dwelling house","House"], "Тюрьма":["Prison","Prison building","Prison"], "Другое":["Other","Other setting","Other"], "Метеорологическая станция":["Meteorological station","Weather station","Meteorological station"], "Школа":["School","School building","School"], "Телеграф":["Telegraph station","Telegraph office","Telegraph"], "Баня":["Bathhouse","Bath house","Bathhouse"], "Мастерская":["Workshop","Workroom/workshop","Workshop"], "Лазарет":["Infirmary","Hospital ward","Infirmary"],
 "Поселенец":["Exile settler (male)","Exile settler","Settled exile"], "Поселка":["Exile settler (female)","Female exile settler","Settled exile (female)"], "Ссыльнокаторжный":["Penal-labour exile (male)","Penal convict (male)","Convict sentenced to penal servitude"], "Ссыльнокаторжная":["Penal-labour exile (female)","Penal convict (female)","Woman sentenced to penal servitude"], "Свободного состояния":["Free-status person","Free person","Person of free status"], "Крестьянин из ссыльных":["Peasant from the exiled population (male)","Exile peasant (male)","Peasant-in-exile"], "Крестьянка из ссыльных":["Peasant from the exiled population (female)","Exile peasant (female)","Peasant-in-exile (female)"],
 "Крестьянин":["Peasant (male)","Male peasant","Peasant"], "Крестьянка":["Peasant (female)","Female peasant","Peasant woman"], "Административный ссыльный":["Administrative exile","Administratively exiled person","Exile by administrative order"], "Мещанин":["Townsperson (meshchanin estate)","Urban commoner","Member of the meshchanstvo"], "Дворянин":["Nobleman","Member of the nobility","Noble"],
 "Хозяин":["Household head (male)","Male household head","Householder"], "Хозяйка":["Household head (female)","Female household head","Householder (female)"], "Жена":["Wife","Wife","Wife"], "Муж":["Husband","Husband","Husband"], "Сожительница":["Cohabiting partner (female)","Female partner","Cohabitant (female)"], "Сожитель":["Cohabiting partner (male)","Male partner","Cohabitant (male)"], "Совладелец":["Joint household head (male)","Male co-head","Joint householder"], "Совладелица":["Joint household head (female)","Female co-head","Joint householder (female)"], "Сын":["Son","Son","Son"], "Дочь":["Daughter","Daughter","Daughter"], "Жилец":["Lodger (male)","Male lodger","Resident/lodger"], "Жилица":["Lodger (female)","Female lodger","Resident/lodger (female)"], "Работник":["Hired worker (male)","Male worker","Worker"], "Работница":["Hired worker (female)","Female worker","Worker (female)"], "Прислуга":["Domestic servant","Servant","Domestic service"],
 "Мужской":["Male","M","Male"], "Женский":["Female","F","Female"],
 "Православное":["Eastern Orthodox","Orthodox","Orthodox confession"], "Католическое":["Roman Catholic","Catholic","Catholic confession"], "Магометанское":["Muslim (source term: Mohammedan)","Muslim","Mohammedan confession"], "Лютеранское":["Lutheran","Lutheran","Lutheran confession"], "Иудейское":["Jewish","Jewish","Jewish confession"], "Раскольничество":["Schismatic (Old Believer tradition)","Old Believer / Schismatic","Schismatic confession"], "Армяно-григорианское":["Armenian Apostolic","Armenian Gregorian","Armenian Gregorian confession"], "Старообрядчество":["Old Believer","Old Rite","Old Belief"], "Молоканское":["Molokan","Molokan","Molokan confession"],
 "Неграмотен":["Illiterate","Not literate","Illiterate"], "Грамотен":["Literate","Able to read and write","Literate"], "Образован":["Educated","Formally educated","Educated"],
 "женат на родине":["Married; spouse in place of origin","Married on the mainland","Married in homeland"], "женат на Сахалине":["Married on Sakhalin","Sakhalin marriage","Married on Sakhalin"], "холост":["Unmarried","Single","Bachelor"], "вдов":["Widowed","Widower","Widowed"], "одинок":["Living alone (male)","Alone","Solitary"], "девица":["Unmarried woman","Single woman","Maiden"],
 "Богадельщик":["Almshouse resident","Institutional-care resident","Almshouse inmate"], "Сифилис":["Syphilis","Syphilis","Syphilis"], "Слепота":["Blindness","Blind","Blindness"], "Психическое расстройство":["Mental disorder (source category)","Mental illness","Mental disorder"], "Удушье":["Breathing difficulty (source: suffocation)","Respiratory distress","Suffocation"], "Глухота":["Deafness","Deaf","Deafness"], "Слабосилен":["Physically weak","Debility","Weak constitution"], "Контужен":["Injury from contusion/blast","Contusion injury","Contused"], "Немой":["Unable to speak","Mute","Dumb (historical)"], "Слабое зрение":["Impaired vision","Poor eyesight","Weak sight"], "Конъюнктивит":["Conjunctivitis","Conjunctivitis","Conjunctivitis"], "Рак":["Cancer","Cancer","Cancer"], "Разбита параличом":["Paralysed","Paralysis","Struck by paralysis"], "Чахотка":["Pulmonary tuberculosis (source: consumption)","Tuberculosis","Consumption"], "Женская болезнь":["Women's ailment (unspecified)","Female disorder, unspecified","Woman's disease"], "Хронический катар желудка и кишок":["Chronic gastric and intestinal catarrh","Chronic gastro-intestinal inflammation","Chronic catarrh of stomach and intestines"], "Плеврит":["Pleurisy","Pleurisy","Pleurisy"], "Ревматизм":["Rheumatism","Rheumatism","Rheumatism"], "Левая рука не работает":["Loss of function in left arm","Left arm disability","Left arm does not work"], "Бронхиальный катар":["Bronchial catarrh","Chronic bronchitis-like condition","Bronchial catarrh"], "Застарелый вывих в левом локтевом сочленении":["Chronic dislocation of the left elbow joint","Old left-elbow dislocation","Long-standing dislocation in left elbow joint"], "Катар желудка":["Gastric catarrh","Gastritis-like condition","Catarrh of the stomach"],
};

const relations={"Сын":"Son","Дочь":"Daughter","Жена":"Wife"};
const bases={"поселенца":["an exile settler","exile settler","a settler"],"поселки":["a female exile settler","female exile settler","a female settled exile"],"ссыльнокаторжного":["a male penal-labour exile","male penal convict","a convict sentenced to penal servitude"],"ссыльнокаторжной":["a female penal-labour exile","female penal convict","a woman sentenced to penal servitude"],"крестьянина из ссыльных":["a male peasant from the exiled population","male exile peasant","a peasant-in-exile"],"крестьянки из ссыльных":["a female peasant from the exiled population","female exile peasant","a female peasant-in-exile"],"каторжного":["a male penal-labour convict","male penal convict","a hard-labour convict"],"каторжной":["a female penal-labour convict","female penal convict","a female hard-labour convict"],"рядового":["a private soldier","private soldier","a rank-and-file soldier"],"отставного рядового":["a retired private soldier","retired private","a retired rank-and-file soldier"],"подполковника":["a lieutenant colonel","lieutenant colonel","a lieutenant-colonel"],"надворного советника":["a court councillor","court councillor","a civil servant of Court Councillor rank"],"солдатки":["a soldier's wife/widow","soldier's wife or widow","a soldatka"]};
function legalTranslation(v){ if(direct[v]) return direct[v]; for(const [ru,en] of Object.entries(relations)){if(v.startsWith(ru+" ")){const b=v.slice(ru.length+1).toLowerCase(); if(bases[b])return [`${en} of ${bases[b][0]}`,`${en} of ${bases[b][1]}`,`${en} of ${bases[b][2]}`];}}
 const ranks={"Запасной рядовой":["Army reservist (private)","Reserve private","Private in the reserve"],"Отставной рядовой":["Retired private soldier","Retired private","Retired rank-and-file soldier"],"Запасной унтер-офицер":["Reserve non-commissioned officer","Reserve NCO","NCO in the reserve"],"Рядовой":["Private soldier","Private","Rank-and-file soldier"],"Отставной унтер-офицер":["Retired non-commissioned officer","Retired NCO","Retired non-commissioned officer"],"Отставной фельдфебель":["Retired sergeant major","Retired senior NCO","Retired feldwebel"],"Унтер-офицер":["Non-commissioned officer","NCO","Non-commissioned officer"],"Капитан":["Captain","Captain","Captain"],"Запасной ефрейтор":["Reserve lance corporal","Reserve corporal","Gefreiter in the reserve"],"Подпоручик":["Second lieutenant","Junior lieutenant","Podporuchik"],"Подполковник":["Lieutenant colonel","Lt colonel","Lieutenant-colonel"],"Надворный советник":["Court councillor (civil rank)","Court councillor","Nadvorny sovetnik"],"Штейгер":["Mine foreman (steiger)","Mine foreman","Steiger"],"Канцелярский служащий":["Clerical official","Clerk","Chancery employee"],"Врач":["Physician","Doctor","Physician"],"Старший надзиратель":["Senior prison overseer","Senior overseer","Senior warder"],"Повивальная бабка":["Midwife","Midwife","Midwife"],"Фельдшер":["Feldsher (medical assistant)","Medical assistant","Feldsher"],"Совладелец":["Joint owner","Co-owner","Joint proprietor"],"Кузнец":["Blacksmith","Smith","Blacksmith"]}; return ranks[v]||["Manual review required","Manual review","Unresolved historical term"]; }

const familyExtra={"Незаконнорожденный сын":["Son born outside marriage","Nonmarital son","Illegitimate son (historical)"],"Незаконнорожденная дочь":["Daughter born outside marriage","Nonmarital daughter","Illegitimate daughter (historical)"],"Приемная дочь":["Foster/adopted daughter","Foster daughter","Adopted daughter"],"Приемный сын":["Foster/adopted son","Foster son","Adopted son"],"Брат":["Brother","Brother","Brother"],"Мать":["Mother","Mother","Mother"],"Внучка":["Granddaughter","Granddaughter","Granddaughter"],"Пасынок":["Stepson","Stepson","Stepson"],"Сестра":["Sister","Sister","Sister"],"Невестка":["Daughter-in-law","Daughter-in-law","Daughter-in-law"],"Падчерица":["Stepdaughter","Stepdaughter","Stepdaughter"],"Отец":["Father","Father","Father"],"Зять":["Son-in-law","Son-in-law","Son-in-law"],"Приемный отец":["Foster/adoptive father","Foster father","Adoptive father"],"Теща":["Wife's mother","Mother-in-law","Mother-in-law (wife's mother)"],"Свекровь":["Husband's mother","Mother-in-law","Mother-in-law (husband's mother)"],"Кухарка":["Cook (female)","Female cook","Cook"],"Повар":["Cook (male)","Male cook","Cook"],"Внук":["Grandson","Grandson","Grandson"],"Служанка":["Maidservant","Maid","Female servant"],"Нянька":["Nursemaid","Nanny","Nursemaid"],"Сторож":["Watchman","Guard","Watchman"]};
function compound(v){ const parts=v.split("; "); if(parts.length>1){const all=parts.map(p=>direct[p]||[p,p,p]);return [0,1,2].map(i=>all.map(x=>x[i]).join("; "));} return direct[v]; }
function marriage(v){if(direct[v])return direct[v]; const repl={"женат на родине":"Married; spouse in place of origin","женат на Сахалине":"Married on Sakhalin","женат в другом месте":"Married elsewhere","женат на каре":"Married while serving sentence","женат в николаевске":"Married in Nikolayevsk","женат во владивостоке":"Married in Vladivostok","холост":"Unmarried","вдов":"Widowed","одинок":"Living alone (male)","одинока":"Living alone (female)","одинокий":"Living alone (male)"}; const ps=v.split(". "); if(ps.length>1)return [ps.map(p=>repl[p]||p).join("; "),ps.map(p=>repl[p]||p).join("; "),ps.map(p=>repl[p]||p).join("; ")]; if(v==="женат на родине и на Сахалине")return ["Married in place of origin and on Sakhalin","Two marriages: mainland and Sakhalin","Married at home and on Sakhalin"]; return [repl[v]||"Manual review required",repl[v]||"Manual review",repl[v]||"Unresolved"];}

const categoryFields=["district","household_type","legal_status_norm","sex","family_status_norm","religion","literacy","marriage_status","allowance_status","illness_norm"];
const reviewedOverrides={
 ["legal_status_norm|"+"\u0416\u0435\u043d\u0430 \u0432\u0440\u0430\u0447\u0430"]:["Wife of a physician","Wife of physician","Wife of a doctor"],
 ["marriage_status|"+"\u0436\u0435\u043d\u0430\u0442 \u043d\u0430 \u0440\u043e\u0434\u0438\u043d\u0435 \u0438 \u043d\u0430 \u0441\u0430\u0445\u0430\u043b\u0438\u043d\u0435"]:["Married in place of origin and on Sakhalin","Two marriages: mainland and Sakhalin","Married at home and on Sakhalin"],
 ["illness_norm|"+"\u0412\u043e\u0434\u044f\u043d\u043a\u0430"]:["Dropsy (oedema)","Oedema","Dropsy"],
 ["illness_norm|"+"\u0412\u043e\u0434\u044f\u043d\u043a\u0430; \u0411\u043e\u0433\u0430\u0434\u0435\u043b\u044c\u0449\u0438\u043a"]:["Dropsy (oedema); Almshouse resident","Oedema; Institutional-care resident","Dropsy; Almshouse inmate"],
};
const catRows=[];
for(const field of categoryFields){for(const [v,n] of counts(field)){if(v==="")continue; let t;
 if(field==="legal_status_norm")t=legalTranslation(v); else if(field==="family_status_norm")t=direct[v]||familyExtra[v]||["Manual review required","Manual review","Unresolved household term"]; else if(field==="marriage_status")t=marriage(v); else if(field==="allowance_status")t=v==="TRUE"?["Receiving allowance","Yes","Allowance: yes"]:["Not receiving allowance","No","Allowance: no"]; else if(field==="illness_norm")t=compound(v)||["Manual review required","Manual review","Unresolved condition"]; else t=direct[v]||["Manual review required","Manual review","Unresolved category"];
 t=reviewedOverrides[field+"|"+v]||reviewedOverrides[field+"|"+v.toLowerCase()]||t;
 const rec=(field==="religion"&&["Магометанское","Раскольничество"].includes(v))?"A":"A";
 const note=t[0].startsWith("Manual")?"Do not apply until manually resolved":(field==="legal_status_norm"?"Preserves penal/legal phase and sex where encoded in Russian":field==="family_status_norm"?"Describes household role, not marital status":"");
 catRows.push([field,v,n,t[0],t[1],t[2],rec,note]);}}

const sources=[
 ["Alma Books publisher page","Current mass-market English edition; Brian Reeve; ISBN 9781847497864; 512 pp.","https://almabooks.com/product/sakhalin-island-2/"],
 ["Google Books, Alma 2018 edition","Searchable terminology includes Alexandrovsk District, Korsakovsk District, Tymovsk District, free-status, cohabitant, penal labour, penal servitude, peasants-in-exile, settled exiles.","https://books.google.com.sg/books?id=WoJjDwAAQBAJ"],
 ["RUDN Journal (2021), Spachil","Scholarly comparison identifies two full English translations: Luba & Michael Terpak (1967) and Brian Reeve (1993), and warns that historical realia cause translation errors.","https://doi.org/10.22363/2312-9220-2021-26-2-169-176"],
 ["Library of Congress, Views of Sakhalin Island","Authoritative historical context uses penal colony, place of exile, convicts, political prisoners, and settler population.","https://www.loc.gov/resource/gdclccn.2018684021/?sp=23&st=text"],
];

const wb=Workbook.create();
const summary=wb.worksheets.add("Read Me");
summary.getRange("A1:H1").merge(); summary.getRange("A1").values=[["Sakhalin 1890 — English Translation Options"]];
summary.getRange("A3:B12").values=[
 ["Purpose","Review three English renderings before any bilingual analytical dataset is generated."],
 ["Source dataset","data/processed/clean_sakhalin_1890_ru_v3_20260712.csv"],
 ["Source records",data.length], ["Source columns",headers.length],
 ["Canonical data changed?","No"], ["Recommended option","Variant A — historically explicit analytical English"],
 ["Variant A","Historically explicit; preserves legal phase, sex distinctions, and source-era ambiguity."],
 ["Variant B","Compact dashboard labels; easiest to chart, but loses some nuance."],
 ["Variant C","Publication-aligned/literary wording, especially Brian Reeve terminology; less uniform for analytics."],
 ["Important limitation","This workbook maps compact categories and field labels. Names are transliterated, while settlements, origins, occupations, detailed status, comments, and notes require dedicated lookup/review stages."],
 ];
 summary.getRange("A14:H14").merge(); summary.getRange("A14").values=[["Decision recommendation"]];
 summary.getRange("A15:H18").merge(true); summary.getRange("A15").values=[["Choose Variant A as the canonical English analytical vocabulary. Keep Variant C in documentation as a concordance to Reeve's English edition. Use Variant B only for compact chart labels. Never replace the Russian columns: add parallel *_en fields through lookup tables after the current quality check is frozen."]];

const fg=wb.worksheets.add("Field Names"); fg.getRange("A1:F1").values=[["Field","Variant A — recommended","Variant B — technical","Variant C — reader-facing","Treatment","Rationale"]]; fg.getRangeByIndexes(1,0,fieldRows.length,6).values=fieldRows;
const cats=wb.worksheets.add("Category Options"); cats.getRange("A1:H1").values=[["Field","Russian value","Records","Variant A — recommended","Variant B — compact","Variant C — edition/historical","Recommended","Notes"]]; cats.getRangeByIndexes(1,0,catRows.length,8).values=catRows;
const ed=wb.worksheets.add("Edition Comparison"); ed.getRange("A1:C1").values=[["Source","Evidence used","URL"]]; ed.getRangeByIndexes(1,0,sources.length,3).values=sources;
ed.getRange("A8:E8").values=[["Russian concept","Reeve/edition evidence","Dataset recommendation","Reason","Caution"]];
ed.getRange("A9:E16").values=[
 ["округ","Alexandrovsk/Korsakovsk/Tymovsk District","… District","Direct alignment with current edition","Do not use modern municipal names"],
 ["ссыльнокаторжный","penal labour / penal servitude / convict","Penal-labour exile","Keeps sentence type and exile context","Penal convict is shorter but less explicit"],
 ["поселенец","settlers / settled exiles","Exile settler","Distinguishes post-katorga legal phase","Settler alone hides coercive exile"],
 ["крестьянин из ссыльных","peasants-in-exile","Peasant from the exiled population","Matches legal transition without implying current imprisonment","Exile peasant is useful only as compact label"],
 ["свободного состояния","free-status","Free-status person","Direct Reeve concordance","Free person may imply modern civil liberty"],
 ["сожительница","cohabitant","Cohabiting partner","Modern clarity with historical concordance","Do not translate as wife"],
 ["хозяин","householders","Household head","Analytically distinguishes role from property ownership","Householder is retained in Variant C"],
 ["магометанское","period term corresponds to Mohammedan","Muslim (source term: Mohammedan)","Readable and transparent about source vocabulary","Do not silently reproduce an outdated label"],
 ];
const scope=wb.worksheets.add("Coverage & Next Stage"); scope.getRange("A1:E1").values=[["Field","Distinct values","Current treatment","Next-stage method","Risk if auto-translated"]];
const scopeRows=headers.map(h=>{const d=counts(h).length; const mapped=categoryFields.includes(h)?"Mapped in this workbook":fieldRows.find(x=>x[0]===h)?.[4]||"Review"; let next="No change"; if(["settlement","origin_place"].includes(h))next="Historical toponym/transliteration lookup"; if(["legal_status","family_status","occupation","illness"].includes(h))next="Dedicated reviewed vocabulary lookup"; if(["name_raw","name_alias"].includes(h))next="One transliteration standard; no translation"; if(["comments","household_details"].includes(h))next="Record-level translation with Russian retained"; return [h,d,mapped,next,(d>100&&next!=="No change")?"High — free text or many proper names":"Low/controlled"];});
scope.getRangeByIndexes(1,0,scopeRows.length,5).values=scopeRows;

for(const sh of wb.worksheets.items){sh.showGridLines=false; const used=sh.getUsedRange(); used.format.font={name:"Aptos",size:10,color:"#1F2937"}; used.format.verticalAlignment="top"; used.format.wrapText=true; used.format.borders={preset:"all",style:"thin",color:"#D9E2F3"}; const cols=used.columnCount; sh.getRangeByIndexes(0,0,1,cols).format={fill:"#183B56",font:{bold:true,color:"#FFFFFF",size:11},verticalAlignment:"center",wrapText:true}; sh.freezePanes.freezeRows(1); used.format.autofitColumns(); used.format.autofitRows(); for(let c=0;c<cols;c++){const col=sh.getRangeByIndexes(0,c,used.rowCount,1); if(col.format.columnWidth>38)col.format.columnWidth=38;} }
summary.getRange("A1:H1").format={fill:"#0B6E69",font:{bold:true,color:"#FFFFFF",size:16},horizontalAlignment:"center",verticalAlignment:"center"}; summary.getRange("A14:H14").format={fill:"#C88A2B",font:{bold:true,color:"#FFFFFF",size:11}}; summary.getRange("A15:H18").format={fill:"#FFF4D6",font:{color:"#4A3420",size:11},wrapText:true}; summary.getRange("A1:H1").format.rowHeight=30; summary.getRange("A:B").format.columnWidth=30; summary.getRange("B:B").format.columnWidth=75;
cats.getRange("C2:C"+(catRows.length+1)).format.numberFormat="#,##0";
await fs.mkdir(outputDir,{recursive:true});
for(const sh of wb.worksheets.items){const prev=await wb.render({sheetName:sh.name,autoCrop:"all",scale:1,format:"png"}); await fs.writeFile(path.join(outputDir,`preview_${sh.name.replace(/[^a-z0-9]+/gi,"_")}.png`),new Uint8Array(await prev.arrayBuffer()));}
const out=await SpreadsheetFile.exportXlsx(wb); await out.save(outputPath);
console.log(JSON.stringify({outputPath,records:data.length,columns:headers.length,categoryRows:catRows.length,sheets:wb.worksheets.items.map(s=>s.name)}));
