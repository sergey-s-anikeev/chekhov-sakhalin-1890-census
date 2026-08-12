import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const root=path.resolve(".");
const sourcePath=path.join(root,"data/processed/clean_sakhalin_1890_ru_v5_20260731.csv");
const stageDir=path.join(root,"data/staging/archive_code_p000107_20260809");
const qaDir=path.join(root,"outputs/qa/archive_code_p000107_20260809");
const stagePath=path.join(stageDir,"clean_sakhalin_1890_ru_v5_20260731_archive_code_staged.csv");
const corrected="ДМЧ (Ялта). КП № 1716.";

function parseCsv(text){const rows=[];let row=[],field="",quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(quoted){if(c==='"'&&text[i+1]==='"'){field+='"';i++;}else if(c==='"')quoted=false;else field+=c;}else if(c==='"')quoted=true;else if(c===','){row.push(field);field="";}else if(c==='\n'){row.push(field.replace(/\r$/,""));rows.push(row);row=[];field="";}else field+=c;}if(field.length||row.length){row.push(field.replace(/\r$/,""));rows.push(row);}return rows;}
function encodeCsv(rows){return rows.map(row=>row.map(v=>{const s=v??"";return /[",\r\n]/.test(s)?`"${s.replaceAll('"','""')}"`:s;}).join(",")).join("\r\n")+"\r\n";}
const sourceText=await fs.readFile(sourcePath,"utf8"); const rows=parseCsv(sourceText); const header=rows[0].map((v,i)=>i===0?v.replace(/^\uFEFF/,""):v);
const personIndex=header.indexOf("person_id"),notesIndex=header.indexOf("notes_raw"); if(personIndex<0||notesIndex<0)throw new Error("Required columns missing");
const matches=rows.slice(1).filter(r=>r[personIndex]==="P000107"); if(matches.length!==1)throw new Error(`Expected one P000107 row, found ${matches.length}`);
if(matches[0][notesIndex]!=="")throw new Error(`P000107 notes_raw is not blank: ${matches[0][notesIndex]}`); matches[0][notesIndex]=corrected;
const stagedText=encodeCsv([header,...rows.slice(1)]); await fs.mkdir(stageDir,{recursive:true});await fs.mkdir(qaDir,{recursive:true});await fs.writeFile(stagePath,stagedText,"utf8");
const qa={status:"PASS",date:"2026-08-09",source:"data/processed/clean_sakhalin_1890_ru_v5_20260731.csv",staged_output:"data/staging/archive_code_p000107_20260809/clean_sakhalin_1890_ru_v5_20260731_archive_code_staged.csv",records:rows.length-1,columns:header.length,changed_records:1,changed_cells:1,person_id:"P000107",field:"notes_raw",old_value:"",new_value:corrected,row_order_preserved:true,schema_preserved:true,canonical_modified:false,source_sha256:crypto.createHash("sha256").update(sourceText).digest("hex"),staged_sha256:crypto.createHash("sha256").update(stagedText).digest("hex")};
await fs.writeFile(path.join(qaDir,"archive_code_p000107_diff_20260809.csv"),encodeCsv([["person_id","field","old_value","new_value"],["P000107","notes_raw","",corrected]]),"utf8");await fs.writeFile(path.join(qaDir,"archive_code_p000107_qa_20260809.json"),JSON.stringify(qa,null,2)+"\n","utf8");console.log(JSON.stringify(qa));
