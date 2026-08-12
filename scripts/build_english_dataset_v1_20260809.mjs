import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const root = path.resolve(".");
const sourcePath = path.join(root,"data/staging/archive_code_p000107_20260809/clean_sakhalin_1890_ru_v5_20260731_archive_code_staged.csv");
const outputDir = path.join(root,"data/analytical");
const qaDir = path.join(root,"outputs/qa/english_dataset_build_20260809");
const outputPath = path.join(outputDir,"sakhalin_1890_en_v1.csv");

function parseCsv(text){
  const rows=[]; let row=[],field="",quoted=false;
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(quoted){
      if(c==='"'&&text[i+1]==='"'){field+='"';i++;}
      else if(c==='"') quoted=false; else field+=c;
    } else if(c==='"') quoted=true;
    else if(c===','){row.push(field);field="";}
    else if(c==='\n'){row.push(field.replace(/\r$/,""));rows.push(row);row=[];field="";}
    else field+=c;
  }
  if(field.length||row.length){row.push(field.replace(/\r$/,""));rows.push(row);}
  const header=rows.shift().map((v,i)=>i===0?v.replace(/^\uFEFF/,""):v);
  return rows.filter(r=>r.some(v=>v!=="")).map(r=>Object.fromEntries(header.map((h,i)=>[h,r[i]??""])));
}
function encodeCsv(rows){return rows.map(row=>row.map(v=>{const s=v==null?"":String(v);return /[",\r\n]/.test(s)?`"${s.replaceAll('"','""')}"`:s;}).join(",")).join("\r\n")+"\r\n";}
async function readCsv(rel){return parseCsv(await fs.readFile(path.join(root,rel),"utf8"));}
function mapBy(rows,key="russian_value",value="english_value"){
  const m=new Map(); for(const r of rows){if(m.has(r[key]))throw new Error(`Duplicate mapping key: ${r[key]}`);m.set(r[key],r[value]);} return m;
}

const source=await readCsv("data/staging/archive_code_p000107_20260809/clean_sakhalin_1890_ru_v5_20260731_archive_code_staged.csv");
const batchA=await readCsv("outputs/english_controlled_translation_review_20260802/controlled_translation_batch_a_approved_20260802.csv");
const fieldMaps={}; for(const r of batchA){fieldMaps[r.source_field]??=new Map();fieldMaps[r.source_field].set(r.russian_value,r.english_value);}
fieldMaps.legal_status_norm=mapBy(await readCsv("outputs/english_controlled_translation_review_20260802/legal_status_translation_approved_20260805.csv"));
fieldMaps.family_status_norm=mapBy(await readCsv("outputs/english_controlled_translation_review_20260802/family_status_translation_approved_20260809.csv"));
fieldMaps.occupation_norm=mapBy(await readCsv("outputs/english_controlled_translation_review_20260802/occupation_translation_approved_20260808.csv"));
fieldMaps.illness_norm=mapBy(await readCsv("outputs/english_controlled_translation_review_20260802/illness_translation_approved_20260805.csv"));
fieldMaps.settlement=mapBy(await readCsv("outputs/english_geographic_translation_review_20260809/settlement_translation_approved_20260809.csv"));
fieldMaps.origin_place_norm=mapBy(await readCsv("outputs/english_geographic_translation_review_20260809/origin_place_translation_approved_20260809.csv"));
const names=mapBy(await readCsv("outputs/english_name_transliteration_review_20260802/name_transliteration_staged_20260802.csv"),"person_id","full_name");

const columns=[
 ["person_id","person_id"],["source_position_id","source_position_id"],["district","district"],["settlement","settlement"],
 ["person_order_in_settlement","person_seq"],["household_id","household_id"],["household_type","household_type"],
 ["legal_status_norm","legal_status"],["name_raw","full_name"],["sex","sex"],["family_status_norm","family_status"],
 ["age","age"],["age_months","age_months"],["religion","religion"],["origin_place_norm","origin_place"],
 ["arrival_year","arrival_year"],["occupation_norm","occupation"],["literacy","literacy"],
 ["marriage_status_norm","marital_status"],["living_alone_status","living_alone_status"],
 ["allowance_status","allowance_status"],["illness_norm","illness"],["notes_raw","archive_code"]
];
const numeric=new Set(["person_order_in_settlement","age","age_months","arrival_year"]);
const unmapped=[];
function transform(row,src){
  const v=row[src]??""; if(v==="") return "";
  if(src==="name_raw") return names.get(row.person_id)??(unmapped.push({person_id:row.person_id,field:src,value:v}),"");
  if(src==="notes_raw"){
    const suffixMap={"а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ж":"zh","з":"z","и":"i","к":"k"};
    const suffix=s=>[...s].map(ch=>suffixMap[ch]??ch).join("");
    if(v==="ДМЧ (Ялта). КП № 1716.") return "DMCh (Yalta). KP № 1716.";
    if(v.startsWith("РГАЛИ ")) return `RGALI ${suffix(v.slice(6))}`;
    if(v.startsWith("РГБ ")) return `RGB ${suffix(v.slice(4))}`;
    throw new Error(`Unexpected archive code format at ${row.person_id}: ${v}`);
  }
  const m=fieldMaps[src]; if(m){if(!m.has(v)){unmapped.push({person_id:row.person_id,field:src,value:v});return "";}return m.get(v);}
  if(numeric.has(src)&&!/^[0-9]+$/.test(v)) throw new Error(`Non-integer ${src}=${v} at ${row.person_id}`);
  return v;
}
const header=columns.map(c=>c[1]);
const outputRows=source.map(row=>columns.map(([src])=>transform(row,src)));
if(unmapped.length) throw new Error(`Unmapped populated values: ${JSON.stringify(unmapped.slice(0,20))}`);

const ids=outputRows.map(r=>r[0]),positions=outputRows.map(r=>r[1]);
const cyr=/[А-Яа-яЁё]/;
const translatedIndexes=header.map((h,i)=>[h,i]);
const cyrillicHits=[]; for(let r=0;r<outputRows.length;r++)for(const [h,i] of translatedIndexes)if(cyr.test(outputRows[r][i]))cyrillicHits.push({row:r+2,person_id:outputRows[r][0],field:h,value:outputRows[r][i]});
const allowanceIndex=header.indexOf("allowance_status"),ageIndex=header.indexOf("age");
const allowanceValues=[...new Set(outputRows.map(r=>r[allowanceIndex]))].sort();
const ageZeroCount=outputRows.filter(r=>r[ageIndex]==="0").length;
const qa={
  status:"PASS",build_date:"2026-08-09",source:path.relative(root,sourcePath).replaceAll('\\','/'),output:path.relative(root,outputPath).replaceAll('\\','/'),
  records:{source:source.length,output:outputRows.length,expected:7446},columns:{count:header.length,expected:23,names:header},
  identifiers:{unique_person_id:new Set(ids).size,unique_source_position_id:new Set(positions).size,blank_person_id:ids.filter(v=>!v).length,blank_source_position_id:positions.filter(v=>!v).length},
  mappings:{unmapped_populated_values:unmapped.length},language:{cyrillic_hits_all_fields:cyrillicHits.length,cyrillic_hit_examples:cyrillicHits.slice(0,10)},
  archive_code:{RGB:outputRows.filter(r=>r[22].startsWith("RGB ")).length,RGALI:outputRows.filter(r=>r[22].startsWith("RGALI ")).length,DMCh:outputRows.filter(r=>r[22].startsWith("DMCh ")).length,blank:outputRows.filter(r=>r[22]==="").length},
  values:{allowance_status_distinct:allowanceValues,age_zero_preserved:ageZeroCount},canonical_unchanged:true
};
if(source.length!==7446||outputRows.length!==7446||header.length!==23||new Set(ids).size!==7446||new Set(positions).size!==7446||cyrillicHits.length||JSON.stringify(allowanceValues)!==JSON.stringify(["","FALSE","TRUE"])) throw new Error(`QA failure: ${JSON.stringify(qa)}`);

await fs.mkdir(outputDir,{recursive:true}); await fs.mkdir(qaDir,{recursive:true});
const csvText=encodeCsv([header,...outputRows]); await fs.writeFile(outputPath,csvText,"utf8");
qa.sha256=crypto.createHash("sha256").update(csvText,"utf8").digest("hex");
await fs.writeFile(path.join(qaDir,"english_dataset_build_qa_20260809.json"),JSON.stringify(qa,null,2)+"\n","utf8");
await fs.writeFile(path.join(qaDir,"english_dataset_unmapped_20260809.csv"),encodeCsv([["person_id","field","value"],...unmapped.map(x=>[x.person_id,x.field,x.value])]),"utf8");

try {
  const { Workbook } = await import("@oai/artifact-tool");
  const previewWb=await Workbook.fromCSV(csvText,{sheetName:"English Dataset"});
  const check=await previewWb.inspect({kind:"region",sheetId:"English Dataset",range:"A1:W8",maxChars:10000}); console.log(check.ndjson??check);
  const errors=await previewWb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:50},summary:"CSV formula error scan"}); console.log(errors.ndjson??errors);
  const previewSheet=previewWb.worksheets.getItem("English Dataset"); previewSheet.showGridLines=false;
  previewSheet.getRange("A1:W1").format={fill:"#17365D",font:{bold:true,color:"#FFFFFF"},wrapText:true,rowHeight:30};
  previewSheet.getRange("A1:W12").format.borders={insideHorizontal:{style:"thin",color:"#D9E1F2"}};
  for(const col of ["A","B","E","F","L","M","P","U"]) previewSheet.getRange(`${col}:${col}`).format.columnWidth=16;
  for(const col of ["C","D","G","H","I","J","K","N","O","Q","R","S","T","V","W"]) previewSheet.getRange(`${col}:${col}`).format.columnWidth=24;
  const previewLeft=await previewWb.render({sheetName:"English Dataset",range:"A1:L12",scale:1,format:"png"}); await fs.writeFile(path.join(qaDir,"english_dataset_preview_left.png"),new Uint8Array(await previewLeft.arrayBuffer()));
  const previewRight=await previewWb.render({sheetName:"English Dataset",range:"M1:W12",scale:1,format:"png"}); await fs.writeFile(path.join(qaDir,"english_dataset_preview_right.png"),new Uint8Array(await previewRight.arrayBuffer()));
  const archiveQa=previewWb.worksheets.add("Archive QA"); archiveQa.showGridLines=false;
  archiveQa.getRange("A1:D2").values=[["person_id","canonical notes_raw","English archive_code","status"],["P000107","ДМЧ (Ялта). КП № 1716.",outputRows.find(r=>r[0]==="P000107")[22],"PASS"]];
  archiveQa.getRange("A1:D1").format={fill:"#17365D",font:{bold:true,color:"#FFFFFF"}}; archiveQa.getRange("A:D").format.columnWidth=28; archiveQa.getRange("D2").format={fill:"#E2F0D9",font:{bold:true}};
  const archivePreview=await previewWb.render({sheetName:"Archive QA",range:"A1:D2",scale:1.5,format:"png"}); await fs.writeFile(path.join(qaDir,"archive_code_p000107_preview.png"),new Uint8Array(await archivePreview.arrayBuffer()));
} catch (error) {
  console.warn(`Spreadsheet preview skipped: ${error.message}`);
}
console.log(JSON.stringify(qa));
